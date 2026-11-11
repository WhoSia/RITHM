"""RITHM R34: lawful individual payoff-history falsification after R33 choice-habit control.

Historical 24-session Partial (trt=2) source SHA-verified in R33 loader.
Same source CV folds/ridge as R33. No private participant row is exported.
Placebo: within each six-person group and completed period, rotate past
received payoffs only among actors who just selected the SAME route.
This preserves all group-route congestion, every route choice/target,
all group/time payoff totals *within chosen route*, and all informed flags.
Only the online cumulative payoff-gap column is sham-computed; the last
real payoff, baseline features and causal state are kept unchanged.
Placebo is a deliberately artificial retrospective falsification, NOT a
possible feedback policy or an actual participant information signal.
"""
from __future__ import annotations
import argparse,json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from scipy.special import expit,xlogy
from r33_within_partial_payoff_learning import (construct_source,personal_online_signals,
                                                  design as r33_design, SOURCE_SHA)
from r31_order_history import fit,session_metrics,TAUS

RIDGE=.02
SEEDS=(34001,34002,34003,34004,34005,34006,34007,34008,
       34009,34010,34011,34012,34013,34014,34015,34016)
METRICS=('actor_logloss','joint_logloss','count_logloss','cost_mae',
         'expected_cost','count_variance','bernoulli_variance',
         'covariance_contribution','actor_brier')


