"""R62: actor-legal feedback + analyst marginal-preserving group-pause residual.

At every heldout session, actor baselines and payoff/tenure offsets are fit using
only the other 23 sessions. Group q is likewise selected on the 23 training
sessions, separately under joint logloss vs A4 no-switch Brier.
"""
from collections import defaultdict
from statistics import mean
import numpy as np
from r61_adaptive_prior import summarize_session_bases,base_without,get_pbase,adaptive_probability,get_predictions
from r62_batch import prepare,batch_law
from r62_statecal import fit_logit_shift,sigmoid
from r62_collective import GRID,aggregate
from r62_legal_feedback import stratum


def fit_legal_by_held(events,base_mode='nested_adaptive'):
    if base_mode not in ('current_only','nested_adaptive'):raise ValueError('unsupported source-lawful actor')
    D=prepare(events)
    y=np.array([[e['flip'] for e in grp] for _,grp,_,_,_ in D['items']],dtype=int)
    state=np.array([[stratum(e,'payoff_tenure_9') for e in grp] for _,grp,_,_,_ in D['items']],dtype=int)
    sessions=sorted(set(D['session']))
    if len(sessions)!=24:raise ValueError('24 sessions required')
    base_total=summarize_session_bases(events)
    tau={s:0 for s in sessions}
    if base_mode=='nested_adaptive':_,tau,_=get_predictions(events)
    for held in sessions:
        trained=base_without(base_total,{held})
        p=np.array([[adaptive_probability(e,get_pbase(e,trained),tau[held]) for e in grp]
                    for _,grp,_,_,_ in D['items']])
        train=D['session']!=held
        delta=np.zeros_like(p);shifts={}
        for k in range(9):
            mask=train[:,None]&(state==k)
            shift=fit_logit_shift(p[mask],y[mask]) if mask.sum()>=10 else 0.
            shifts[k]=shift
            delta[state==k]=shift
        updated=sigmoid(np.log(p/(1-p))+delta)
        yield held,D,updated,shifts,trained,tau[held]


def legal_joint_cv(events,*,base_mode='nested_adaptive',bootstrap=2000):
    modes={
      'legal_independent':('independent',0,'joint'),
      'legal_pause_joint':('pause_at_four',None,'joint'),
      'legal_pause_stability':('pause_at_four',None,'stability'),
      'legal_common_shock_joint':('common_positive',None,'joint'),
    }
    result={m:defaultdict(list) for m in modes}
    selected={m:[] for m in modes if m!='legal_independent'}
    for held,D,p,shifts,b,tau in fit_legal_by_held(events,base_mode):
        train=D['session']!=held;test=~train
        for name,(model,q,objective) in modes.items():
            if q is None:
                scores=[]
                for c in GRID:
                    v,pzero=batch_law(D['old'][train],p[train],D['u'][train],D['d'][train],D['period'][train],model,c)
                    if objective=='joint':scores.append(float(np.mean(-np.log(v))))
                    else:
                        atfour=train&(D['old'].sum(axis=1)==4)
                        _,z=batch_law(D['old'][atfour],p[atfour],D['u'][atfour],D['d'][atfour],D['period'][atfour],model,c)
                        obs=(D['u'][atfour]==0)&(D['d'][atfour]==0)
                        scores.append(float(np.mean((z-obs)**2)))
                q=GRID[int(np.argmin(scores))]
                selected[name].append(q)
            v,pzero=batch_law(D['old'][test],p[test],D['u'][test],D['d'][test],D['period'][test],model,q)
            for pos,i in enumerate(np.where(test)[0]):
                result[name][held].append((held,int(D['period'][i]),int(D['old'][i].sum()),float(-np.log(v[pos])),float(pzero[pos]),int(D['u'][i]==0 and D['d'][i]==0),float(p[i].sum()),int(D['u'][i]+D['d'][i])))
    # aggregate requires literal independent baseline alias
    x={'independent':result['legal_independent']}
    x.update({k:v for k,v in result.items() if k!='legal_independent'})
    sel={k:v for k,v in selected.items()}
    a=aggregate(x,sel,bootstrap=bootstrap)['scores']
    return {'base_mode':base_mode,'scored':a,'training_strata':'nine prior-own-payoff/tenure categories; no researcher full occupancy in personal actor p; analyst-only pause gate',
            'same_person_marginal_law_for_joint_rivals':True}
