"""RITHM R29: payoff and lawful public-count feedback in Partial (trt=2).

Original-author protocol: 3 of 6 group members get previous route
counts; all receive their previous realized payoff; informed status fixed
across 40 periods. Realized Cost/Value are NOT observed choice features.
Exploratory observational source replay. Never publish individual rows.
"""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit,xlogy

SOURCE_SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
MODELS=('route_info','route_info_payoff','route_info_payoff_public')

def design(prev_route:int,prev_occupancy:int,prev_payoff:float,informed:int,model:str):
    if model not in MODELS:raise ValueError('unsupported prediction model')
    if prev_route not in (0,1) or informed not in (0,1) or not 0<=prev_occupancy<=6:
        raise ValueError('invalid history')
    y=2*prev_route-1
    p=prev_payoff/10
    base=[1.,y,float(informed),informed*y]
    if model!='route_info':base.extend([p,y*p,informed*p,informed*y*p])
    if model=='route_info_payoff_public':
        n=(prev_occupancy-3)/3
        base.extend([informed*n,informed*y*n])
    return base

def load(path):
    p=Path(path)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('original CSV SHA mismatch')
    grouped=defaultdict(lambda:defaultdict(dict))
    with p.open(newline='',encoding='utf-8-sig') as stream:
        for r in csv.DictReader(stream):
            session,trt,t=(int(r[k]) for k in ('session','trt','Period'))
            if session in (2,101) or trt!=2 or not 1<=t<=40:continue
            key=(session,int(r['section']),int(r['Group']))
            aid=int(r['ID'])
            if aid in grouped[key][t]:raise ValueError('duplicated actor')
            grouped[key][t][aid]=(int(r['RouteA']),int(r['NumA']),float(r['profit']),int(r['Informed']))
    sessions=defaultdict(list)
    for (sid,section,g),periods in grouped.items():
        if set(periods)!=set(range(1,41)):raise ValueError('incomplete 40 periods')
        actors=sorted(periods[1])
        if len(actors)!=6 or any(sorted(periods[t])!=actors for t in range(1,41)):
            raise ValueError('actor membership instability')
        marks={a:periods[1][a][3] for a in actors}
        if set(marks.values())!={0,1} or sum(marks.values())!=3:
            raise ValueError('partial information is not 3-of-6')
        for t,record in periods.items():
            if any(record[a][3]!=marks[a] for a in actors):
                raise ValueError('information assignment changed within group')
            n=sum(record[a][0] for a in actors)
            if any(record[a][1]!=n for a in actors):raise ValueError('occupancy inconsistent')
        for t in range(2,41):
            values=tuple((*periods[t-1][a],periods[t][a][0]) for a in actors)
            sessions[sid].append(values)
    if len(sessions)!=24 or sum(map(len,sessions.values()))!=1872:
        raise ValueError('wrong 24-session Partial census')
    return dict(sessions)

def fit(rows,labels,ridge=.02):
    X=np.asarray(rows,float);y=np.asarray(labels,float)
    if X.ndim!=2 or y.shape!=(len(X),) or not len(X):raise ValueError('bad design')
    def fun(b):
        z=X@b
        value=np.logaddexp(0,z).mean()-np.mean(y*z)+ridge*np.dot(b[1:],b[1:])/2
        grad=X.T@(expit(z)-y)/len(y);grad[1:]+=ridge*b[1:]
        return float(value),grad
    r=minimize(fun,np.zeros(X.shape[1]),jac=True,method='L-BFGS-B',options={'maxiter':300,'ftol':1e-12})
    if not r.success and np.linalg.norm(r.jac)>1e-5:raise ArithmeticError('fit failed')
    return r.x

def metrics_for_group(p,y,informed):
    p=np.asarray(p,float);y=np.asarray(y,float);info=np.asarray(informed,bool)
    log=-xlogy(y,p)-xlogy(1-y,1-p)
    brier=(y-p)**2
    dist=np.array([1.])
    for v in p:dist=np.convolve(dist,[1-v,v])
    n=int(sum(y))
    cost=np.array([24+3*(j-4)**2 for j in range(7)])
    return np.array([log.mean(),brier.mean(),log[info].mean(),log[~info].mean(),
        brier[info].mean(),brier[~info].mean(),-np.log(max(dist[n],1e-300)),
        abs(dist@cost-cost[n]),np.sum(y!=np.round(p))/6])

def run(path):
    groups=load(path);session_ids=sorted(groups)
    fold={s:i%6 for i,s in enumerate(session_ids)}
    models={};per_session={}
    for model in MODELS:
        results={}
        for f in range(6):
            train=[s for s in session_ids if fold[s]!=f]
            held=[s for s in session_ids if fold[s]==f]
            if len(train)!=20 or len(held)!=4:raise ValueError('fold violation')
            X=[design(row[0],row[1],row[2],row[3],model)
                for s in train for group in groups[s] for row in group]
            Y=[row[4] for s in train for group in groups[s] for row in group]
            coef=fit(X,Y)
            for sid in held:
                values=[]
                for group in groups[sid]:
                    p=expit(np.asarray([design(row[0],row[1],row[2],row[3],model) for row in group])@coef)
                    values.append(metrics_for_group(p,[row[4] for row in group],[row[3] for row in group]))
                results[sid]=np.mean(values,axis=0)
        if set(results)!=set(session_ids):raise ValueError('missing heldout sessions')
        per_session[model]=results
        models[model]=np.mean([results[s] for s in session_ids],axis=0).tolist()
    base=per_session['route_info_payoff']
    advanced=per_session['route_info_payoff_public']
    paired={s:(advanced[s]-base[s]) for s in session_ids}
    rng=np.random.default_rng(20261110)
    boot=np.array([np.mean([paired[session_ids[i]] for i in rng.integers(0,24,24)],axis=0)
                   for _ in range(2000)])
    percentiles=np.percentile(boot,[2.5,97.5],axis=0).T.tolist()
    return dict(source_sha256=SOURCE_SHA,population='24 paper-restricted sessions; Partial trt2',
        groups=48,group_periods=1872,individual_decisions=11232,
        informed_decisions=5616,uninformed_decisions=5616,
        session_cv='six folds, 20 train/4 heldout, fixed ridge 0.02, sessions equally weighted',
        columns=['actor_logloss','actor_brier','informed_logloss','uninformed_logloss',
                 'informed_brier','uninformed_brier','group_count_logloss','cost_mae','threshold_error_rate'],
        results=models,
        delta_public_minus_payoff=np.mean([paired[s] for s in session_ids],axis=0).tolist(),
        exploratory_cluster_bootstrap95=percentiles,
        disclosure='Partial: only 3 fixed actors/group know previous route counts, all 6 observe own previous payoff; do not use hidden count for uninformed predictors',
        limitation='Observational predictive association only. No causal information effect, no actual cognitive effort or hassle identification; no order correction; group forecast assumes conditionally independent individual probabilities.')

if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r29_partial_information_cv.py ORIGINAL_PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
