"""RITHM R28: source-honest prior-payoff and public-occupancy forecasts.

Original paper §4.1: uninformed participants receive stage payoff only;
Full receive payoff and just-finished route counts. Value and realized
route cost are NOT introduced as observed predictors. Treatment 1 No,
treatment 3 Full, 24 paper-main sessions, six train/heldout session folds.
Results are exploratory prediction, NOT observed cognition or causality.
"""
from __future__ import annotations
import csv,hashlib,json,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit,xlogy

SHA="d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb"
FAMILIES={"choice":("route",),
          "choice_payoff":("route","payoff","route_payoff"),
          "choice_public":("route","occupancy","route_occupancy"),
          "choice_public_payoff":("route","occupancy","route_occupancy","payoff","route_payoff")}


def design(previous_route,previous_n,previous_payoff,family):
    if family not in FAMILIES:raise ValueError('unknown family')
    y=2*previous_route-1
    n=(previous_n-3)/3
    p=previous_payoff/10
    x={"route":y,"occupancy":n,"route_occupancy":y*n,
       "payoff":p,"route_payoff":y*p}
    return [1.]+[x[k] for k in FAMILIES[family]]


def load(path):
    p=Path(path)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=SHA:
        raise ValueError('raw author CSV SHA mismatch')
    groups=defaultdict(lambda:defaultdict(dict))
    with p.open(newline="",encoding="utf-8-sig") as stream:
        for r in csv.DictReader(stream):
            sid,trt,t=(int(r[k]) for k in ('session','trt','Period'))
            if sid in (2,101) or trt not in (1,3) or not 1<=t<=40:continue
            if int(r["Informed"])!=int(trt==3):
                raise ValueError('protocol info assignment mismatch')
            key=(sid,trt,int(r["section"]),int(r["Group"]))
            aid=int(r["ID"])
            if aid in groups[key][t]:raise ValueError('duplicate actor-period')
            groups[key][t][aid]=(int(r["RouteA"]),int(r["NumA"]),float(r["profit"]))
    results=defaultdict(list)
    for (sid,trt,section,group),periods in groups.items():
        if set(periods)!=set(range(1,41)):raise ValueError('incomplete group')
        actors=sorted(periods[1])
        if len(actors)!=6 or any(sorted(periods[t])!=actors for t in range(1,41)):
            raise ValueError('unstable six actors')
        for t in range(2,41):
            results[sid,trt].append(tuple((*periods[t-1][a],periods[t][a][0]) for a in actors))
    for trt in (1,3):
        sessions={sid for sid,t in results if t==trt}
        if len(sessions)!=24 or sum(len(results[s,trt]) for s in sessions)!=1872:
            raise ValueError('unexpected paper-main treatment group census')
    return dict(results)


def fit(xs,ys,ridge=.02):
    X=np.asarray(xs,dtype=float)
    y=np.asarray(ys,dtype=float)
    if X.ndim!=2 or y.shape!=(X.shape[0],):raise ValueError('invalid design')
    def objective(b):
        z=X@b
        value=np.logaddexp(0,z).mean()-np.mean(y*z)+.5*ridge*np.dot(b[1:],b[1:])
        grad=X.T@(expit(z)-y)/len(y)
        grad[1:]+=ridge*b[1:]
        return float(value),grad
    opt=minimize(objective,np.zeros(X.shape[1]),jac=True,method="L-BFGS-B",
                 options={"maxiter":250,"ftol":1e-12})
    if not opt.success and np.linalg.norm(opt.jac)>1e-5:
        raise ArithmeticError("optimizer did not converge")
    return opt.x


def group_metrics(probs,observed):
    p=np.asarray(probs)
    y=np.asarray(observed)
    actor_ll=np.mean(-xlogy(y,p)-xlogy(1-y,1-p))
    actor_brier=np.mean((p-y)**2)
    dist=np.array([1.])
    for q in p:dist=np.convolve(dist,[1-q,q])
    n=int(sum(y))
    stage_costs=np.array([24+3*(j-4)**2 for j in range(7)])
    return float(actor_ll),float(actor_brier),float(-np.log(max(dist[n],1e-300))),float(abs(dist@stage_costs-stage_costs[n]))


def run(path):
    groups=load(path)
    sessions=sorted({s for s,t in groups if t==3})
    folds={s:i%6 for i,s in enumerate(sessions)}
    results={}
    for trt in (1,3):
        families=("choice","choice_payoff") if trt==1 else tuple(FAMILIES)
        output={}
        for family in families:
            heldout_scores={}
            for f in range(6):
                train=[s for s in sessions if folds[s]!=f]
                test=[s for s in sessions if folds[s]==f]
                if len(train)!=20 or len(test)!=4:raise ValueError('bad session folds')
                X=[design(*v[:3],family) for s in train for g in groups[s,trt] for v in g]
                y=[v[3] for s in train for g in groups[s,trt] for v in g]
                coeff=fit(X,y)
                for s in test:
                    score=[]
                    for group in groups[s,trt]:
                        ps=expit(np.asarray([design(*v[:3],family) for v in group])@coeff)
                        score.append(group_metrics(ps,[v[3] for v in group]))
                    heldout_scores[s]=np.mean(score,axis=0)
            if set(heldout_scores)!=set(sessions):raise ValueError('missing session')
            output[family]=np.mean([heldout_scores[s] for s in sessions],axis=0).tolist()
        results[{1:"No",3:"Full"}[trt]]=output
    return dict(source_sha256=SHA,population="24 paper-main sessions exclude2,101",
                groups_per_treatment=48,scored_groups_per_treatment=1872,
                actor_choices_per_treatment=11232,
                cv="sixfold 20 train/4 heldout sessions, ridge=.02 fixed; 24 equal-session-weight results",
                metrics=["actor_logloss","actor_brier","occupancy_logloss","cost_mae"],
                results=results,
                authority="No: lagged own route and payoff only. Full: these and lagged public group count. Value/Cost NOT included as participants' disclosed features. Predictive association only.")


if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit('usage: python r28_payoff_filtration_cv.py PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
