"""R27-R4: independent revision opportunities vs resource switching costs.

Source-free synthetic 6-actor exact 448-state/40-period probability propagation.
Eligibility is independent conditional on history; with no opportunity, keep
prior route. State-dependent hazard uses private net gain from unilateral change.
NOT a human cognitive estimate, social intervention or a theorem of optimality.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp,isfinite,prod
from r27_r3_switching_welfare import BITS,COUNTS,COST,Params,state_marginals


def logistic(x):
    if x >= 0: return 1/(1+exp(-x))
    q=exp(x);return q/(1+q)


@dataclass(frozen=True)
class Revision:
    chance:float=1.
    hazard_slope:float=0.
    hazard_center:float=0.
    def __post_init__(self):
        if any(not isfinite(v) for v in (self.chance,self.hazard_slope,self.hazard_center)):
            raise ValueError('nonfinite revision parameter')
        if not 0<=self.chance<=1 or self.hazard_slope<0:
            raise ValueError('invalid revision parameter')


def revision_marginals(mask,older,p,rev):
    base=state_marginals(mask,older,p)
    n=(1-p.memory)*COUNTS[mask]+p.memory*older
    effective=[];rates=[]
    for y,q in zip(BITS[mask],base):
        # For prior A: A->B private improvement=3*n-14-s;
        # for prior B: B->A private improvement=11-3*n-s.
        gain=(3*n-14-p.friction) if y else (11-3*n-p.friction)
        rate=rev.chance if rev.hazard_slope==0 else rev.chance*logistic(rev.hazard_slope*(gain-rev.hazard_center))
        effective.append((1-rate)*y+rate*q)
        rates.append(rate)
    return tuple(effective),tuple(rates)


def _product(ps):
    return tuple(prod(q if bit else 1-q for bit,q in zip(bits,ps)) for bits in BITS)


def transition(mask,older,p,rev):
    ps,_=revision_marginals(mask,older,p,rev)
    if p.tau==0:return _product(ps)
    shifts=[p.tau*(2*y-1)*min(q,1-q) for y,q in zip(BITS[mask],ps)]
    hi=_product([q+d for q,d in zip(ps,shifts)])
    lo=_product([q-d for q,d in zip(ps,shifts)])
    return tuple((a+b)/2 for a,b in zip(hi,lo))


def exact_horizon(p,rev,horizon=40):
    if type(horizon) is not int or not 1<=horizon<=400:raise ValueError('invalid horizon')
    states={(m,COUNTS[m]):1/64 for m in range(64)}
    cache={};series=[]
    for t in range(1,horizon+1):
        next_states={};congestion=switches=turnover=0.
        for (mask,older),weight in states.items():
            key=(mask,older)
            if key not in cache:cache[key]=transition(mask,older,p,rev)
            for nxt,prob in enumerate(cache[key]):
                mass=weight*prob
                if mass==0:continue
                n=COUNTS[nxt];sw=(mask^nxt).bit_count()
                congestion+=mass*COST[n]
                switches+=mass*sw
                turnover+=mass*abs(n-COUNTS[mask])
                key2=(nxt,COUNTS[mask])
                next_states[key2]=next_states.get(key2,0.)+mass
        if abs(sum(next_states.values())-1)>1e-9:raise ArithmeticError('lost probability mass')
        series.append(dict(period=t,congestion=congestion,switches=switches,
                           social=congestion+p.friction*switches,turnover=turnover))
        states=next_states
    return dict(parameters=vars(p),revision=vars(rev),horizon=horizon,
                mean_congestion=sum(x['congestion'] for x in series)/horizon,
                mean_switches=sum(x['switches'] for x in series)/horizon,
                mean_social_cost=sum(x['social'] for x in series)/horizon,
                mean_turnover=sum(x['turnover'] for x in series)/horizon,
                series=series)


if __name__=='__main__':
    import json
    for s in (0.,4.,7.25):
        for rho in (1.,.75,.5,.25,.1):
            v=exact_horizon(Params(.6,s),Revision(rho))
            print(json.dumps({k:x for k,x in v.items() if k!='series'},sort_keys=True))
