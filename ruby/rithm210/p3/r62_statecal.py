"""R62: state-conditioned *RESEARCHER ORACLE* independent actor calibration.

Access to previous exact six-seat occupancy A(t-1) is NOT legal as a
No-information participant cognitive feature. This rival is an analyst-only
negative control for marginal misspecification, NOT a lawful actor mechanism.
"""
from collections import defaultdict
from math import log
from random import Random
from statistics import mean
import numpy as np
from r61_adaptive_prior import summarize_session_bases,base_without,get_pbase,adaptive_probability,get_predictions
from r62_batch import prepare,batch_law
from r62_collective import aggregate


def logit(p):
    if not 0<p<1:raise ValueError('open probability')
    return np.log(p/(1-p))


def sigmoid(x):return 1/(1+np.exp(-np.clip(x,-80,80)))


def fit_logit_shift(p,flip):
    """Unique unpenalized likelihood intercept; tiny pseudocount shrinks extremes."""
    if not len(p) or len(p)!=len(flip):raise ValueError('training must contain predictions and outcomes')
    z=np.log(p/(1-p)); y=np.asarray(flip)
    if not np.all((p>0)&(p<1)) or not np.all((y==0)|(y==1)):
        raise ValueError('invalid original outcomes/probabilities')
    # Add .5 pseudo observation at each boundary by shrinking fitted mean.
    target=(y.sum()+.5)/(len(y)+1)
    lo,hi=-8.,8.
    for _ in range(60):
        mid=(lo+hi)/2
        if sigmoid(z+mid).mean()<target:lo=mid
        else:hi=mid
    return (lo+hi)/2


def score_statecal(events,*,mode='a4',actor_model='current_only',bootstrap=2000,seed=20261121):
    if mode not in ('a4','a4_early_late') or actor_model not in ('current_only','nested_adaptive'):
        raise ValueError('unsupported oracle state condition')
    D=prepare(events); sids=sorted(set(D['session']))
    if len(sids)!=24:raise ValueError('24 sessions required')
    a=D['old'].sum(axis=1)
    epoch=(D['period']>=21).astype(int)
    strata=(a==4).astype(int) if mode=='a4' else ((a==4).astype(int)*2+epoch)
    y=np.array([[e['flip'] for e in gr] for _,gr,_,_,_ in D['items']],dtype=int)
    totals=summarize_session_bases(events)
    chosen={s:0 for s in sids}
    if actor_model=='nested_adaptive':_,chosen,_=get_predictions(events)
    by_s=defaultdict(list)
    shifts=[]
    for held in sids:
        base=base_without(totals,{held})
        p=np.array([[adaptive_probability(e,get_pbase(e,base),chosen[held]) for e in group]
                    for _,group,_,_,_ in D['items']])
        train=D['session']!=held
        delta={}
        for group in sorted(set(strata)):
            mask=train&(strata==group)
            delta[int(group)]=fit_logit_shift(p[mask].ravel(),y[mask].ravel())
        shifts.append(delta)
        updated=sigmoid(np.log(p/(1-p))+np.array([delta[int(k)] for k in strata])[:,None])
        check=D['session']==held
        t,pno=batch_law(D['old'][check],updated[check],D['u'][check],D['d'][check],D['period'][check],'independent',0)
        ix=np.where(check)[0]
        for pos,i in enumerate(ix):
            by_s[held].append((held,int(D['period'][i]),int(a[i]),float(-np.log(t[pos])),float(pno[pos]),int(D['u'][i]==0 and D['d'][i]==0),float(updated[i].sum()),int(D['u'][i]+D['d'][i])))
    item={mode:by_s,'independent':by_s}
    d=aggregate({'independent':by_s},{},bootstrap=bootstrap,seed=seed)['scores']['independent']
    d['researcher_oracle_not_legal_for_no_info']=True
    d['average_train_only_intercepts']={str(k):mean(x[k] for x in shifts) for k in shifts[0]}
    d['per_session_group_logloss']=None  # never publish per-session original measurements
    return d,shifts,by_s
