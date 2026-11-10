"""RITHM R27-R3: exact labelled six-actor switching-friction welfare model.

Synthetic 448-state probability propagation. Private choice compares hypothetical
unilateral route costs, holding OTHER actors at their previously chosen routes.
Realised simultaneous choices need not equal those unilateral predictions.
friction is a REAL switching resource cost included in social welfare, not
a calibrated psychological aversion. No human-causal claim.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp, prod, isfinite

BITS=tuple(tuple((m>>i)&1 for i in range(6)) for m in range(64))
COUNTS=tuple(sum(b) for b in BITS)
COST=tuple(24+3*(n-4)**2 for n in range(7))

def sigmoid(x):
    if x>=0:return 1/(1+exp(-x))
    e=exp(x)
    return e/(1+e)

@dataclass(frozen=True)
class Params:
    beta:float
    friction:float
    memory:float=0.
    tau:float=0.
    def __post_init__(self):
        if any(not isfinite(x) for x in (self.beta,self.friction,self.memory,self.tau)):
            raise ValueError('finite parameters required')
        if self.beta<0 or self.friction<0 or not 0<=self.memory<=1 or not 0<=self.tau<=1:
            raise ValueError('invalid parameter')

def private_improvement(n,prior_route):
    if type(n) is not int or n not in range(7) or prior_route not in (0,1):
        raise ValueError('invalid state')
    if prior_route==0:
        if n==6:raise ValueError('no B actor')
        return 11-3*n
    if n==0:raise ValueError('no A actor')
    return 3*n-14

def social_improvement(n,prior_route):
    if type(n) is not int or n not in range(7) or prior_route not in (0,1):
        raise ValueError('invalid state')
    if prior_route==0:
        if n==6:raise ValueError('no B actor')
        return COST[n]-COST[n+1]
    if n==0:raise ValueError('no A actor')
    return COST[n]-COST[n-1]

def state_marginals(mask,older,p):
    if type(mask) is not int or mask not in range(64) or type(older) is not int or older not in range(7):
        raise ValueError('invalid history')
    n=(1-p.memory)*COUNTS[mask]+p.memory*older
    return tuple(sigmoid(p.beta*((14-3*n+p.friction) if prior else
                                   (11-3*n-p.friction))) for prior in BITS[mask])

def _product(ps):
    return tuple(prod(q if bit else 1-q for bit,q in zip(bits,ps)) for bits in BITS)

def transition(mask,older,p):
    ps=state_marginals(mask,older,p)
    if p.tau==0:return _product(ps)
    shifts=[p.tau*(2*y-1)*min(q,1-q) for y,q in zip(BITS[mask],ps)]
    plus=_product([q+d for q,d in zip(ps,shifts)])
    minus=_product([q-d for q,d in zip(ps,shifts)])
    return tuple((a+b)/2 for a,b in zip(plus,minus))

def exact_horizon(p,horizon=40):
    if type(horizon) is not int or not 1<=horizon<=400:raise ValueError('invalid horizon')
    states={(mask,COUNTS[mask]):1/64 for mask in range(64)}
    cache={}
    series=[]
    for t in range(1,horizon+1):
        future={}
        congestion=switches=turnover=0.
        for (mask,older),mass in states.items():
            if (mask,older) not in cache:cache[mask,older]=transition(mask,older,p)
            for nxt,prob in enumerate(cache[mask,older]):
                q=mass*prob
                if q==0:continue
                n=COUNTS[nxt]
                congestion+=q*COST[n]
                switches+=q*(mask^nxt).bit_count()
                turnover+=q*abs(n-COUNTS[mask])
                key=(nxt,COUNTS[mask])
                future[key]=future.get(key,0.)+q
        if abs(sum(future.values())-1)>1e-9:raise ArithmeticError('mass conservation')
        series.append({'t':t,'expected_congestion':congestion,
                       'expected_switches':switches,
                       'expected_total_social':congestion+p.friction*switches,
                       'expected_abs_delta_occupancy':turnover})
        states=future
    return {'parameters':vars(p),'horizon':horizon,
            'mean_congestion':sum(r['expected_congestion'] for r in series)/horizon,
            'mean_switches':sum(r['expected_switches'] for r in series)/horizon,
            'mean_social_cost':sum(r['expected_total_social'] for r in series)/horizon,
            'mean_turnover':sum(r['expected_abs_delta_occupancy'] for r in series)/horizon,
            'series':series}

if __name__=='__main__':
    import json,argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--beta',type=float,default=.6)
    parser.add_argument('--friction',type=float,default=7.25)
    parser.add_argument('--memory',type=float,default=0.)
    parser.add_argument('--tau',type=float,default=0.)
    a=parser.parse_args()
    z=exact_horizon(Params(a.beta,a.friction,a.memory,a.tau))
    print(json.dumps({k:v for k,v in z.items() if k!='series'},indent=2))
