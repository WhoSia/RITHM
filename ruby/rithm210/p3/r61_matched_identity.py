"""Matched person-identity counterfactual for R61's strictly train-selected rates.

The model (and tau selected from other sessions) is frozen. Only the *source*
actor's previous-section switch count is relabelled within a fixed group and,
when requested, a stringent information/route-stratum. The current target
route prefix, actual outcome, and treatment are unchanged. Source rows stay
in RAM, only aggregate expected/null scores can leave the operator runtime.
"""
from collections import defaultdict
from math import log, log1p
from random import Random
from statistics import mean
from r60_identity_placebo import blocks
from r61_adaptive_prior import (base_without,get_pbase,prior_weight,
                                summarize_session_bases)


def build_adaptive_cost_matrices(events,selection,*,shrink=20):
    by_group=defaultdict(lambda:defaultdict(list))
    for e in events:by_group[e['session'],e['section'],e['group']][e['actor']].append(e)
    if len(by_group)!=96:raise ValueError('must have precisely 96 original target groups')
    total=summarize_session_bases(events)
    matrices=[]
    for (s,sec,g),records in sorted(by_group.items()):
        if s not in selection:raise ValueError('heldout tau not selected from training')
        fitted=base_without(total,{s});tau=selection[s]
        ids=sorted(records)
        if len(ids)!=6:raise ValueError('six people')
        prior=[records[i][0]['own_count'] for i in ids]
        attrs=[];matrix=[]
        for actor in ids:
            history=sorted(records[actor],key=lambda e:e['period'])
            if [e['period'] for e in history]!=list(range(2,41)):
                raise ValueError('incomplete original target route prefix')
            if any(e['own_count']!=history[0]['own_count'] for e in history):
                raise ValueError('prior source count changed')
            x=history[0]
            attrs.append((x['info'],x['info']^x['info_changed'],
                          x['prior_terminal_route'],x['target_initial_route']))
            row=[]
            for old_flips in prior:
                error=0.
                for e in history:
                    w=prior_weight(e['current_exposure'],tau)
                    p=(e['current_count']+w*old_flips+shrink*get_pbase(e,fitted))/(
                        e['current_exposure']+39*w+shrink)
                    error+=-log(p) if e['flip'] else -log1p(-p)
                row.append(error)
            matrix.append(row)
        matrices.append({'attrs':attrs,'loss_matrix':matrix})
    return matrices


def check_identity_null(matrices,*,scope='same_information_and_boundary_route',reps=2000,seed=20261121):
    if not isinstance(reps,int) or reps<=0:raise ValueError('invalid number of permutations')
    n=len(matrices)*6*39
    if n<=0:raise ValueError('empty null')
    actual=sum(sum(M['loss_matrix'][i][i] for i in range(6)) for M in matrices)/n
    expected=0.;eligible=0;eligible_groups=0
    for M in matrices:
        bs=blocks(M['attrs'],scope)
        eligible+=sum(len(b) for b in bs if len(b)>1)
        eligible_groups+=int(any(len(b)>1 for b in bs))
        for b in bs:
            for i in b:
                expected+=sum(M['loss_matrix'][i][j] for j in b)/len(b)
    rng=Random(seed);null=[]
    for _ in range(reps):
        score=0.
        for M in matrices:
            for b in blocks(M['attrs'],scope):
                perm=b[:]
                rng.shuffle(perm)
                score+=sum(M['loss_matrix'][i][j] for i,j in zip(b,perm))
        null.append(score/n)
    null.sort()
    return {'scope':scope,'num_target_actor_decisions':n,'num_people_section_pairs':len(matrices)*6,
            'permutable_pairs':eligible,'permutable_groups':eligible_groups,
            'observed_logloss':actual,'exact_null_mean_logloss':expected/n,
            'null_percentile95_descriptive':[null[int(.025*reps)],null[min(reps-1,int(.975*reps))]],
            'p_value_plus_one':(1+sum(v<=actual for v in null))/(reps+1),
            'interpretation':'Only label assignment under preserved group and information-route strata, not a causal type-memory test.'}


if __name__=='__main__':
    import json,sys
    from r59_prior_exposure import parse_source_section_histories
    from r60_cross_segment import events_from_histories
    from r61_adaptive_prior import get_predictions
    if len(sys.argv)!=2:raise SystemExit('usage: python r61_matched_identity.py PRIVATE_APPROVED_ZIP')
    people=parse_source_section_histories(sys.argv[1]);events,_=events_from_histories(people)
    _,sel,_=get_predictions(events)
    matrices=build_adaptive_cost_matrices(events,sel)
    print(json.dumps(check_identity_null(matrices),sort_keys=True,indent=2))
