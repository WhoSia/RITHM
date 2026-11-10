"""RITHM R27-R5: matched expected revision vs matched switching budgets.

Exact 448-state forward Markov calculation with NumPy, no Monte Carlo.
The benchmark matches the ADAPTIVE model's own 40-round endogenous expected
review opportunities (or switches), not per-period opportunity allocations.
Assumed zero review/agency cost; synthetic not an identified policy effect.
"""
from __future__ import annotations
from dataclasses import dataclass,asdict
import math
import numpy as np
from r27_r3_switching_welfare import Params

MASKS=np.repeat(np.arange(64),7)
OLDERS=np.tile(np.arange(7),64)
BITS=((MASKS[:,None]>>np.arange(6))&1).astype(float)
NEXT_BITS=((np.arange(64)[:,None]>>np.arange(6))&1).astype(float)
COUNTS=NEXT_BITS.sum(axis=1).astype(int)
PREV_COUNT=COUNTS[MASKS]
COST=(24+3*(COUNTS-4)**2).astype(float)
TURN=np.abs(COUNTS[None,:]-PREV_COUNT[:,None])
DEST=(np.arange(64)[None,:]*7+PREV_COUNT[:,None]).astype(int)
SRC=np.broadcast_to(np.arange(448)[:,None],DEST.shape)
PRIOR=np.zeros(448)
PRIOR[np.arange(64)*7+COUNTS]=1/64


def _sigmoid(z):
    return np.exp(-np.logaddexp(0,-z))


@dataclass(frozen=True)
class Policy:
    max_chance:float
    slope:float=0.
    center:float=0.
    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.max_chance,self.slope,self.center)):
            raise ValueError('nonfinite revision policy')
        if not 0<=self.max_chance<=1 or self.slope<0:
            raise ValueError('invalid revision policy')


def compile_kernel(p:Params,policy:Policy):
    n=(1-p.memory)*PREV_COUNT[:,None]+p.memory*OLDERS[:,None]
    gain=np.where(BITS==1,3*n-14-p.friction,11-3*n-p.friction)
    logits=np.where(BITS==1,p.beta*(14-3*n+p.friction),
                     p.beta*(11-3*n-p.friction))
    revise_A=_sigmoid(logits)
    if policy.slope==0:
        h=np.full_like(gain,policy.max_chance)
    else:
        h=policy.max_chance*_sigmoid(policy.slope*(gain-policy.center))
    ps=(1-h)*BITS+h*revise_A
    def product_law(z):
        return np.prod(np.where(NEXT_BITS[None,:,:]==1,z[:,None,:],
                                1-z[:,None,:]),axis=2)
    if p.tau==0:
        law=product_law(ps)
    else:
        d=p.tau*(2*BITS-1)*np.minimum(ps,1-ps)
        law=(product_law(ps+d)+product_law(ps-d))/2
    mat=np.zeros((448,448))
    mat[SRC,DEST]=law
    if not np.allclose(mat.sum(axis=1),1,atol=5e-13):
        raise ArithmeticError('transition not normalized')
    return (mat,law@COST,np.sum(law*TURN,axis=1),
            h.sum(axis=1),np.abs(ps-BITS).sum(axis=1))


def evaluate(p:Params,policy:Policy,horizon:int=40):
    if type(horizon) is not int or not 1<=horizon<=400:
        raise ValueError('bad horizon')
    mat,cost,turn,review,switch=compile_kernel(p,policy)
    state=PRIOR.copy()
    total=np.zeros(5)
    trace=[]
    for t in range(1,horizon+1):
        vals=np.array([state@cost,state@turn,state@review,state@switch,
                       state@(cost+p.friction*switch)])
        total+=vals
        trace.append(dict(t=t,congestion=float(vals[0]),turnover=float(vals[1]),
                          review_opportunities=float(vals[2]),
                          actual_switches=float(vals[3]),total_social=float(vals[4])))
        state=state@mat
        if abs(state.sum()-1)>1e-10:
            raise ArithmeticError('probability mass drift')
    a=total/horizon
    return dict(params=vars(p),policy=asdict(policy),horizon=horizon,
                mean_congestion=float(a[0]),mean_turnover=float(a[1]),
                mean_review_opportunities=float(a[2]),
                mean_actual_switches=float(a[3]),mean_total_social=float(a[4]),
                trace=trace)


def _comparison(adaptive,baseline):
    names=('mean_congestion','mean_turnover','mean_review_opportunities',
           'mean_actual_switches','mean_total_social')
    return dict(adaptive=adaptive,matched_uniform=baseline,
                delta_adaptive_minus_matched={
                    key:adaptive[key]-baseline[key] for key in names})


def match_uniform(p:Params,adaptive:Policy,horizon:int=40,tolerance=5e-8):
    """Match REALIZED expected review opportunities, not merely max_chance."""
    if adaptive.slope<=0:raise ValueError('must be adaptive')
    a=evaluate(p,adaptive,horizon)
    # Uniform hazard gives 6*rho review opportunities on every state/time.
    rho=a['mean_review_opportunities']/6
    b=evaluate(p,Policy(rho),horizon)
    if abs(a['mean_review_opportunities']-b['mean_review_opportunities'])>tolerance:
        raise ArithmeticError('opportunity budget not matched')
    return _comparison(a,b)


def match_switches(p:Params,adaptive:Policy,horizon:int=40,tolerance=5e-6):
    """Match expected ACTUAL switches using checked monotone uniform family."""
    if adaptive.slope<=0:raise ValueError('must be adaptive')
    a=evaluate(p,adaptive,horizon)
    target=a['mean_actual_switches']
    grid=[evaluate(p,Policy(i/10),horizon)['mean_actual_switches']
          for i in range(11)]
    if any(x>y+1e-9 for x,y in zip(grid,grid[1:])):
        raise ValueError('nonmonotone uniform switch response')
    if target>grid[-1]+tolerance:
        raise ValueError('unreachable target')
    lo,hi=0.,1.
    for _ in range(24):
        mid=(lo+hi)/2
        rate=evaluate(p,Policy(mid),horizon)['mean_actual_switches']
        if rate<target:lo=mid
        else:hi=mid
    b=evaluate(p,Policy((lo+hi)/2),horizon)
    if abs(b['mean_actual_switches']-target)>tolerance:
        raise ArithmeticError('switch budget not matched')
    return _comparison(a,b)


if __name__=='__main__':
    import json
    p=Params(.6,0.)
    for rho in (.1,.3,.5,1.):
        a=match_uniform(p,Policy(rho,3.))
        b=match_switches(p,Policy(rho,3.))
        print(json.dumps(dict(max_chance=rho,
              adaptive_cost=a['adaptive']['mean_congestion'],
              matched_opportunity_cost=a['matched_uniform']['mean_congestion'],
              matched_switch_cost=b['matched_uniform']['mean_congestion'],
              review_budget=a['adaptive']['mean_review_opportunities'],
              switch_budget=a['adaptive']['mean_actual_switches']),
              sort_keys=True))


def occupancy_quadratic_drift(p:Params,policy:Policy):
    """Conditional E[V(next)-V(now)], V=(previous occupancy - 4)^2.

    Not a strict stochastic Lyapunov certificate: noise can create positive
    drift at the zero of V even when the stochastic chain is ergodic.
    """
    mat,*_=compile_kernel(p,policy)
    v=(PREV_COUNT-4.)**2
    return mat@v-v
