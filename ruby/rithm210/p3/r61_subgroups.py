"""R61 descriptive participant-information/time subgroups; session clusters kept.

All subgroups defined by predecision-known covariates. Selection of tau stays
fixed, as trained on non-heldout sessions by the main R61 pipeline. No session
or actor rows are returned or written.
"""
from collections import defaultdict
from math import log,log1p
from random import Random
from statistics import mean


def stratified_actor_scores(predictions,*,reps=4000,seed=20261121):
    def label(e):
        return ('information_status_'+('changed' if e['info_changed'] else 'unchanged'),
                'target_section_'+str(e['section']),
                'previous_route_'+str(e['previous_route']))
    strata=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    for e,ps in predictions:
        for scope in label(e):
            strata[scope][e['session']]['current_only'].append(-log(ps['current_only']) if e['flip'] else -log1p(-ps['current_only']))
            strata[scope][e['session']]['nested_adaptive'].append(-log(ps['nested_adaptive']) if e['flip'] else -log1p(-ps['nested_adaptive']))
            strata[scope][e['session']]['static_prior'].append(-log(ps['static_prior']) if e['flip'] else -log1p(-ps['static_prior']))
    out={}
    for scope,by in sorted(strata.items()):
        if len(by)!=24:raise ValueError('expected all 24 sessions in each subgroup')
        rng=Random(seed+len(scope))
        paired=[mean(by[s]['nested_adaptive'])-mean(by[s]['current_only']) for s in sorted(by)]
        drawn=sorted(mean(paired[rng.randrange(24)] for _ in range(24)) for _ in range(reps))
        out[scope]={
            'actor_decisions':sum(len(v['current_only']) for v in by.values()),
            'equal_session_actor_logloss':{name:mean(mean(by[s][name]) for s in by) for name in ('current_only','nested_adaptive','static_prior')},
            'adaptive_minus_online_nats':mean(paired),
            'session_resampling_95_descriptive':[drawn[int(.025*reps)],drawn[int(.975*reps)]]}
    return out
