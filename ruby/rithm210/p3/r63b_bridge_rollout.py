"""R63B-P2: permissioned 40-round Partial group trajectory forecast, aggregate-only.

Models are frozen, all six decisions simultaneous. Original personal Value(t)
is supplied only after simulated t action. No original actor/round rows exported.
"""
from collections import defaultdict
from hashlib import sha256
from math import log
from pathlib import Path
from random import Random
from statistics import mean
import argparse
import csv
import io
import json
import zipfile
from r63b_legal_bridge import (APPROVED_SHA,SOURCE_CSV,EXCLUDED,TAU,
    legal_bin,fit_model,predict,load_private_events,bootstrap_diff)


def read_private_tapes(source):
    if sha256(Path(source).read_bytes()).hexdigest()!=APPROVED_SHA:
        raise ValueError('source SHA must match before opening')
    tapes=defaultdict(dict)
    with zipfile.ZipFile(source) as archive:
        with io.TextIOWrapper(archive.open(SOURCE_CSV),encoding='utf-8-sig') as fp:
            for row in csv.DictReader(fp):
                s,sec,t=(int(row[k]) for k in ('session','section','Period'))
                if s in EXCLUDED or sec not in (3,4) or t not in range(1,41):continue
                key=(s,sec,int(row['Group']),int(row['ID']))
                if t in tapes[key]:raise ValueError('duplicate period in value tape')
                tapes[key][t]=(int(row['RouteA']),float(row['Value']),float(row['profit']))
    if len(tapes)!=576 or any(len(v)!=40 for v in tapes.values()):
        raise ValueError('R62 source trajectory support changed')
    return tapes


def cost(a):
    if type(a) is not int or not 0<=a<=6:raise ValueError('occupancy is a count of six')
    return 3*(a-4)**2


def payoff(value,a,route):
    return value - (a if route else 2*(6-a))


def simulate(group, model_by_mask, tapes, coins, *, start='observed', tau=TAU):
    """Transient labelled routes; return ONLY group aggregate cost/moves/stability."""
    if len(group)!=6 or len(coins)!=40 or start not in ('observed','fair'):
        raise ValueError('invalid six-actor 40-round plan')
    group=sorted(group,key=lambda e:e['actor'])
    if any(e['period']!=2 for e in group):raise ValueError('group must be its t2 predecision members')
    if len(tapes)!=6:raise ValueError('need six private exogenous tapes')
    if any(m['tau']!=tau for m in model_by_mask.values()):raise ValueError('memory-clock mismatch')
    if any(set(tape)!=set(range(1,41)) for tape in tapes):
        raise ValueError('each tape must cover full horizon')
    routes=[tape[1][0] for tape in tapes] if start=='observed' else [int(u<.5) for u in coins[0]]
    prev_flips=[e['prior_flips'] for e in group]
    info=[e['info'] for e in group]
    a=sum(routes)
    previous_profit=[payoff(tapes[i][1][1],a,r) for i,r in enumerate(routes)]
    if start=='observed' and any(abs(previous_profit[i]-tapes[i][1][2])>1e-8 for i in range(6)):
        raise ValueError('original first-period reward inconsistency')
    tenure=[1]*6;counts=[0]*6
    total_cost=cost(a);gross=0;a4_count=int(a==4);a4_old_transitions=0;a4_no_switch=0
    for t in range(2,41):
        old_a=a
        probabilities=[]
        for i,e0 in enumerate(group):
            e={'info':info[i], 'previous_route':routes[i], 'prior_flips':prev_flips[i],
               'current_flips':counts[i], 'exposure':t-2,
               'legal_bin':legal_bin(previous_profit[i],tenure[i])}
            probabilities.append(predict(e,model_by_mask[info[i]]))
        # All six actors choose from the SAME old t-1 state before anyone moves.
        flips=[int(u<p) for u,p in zip(coins[t-1],probabilities)]
        if old_a==4:
            a4_old_transitions+=1
            a4_no_switch+=int(not any(flips))
        routes=[r^f for r,f in zip(routes,flips)]
        counts=[x+f for x,f in zip(counts,flips)]
        tenure=[1 if f else old+1 for f,old in zip(flips,tenure)]
        gross+=sum(flips);a=sum(routes)
        a4_count+=int(a==4)
        total_cost+=cost(a)
        # The source Value(t) is observed only AFTER every current choice.
        previous_profit=[payoff(tapes[i][t][1],a,r) for i,r in enumerate(routes)]
    return total_cost,gross,a4_count,a4_old_transitions,a4_no_switch


