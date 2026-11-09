"""Read saved public runs; reconstruct response/action boundaries without executing model code."""
from collections import Counter
from pathlib import Path
import ast
import hashlib
import json
import re

def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def metadata(part):
    meta=re.split(r'^\[(?:THINKING|ASSISTANT|TOOL CALL|ANALYZER STATUS|USER PROMPT|SYSTEM PROMPT)',part,maxsplit=1,flags=re.M)[0]
    finish=re.match(r'finish_reason: ([^\n]+)',meta).group(1)
    raw=meta.partition('raw_tool_calls:\n')[2].strip()
    shortened=False
    try: calls=json.loads(raw) if raw else []
    except json.JSONDecodeError:
        assert re.search(r'\.\.\. \[truncated \d+ chars\]',raw),'Unexplained damaged call metadata'
        shortened=True;calls=[]
        blocks=re.findall(r'^\[TOOL CALL: python\]\n(.*?)(?=^\[|^---|\Z)',part,re.M|re.S)
        for j,block in enumerate(blocks):
            match=re.search(r'<parameter=code>\n(.*?)\n</parameter>',block,re.S)
            assert match,'Missing complete dispatch payload'
            calls.append({'id':f'recovered-{j}','type':'function','function':{'name':'python','arguments':{'code':match.group(1)}}})
    count=int(re.search(r'^tool_call_count: (\d+)',meta,re.M).group(1))
    assert count==len(calls),(count,len(calls))
    return finish,calls,shortened

def action_owners(tokens,history):
    """Each positive history charge ends a contiguous completion-token prefix.

    Preconditions: strictly positive response usage and atomic charging before dispatch.
    Zero-charge actions belong to the preceding owner, except initial native RESETs.
    No transcript markers or generated Python strings are treated as trusted actions.
    """
    assert all(type(t) is int and t>0 for t in tokens)
    cursor=0;owners=Counter();initial=0;last=None
    for row in history:
        charge=row['generated_tokens'];assert type(charge) is int and charge>=0
        if charge:
            acc=0
            while acc<charge:
                assert cursor<len(tokens),'Action ledger exceeds returned usage'
                acc+=tokens[cursor];cursor+=1
            assert acc==charge,('Non-atomic or misaligned action charge',acc,charge)
            last=cursor-1
        if last is None:
            assert row['action']['id']=='RESET','Unattributed noninitial action'
            initial+=1
        else: owners[last]+=1
    return owners,cursor,initial

