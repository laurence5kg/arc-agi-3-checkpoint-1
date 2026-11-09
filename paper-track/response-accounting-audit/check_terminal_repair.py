"""Test a labeled post-hoc patch in temporary source copies. No deployment changes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

OLD='''                if self._test1_bad_calls>=4:
                    raise TokenContractError("four consecutive malformed or output-capped tool-call responses")'''
NEW='''                if self._test1_bad_calls>=4:
                    # Post-hoc repair: return the latest nonempty terminal reasoning.
                    # This changes neither dispatch nor the four-response stop rule.
                    if reasoning:
                        captured_reasoning = reasoning
                        append_transcript("THINKING", reasoning)
                    raise TokenContractError("four consecutive malformed or output-capped tool-call responses")'''

def child(source,mode,repaired):
    os.environ.update(ARC3_REASONING_HISTORY_KEY='reasoning_content',ARC3_STUB_DEAD_REASONING='0',
        LOCAL_ANALYZER_CONTEXT_WINDOW='131072',LOCAL_ANALYZER_MAX_OUTPUT='12288')
    sys.path.insert(0,str(source))
    from inference.agent import tool_agent as module
    from inference.agent.runtime_state import Frame,write_runtime_state
    def forbid(*a,**k):raise AssertionError('Unexpected network or dispatch')
    module.requests.sessions.Session.request=forbid
    with tempfile.TemporaryDirectory(prefix='paper-posthoc-state-') as td:
        state=Path(td)/'state.json';write_runtime_state(state,current_frame=Frame(grid=((0,),),step=0,level=1),history=[])
        agent=module.ToolAgent(model='fixture',provider='vllm',base_url='http://127.0.0.1:9999/v1');agent._yield_tokens=None
        calls=[]
        def completion(messages,**kwargs):
            calls.append(1);i=len(calls);assert i<=4
            reasoning='' if mode=='empty_final' and i==4 else f'CAP_REASONING_{i}'
            arguments='{"code":' if mode=='malformed' else '{"code":"SAFE_BUT_CAPPED"}'
            return module._ChatCompletionResult(message={'role':'assistant','content':'','reasoning_content':reasoning,
                'tool_calls':[{'id':f'cap-{i}','type':'function','function':{'name':'python','arguments':arguments}}]},
                finish_reason='tool_calls' if mode=='malformed' else 'length',usage={'completion_tokens':512})
        agent._chat_completion=completion;agent._dispatch_tool=forbid
        result=agent.analyze(state,0,valid_actions=['UP'])
        expected='CAP_REASONING_4' if repaired and mode!='empty_final' else 'CAP_REASONING_3'
        assert result.reasoning==expected,(result.reasoning,expected)
        assert len(calls)==4 and agent.generated_tokens==2048 and 'four consecutive' in result.token_failure
        assert not result.step_executed
        return {'mode':mode,'repaired':repaired,'returned_reasoning':result.reasoning,'completion_tokens':2048,
                'requests':4,'tool_dispatches':0,'network_used':False}

def main(root):
    source=root/'runtime';original=source/'inference/agent/tool_agent.py'
    digest=hashlib.sha256(original.read_bytes()).hexdigest()
    manifest=json.loads((root/'runtime_manifest.json').read_text())
    assert next(r['sha256'] for r in manifest['files'] if r['path']=='runtime/inference/agent/tool_agent.py')==digest
    text=original.read_text(encoding='utf-8');assert text.count(OLD)==1
    rows=[]
    with tempfile.TemporaryDirectory(prefix='paper-posthoc-runtime-') as td:
        copied=Path(td)/'runtime';shutil.copytree(source,copied)
        patched=copied/'inference/agent/tool_agent.py'
        # Canonical LF bytes match the published patch manifest on every host.
        patched.write_bytes(text.replace(OLD,NEW).encode('utf-8'))
        patched_hash=hashlib.sha256(patched.read_bytes()).hexdigest()
        for repaired in [False,True]:
            for mode in ['length','malformed','empty_final']:
                command=[sys.executable,'-X','utf8',str(Path(__file__).resolve()),'--child-source',str(copied if repaired else source),'--mode',mode]
                if repaired:command.append('--repaired')
                result=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',check=True,timeout=45)
                rows.append(json.loads(result.stdout))
    assert hashlib.sha256(original.read_bytes()).hexdigest()==digest
    return {'scope':'Post-hoc CPU-only repair; never part of the scored submission; no neural score evidence',
        'frozen_source_sha256':digest,'temporary_patched_source_sha256':patched_hash,'frozen_source_unchanged':True,'cases':rows}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--output',type=Path);p.add_argument('--child-source',type=Path);p.add_argument('--mode');p.add_argument('--repaired',action='store_true');a=p.parse_args()
    result=child(a.child_source,a.mode,a.repaired) if a.child_source else main(a.root)
    text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text,encoding='utf-8')
    print(text)
