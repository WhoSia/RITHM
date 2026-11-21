"""R61 macro failure diagnostic: report only whole-cohort occupancy and activity rates.

All source subject IDs/routes stay in memory, and no group × period rows leave.
"""
from collections import defaultdict
from random import Random
from r61_closed_loop import collect_groups,rollout_one
from r61_adaptive_prior import summarize_session_bases,base_without


def observe_trajectory(group):
    prev=group['initial_route'][:];traj=[(sum(prev),0)]
    for t in range(2,41):
        g=[h[t-2] for h in group['actors']]
        if any(e['previous_route']!=prev[i] for i,e in enumerate(g)):
            raise ValueError('not a valid observed human prefix')
        next_route=[prev[i]^g[i]['flip'] for i in range(6)]
        traj.append((sum(next_route),sum(e['flip'] for e in g)))
        prev=next_route
    return traj


def gather(aggregate,trajectory):
    if len(trajectory)!=40:raise ValueError('40 period trajectory only')
    for stage,range_t in [('all',range(40)),('first_10',range(10)),('last_10',range(30,40))]:
        acc=aggregate[stage]
        for idx in range_t:
            a,g=trajectory[idx]
            acc['n']+=1;acc['optimal_n4']+=int(a==4)
            acc['excess']+=3*(a-4)**2
            if idx:
                acc['g_count']+=1;acc['gross']+=g
                prev=trajectory[idx-1][0]
                if prev==4:
                    acc['prior_four_transitions']+=1
                    acc['four_to_four']+=int(a==4)
                    acc['four_to_four_no_switch']+=int(a==4 and g==0)


def normalize(aggregate):
    result={}
    for stage,a in aggregate.items():
        result[stage]={
            'choice_periods':a['n'],
            'optimal_occupancy_4_fraction':a['optimal_n4']/a['n'],
            'excess_congestion_per_period':a['excess']/a['n'],
            'gross_switches_per_internal_transition':a['gross']/a['g_count'],
            'n_from_prior_4_transitions':a['prior_four_transitions'],
            'p4_to4_given_prev4':a['four_to_four']/a['prior_four_transitions'],
            'p4_to4_with_no_switch_given_prev4':a['four_to_four_no_switch']/a['prior_four_transitions']}
    return result


def run_diagnostics(events,selected,*,reps=64,seed=20261121,start='observed'):
    groups=collect_groups(events)
    fits={s:base_without(summarize_session_bases(events),{s}) for s in selected}
    store={name:defaultdict(lambda:defaultdict(float)) for name in ('source_observed','current_only','nested_adaptive','static_prior')}
    rng=Random(seed)
    for group in groups:
        gather(store['source_observed'],observe_trajectory(group))
        for _ in range(reps):
            coins=[[rng.random() for _ in range(6)] for _ in range(40)]
            for model in ('current_only','nested_adaptive','static_prior'):
                _,_,trajectory=rollout_one(group,fits[group['session']],selected[group['session']],model,coins,first=start,trace=True)
                gather(store[model],trajectory)
    return {'start':start,'source_groups':len(groups),'simulations_per_group':reps,
            'whole_cohort_aggregate_no_original_rows':{model:normalize(data) for model,data in store.items()},
            'limitation':'Descriptive whole-cohort occupancy; does not isolate common group shock or infer policy treatment response.'}

if __name__=='__main__':
    import json,sys
    from r59_prior_exposure import parse_source_section_histories
    from r60_cross_segment import events_from_histories
    from r61_adaptive_prior import get_predictions
    if len(sys.argv)!=2:raise SystemExit('usage: python r61_macro_diagnostics.py APPROVED_PRIVATE_ZIP')
    e,_=events_from_histories(parse_source_section_histories(sys.argv[1]));_,selected,_=get_predictions(e)
    print(json.dumps(run_diagnostics(e,selected),indent=2,sort_keys=True))