def audit(label,folder,native=False):
    summary_path=folder/('benchmark.json' if native else 'test1_experiment_summary.json')
    summary=read(summary_path)
    runs={Path(r['solver_analysis_html']).stem:r for r in summary['game_runs']}
    totals=Counter();buckets={k:Counter() for k in ['action_issuing','non_action_tool','no_call','terminal']}
    cap_parse=Counter();cases=[];run_rows=[];provenance=[];compact_rows=[]
    for path in sorted((folder/'transcripts').glob('*.txt')):
        run=runs[path.stem]
        trace=(folder/(path.stem+'_requests.jsonl')) if native else (folder/'artifacts'/(path.stem+'_tool_runtime_state_token_trace.jsonl'))
        parts=path.read_text(encoding='utf-8').split('[MODEL RESPONSE META]\n')[1:]
        if not trace.exists():
            assert not parts and not run['history'] and run['final_generated_tokens']==0,trace
            assert 'time budget exhausted' in run['solver_note']
            totals['zero_request_unadmitted_episodes']+=1
            continue
        responses=[];requests=0
        with trace.open(encoding='utf-8') as f:
            for line in f:
                row=json.loads(line)
                if row['event']=='request':requests+=1
                if row['event']=='response':responses.append({'finish_reason':row['finish_reason'],'usage':row['usage']})
        assert len(parts)==len(responses),(label,path.stem,len(parts),len(responses))
        tokens=[r['usage']['completion_tokens'] for r in responses]
        owners,boundary,initial=action_owners(tokens,run['history'])
        terminal=sum(tokens[boundary:]);history=sum(h['generated_tokens'] for h in run['history'])
        assert sum(tokens)==history+terminal
        if not native:assert terminal==run['final_generated_tokens'],(path.stem,terminal,run['final_generated_tokens'])
        totals.update(responses=len(tokens),tokens=sum(tokens),history_tokens=history,terminal_tokens=terminal,
                      actions=len(run['history'])-initial,initial_resets=initial,unknown_requests=requests-len(responses),runs_with_responses=bool(tokens))
        run_rows.append({'run':path.stem,'responses':len(tokens),'tokens':sum(tokens),'history_tokens':history,
                         'terminal_tokens':terminal,'terminal_responses':len(tokens)-boundary,'unknown_requests':requests-len(responses),
                         'actions':len(run['history'])-initial,'initial_resets':initial,'state':run['state']})
        for i,(part,response) in enumerate(zip(parts,responses)):
            finish,calls,shortened=metadata(part)
            assert finish==response['finish_reason']
            t=tokens[i];cap=finish=='length';action_count=owners.get(i,0);terminal_response=i>=boundary
            category='terminal' if terminal_response else ('action_issuing' if action_count else ('non_action_tool' if calls else 'no_call'))
            buckets[category].update(responses=1,tokens=t)
            compact_rows.append({'run':path.stem,'response':i,'tokens':t,'category':category,'capped':cap,'tool_calls':len(calls),'actions':action_count})
            totals['shortened_metadata_recovered']+=shortened
            if cap:
                totals.update(capped_responses=1,capped_tokens=t,capped_actions=action_count)
            if cap and calls:
                totals.update(capped_tool_responses=1,capped_tool_tokens=t,capped_tool_actions=action_count,
                              capped_tool_responses_with_actions=bool(action_count))
                labels=[]
                for call in calls:
                    fn=call['function'];assert fn['name']=='python'
                    args=fn['arguments']
                    try:args=json.loads(args) if isinstance(args,str) else args
                    except json.JSONDecodeError:labels.append('invalid_arguments_json');continue
                    code=args.get('code')
                    if not isinstance(code,str) or not code.strip():labels.append('missing_code');continue
                    try:ast.parse(code);labels.append('python_parses_but_response_is_capped')
                    except SyntaxError:labels.append('incomplete_or_invalid_python')
                cap_parse.update(labels)
                cases.append({'case':f'{label}-cap-{len(cases)+1:02d}','arm':label,'public_game_run':path.stem,
                              'response_index':i,'calls':calls,'completion_tokens':t,'classification':labels,
                              'recorded_environment_actions':action_count,'terminal':terminal_response,
                              'dispatch_logged':'[TOOL CALL: python]' in part,
                              'tool_result_logged':'[TOOL RESULT: python]' in part})
        provenance.append({'run':path.stem,'transcript_sha256':sha(path),'usage_log_sha256':sha(trace)})
    assert sum(b['tokens'] for b in buckets.values())==totals['tokens']
    assert sum(b['responses'] for b in buckets.values())==totals['responses']
    assert sum(r['actions'] for r in compact_rows)==totals['actions']
    for bucket in buckets.values(): bucket['token_percent']=100*bucket['tokens']/totals['tokens']
    for k in ['terminal','capped','capped_tool']:totals[k+'_token_percent']=100*totals[k+'_tokens']/totals['tokens']
    result={'label':label,'declared_episodes':len(runs),'totals':dict(totals),'buckets':buckets,
            'cap_parse_counts':dict(cap_parse),'runs':run_rows,'response_rows':compact_rows,
            'source_summary_sha256':sha(summary_path),'provenance':provenance,
            'duration_note':'25-minute per-game native practice' if native else f"{summary['budget_seconds']/3600:g}-hour whole-notebook ceiling; includes startup/cleanup; not per-game duration"}
    return result,cases

def main():
    import argparse
    p=argparse.ArgumentParser(description="Extract saved public-run evidence; never execute saved model code")
    for flag in ['r0','r1','r2','qualification','native']:p.add_argument('--'+flag,type=Path,required=True)
    p.add_argument('--output-dir',type=Path,required=True);a=p.parse_args()
    a.output_dir.mkdir(parents=True,exist_ok=True);rows={};cases=[]
    for label,folder,is_native in [('R0',a.r0,False),('R1',a.r1,False),('R2',a.r2,False),('qualification',a.qualification,False),('native_Franzen',a.native,True)]:
        row,found=audit(label,folder,is_native);rows[label]=row
        if label in ['R0','R1','R2']:cases.extend(found)
    result={'scope':'Saved public-run reanalysis; no gameplay or score-effect estimate',
            'partition':'Terminal suffix first; remaining responses split by exact action-ledger token boundaries and visible calls. Caps are an overlapping flag.','populations':rows}
    (a.output_dir/'response_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (a.output_dir/'pooled_capped_responses.json').write_text(json.dumps(cases,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
