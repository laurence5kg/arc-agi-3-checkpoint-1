"""Reproduce aggregate paper measurements with Python's standard library only."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import statistics


def analyze(root):
    data=json.loads((root/'data/experiments.json').read_text(encoding='utf-8'))
    checks=[]
    def check(ok,label):
        if not ok: raise AssertionError(label)
        checks.append(label)
    ledgers={}
    for name, row in data['accounting'].items():
        check(row['api_tokens']==row['action_tokens']+row['terminal_tokens'],name+' completed-response conservation')
        check(row['pending_requests']>0,name+' pending work retained as unknown')
        ledgers[name]={'completed_tokens':row['api_tokens'],'terminal_share_percent':100*row['terminal_tokens']/row['api_tokens'],
                      'unanswered_requests':row['pending_requests'],'complete_server_billing':False}
    n=data['native_throughput']
    tps=n['completed_tokens']/n['common_wall_seconds']
    check(abs(tps-n['reported_tps'])<1e-10,'Common-wall throughput')
    pairs=data['retention']['pairs']
    check(len(pairs)==10 and len({x['game'] for x in pairs})==5,'Retention units: five games, two blocks')
    check(len({(x['game'],x['block']) for x in pairs})==10,'One observation per game/block/arm')
    ma=statistics.mean(x['A'] for x in pairs);mb=statistics.mean(x['B'] for x in pairs)
    check(abs(ma-data['retention']['mean_A'])<1e-10 and abs(mb-data['retention']['mean_B'])<1e-10,'Retention means')
    comparisons={}
    arms=data['comparison_arms'];games=list(arms['R0']['per_game_scores'])
    for name,row in arms.items():
        check(set(row['per_game_scores'])==set(games),name+' matched games')
        check(all(len(x)==4 for x in row['per_game_scores'].values()),name+' four passes per game')
        check(abs(statistics.mean(statistics.mean(v) for v in row['per_game_scores'].values())-row['score_mean'])<1e-10,name+' aggregate mean')
    for name in ['R1','R2']:
        delta=[statistics.mean(arms[name]['per_game_scores'][g])-statistics.mean(arms['R0']['per_game_scores'][g]) for g in games]
        rng=random.Random(20261024);draws=12000;alpha=.05/3
        distribution=sorted(statistics.mean(rng.choices(delta,k=len(delta))) for _ in range(draws))
        interval=[distribution[int(alpha/2*draws)],distribution[min(draws-1,int((1-alpha/2)*draws))]]
        expected=data['comparisons'][name+'_vs_R0']
        check(abs(statistics.mean(delta)-expected['mean_delta'])<1e-10,name+' paired mean')
        check(all(abs(a-b)<1e-10 for a,b in zip(interval,expected['paired_game_interval'])),name+' bootstrap reproduction')
        comparisons[name]={'delta':statistics.mean(delta),'interval':interval,'resampling_units':25,'draws':draws,'alpha':alpha}
    caps=data['output_caps']
    check(caps['invalid_python']+caps['parseable_python']==caps['tool_payloads']==9,'Capped payload classification')
    check(data['feature_adoption']['added_api_calls']==0,'Zero observed added model API calls')
    q=data['qualified_context']
    check(q['max_observed_prompt']+q['full_reply_allowance']<=q['harness_capacity'],'Observed full-reply context capacity')
    # Interpretive checks on new local boundary evidence, not neural performance tests.
    boundary=data['terminal_boundary']
    check(boundary['completion_tokens']==2048 and boundary['tool_dispatches']==0,'Terminal cap usage and dispatch')
    check(boundary['fourth_reasoning_returned'] is False,'Terminal reasoning limitation preserved')
    return {'checks_passed':len(checks),'checks':checks,'accounting':ledgers,'native_completed_api_tps':tps,
        'retention':{'A':ma,'B':mb,'delta':mb-ma,'independent_games':5,'significance_claim':False},
        'comparisons':comparisons,'public_data_is_held_out':False,'new_gameplay':False}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
    result=analyze(Path(__file__).resolve().parent)
    rendered=json.dumps(result,indent=2)+'\n'
    if a.output:a.output.write_text(rendered,encoding='utf-8')
    print(rendered)
