"""RITHM R37: author Appendix B SSM5 and SSM1-9 teacher-forced source prediction.

Predict actual choices from only previously experienced feedback. For informed agents
counterfactual route values inferred from publicly disclosed past occupancy and
own received payoff; value cancels from A-vs-B difference. For uninformed agents
only route-specific *received* payoffs are used. The SSM1-9 sample size q_i is fixed
per person; we filter its posterior with past observed choices, rather than re-draw
it every period. Tie resolution is declared 50/50. Current-period outcome and Value
are not predictors. Source data remain private; print only aggregate metrics.

Important scope: teacher-forced one-step probabilities for a source-trace are NOT
unconditional simulations of the author's 40-period model, and original Appendix B
provides insufficient verification of every implementation choice (ties, etc.).
"""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
SOURCE_SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
COST=np.array([24+3*(n-4)**2 for n in range(7)],float)

def source_groups(path):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('original source hash mismatch')
    grouped=defaultdict(lambda:defaultdict(dict))
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            s=int(row['session']);trt=int(row['trt']);t=int(row['Period'])
            if s in (2,101) or trt!=2 or not 1<=t<=40:continue
            key=(s,int(row['section']),int(row['Group']))
            aid=int(row['ID']);y=int(row['RouteA']);info=int(row['Informed'])
            profit=float(row['profit']);n=int(row['NumA']);cost=float(row['Cost'])
            if aid in grouped[key][t] or y not in (0,1) or info not in (0,1) or abs(profit+cost-float(row['Value']))>1e-7:
                raise ValueError('invalid actor-period')
            grouped[key][t][aid]=(y,info,profit,n)
    result=[]
    for (s,sec,g),periods in sorted(grouped.items()):
        actors=sorted(periods[1]);marks={a:periods[1][a][1] for a in actors}
        if len(actors)!=6 or sum(marks.values())!=3 or set(periods)!=set(range(1,41)):
            raise ValueError('partial cohort structure invalid')
        if any(set(periods[t])!=set(actors) or any(periods[t][a][1]!=marks[a] for a in actors) for t in range(1,41)):
            raise ValueError('actor identity/information drift')
        for t in range(1,41):
            n=sum(periods[t][a][0] for a in actors)
            if any(periods[t][a][3]!=n for a in actors):raise ValueError('occupancy mismatch')
        result.append((s,sec,g,actors,periods))
    if len(result)!=48 or len({x[0] for x in result})!=24:raise ValueError('source census')
    return result

def pmf_sum(sample,q):
    """Small discrete empirical distributions on 0.1-point grid, replacement draws."""
    vals=np.rint(np.asarray(sample)*10).astype(int)
    if len(vals)==0:raise ValueError('empty sample')
    lo=int(vals.min());hi=int(vals.max())
    probs=np.bincount(vals-lo,minlength=hi-lo+1).astype(float)/len(vals)
    acc=np.array([1.])
    for _ in range(q):acc=np.convolve(acc,probs)
    return acc,lo*q

def p_a_from_sum_difference(diff,q):
    # Informed: each draw is one previous period with both revealed or
    # reconstructible payoffs; difference cancels independently drawn value.
    p,origin=pmf_sum(diff,q)
    indices=origin+np.arange(len(p))
    return float(p[indices>0].sum()+.5*p[indices==0].sum())

def p_a_from_observed_payoffs(a,b,q):
    # Uninformed: separate samples of q from previously CHOSEN A and B.
    if not a or not b:return .5
    pa,la=pmf_sum(a,q);pb,lb=pmf_sum(b,q)
    # Difference of two independently sampled averages. Equal q so sums suffice.
    # Use mass of B sums strictly below A sums with tie at 1/2.
    from_b=lb+np.arange(len(pb))
    cdf=np.cumsum(pb)
    from_a=la+np.arange(len(pa))
    off=from_a-lb
    less=np.where(off<=0,0.,np.where(off>len(pb),1.,cdf[np.clip(off-1,0,len(pb)-1)]))
    tie=np.where((off>=0)&(off<len(pb)),pb[np.clip(off,0,len(pb)-1)],0.)
    return float(np.dot(pa,less+.5*tie))

def posterior_update(weights,allq,chosen):
    q=np.clip(np.asarray(allq,float),1e-12,1-1e-12)
    lh=q if chosen else 1-q
    new=np.asarray(weights)*lh
    return new/new.sum()