def swap_conditional_payoffs(source,seed):
    """One permutation per group/previous period, before any next-period use."""
    rng=np.random.default_rng(int(seed));out={};nontrivial=0;possible=0
    for sid,values in source.items():
        if len(values)%39:raise ValueError('wrong group period count')
        result=[]
        for g in range(len(values)//39):
            memory=[[] for _ in range(6)]
            for j in range(39):
                t,rows,contexts,traits,_=values[g*39+j]
                if t!=j+2 or len(rows)!=6:raise ValueError('time/actor alignment failed')
                payoff=[float(row[2]) for row in rows]
                sham=payoff.copy()
                for route in (0,1):
                    positions=[i for i,row in enumerate(rows) if int(row[0])==route]
                    if len(positions)<=1:continue
                    shift=int(rng.integers(1,len(positions)))
                    rotated=np.roll([payoff[i] for i in positions],shift)
                    for i,x in zip(positions,rotated):
                        sham[i]=float(x)
                        possible+=1
                        nontrivial+=int(x!=payoff[i])
                if abs(sum(sham)-sum(payoff))>1e-8:raise ArithmeticError('group payoff changed')
                for route in (0,1):
                    pos=[i for i,row in enumerate(rows) if int(row[0])==route]
                    if abs(sum(sham[i] for i in pos)-sum(payoff[i] for i in pos))>1e-8:
                        raise ArithmeticError('route-group payoff changed')
                for i,row in enumerate(rows):
                    memory[i].append((int(row[0]),sham[i]))
                    if len(memory[i])!=t-1:raise ValueError('future reward leak')
                online=[personal_online_signals(hist) for hist in memory]
                # Keep the actual recent payoff row untouched; only online history gap is sham.
                if any(abs(online[i][0]-values[g*39+j][4][i][0])>1e-12 for i in range(6)):
                    raise ArithmeticError('choice habit changed under reward placebo')
                result.append((t,rows,contexts,traits,online))
        out[sid]=result
    return out,{'seed':int(seed),'eligible_actor_periods':possible,
                 'changed_actor_periods':nontrivial,
                 'change_fraction':float(nontrivial/possible) if possible else 0.}


def features(source,family):
    res={}
    for sid,items in source.items():
        X=[];Y=[];prior=[];informed=[]
        for t,rows,ctx,traits,online in items:
            for row,c,tr,h in zip(rows,ctx,traits,online):
                X.append(r33_design(row,int(t),family,c,tr,h))
                Y.append(int(row[4]))
                prior.append(int(row[0]))
                informed.append(int(row[3]))
        X=np.asarray(X,float);Y=np.asarray(Y,int)
        prior=np.asarray(prior,int);informed=np.asarray(informed,int)
        if len(Y)%6 or len(Y)==0:raise ValueError('non-six-actor source')
        res[sid]=(X,Y,prior,informed)
    return res


def eval_session(data,coef,tau):
    X,y,prior,info=data
    p=expit(X@coef)
    logged=-xlogy(y,p)-xlogy(1-y,1-p)
    if set(info)!={0,1}:raise ValueError('missing info stratum')
    gr=[(p.reshape(-1,6)[j],prior.reshape(-1,6)[j],y.reshape(-1,6)[j])
        for j in range(len(y)//6)]
    core=session_metrics(gr,tau)
    return np.r_[core,logged[info==1].mean(),logged[info==0].mean(),
                 ((p-y)**2)[info==1].mean(),((p-y)**2)[info==0].mean()]


def run_candidate(source,expected_shape=24):
    values=features(source,'both');sessions=sorted(values)
    if len(sessions)!=expected_shape:raise ValueError('session count changed')
    fold={s:i%6 for i,s in enumerate(sessions)}
    per_session={};tau_choices=[]
    for f in range(6):
        train=[s for s in sessions if fold[s]!=f]
        test=[s for s in sessions if fold[s]==f]
        if len(train)!=20 or len(test)!=4:raise ValueError('fold imbalance')
        X=np.concatenate([values[s][0] for s in train]);Y=np.concatenate([values[s][1] for s in train])
        coef=fit(X,Y,ridge=RIDGE)
        choice=min(TAUS,key=lambda tau:(float(np.mean([eval_session(values[s],coef,tau)[1] for s in train])),tau))
        tau_choices.append(choice)
        for sid in test:
            per_session[sid]={'independent':eval_session(values[sid],coef,0.),
                              'joint':eval_session(values[sid],coef,choice)}
    return per_session,tau_choices


def run_choice_baseline(source):
    values=features(source,'within_choice');sessions=sorted(values);fold={s:i%6 for i,s in enumerate(sessions)}
    out={}
    for f in range(6):
        train=[s for s in sessions if fold[s]!=f];test=[s for s in sessions if fold[s]==f]
        coef=fit(np.concatenate([values[s][0] for s in train]),np.concatenate([values[s][1] for s in train]),ridge=RIDGE)
        tau=min(TAUS,key=lambda x:(float(np.mean([eval_session(values[s],coef,x)[1] for s in train])),x))
        for sid in test:
            out[sid]={'independent':eval_session(values[sid],coef,0.),
                      'joint':eval_session(values[sid],coef,tau)}
    return out


def mean(per,key):
    return np.mean([per[s][key] for s in sorted(per)],axis=0)


def bootstrap(differences,seed=20261111,reps=3000):
    dif=np.asarray(differences,float)
    rng=np.random.default_rng(seed)
    selected=dif[rng.integers(0,len(dif),(reps,len(dif)))].mean(axis=1)
    return np.quantile(selected,[.025,.975],axis=0).T.tolist()


def run(source_path,seeds=SEEDS):
    source=construct_source(source_path)
    choice=run_choice_baseline(source)
    factual,chosen_tau=run_candidate(source)
    sessions=sorted(factual)
    per_seed=[];per_seed_hold=[]
    for seed in seeds:
        placebo,mix=swap_conditional_payoffs(source,seed)
        output,tau=run_candidate(placebo)
        delta={metric:(mean(output,metric)-mean(choice,metric)).tolist() for metric in ('independent','joint')}
        per_seed.append(dict(**mix,delta_from_choice=delta,selected_tau=tau))
        per_seed_hold.append(output)
    comparisons={}
    for metric in ('independent','joint'):
        actual=np.asarray([factual[s][metric]-choice[s][metric] for s in sessions])
        comparisons[metric]={'actual_minus_choice':actual.mean(axis=0).tolist(),
                             'bootstrap_95_exploratory':bootstrap(actual),
                             'placebo_minus_choice_summary':{
                                 'minimum':np.min([x['delta_from_choice'][metric] for x in per_seed],axis=0).tolist(),
                                 'median':np.median([x['delta_from_choice'][metric] for x in per_seed],axis=0).tolist(),
                                 'maximum':np.max([x['delta_from_choice'][metric] for x in per_seed],axis=0).tolist()},
                             'actual_minus_placebo_by_seed':[
                                 (mean(factual,metric)-mean(p,metric)).tolist() for p in per_seed_hold]}
    return {'study':'R34 original-route-matched within-group/period payoff permutation falsification',
      'source_sha256':SOURCE_SHA,'population':'24 original-paper sessions Partial 48 groups 1872 group-periods',
      'test':'Preserve prior route, own actual last payoff, current y, informed state, group-period route totals. Scramble ONLY cumulative past route-conditioned personal received payoffs among previous SAME-route actors.',
      'metrics':list(METRICS)+['informed_actor_logloss','uninformed_actor_logloss','informed_brier','uninformed_brier'],
      'baseline':{key:mean(choice,key).tolist() for key in ('independent','joint')},
      'actual':{key:mean(factual,key).tolist() for key in ('independent','joint')},
      'actual_tau_selected':chosen_tau,'comparisons':comparisons,
      'placebos':per_seed,'seeds_count':len(seeds),
      'limitations':['Original data have been repeatedly used; all uncertainty exploratory, not confirmatory.',
                     'Within-route group-time permutation of already observed payoffs is an ARTIFICIAL negative control; no real participant received another person\'s payoff.',
                     'Same-route payoffs share congestion cost; reshuffling chiefly destroys idiosyncratic travel-value assignment, not aggregate congestion.',
                     'Never assign causal reward-learning or cognitive hassle from observed payoff associations.',
                     'Potential outcome of unchosen route remains unobserved; model forecasts not policy interventions.',
                     'Time-varying endogenous occupancy and repeated treatment effects remain confounders.']}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('private_csv');ap.add_argument('--seeds',type=int,default=len(SEEDS));a=ap.parse_args()
    if not 1<=a.seeds<=len(SEEDS):raise SystemExit('bad seeds count')
    print(json.dumps(run(a.private_csv,SEEDS[:a.seeds]),indent=2))