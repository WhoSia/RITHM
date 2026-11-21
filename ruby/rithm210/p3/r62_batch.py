"""Vectorized exact six-person Poisson-binomial score; same stochastic law as r62_collective.
Only arithmetic is vectorized. Fold assignment and information filtration unchanged.
"""
from collections import Counter, defaultdict
import numpy as np
from r61_adaptive_prior import get_predictions, summarize_session_bases,base_without,get_pbase,adaptive_probability
from r62_collective import FROZEN,GRID


def batch_pb(p):
    """Compute P(sum of independent Bernoulli)=k over each row of six (0 allowed)."""
    if p.ndim!=2 or p.shape[1]!=6:raise ValueError('six Bernoulli trials required')
    n=p.shape[0]
    out=np.zeros((n,7));out[:,0]=1
    for j in range(6):
        x=p[:,j]
        nxt=np.zeros_like(out)
        nxt[:,0]=out[:,0]*(1-x)
        nxt[:,1:]=out[:,1:]*(1-x[:,None])+out[:,:-1]*x[:,None]
        out=nxt
    return out


def batch_law(old,ps,u,d,period,mode,q):
    """Vectorized true target (U,D) mass and no-switch mass, per group."""
    if old.shape!=ps.shape or old.ndim!=2 or old.shape[1]!=6:raise ValueError('six-person inputs')
    n=old.shape[0];r=np.arange(n)
    if not n:return (np.array([]),np.array([]))
    if not np.all((ps>0)&(ps<1)):raise ValueError('strictly open marginals')
    def joint(pp):
        up=batch_pb(np.where(old==0,pp,0))
        down=batch_pb(np.where(old==1,pp,0))
        return up[r,u]*down[r,d]
    if mode=='common_positive':
        delta=q*np.minimum(ps,1-ps)
        target=.5*(joint(ps+delta)+joint(ps-delta))
        no=.5*(np.prod(1-ps-delta,axis=1)+np.prod(1-ps+delta,axis=1))
    else:
        qq=np.minimum(q,(1-ps.max(axis=1))*.999999)
        if mode=='independent':qq*=0
        elif mode=='pause_uniform':pass
        elif mode=='pause_at_four':qq=np.where(old.sum(axis=1)==4,qq,0)
        elif mode=='pause_late_four':qq=np.where((old.sum(axis=1)==4)&(period>=21),qq,0)
        else:raise ValueError('bad mode')
        act=ps/(1-qq[:,None])
        target=(1-qq)*joint(act)+np.where((u==0)&(d==0),qq,0)
        no=qq+(1-qq)*np.prod(1-act,axis=1)
    if np.any(target<=0) or np.any(no<=0):raise ArithmeticError('zero event probability')
    return target,no


def prepare(events):
    """Transient researcher-only original rows, returned solely inside process."""
    group=defaultdict(list)
    for e in events:group[e['session'],e['section'],e['group'],e['period']].append(e)
    items=[]
    for key,g in sorted(group.items()):
        if len(g)!=6:raise ValueError('six-person source required')
        g=sorted(g,key=lambda x:x['actor'])
        old=[e['previous_route'] for e in g]
        u=sum(e['flip'] and not e['previous_route'] for e in g)
        d=sum(e['flip'] and e['previous_route'] for e in g)
        items.append((key,g,old,u,d))
    return {'items':items,
       'session':np.array([x[0][0] for x in items],dtype=int),
       'period':np.array([x[0][3] for x in items],dtype=int),
       'old':np.array([x[2] for x in items],dtype=int),
       'u':np.array([x[3] for x in items],dtype=int),
       'd':np.array([x[4] for x in items],dtype=int)}


def full_cv_fast(events,*,actor_model='current_only',selector='joint'):
    if actor_model not in ('current_only','nested_adaptive'):raise ValueError('bad actor model')
    if selector not in ('joint','a4_no_switch_brier'):raise ValueError('bad tuning loss')
    sessions=sorted({e['session'] for e in events})
    if len(sessions)!=24:raise ValueError('24 original sessions required')
    D=prepare(events);G=len(D['items'])
    total=summarize_session_bases(events)
    tau_choice={s:0 for s in sessions}
    if actor_model=='nested_adaptive':_,tau_choice,_=get_predictions(events)
    result={m:defaultdict(list) for m in FROZEN}
    q_sel={m:[] for m in FROZEN if m!='independent'}
    for held in sessions:
        base=base_without(total,{held})
        ps=np.array([[adaptive_probability(e,get_pbase(e,base),tau_choice[held]) for e in gr]
                     for _,gr,_,_,_ in D['items']])
        train=D['session']!=held; test=~train
        for m in FROZEN:
            if m=='independent':q=0
            else:
                score=[]
                for candidate in GRID:
                    target,pzero=batch_law(D['old'][train],ps[train],D['u'][train],D['d'][train],D['period'][train],m,candidate)
                    if selector=='joint': score.append(float(np.mean(-np.log(target))))
                    else:
                        a4=train&(D['old'].sum(axis=1)==4)
                        _,z_at_four=batch_law(D['old'][a4],ps[a4],D['u'][a4],D['d'][a4],D['period'][a4],m,candidate)
                        truth=(D['u'][a4]==0)&(D['d'][a4]==0)
                        score.append(float(np.mean((z_at_four-truth)**2)))
                q=GRID[int(np.argmin(score))]
                q_sel[m].append(q)
            targ,no=batch_law(D['old'][test],ps[test],D['u'][test],D['d'][test],D['period'][test],m,q)
            idxs=np.where(test)[0]
            for j,i in enumerate(idxs):
                result[m][held].append((held,int(D['period'][i]),int(D['old'][i].sum()),float(-np.log(targ[j])),float(no[j]),int(D['u'][i]==0 and D['d'][i]==0),float(ps[i].sum()),int(D['u'][i]+D['d'][i])))
    return result,q_sel
