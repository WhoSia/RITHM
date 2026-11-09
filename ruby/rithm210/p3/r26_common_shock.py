"""R26: two-point marginal-preserving latent group innovations.

The new joint law is 1/2 product_i Bern(p_i + tau*s_i*m_i)
                     + 1/2 product_i Bern(p_i - tau*s_i*m_i),
where m_i=min(p_i,1-p_i). This is a mathematical competitor, NOT
identified strategic coordination. Under tau=0 it equals independence.
"""
from __future__ import annotations
import math
from dataclasses import dataclass

TAUS=(0.0,0.15,0.30,0.45,0.60,0.80,1.0)
FAMILIES=('common','previous_route_signed')


def convolve(ps):
    dist=[1.0]
    for p in ps:
        out=[0.0]*(len(dist)+1)
        for i,old in enumerate(dist):
            out[i]+=old*(1-p)
            out[i+1]+=old*p
        dist=out
    return dist


def validate(ps, ys=None, previous=None):
    if len(ps)!=6 or any(not isinstance(p,(int,float)) or not math.isfinite(p) or not 0<=p<=1 for p in ps):
        raise ValueError('exactly six valid marginal probabilities required')
    if ys is not None and (len(ys)!=6 or any(type(y) is not int or y not in (0,1) for y in ys)):
        raise ValueError('six binary outcomes required')
    if previous is not None and (len(previous)!=6 or any(type(p) is not int or p not in (-1,0,1) for p in previous)):
        raise ValueError('six preceding routes required (-1 signifies no history)')


def conditional_ps(ps,tau,family,previous=None):
    validate(ps,previous=previous)
    if family not in FAMILIES:raise ValueError('unknown shock loading family')
    if not isinstance(tau,(int,float)) or not math.isfinite(tau) or not 0<=tau<=1:
        raise ValueError('tau outside 0..1')
    if family=='previous_route_signed' and previous is None:raise ValueError('missing previous routes')
    direction=([1]*6 if family=='common' else
               [0 if x==-1 else (1 if x==1 else -1) for x in previous])
    shift=[tau*s*min(p,1-p) for s,p in zip(direction,ps)]
    return [p+d for p,d in zip(ps,shift)], [p-d for p,d in zip(ps,shift)]


@dataclass(frozen=True)
class Forecast:
    p:tuple
    plus:tuple
    minus:tuple
    occupancy:tuple
    tau:float
    family:str
    def marginal(self):return [(a+b)/2 for a,b in zip(self.plus,self.minus)]
    def expectation_cost(self):
        return sum(d*(24+3*(n-4)**2) for n,d in enumerate(self.occupancy))
    def covariance_sum(self):
        return sum((a-p)*(b-q) for i,(a,p) in enumerate(zip(self.plus,self.p))
                   for b,q in zip(self.plus[i+1:],self.p[i+1:]))
    def evaluate(self,ys):
        validate(self.p,ys=ys)
        n=sum(ys)
        mass=max(self.occupancy[n],1e-300)
        joint=0.0
        for weight,ps in ((0.5,self.plus),(0.5,self.minus)):
            likelihood=weight
            for y,p in zip(ys,ps):likelihood*=p if y else (1-p)
            joint+=likelihood
        observed=24+3*(n-4)**2
        errors=[d-(1 if i==n else 0) for i,d in enumerate(self.occupancy)]
        return {'logloss':-math.log(mass),
                'joint_logloss':-math.log(max(joint,1e-300)),
                'brier':sum(e*e for e in errors),
                'cost_mae':abs(self.expectation_cost()-observed),
                'cost_bias':self.expectation_cost()-observed,
                'actor_brier':sum((y-p)**2 for y,p in zip(ys,self.p))/6}


def forecast(ps,tau=0.0,family='common',previous=None):
    plus,minus=conditional_ps(ps,tau,family,previous)
    a=convolve(plus);b=convolve(minus)
    dist=tuple((x+y)*0.5 for x,y in zip(a,b))
    if abs(sum(dist)-1.0)>1e-10:raise ArithmeticError('probability normalization')
    return Forecast(tuple(ps),tuple(plus),tuple(minus),dist,tau,family)


def candidates():
    return tuple([('common',0.0)]+[(f,t) for f in FAMILIES for t in TAUS if t>0])
