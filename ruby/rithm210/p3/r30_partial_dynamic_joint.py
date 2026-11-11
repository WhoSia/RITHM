"""RITHM R30: legal Partial payoff×information×time prediction and R26 joint-shock rival.

24 original paper-main sessions; original CSV SHA verified by r29_partial_information_cv.load.
Exploratory reused source, not causal cognitive effort evidence. No actor rows are exported.
"""
from __future__ import annotations
import json,sys
import numpy as np
from scipy.special import expit,xlogy
from r29_partial_information_cv import load,fit,SOURCE_SHA

FAMILIES=('payoff_public','payoff_public_late')
TAUS=(0.,.2,.4,.6)
COST=np.array([24+3*(n-4)**2 for n in range(7)])

def design(row,t,family):
    if family not in FAMILIES or type(t) is not int or not 2<=t<=40:raise ValueError('bad model/period')
    y,n,p,info,_=row
    if y not in (0,1) or info not in (0,1) or not np.isfinite(p):raise ValueError('bad actor history')
    a=2*y-1;p/=10
    # No public occupancy for uninformed actor; the hidden input never affects these features.
    n=(n-3)/3 if info else 0.
    x=[1.,a,float(info),info*a,p,a*p,info*p,info*a*p,n,n*a]
    if family=='payoff_public_late':
        late=float(t>=21)
        x.extend([late,late*a,late*info,late*info*a,late*p,late*a*p,
                  late*info*p,late*info*a*p,late*n,late*n*a])
    return x

def poisson_binomial(q):
    law=np.array([1.])
    for x in q:law=np.convolve(law,[1-x,x])
    return law

def score(q,previous,y,tau):
    q=np.asarray(q,float);previous=np.asarray(previous,int);y=np.asarray(y,int)
    if q.shape!=(6,) or previous.shape!=(6,) or y.shape!=(6,) or not 0<=tau<=1:
        raise ValueError('six-person probability contract')
    if np.any((q<=0)|(q>=1)):raise ValueError('bad probability')
    delta=tau*(2*previous-1)*np.minimum(q,1-q)
    a,b=q+delta,q-delta
    pa,pb=poisson_binomial(a),poisson_binomial(b)
    count=(pa+pb)/2
    joint=(np.prod(np.where(y,a,1-a))+np.prod(np.where(y,b,1-b)))/2
    n=int(sum(y));mean=float(q.sum());variance=float(np.dot(count,np.arange(7)**2)-mean**2)
    bernoulli=float(sum(q*(1-q)));pred=float(count@COST)
    return np.array([np.mean(-xlogy(y,q)-xlogy(1-y,1-q)),
       -np.log(max(joint,1e-300)),-np.log(max(count[n],1e-300)),
       abs(pred-COST[n]),pred,variance,bernoulli,variance-bernoulli,
       np.mean((q-y)**2)])


def joint_scores(ps, prior_routes, observed, tau):
    """R31/R32/R33 compatibility alias for the unchanged R30 nine-metric score law.

    Keep this stable public function when renaming internal scorer.
    The original source-free checker imports this name from R31.
    """
    return score(ps, prior_routes, observed, tau)


def predictions(groups,coef,family):
    out=[]
    for idx,g in enumerate(groups):
        t=idx%39+2
        q=expit(np.asarray([design(r,t,family) for r in g])@coef)
        out.append((q,[r[0] for r in g],[r[4] for r in g]))
    return out

def average(preds,tau):
    return np.mean([score(*v,tau) for v in preds],axis=0)

def run(path):
    source=load(path)
    sessions=sorted(source)
    if len(sessions)!=24:raise ValueError('24 source sessions required')
    fold={s:i%6 for i,s in enumerate(sessions)}
    results={};saved={};selections={}
    for family in FAMILIES:
        held={};select=[]
        for f in range(6):
            training=[s for s in sessions if fold[s]!=f]
            testing=[s for s in sessions if fold[s]==f]
            if len(training)!=20 or len(testing)!=4:raise ValueError('bad fold')
            X=[];Y=[]
            for s in training:
                for idx,g in enumerate(source[s]):
                    t=idx%39+2
                    for r in g:
                        X.append(design(r,t,family));Y.append(r[4])
            coef=fit(X,Y,ridge=.02)
            train={s:predictions(source[s],coef,family) for s in training}
            train_loss={tau:float(np.mean([average(train[s],tau)[1] for s in training]))
                        for tau in TAUS}
            chosen=min(TAUS,key=lambda tau:(train_loss[tau],tau))
            select.append({'fold':f,'chosen_tau':chosen,'training_joint_loss':train_loss})
            for s in testing:
                p=predictions(source[s],coef,family)
                held[s]={'independent':average(p,0.),
                         'selected':average(p,chosen)}
        if set(held)!=set(sessions):raise ValueError('heldout incomplete')
        results[family]={key:np.mean([held[s][key] for s in sessions],axis=0).tolist()
                         for key in ('independent','selected')}
        saved[family]=held;selections[family]=select
    pairs=(('time_interaction','payoff_public','independent','payoff_public_late','independent'),
           ('joint_shock_baseline','payoff_public','independent','payoff_public','selected'),
           ('joint_shock_time','payoff_public_late','independent','payoff_public_late','selected'))
    contrasts={}
    for name,af,at,bf,bt in pairs:
        values=np.array([saved[bf][s][bt]-saved[af][s][at] for s in sessions])
        rng=np.random.default_rng(20261110)
        resamples=values[rng.integers(0,24,(3000,24))].mean(axis=1)
        contrasts[name]={'delta':values.mean(axis=0).tolist(),
             'exploratory_session_bootstrap95':np.quantile(resamples,[.025,.975],axis=0).T.tolist()}
    return {'source_sha256':SOURCE_SHA,
      'population':'Partial 24 source sessions; 48 groups, 39 predicted periods each',
      'metrics':['actor_logloss','six_mask_joint_logloss','occupancy_logloss','cost_MAE',
                 'expected_cost','total_count_variance','independent_variance',
                 'covariance_contribution','actor_brier'],
      'result':results,'train_only_tau':selections,'contrasts':contrasts,
      'authority':'Exploratory historical reuse; Partial 3 informed with public last count; all 6 know last own payoff; endogenous prior route; t>=21 known. No cost/value oracle and no causality.'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python r30_partial_dynamic_joint.py PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
