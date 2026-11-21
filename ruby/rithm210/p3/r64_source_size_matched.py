"""RITHM R64A: source-size-matched No+Full -> Partial learning transport.

Author-approved original ZIP is SHA gated by R63B dependencies. Participant
panels are private and never emitted. Source sampling depends on design keys
only; all 39 periods of a selected actor panel are retained. A held-out original
session is never used for fitting. Outputs aggregate-only, exploratory.
"""
from collections import defaultdict
from math import log, log1p
from pathlib import Path
from random import Random
from statistics import mean
import argparse, json
from r63b_legal_bridge import load_private_events, fit_model, predict, group_joint, bootstrap_diff
from r63b_bridge_rollout import read_private_tapes, simulate, original_group_cost

SEEDS=(20261121,20261123,20261125,20261127,20261129,20261131,20261133,20261135)


def panel_key(e):
    return (e['session'],e['section'],e['group'],e['actor'])


def source_panel_sample(events,held,mask,seed):
    """Match info-specific Partial other-session actor panels exactly."""
    source={panel_key(e) for e in events if e['session']!=held
            and e['treatment']==(1 if mask==0 else 3) and e['info']==mask}
    target={panel_key(e) for e in events if e['session']!=held
            and e['treatment']==2 and e['info']==mask}
    n=len(target)
    if not 0<n<len(source):
        raise ValueError('insufficient source panels for exact match')
    selected=set(Random(seed+held*1009+mask*7919).sample(sorted(source),n))
    return selected,{'source_panels_available':len(source),
                     'matched_source_panels':n,'comparator_partial_panels':n,
                     'source_ratio_raw_to_target':len(source)/n}


def fit_matched(events,held,seed):
    fits={};sizes={}
    for mask in (0,1):
        panels,contract=source_panel_sample(events,held,mask,seed)
        source_trt=1 if mask==0 else 3
        fits[mask]=fit_model(events,held,lambda e,e_trt=source_trt,p=panels:
            e['treatment']==e_trt and panel_key(e) in p)
        sizes[mask]=contract
        if fits[mask]['n_source']!=39*contract['matched_source_panels']:
            raise AssertionError('actor panel split or missing period')
    return fits,(sizes[0],sizes[1])


def fit_full_bridge(events,held):
    return {0:fit_model(events,held,lambda e:e['treatment']==1 and e['info']==0),
            1:fit_model(events,held,lambda e:e['treatment']==3 and e['info']==1)}


def partial_model(events,held):
    m=fit_model(events,held,lambda e:e['treatment']==2)
    return {0:m,1:m}


def prep_target(events,groups):
    target=defaultdict(list);t2={}
    for key,actors in groups.items():
        if actors[0]['treatment']!=2:continue
        target[key[0]].append(actors)
        if key[3]==2:t2[key[:3]]=sorted(actors,key=lambda x:x['actor'])
    if len(target)!=17 or len(t2)!=32:
        raise ValueError('R63B original Partial population drift')
    return target,t2


def score_one_step(target,fits):
    stats=defaultdict(lambda:[0.,0.,0.,0.,0.])
    for sid,groups in target.items():
        for group in groups:
            ps=[predict(e,fits[sid][e['info']]) for e in group]
            joint,pzero=group_joint(group,ps)
            a=stats[sid]
            a[0]+=sum(-log(p) if e['flip'] else -log1p(-p)
                      for e,p in zip(group,ps))
            a[1]+=joint;a[2]+=1
            if sum(e['previous_route'] for e in group)==4:
                obs=int(not any(e['flip'] for e in group))
                a[3]+=(pzero-obs)**2;a[4]+=1
    return stats


def metrics(stats):
    return {'actor_logloss_equal_session':mean(v[0]/(6*v[2]) for v in stats.values()),
            'joint_U_D_logloss_equal_session':mean(v[1]/v[2] for v in stats.values()),
            'old_A4_no_switch_brier_equal_session':mean(v[3]/v[4] for v in stats.values() if v[4]),
            'sessions':len(stats),'target_group_transitions':sum(v[2] for v in stats.values())}


