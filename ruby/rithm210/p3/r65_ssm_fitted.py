"""RITHM R65B: independent source-FREE Full-information SSM replication.

This implementation follows Noussair & Qiao (Management Science, 2026),
online Appendix B.1 Table 4: first choice random, q WITH-replacement
experience samples, current six decisions simultaneous, full information
permits payoff comparison on matched historical opponent states.

Under Full information, own travel value cancels from the payoff difference,
so the observed opponent choice count is sufficient: A−B payoff advantage
is 11 - 3*(number of other drivers on A). No participant data required.

SSMq q=3 and SSM1-q qmax=4 are Full-specific fitted values from authors'
Appendix D Table 6(b) with Segments 1–3; q5 is previously replicated
unfitted illustrative Table7 author model. These are model simulations, NOT
previously unseen evidence, external validation or claim of cognition.
"""
import argparse
from collections import Counter
import json
from random import Random
from statistics import mean


def choose(advantage_history, q, rng):
    if not advantage_history:
        return rng.randrange(2)
    advantage = sum(advantage_history[rng.randrange(len(advantage_history))]
                    for _ in range(q))
    return 1 if advantage > 0 else (0 if advantage < 0 else rng.randrange(2))


def one_game(qmax, mode, rng, rounds=40):
    if mode not in ('fixed', 'heterogeneous') or not 1 <= qmax <= 30 or rounds < 2:
        raise ValueError('invalid SSM setting')
    qs = [qmax if mode == 'fixed' else rng.randint(1, qmax) for _ in range(6)]
    histories = [[] for _ in range(6)]
    prev = None
    counts = {epoch:Counter() for epoch in ('early','late')}
    cost = Counter()
    for t in range(1, rounds+1):
        choice = [choose(histories[i], qs[i], rng) for i in range(6)]
        n = sum(choice)
        # Appendix B Table 7 individual travel congestion cost; source-free
        cost['early' if t <= 10 else 'late' if t >= 31 else 'mid'] += (n*n+2*(6-n)**2)/6
        if prev is not None:
            old_a = sum(prev)
            epoch = ('early' if t <= 11 else 'late' if t >= 31 else None)
            if epoch is not None and old_a == 4:
                x=counts[epoch]
                x['previous_A4'] += 1
                x['all_stay_A4'] += int(prev==choice)
                u=sum(prev[i]==0 and choice[i]==1 for i in range(6))
                d=sum(prev[i]==1 and choice[i]==0 for i in range(6))
                x['balanced_cancel_A4'] += int(u==d and u>0)
                x['exit_A4'] += int(u!=d)
        for i in range(6):
            histories[i].append(11-3*(n-choice[i]))
        prev = choice
    return counts, {'cost_early':cost['early']/10,
                    'cost_late':cost['late']/10}


def simulate(variants, reps=5000, seed=20261121):
    if not reps > 0:raise ValueError('reps must be positive')
    out={}
    for label,setting in variants.items():
        rng=Random(seed)
        group_counts={e:Counter() for e in ('early','late')}
        cost=Counter()
        for i in range(reps):
            data,avg=one_game(setting['qmax'], setting['mode'],rng)
            for ep in group_counts:group_counts[ep].update(data[ep])
            for name,val in avg.items():cost[name]+=val
        entry={'mode':setting['mode'],'qmax':setting['qmax'], 'reps':reps,
               'mean_cost_early':cost['cost_early']/reps,
               'mean_cost_late':cost['cost_late']/reps}
        for epoch in ('early','late'):
            c=group_counts[epoch]
            entry[epoch]={'old_A4_transitions':c['previous_A4'],
                           'all_stay_A4':c['all_stay_A4'],
                           'p_all_stay_A4':c['all_stay_A4']/c['previous_A4'],
                           'p_balanced_cancel_A4':c['balanced_cancel_A4']/c['previous_A4'],
                           'p_exit_A4':c['exit_A4']/c['previous_A4']}
        entry['delta_late_minus_early']=entry['late']['p_all_stay_A4']-entry['early']['p_all_stay_A4']
        out[label]=entry
    return {'scope':'Source-free autonomous Full six-person simulations; original author fitted q from Appendix D; no human data and no RNG parity claim',
            'simulation_seed':seed,'models':out,
            'author_source':'Noussair Qiao 2026 Management Science original 2026-07-24 revision Appendix B.1 Table4 and D Table6(b)'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('output_json')
    p.add_argument('--reps',type=int,default=5000)
    p.add_argument('--seed',type=int,default=20261121)
    args=p.parse_args()
    obj=simulate({'author_R7_ssm5':{'mode':'fixed','qmax':5},
                  'author_fitted_full_ssmq3':{'mode':'fixed','qmax':3},
                  'author_fitted_full_ssm1q4':{'mode':'heterogeneous','qmax':4}},
                  reps=args.reps,seed=args.seed)
    with open(args.output_json,'w',encoding='utf-8') as f:json.dump(obj,f,indent=2,sort_keys=True)
    print(json.dumps({'source_free':True,'models':{k:v['delta_late_minus_early'] for k,v in obj['models'].items()}}))

if __name__=='__main__': main()
