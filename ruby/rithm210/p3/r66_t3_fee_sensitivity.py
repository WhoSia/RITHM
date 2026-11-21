"""R66-T3B: source-private Endogenous information price / stage-profit sensitivity.

The original `profit` variable is actual received reward, and is lawful at t+1.
The alternative `Value - Cost` is a researcher-reconstructed price-excluded
route reward, NOT assumed observable to the participant unless price deduction
and exact reward presentation are independently verified. It is a diagnostic.
All public outputs are large pooled condition/epoch aggregates, never actor rows.
"""
import argparse
from collections import Counter,defaultdict
import csv
from hashlib import sha256
from io import TextIOWrapper
import json
from pathlib import Path
from random import Random
from zipfile import ZipFile

from r65_endogenous_stability import load_private, APPROVED_SHA, CSV, TREATMENT
from r66_t3_payoff_streak import (MODELS,build_tables,create_events,group_scores,
                                   payoff_bin,predict,public_mean,_percentile_interval)


def load_alternative_rewards(source,groups):
    if sha256(Path(source).read_bytes()).hexdigest()!=APPROVED_SHA:
        raise ValueError('source sha gate failed')
    observed={};derived={};adjustment=defaultdict(Counter)
    with ZipFile(source) as z, TextIOWrapper(z.open(CSV),encoding='utf-8-sig') as fp:
        for row in csv.DictReader(fp):
            sid,group,trt,t,actor=(int(row[k]) for k in ('session','Group','trt','Period','ID'))
            if (sid,group,trt) not in groups:continue
            key=sid,group,trt,t,actor
            if key in observed:raise ValueError('duplicate source key')
            net=float(row['profit']);route=float(row['Value'])-float(row['Cost'])
            observed[key]=net;derived[key]=route
            adjustment[trt]['total_rows']+=1
            if abs(net-route)>1e-9:adjustment[trt]['nonzero_adjustment']+=1
            if payoff_bin(net)!=payoff_bin(route): adjustment[trt]['payoff_bin_changed']+=1
    if len(observed)!=48*4*40*6:raise ValueError('unexpected cohort')
    return observed,derived,adjustment


def paired_interval(per_session,*,draws=4000,seed=20261121):
    sessions=sorted(set(k[0] for k in per_session))
    if len(sessions)!=24:raise ValueError('need 24 original sessions')
    metrics=('actor_logloss','brier_allstay','welfare_sqerr','residual_welfare')
    out={};rng=Random(seed)
    for trt in TREATMENT:
        for epoch in ('early','late'):
            def p(selected,variant):
                c=Counter()
                for s in selected:c.update(per_session.get((s,trt,epoch,variant),{}))
                return c
            a=p(sessions,'received_profit');b=p(sessions,'route_reward_reconstructed')
            if min(a['n'],b['n'])<20:raise ValueError('unsafe pooled cell')
            point={m:b[m]/b['n']-a[m]/a['n'] for m in metrics}
            draws_by_metric={m:[] for m in metrics}
            for _ in range(draws):
                s=[sessions[rng.randrange(24)] for _ in sessions]
                x=p(s,'received_profit');y=p(s,'route_reward_reconstructed')
                if min(x['n'],y['n'])<20:continue
                for m in metrics:draws_by_metric[m].append(y[m]/y['n']-x[m]/x['n'])
            out[TREATMENT[trt]+'_'+epoch]={m:{'route_minus_received':point[m],
                'descriptive_95':_percentile_interval(draws_by_metric[m])}
                for m in metrics}
    return out


def run(source,*,draws=4000):
    groups=load_private(source)
    paid,route,adjust=load_alternative_rewards(source,groups)
    e_paid,j_paid=create_events(groups,paid)
    e_route,j_route=create_events(groups,route)
    # Same participants and choices, only previous-payoff bin differs
    if set(j_paid)!=set(j_route):raise AssertionError('source groups changed')
    sessions=sorted(set(x[0] for x in groups))
    pooled=defaultdict(Counter);by_session=defaultdict(Counter)
    for held in sessions:
        fits={'received_profit':build_tables(e_paid,held),
              'route_reward_reconstructed':build_tables(e_route,held)}
        for key,ge in j_paid.items():
            if key[0]!=held or ge[0]['previous_A']!=4:continue
            trt=ge[0]['treatment'];epoch=ge[0]['epoch']
            for variant,rows in (('received_profit',ge),('route_reward_reconstructed',j_route[key])):
                pp=[predict(e,fits[variant])['legal_payoff_tenure'] for e in rows]
                record=group_scores(rows,pp)
                pooled[trt,epoch,variant].update(record)
                by_session[held,trt,epoch,variant].update(record)
    return {'scope':'EXPLORATORY original-source 24 sessions; route reward rebuilt from value-cost analyst record; no causal price effect',
            'original_author_zip_sha256':APPROVED_SHA,'groups':48,'sessions':24,
            'definition_received':'source profit at period t; participant learns realized payoff at end of t',
            'definition_reconstructed':'Value(t) - Cost(t), subtracts observed bonus or fee; NOT independently verified as displayed to all participants',
            'source_adjustments_aggregate':{TREATMENT[t]:dict(c) for t,c in adjust.items()},
            'pooled':{TREATMENT[trt]:{ep:{variant:public_mean(pooled[trt,ep,variant])
                                    for variant in ('received_profit','route_reward_reconstructed')}
                                  for ep in ('early','late')} for trt in TREATMENT},
            'descriptive_24_session_paired':paired_interval(by_session,draws=draws),
            'limitations':['Price/payment may be known but visibility of separately reconstructed route-only reward not established',
              'Endogenous always last with nonrandom price and information selection',
              'Experimenter-valued Value and Cost were not input to participant-legal model',
              'Private actor rows, individual reward histories, source identifiers excluded from public aggregate']}

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('original_zip');ap.add_argument('output_json');ap.add_argument('--draws',type=int,default=4000)
    a=ap.parse_args()
    v=run(a.original_zip,draws=a.draws)
    Path(a.output_json).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'source_exposure':'aggregate_only','Endogenous_adjustments':v['source_adjustments_aggregate']['Endogenous']}))
