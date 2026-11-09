"""Replay saved capped calls through the frozen guard, with all dispatch mocked."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile


def replay(root):
    os.environ.update(ARC3_REASONING_HISTORY_KEY='reasoning_content',ARC3_STUB_DEAD_REASONING='0',
                      LOCAL_ANALYZER_CONTEXT_WINDOW='131072',LOCAL_ANALYZER_MAX_OUTPUT='12288')
    sys.path.insert(0,str(root/'runtime'))
    from inference.agent import tool_agent as module
    from inference.agent.runtime_state import Frame,write_runtime_state
    cases=json.loads((root/'data/pooled_capped_responses.json').read_text(encoding='utf-8'))
    old=module.requests.sessions.Session.request
    def forbid_network(*args,**kwargs): raise AssertionError('Network access in CPU replay')
    module.requests.sessions.Session.request=forbid_network
    rows=[]
    try:
        with tempfile.TemporaryDirectory(prefix='paper-replay-') as folder:
            for i,case in enumerate(cases):
                path=Path(folder)/f'{i}.json'
                write_runtime_state(path,current_frame=Frame(grid=((0,),),step=0,level=1),history=[])
                agent=module.ToolAgent(model='fixture',provider='vllm',base_url='http://127.0.0.1:9999/v1')
                agent._yield_tokens=None
                requests=[];dispatched=[]
                def completion(messages,**kwargs):
                    requests.append(json.loads(json.dumps(messages)))
                    if len(requests)==1:
                        return module._ChatCompletionResult(message={'role':'assistant','content':'',
                            'reasoning_content':'RECOVERABLE_REASONING','tool_calls':case['calls']},
                            finish_reason='length',usage={'completion_tokens':case['completion_tokens']})
                    return module._ChatCompletionResult(message={'role':'assistant','content':'','tool_calls':[
                        {'id':'safe','type':'function','function':{'name':'python','arguments':'{"code":"SAFE_MARKER"}'}}]},
                        finish_reason='tool_calls',usage={'completion_tokens':7})
                def dispatch(state_path,name,args):
                    assert args=={'code':'SAFE_MARKER'},'Saved game code reached dispatch'
                    dispatched.append(args)
                    return module._ToolDispatchResult(content='Synthetic marker',step_executed=True)
                agent._chat_completion=completion;agent._dispatch_tool=dispatch
                agent.analyze(path,0,valid_actions=['UP'])
                assert len(requests)==2 and len(dispatched)==1
                assert agent.generated_tokens==case['completion_tokens']+7
                assert any(m.get('reasoning_content')=='RECOVERABLE_REASONING' for m in requests[1])
                old_ids={c['id'] for c in case['calls']}
                assert not any(c.get('id') in old_ids for m in requests[1] for c in m.get('tool_calls',[]))
                rows.append({'case':case['case'],'recovered':True,'original_code_executed':False,
                             'reported_completion_tokens':agent.generated_tokens})
    finally:
        module.requests.sessions.Session.request=old
    assert len(rows)==29
    return {'scope':'CPU response replay; no real gameplay','cases':rows,'network_used':False,'saved_python_executed':False}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
    result=replay(Path(__file__).resolve().parent)
    text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text,encoding='utf-8')
    print(text)
