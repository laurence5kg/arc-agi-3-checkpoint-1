"""Reproduce disjoint token shares and cap counts from portable per-response records."""
from collections import Counter
from pathlib import Path
import argparse
import ast
import json

def analyze(root):
    data=json.loads((root/'data/response_audit.json').read_text(encoding='utf-8'))
    cases=json.loads((root/'data/pooled_capped_responses.json').read_text(encoding='utf-8'))
    checks=0;results={}
    def check(condition):
        nonlocal checks
        assert condition
        checks+=1
    for label,pop in data['populations'].items():
        rows=pop['response_rows'];tot=pop['totals'];buckets={k:Counter() for k in pop['buckets']}
        check(len(rows)==tot['responses']);check(sum(r['tokens'] for r in rows)==tot['tokens'])
        check(tot['history_tokens']+tot['terminal_tokens']==tot['tokens'])
        check(sum(r['actions'] for r in rows)==tot['actions'])
        check(len({(r['run'],r['response']) for r in rows})==len(rows))
        for r in rows:buckets[r['category']].update(tokens=r['tokens'],responses=1)
        for k,b in buckets.items():
            check(b['tokens']==pop['buckets'][k]['tokens']);check(b['responses']==pop['buckets'][k]['responses'])
        check(buckets['terminal']['tokens']==tot['terminal_tokens'])
        check(sum(r['tokens'] for r in rows if r['capped'])==tot['capped_tokens'])
        check(sum(r['capped'] for r in rows)==tot['capped_responses'])
        check(sum(r['tokens'] for r in rows if r['capped'] and r['tool_calls'])==tot.get('capped_tool_tokens',0))
        check(sum(r['capped'] and bool(r['tool_calls']) for r in rows)==tot.get('capped_tool_responses',0))
        results[label]={k:100*b['tokens']/tot['tokens'] for k,b in buckets.items()}
    check(len(cases)==29)
    classes=Counter()
    for case in cases:
        labels=[]
        for call in case['calls']:
            args=call['function']['arguments'];args=json.loads(args) if isinstance(args,str) else args
            code=args.get('code')
            if not code:labels.append('missing_code')
            else:
                try:ast.parse(code);labels.append('python_parses_but_response_is_capped')
                except SyntaxError:labels.append('incomplete_or_invalid_python')
        check(labels==case['classification']);classes.update(labels)
        row=next(r for r in data['populations'][case['arm']]['response_rows'] if r['run']==case['public_game_run'] and r['response']==case['response_index'])
        check(row['capped'] and row['actions']==case['recorded_environment_actions'] and row['tokens']==case['completion_tokens'])
    check(dict(classes)=={'incomplete_or_invalid_python':20,'python_parses_but_response_is_capped':8,'missing_code':1})
    check(sum(c['recorded_environment_actions'] for c in cases)==1)
    check(sum(c['completion_tokens'] for c in cases)==356352)
    check(sum(data['populations'][p]['totals']['capped_tokens'] for p in ['R0','R1','R2'])==3624960)
    return {'checks_passed':checks,'token_percentages':results,'pooled_caps':len(cases),'parse_counts':dict(classes),
            'capped_tool_actions':1,'harm_or_gain_established':False,'new_gameplay':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
    result=analyze(Path(__file__).resolve().parent);text=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(text,encoding='utf-8')
    print(text)