def rollout_all(t2,fits,tapes,seed,*,reps=64):
    rng=Random(seed);errors=defaultdict(lambda:[0.,0.]);a=defaultdict(float)
    for (sid,sec,g),actors in sorted(t2.items()):
        orig=[tapes[sid,sec,g,e['actor']] for e in actors]
        ref_cost=original_group_cost(orig)[0]
        for _ in range(reps):
            coins=[tuple(rng.random() for _ in range(6)) for _ in range(40)]
            cost,moves,four,oldfour,stay=simulate(actors,fits[sid],orig,coins)
            errors[sid][0]+=(cost-ref_cost)**2/reps
            errors[sid][1]+=1/reps
            a['cost']+=cost/reps;a['gross']+=moves/reps
            a['a4']+=four/reps;a['a4old']+=oldfour/reps;a['stay']+=stay/reps
    bysession={sid:v[0]/v[1] for sid,v in errors.items()}
    return {'MSE_equal_group':sum(v[0] for v in errors.values())/32,
            'MSE_equal_session':mean(bysession.values()),
            'mean_group_cost':a['cost']/32,
            'mean_group_gross_switches':a['gross']/32,
            'optimal_A4_fraction':a['a4']/(32*40),
            'P0_given_old_A4':a['stay']/a['a4old']},bysession


def run(source,*,seeds=SEEDS,reps=64):
    events,groups=load_private_events(source)
    target,t2=prep_target(events,groups)
    held=sorted(target);tapes=read_private_tapes(source)
    p_models={s:partial_model(events,s) for s in held}
    b_models={s:fit_full_bridge(events,s) for s in held}
    ps=score_one_step(target,p_models);bs=score_one_step(target,b_models)
    ref,ref_s=rollout_all(t2,p_models,tapes,20261121,reps=reps)
    full,full_s=rollout_all(t2,b_models,tapes,20261121,reps=reps)
    result={'source_population':{'original_sessions':24,'target_bearing_sessions':17,
                'target_partial_groups':32,'target_group_transitions':1248},
            'contract':'Reused original cohort: exactly matched source vs Partial info-mask actor panels for each entire-session-heldout fold; no target outcome in source fit; not independent validation.',
            'original_one_step':{'partial':metrics(ps),'full_bridge':metrics(bs)},
            'same_seed_reference_rollout':{'partial_only':ref,'unthinned_bridge':full},
            'design':{'panel_key':'same actor within source session/section/group, all 39 decision periods preserved',
                 'random_source_subset_seeds':list(seeds),'tau':8,
                 'rollout_reps':reps,'rollout_coin_seed':20261121,
                 'rollout_subset_seed_rule':'first three matching seeds only',
                 'conditional_original_exogenous_tape':'Value(t) enters simulated payoff after all six decisions at t only'},
            'matched_repeats':[]}
    for seed in seeds:
        fm={};ratios=[]
        for sid in held:
            fm[sid],c=fit_matched(events,sid,seed)
            ratios.extend(z['source_ratio_raw_to_target'] for z in c)
        stat=score_one_step(target,fm)
        diff=[(stat[s][1]-ps[s][1])/stat[s][2] for s in held]
        rec={'seed':seed,'training_raw_to_matched_ratio_range':[min(ratios),max(ratios)],
             'one_step':metrics(stat),'joint_minus_partial_mean_equal_session':mean(diff)}
        if seed in SEEDS[:3]:
            rollout,by_s=rollout_all(t2,fm,tapes,20261121,reps=reps)
            rec['autonomous_40_round']=rollout
            rec['MSE_equal_session_minus_partial']=mean(by_s[s]-ref_s[s] for s in held)
            rec['MSE_equal_session_minus_partial_cluster']=bootstrap_diff(
                [by_s[s]-ref_s[s] for s in held],seed=seed+17,reps=4000)
        result['matched_repeats'].append(rec)
    dd=[v['joint_minus_partial_mean_equal_session'] for v in result['matched_repeats']]
    result['summary']={'matched_joint_minus_partial_range':[min(dd),max(dd)],
        'raw_source_per_mask_actor_decisions':7488,
        'raw_partial_per_mask_actor_decisions':3744,
        'pooled_training_ratio_approx':2.0,
        'note':'Repeated source subset seeds are correlated robustness checks, not independent experiments; holdout cohort was already explored.'}
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description='Private SHA-authorized source -> aggregate only')
    p.add_argument('source');p.add_argument('output')
    p.add_argument('--reps',type=int,default=64)
    p.add_argument('--seeds',type=int,default=8)
    a=p.parse_args()
    result=run(a.source,seeds=SEEDS[:a.seeds],reps=a.reps)
    Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':'aggregate-only','matched_repeats':len(result['matched_repeats'])}))