def conditional_models(past,info,weights):
    if len(past)==0:return .5,.5,weights
    a=[p for y,p,n in past if y==1];b=[p for y,p,n in past if y==0]
    if info:
        # For a given old congestion count n and own historical route y,
        # foregone unilateral switch changes the counts by one.
        # own value cancels; Delta payoff(A)-payoff(B) = Cost(B)-Cost(A).
        differences=[(2*(6-n) if y==0 else 2*(7-n))-(n if y==1 else n+1)
                     for y,p,n in past]
        values=[p_a_from_sum_difference(differences,q) for q in range(1,10)]
    else:
        values=[p_a_from_observed_payoffs(a,b,q) for q in range(1,10)]
    q5=values[4]
    mix=float(np.dot(weights,values))
    return q5,mix,np.asarray(values,float)

def group_metrics(ps,ys):
    p=np.clip(np.asarray(ps,float),1e-12,1-1e-12)
    y=np.asarray(ys,int)
    actor=float(np.mean(-y*np.log(p)-(1-y)*np.log1p(-p)))
    joint=actor*6
    count=np.array([1.])
    for x in p:count=np.convolve(count,[1-x,x])
    n=sum(y);cost=float(count@COST)
    return [actor,joint,float(-np.log(max(count[n],1e-300))),abs(cost-COST[n])]

def run(path, return_prediction_rows=False):
    groups=source_groups(path)
    # Exact conditional q-mixture using actor-specific posterior over fixed q_i.
    # Teacher-forced realized histories; each actor's posterior updated after each
    # observed current route, conditional on history and informed status.
    scores=defaultdict(lambda:defaultdict(list));by_info=defaultdict(lambda:defaultdict(list))
    records=defaultdict(list)
    for sid,sec,g,actors,periods in groups:
        past={a:[] for a in actors}
        weights={a:np.ones(9)/9 for a in actors}
        for t in range(1,41):
            p5=[];p9=[];ys=[];infos=[];likelihood=[]
            for aid in actors:
                y,info,payoff,n=periods[t][aid]
                q5,q9,lik=conditional_models(past[aid],info,weights[aid])
                p5.append(q5);p9.append(q9);ys.append(y);infos.append(info);likelihood.append(lik)
            if t>=2:
                s5=group_metrics(p5,ys);s9=group_metrics(p9,ys)
                scores['SSM5'][sid].append(s5)
                scores['SSM1-9_fixed_q_posterior'][sid].append(s9)
                if return_prediction_rows:records[sid].append((np.asarray(p5),np.asarray(p9),np.asarray(ys)))
                for info in (0,1):
                    a=np.array(ys)[np.array(infos)==info]
                    for name,pp in [('SSM5',p5),('SSM1-9_fixed_q_posterior',p9)]:
                        q=np.clip(np.asarray(pp)[np.array(infos)==info],1e-12,1-1e-12)
                        by_info[name,info][sid].extend((-a*np.log(q)-(1-a)*np.log1p(-q)).tolist())
            for i,aid in enumerate(actors):
                y,info,payoff,n=periods[t][aid]
                if t>=2:weights[aid]=posterior_update(weights[aid],likelihood[i],y)
                past[aid].append((y,payoff,n))
    out={}
    for name,session_stats in scores.items():
        means=np.array([np.mean(session_stats[s],axis=0) for s in sorted(session_stats)])
        out[name]={'metrics':means.mean(axis=0).tolist(),
                   'info_actor_logloss':{str(i):float(np.mean([np.mean(by_info[name,i][s]) for s in sorted(session_stats)])) for i in (0,1)},
                   'session_loss_quantiles':np.quantile(means[:,1],[.1,.5,.9]).tolist()}
    result={'source_sha256':SOURCE_SHA,'sessions':24,'groups':48,'groups_scored':1872,
     'scoring':'teacher-forced actual 39 transitions/group, 24 session equal weights, no coefficient fitted to evaluation sessions',
     'original_author_Appendix_B':'SSM5 exact q=5 resampling; SSM1-9 fixed per-actor q with posterior filtering from previous actual choice likelihood; historical actual received payoffs; full info inferred foregone payoff via disclosed occupancy',
     'metrics':['actor_logloss','independent_six_choice_joint_logloss','occupancy_logloss','cost_forecast_MAE'],
     'results':out,
     'caveats':['SSM tie resolved 0.5 (paper Table12 leaves tie handling underspecified)','Posterior q updating is an explicitly declared conditional-scoring choice; do not claim authors used this update in unconditional simulations','Teacher-forced realized histories differs from original unconditional 40-period SSM simulations','SSM1-9 q_i drawn once/person, not separately each period','Uninformed learns chosen-route payoff, not true cost/value/hidden count','Original EWA-lite Appendix A inference and attention model pending separate exact implementation','RITHM R33 comparison from existing archived score is not a fresh simultaneous clean-checkout run']}

    return (result,records) if return_prediction_rows else result

if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r37_ssm_source_cv.py PRIVATE_ORIGINAL_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
