"""RITHM-2.10 R27-R2: exact six-actor observable-lag dynamics.

SYNTHETIC (not fitted). State at t is (labelled previous choices, older
occupancy). In the author experiment, Full-treatment participants received previous
period route counts; the older signal was available one period earlier but
actual memory/use is unobserved. No human cognition is identified. Independent Bernoulli choices or R26-compatible fair
previous-route-signed common innovation preserve each person's marginal.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import exp,isfinite,prod

BITS=tuple(tuple((m>>i)&1 for i in range(6)) for m in range(64))
COUNTS=tuple(sum(x) for x in BITS)
COSTS=tuple(24+3*(n-4)**2 for n in range(7))

def sigmoid(x):
    if x>=0:return 1/(1+exp(-x))
    z=exp(x);return z/(1+z)

@dataclass(frozen=True)
class Params:
    beta:float
    inertia:float=0.
    memory_weight:float=0.
    tau:float=0.
    bias:float=0.
    def __post_init__(self):
        if any(not isfinite(v) for v in (self.beta,self.inertia,self.memory_weight,self.tau,self.bias)):
            raise ValueError('nonfinite parameter')
        if self.beta<0 or self.inertia<0 or not 0<=self.memory_weight<=1 or not 0<=self.tau<=1:
            raise ValueError('out-of-range parameter')

def actor_ps(mask,older,p):
    if type(mask) is not int or not 0<=mask<64 or type(older) is not int or not 0<=older<=6:
        raise ValueError('invalid history')
    d=(1-p.memory_weight)*(12-3*COUNTS[mask])+p.memory_weight*(12-3*older)
    return tuple(sigmoid(p.bias+p.beta*d+p.inertia*(2*y-1)) for y in BITS[mask])

def product_law(ps):
    return tuple(prod(p if y else 1-p for p,y in zip(ps,bits)) for bits in BITS)

def next_law(mask,older,p):
    ps=actor_ps(mask,older,p)
    if p.tau==0:return product_law(ps)
    shifts=[p.tau*(2*y-1)*min(a,1-a) for y,a in zip(BITS[mask],ps)]
    a=product_law(tuple(v+s for v,s in zip(ps,shifts)))
    b=product_law(tuple(v-s for v,s in zip(ps,shifts)))
    return tuple((x+y)/2 for x,y in zip(a,b))

def run_exact(p,horizon=40):
    if type(horizon) is not int or not 1<=horizon<=400:raise ValueError('invalid horizon')
    states={(m,COUNTS[m]):1/64 for m in range(64)}
    cache={};series=[]
    for t in range(1,horizon+1):
        nxtstates={};cost=0.;mean_n=0.;n2=0.;turnover=0.;switch=0.
        for (mask,older),weight in states.items():
            key=(mask,older)
            if key not in cache:cache[key]=next_law(mask,older,p)
            for nxt,prob in enumerate(cache[key]):
                mass=weight*prob
                if mass==0:continue
                n=COUNTS[nxt];old=COUNTS[mask]
                cost+=mass*COSTS[n];mean_n+=mass*n;n2+=mass*n*n
                turnover+=mass*abs(n-old)
                switch+=mass*((mask^nxt).bit_count()/6)
                newkey=(nxt,old)
                nxtstates[newkey]=nxtstates.get(newkey,0.)+mass
        if abs(sum(nxtstates.values())-1)>1e-9:raise ArithmeticError('lost probability mass')
        states=nxtstates
        series.append(dict(period=t,expected_cost=cost,mean_n=mean_n,
                           variance_n=n2-mean_n**2,abs_delta_n=turnover,
                           switch_rate=switch))
    return dict(parameters=vars(p),horizon=horizon,
                J=sum(r['expected_cost'] for r in series),
                mean_cost=sum(r['expected_cost'] for r in series)/horizon,
                mean_abs_delta_n=sum(r['abs_delta_n'] for r in series)/horizon,
                mean_switch_rate=sum(r['switch_rate'] for r in series)/horizon,
                series=series)

def mean_field_fixed_point(beta):
    """n*=6*sigma(beta*(12-3*n*)), derivative of n-only reduction.
    NOT the full 448-state process or a rigorous phase-transition claim.
    """
    if not isfinite(beta) or beta<0:raise ValueError('bad beta')
    lo,hi=0.,6.
    for _ in range(80):
        n=(lo+hi)/2
        if 6*sigmoid(beta*(12-3*n))>n:lo=n
        else:hi=n
    n=(lo+hi)/2
    return n,-3*beta*n*(1-n/6)

if __name__=='__main__':
    import argparse,json
    parser=argparse.ArgumentParser()
    parser.add_argument('--beta',type=float,default=.3)
    parser.add_argument('--inertia',type=float,default=0.)
    parser.add_argument('--memory',type=float,default=0.)
    parser.add_argument('--tau',type=float,default=0.)
    args=parser.parse_args()
    z=run_exact(Params(args.beta,args.inertia,args.memory,args.tau))
    print(json.dumps({k:v for k,v in z.items() if k!='series'},indent=2))
