"""Track only the launched server tree and verify bounded GPU release."""
from pathlib import Path
import json
import os
import signal
import subprocess
import threading
import time
from inference.test1.lifecycle import stop_owned_process,bind_owned_server


def proc_snapshot():
    result={}
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit(): continue
        try:
            text=(entry/'stat').read_text()
            fields=text[text.rfind(')')+2:].split()
            result[int(entry.name)]={'state':fields[0],'ppid':int(fields[1]),'group':int(fields[2]),
                'session':int(fields[3]),'start':int(fields[19])}
        except (OSError,ValueError,IndexError):
            continue
    return result


def gpu_snapshot():
    result=subprocess.run(['nvidia-smi','--query-compute-apps=pid,used_gpu_memory',
        '--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5)
    if result.returncode: raise RuntimeError('nvidia-smi cleanup query failed')
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


class Ownership:
    def __init__(self,process):
        self.process=process
        self.known={}
        self.guard=threading.Lock()
        self.close_guard=threading.Lock()
        self.stop=threading.Event()
        self.result=None
        self.errors=[]
        self.root_start=None
        self.refresh()
        if process.pid not in self.known:
            raise RuntimeError('Could not establish ownership of launched server')
        self.root_start=self.known[process.pid]
        self.thread=threading.Thread(target=self.monitor,daemon=True,name='test1-owned-process-tree')
        self.thread.start()

    def refresh(self):
        snapshot=proc_snapshot()
        with self.guard:
            root=snapshot.get(self.process.pid)
            if not self.known and root:
                if root['group']!=self.process.pid or root['session']!=self.process.pid:
                    raise RuntimeError('Server was not launched in its own process session')
                self.known[self.process.pid]=root['start']
            active={pid for pid,start in self.known.items() if pid in snapshot and snapshot[pid]['start']==start}
            changed=True
            while changed:
                changed=False
                for pid,item in snapshot.items():
                    if pid in self.known: continue
                    root_identity_safe=root is None or root['start']==self.root_start
                    in_original_session=(root_identity_safe and self.root_start is not None and item['session']==self.process.pid
                                         and item['start']>=self.root_start)
                    if item['ppid'] in active or in_original_session:
                        self.known[pid]=item['start']
                        active.add(pid)
                        changed=True
            owned={pid:snapshot[pid] for pid,start in self.known.items()
                   if pid in snapshot and snapshot[pid]['start']==start}
        return owned

    def monitor(self):
        while not self.stop.wait(1):
            try: self.refresh()
            except Exception as exc: self.errors.append(type(exc).__name__)

    def terminate_live(self,owned):
        for pid,item in owned.items():
            if item['state'] in ('Z','X'): continue
            # Recheck creation identity just before signaling a retained descendant.
            current=proc_snapshot().get(pid)
            if current and current['start']==self.known[pid]:
                try: os.kill(pid,signal.SIGKILL)
                except ProcessLookupError: pass

    def close(self,timeout=90):
        with self.close_guard:
            if self.result is not None: return self.result
            started=time.monotonic()
            self.refresh()
            stop_owned_process(self.process)
            observations=[]
            stable=0
            while time.monotonic()-started<timeout:
                owned=self.refresh()
                live=[pid for pid,item in owned.items() if item['state'] not in ('Z','X')]
                zombies=[pid for pid,item in owned.items() if item['state']=='Z']
                if live: self.terminate_live(owned)
                try:
                    gpu=gpu_snapshot()
                    gpu_error=None
                except Exception as exc:
                    gpu=None
                    gpu_error=type(exc).__name__
                clean=not live and gpu==[] and self.process.poll() is not None
                stable=stable+1 if clean else 0
                observations.append({'elapsed':time.monotonic()-started,'live_owned_pids':live,
                    'zombie_owned_pids':zombies,'gpu_apps':gpu,'gpu_query_error':gpu_error})
                if stable>=2: break
                time.sleep(1)
            self.stop.set()
            self.thread.join(timeout=2)
            final=observations[-1] if observations else {}
            self.result={'schema_version':1,'verified':stable>=2 and not self.errors,
                'ownership_tracking':True,'known_owned_processes':len(self.known),
                'leader_returncode':self.process.poll(),'live_owned_pids':final.get('live_owned_pids'),
                'zombie_owned_pids':final.get('zombie_owned_pids'),'gpu_apps_after':final.get('gpu_apps'),
                'stable_clean_samples':stable,'tracking_errors':self.errors,'observations':observations,
                'elapsed':time.monotonic()-started}
            return self.result


def register_owned_process(process):
    if os.name!='posix': raise RuntimeError('Real serving cleanup verification requires Linux')
    process._test1_ownership=Ownership(process)
    bind_owned_server(process)
    return process


def close_owned_process(process,timeout=90):
    if process is None: return None
    owner=getattr(process,'_test1_ownership',None)
    if owner is None:
        stop_owned_process(process)
        result={'verified':False,'error':'server ownership was not registered'}
    else:
        result=owner.close(timeout)
    destination=os.environ.get('TEST1_CLEANUP_REPORT')
    if destination:
        Path(destination).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result
