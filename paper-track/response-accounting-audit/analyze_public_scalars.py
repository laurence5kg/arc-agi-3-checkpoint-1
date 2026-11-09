"""Reproduce disjoint token shares and cap counts from portable per-response records."""
from collections import Counter
from pathlib import Path
import argparse
import ast
import json

def analyze(root):
    data=json.loads((root/'data/response_audit.json').read_text(encoding='utf-8'))
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
    estimator=json.loads((root/'data/r0_estimator_deltas.json').read_text(encoding='utf-8'))['rows']
    check(len(estimator)==8840)
    check(all(r['returned_prompt_tokens']-r['estimated_prompt_tokens']==11 for r in estimator))
    return {'checks_passed':checks,'token_percentages':results,'estimator_rows_checked':len(estimator),
            'scope':'Scalar reconstruction only; original payload syntax and dispatch are not replayed','new_gameplay':False}

if __name__=='__main__':
    print(json.dumps(analyze(Path(__file__).resolve().parent),indent=2))
