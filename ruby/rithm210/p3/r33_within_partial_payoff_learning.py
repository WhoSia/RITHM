"""RITHM R33: incremental past-payoff-learning signals beyond pre-Partial route traits.

Original-author private source SHA-verified. Official 24-session Partial cohort.
Features are constructed online from *completed current Partial rounds* only.
Own observed payoff and own past route are legal for all actors. Only informed
actors can use past public occupancy through existing R32 base features.
No causal effect/trait identification, all source evaluations exploratory.
"""
from __future__ import annotations
import csv, json, sys
from collections import defaultdict
import numpy as np
from scipy.special import expit
from r32_trait_rival import previous_route_traits, design as r32_design
from r31_order_history import prior_contexts,session_metrics,TAUS,fit,load_partial,SOURCE_SHA

FAMILIES=('prior_preference','within_choice','within_payoff','both')
METRICS=('actor_logloss','joint_logloss','count_logloss','cost_mae','expected_cost',
         'count_variance','independent_variance','covariance_contribution','actor_brier')


def personal_online_signals(past):
    """Input: [(prior_choice_A, prior_received_payoff),...], strictly before t.

    Shrink to neutral 0.5 for choice tendency and zero for each route's
    observed reward rate; avoid claims about counterfactual route rewards.
    """
    m=len(past)
    if m<1: raise ValueError('at least first completed Partial period is needed')
    a=sum(int(y) for y,_ in past)
    for y,pay in past:
        if y not in (0,1) or not np.isfinite(pay):raise ValueError('bad past history')
    habit=2*(a+2)/(m+4)-1
    payoff_a=sum(float(pay) for y,pay in past if y==1)/(a+4)
    payoff_b=sum(float(pay) for y,pay in past if y==0)/(m-a+4)
    # Difference of RECEIVED payoff averages by observed chosen route.
    # This is NOT causal route payoff or exact congestion-cost advantage.
    observed_gap=(payoff_a-payoff_b)/10
    return float(habit),float(observed_gap)


def design(row,t,family,context,trait,online):
    if family not in FAMILIES:raise ValueError('unrecognized R33 family')
    core=r32_design(row,t,'preference',context,trait)
    habit,gap=online
    info=int(row[3])
    if not all(np.isfinite(v) for v in (habit,gap)) or abs(habit)>1 or abs(gap)>100:
        raise ValueError('invalid online experience')
    if family in ('within_choice','both'):
        core.extend((habit,info*habit))
    if family in ('within_payoff','both'):
        core.extend((gap,info*gap))
    return core