def original_group_cost(tapes):
    """Observed reference, never forwarded to the generated actor policy."""
    n=len(tapes)
    if n!=6:raise ValueError('six original people required')
    routes=[[tape[t][0] for tape in tapes] for t in range(1,41)]
    a=[sum(r) for r in routes]
    gross=sum(sum(x!=y for x,y in zip(routes[t-1],routes[t])) for t in range(1,40))
    a4old=sum(a[t-1]==4 for t in range(1,40))
    a4no=sum(a[t-1]==4 and routes[t-1]==routes[t] for t in range(1,40))
    return sum(cost(z) for z in a),gross,sum(z==4 for z in a),a4old,a4no


def run(source,*,start='observed',seed=20261121,reps=64,tau=TAU,bootstrap=4000):
    if reps<1 or start not in ('observed','fair'):raise ValueError('bad Monte Carlo controls')
    events,by_group=load_private_events(source)
    tape=read_private_tapes(source)
    groups={key[:3]:sorted(g,key=lambda e:e['actor']) for key,g in by_group.items()
            if key[3]==2 and g[0]['treatment']==2}
    if len(groups)!=32 or len({key[0] for key in groups})!=17:
        raise ValueError('original 32 Partial sections/17 source sessions required')
    rng=Random(seed)
    variants=('bridge','partial_invariant')
    totals={m:defaultdict(lambda:[0.,0.]) for m in variants}
    summary={m:defaultdict(float) for m in variants}
    original=defaultdict(float)
    for (sid,sec,g),actors in sorted(groups.items()):
        ts=[tape[sid,sec,g,e['actor']] for e in actors]
        real=original_group_cost(ts)
        original['cost']+=real[0];original['gross']+=real[1];original['four']+=real[2]
        original['four_old']+=real[3];original['four_stay']+=real[4]
        no=fit_model(events,sid,lambda e:e['treatment']==1 and e['info']==0,tau=tau)
        full=fit_model(events,sid,lambda e:e['treatment']==3 and e['info']==1,tau=tau)
        partial=fit_model(events,sid,lambda e:e['treatment']==2,tau=tau)
        masks={'bridge':{0:no,1:full}, 'partial_invariant':{0:partial,1:partial}}
        for _ in range(reps):
            coins=[tuple(rng.random() for _ in range(6)) for _ in range(40)]
            for model in variants:
                C,G,N4,A4,N0=simulate(actors,masks[model],ts,coins,start=start,tau=tau)
                err=totals[model][sid]
                err[0]+=(C-real[0])**2/reps
                err[1]+=1/reps
                s=summary[model]
                s['cost']+=C/reps;s['gross']+=G/reps
                s['four']+=N4/reps;s['four_old']+=A4/reps;s['four_stay']+=N0/reps
    out={'scope':'R63B-P2 permissioned original retrospective, aggregate-only; NOT causal, not external validation',
         'approved_zip_sha256':APPROVED_SHA,'design':{'source_sessions':24,'target_bearing_sessions':len({key[0] for key in groups}),
         'target_partial_groups':32,'repetitions':reps,'horizon':40,'start':start,'seed':seed,'tau':tau,
         'information_rule':'six simultaneous decisions; own previous route/payoff/streak; Value(t) only post-choice'},
         'historical_partial':{'mean_cost':original['cost']/len(groups),'mean_gross_switches':original['gross']/len(groups),
         'optimal_A4_fraction':original['four']/(len(groups)*40),
         'P0_given_old_A4':original['four_stay']/original['four_old']}}
    bymodel={}
    for m in variants:
        s=summary[m]; bymodel[m]={'group_total_congestion_MSE':sum(v[0] for v in totals[m].values())/len(groups),
           'predicted_mean_cost':s['cost']/len(groups), 'predicted_mean_gross_switches':s['gross']/len(groups),
           'optimal_A4_fraction':s['four']/(len(groups)*40),
           'P0_given_old_A4':s['four_stay']/s['four_old']}
    out['models']=bymodel
    diff=[]
    for sid in sorted(totals['bridge']):
        a=totals['bridge'][sid];b=totals['partial_invariant'][sid]
        diff.append((a[0]-b[0])/a[1])
    out['bridge_minus_partial_MSE']=bootstrap_diff(diff,seed=seed+31,reps=bootstrap)
    return out


def main():
    parser=argparse.ArgumentParser(description='Private original -> source-free group aggregate JSON only')
    parser.add_argument('approved_zip');parser.add_argument('aggregate_json')
    parser.add_argument('--start',choices=['observed','fair'],default='observed')
    parser.add_argument('--seed',type=int,default=20261121)
    parser.add_argument('--reps',type=int,default=64)
    args=parser.parse_args()
    result=run(args.approved_zip,start=args.start,seed=args.seed,reps=args.reps)
    Path(args.aggregate_json).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'aggregate-only', 'target_partial_groups':result['design']['target_partial_groups']}))

if __name__=='__main__':main()
