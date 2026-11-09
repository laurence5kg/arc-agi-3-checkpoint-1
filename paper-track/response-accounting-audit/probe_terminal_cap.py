"""Mocked terminal-cap probe against a frozen source. No game Python is executed."""
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile


def probe(source, output):
    os.environ.update(ARC3_REASONING_HISTORY_KEY='reasoning_content', ARC3_STUB_DEAD_REASONING='0',
                      LOCAL_ANALYZER_CONTEXT_WINDOW='131072', LOCAL_ANALYZER_MAX_OUTPUT='12288')
    sys.path.insert(0, str(source))
    from inference.agent import tool_agent as module
    from inference.agent.runtime_state import Frame, write_runtime_state
    source_hash = hashlib.sha256((source/'inference/agent/tool_agent.py').read_bytes()).hexdigest()
    original_request = module.requests.sessions.Session.request
    def forbid_network(*args, **kwargs):
        raise AssertionError('The local cap probe must not access the network')
    module.requests.sessions.Session.request = forbid_network
    try:
        with tempfile.TemporaryDirectory(prefix='paper-cap-') as temp:
            state_path = Path(temp)/'state.json'
            write_runtime_state(state_path,current_frame=Frame(grid=((0,),),step=0,level=1),history=[])
            agent=module.ToolAgent(model='fixture',provider='vllm',base_url='http://127.0.0.1:9999/v1')
            agent._yield_tokens=None
            requests=[]
            def completion(messages,**kwargs):
                requests.append(json.loads(json.dumps(messages)))
                i=len(requests)
                return module._ChatCompletionResult(message={'role':'assistant','content':'',
                    'reasoning_content':f'CAP_REASONING_{i}',
                    'tool_calls':[{'id':f'cap-{i}','type':'function','function':{'name':'python',
                        'arguments':json.dumps({'code':'def partial_helper():\n    return None'})}}]},
                    finish_reason='length',usage={'completion_tokens':512})
            def dispatch(*args,**kwargs):
                raise AssertionError('A capped call reached dispatch')
            agent._chat_completion=completion
            agent._dispatch_tool=dispatch
            result=agent.analyze(state_path,0,valid_actions=['UP'])
            assert len(requests)==4 and agent.generated_tokens==2048
            assert result.reasoning=='CAP_REASONING_3'
            assert 'output-capped' in result.token_failure
            report={'scope':'Synthetic post-competition CPU probe; actual frozen guard; no neural performance claim',
                'source_file_sha256':source_hash,'response_count':4,'completion_tokens':2048,
                'tool_dispatches':0,'termination_reason':result.token_failure,
                'returned_reasoning':result.reasoning,'fourth_response_reasoning':'CAP_REASONING_4',
                'fourth_reasoning_returned':False,'preservation_claim_must_exclude_terminal_fourth_reply':True}
    finally:
        module.requests.sessions.Session.request=original_request
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(probe(a.source,a.output),indent=2))