def construct_source(path):
    partial=load_partial(path)
    contexts,orders=prior_contexts(path)
    traits=previous_route_traits(path,orders)
    sids=sorted(partial)
    ids={}
    # Same six actor IDs in each group, preserving R32's documented actor ordering.
    by=defaultdict(set)
    with open(path,newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            s=int(r['session']);trt=int(r['trt']);period=int(r['Period'])
            if s in (2,101) or trt!=2 or period!=1:continue
            by[s,int(r['Group'])].add(int(r['ID']))
    for sid in sids:
        ids[sid]=[sorted(by[sid,g]) for g in orders[sid]]
        if len(ids[sid])*39!=len(partial[sid]):raise ValueError('inconsistent actor-group mapping')
    dataset={sid:[] for sid in sids}
    # Records in groups[sid] include prior round values at t-1, and current
    # outcome y_t, not the current payoff. Build online-only states in order.
    for sid in sids:
        for gi,actors in enumerate(ids[sid]):
            memories=[[] for _ in range(6)]
            for j in range(39):
                t=j+2
                rows=partial[sid][gi*39+j]
                if len(rows)!=6:raise ValueError('wrong group size')
                # At round t, participant has observed payoff & choice at t-1.
                # Append only the known last-round feedback before constructing features.
                for i,row in enumerate(rows):
                    memories[i].append((int(row[0]),float(row[2])))
                    if len(memories[i])!=t-1:raise ValueError('future/incorrect online history')
                online=[personal_online_signals(x) for x in memories]
                ctx=[contexts[sid,gi,aid] for aid in actors]
                tr=[traits[sid,gi,aid] for aid in actors]
                dataset[sid].append((t,rows,ctx,tr,online))
    if len(dataset)!=24 or sum(len(v) for v in dataset.values())!=1872:
        raise ValueError('source group-period census mismatch')
    return dataset


def x_y(dataset,sid,family):
    x=[];y=[]
    for t,rows,contexts,traits,online in dataset[sid]:
        for row,c,tr,h in zip(rows,contexts,traits,online):
            x.append(design(row,t,family,c,tr,h));y.append(row[4])
    return np.asarray(x,float),np.asarray(y,int)


def predictions(X,y,coef):
    p=expit(X@coef).reshape(-1,6)
    if len(y)%6:raise ValueError('mismatched group count')
    target=y.reshape(-1,6)
    # Current y_t only used in scoring, NEVER in predictors.
    return [(p[j],None,target[j]) for j in range(len(p))]


def session_scores(X,y,coef,previous,tau):
    p=expit(X@coef).reshape(-1,6)
    ys=np.asarray(y).reshape(-1,6)
    from r31_order_history import session_metrics
    pred=[(p[j],previous[j],ys[j]) for j in range(len(p))]
    return session_metrics(pred,tau)


def run(path):
    source=construct_source(path)
    sessions=sorted(source);fold={sid:i%6 for i,sid in enumerate(sessions)}
    features={family:{sid:x_y(source,sid,family) for sid in sessions} for family in FAMILIES}
    previous={sid:[[row[0] for row in group] for _,group,*_ in source[sid]] for sid in sessions}
    out={};held={};selected={}
    for family in FAMILIES:
        by_session={};choices=[]
        for f in range(6):
            train=[s for s in sessions if fold[s]!=f]
            test=[s for s in sessions if fold[s]==f]
            if len(train)!=20 or len(test)!=4:raise ValueError('crossvalidation split violation')
            X=np.concatenate([features[family][s][0] for s in train]); y=np.concatenate([features[family][s][1] for s in train])
            coef=fit(X,y,ridge=.02)
            losses={tau:float(np.mean([session_scores(*features[family][s],coef,previous[s],tau)[1] for s in train])) for tau in TAUS}
            tau=min(TAUS,key=lambda z:(losses[z],z))
            choices.append(tau)
            for s in test:
                test_X,test_y=features[family][s]
                by_session[s]={'independent':session_scores(test_X,test_y,coef,previous[s],0.),
                               'joint':session_scores(test_X,test_y,coef,previous[s],tau)}
        if set(by_session)!=set(sessions):raise ValueError('out of fold incomplete')
        held[family]=by_session
        selected[family]=choices
        out[family]={k:np.mean([by_session[s][k] for s in sessions],axis=0).tolist() for k in ('independent','joint')}
    contrasts={}
    for model,reference in [(name,'prior_preference') for name in FAMILIES[1:]] + [('both','within_choice'),('both','within_payoff')]:
        for target in ('independent','joint'):
            delta=np.array([held[model][s][target]-held[reference][s][target] for s in sessions])
            rng=np.random.default_rng(20261111)
            sampling=rng.integers(0,24,(2000,24))
            ci=np.quantile(delta[sampling].mean(axis=1),[.025,.975],axis=0).T
            contrasts[f'{model}_minus_{reference}_{target}']={'delta':delta.mean(axis=0).tolist(),
                        'exploratory_session_bootstrap95':ci.tolist()}
    return {'study':'R33 individual route habit vs observed per-route payoff running feedback',
            'source_sha256':SOURCE_SHA,'population':'24 main paper sessions, Partial, 48 groups / 1872 group periods',
            'metrics':METRICS,'result':out,'selected_tau':selected,'contrasts':contrasts,
            'limitations':'Historical reused dataset, all prior-only. No causal learning/hassle or trait identification; route-specific received payoffs are selected outcomes and not potential outcomes. No independent confirmation.'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python r33_within_partial_payoff_learning.py PRIVATE_AUTHOR_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))