"""Exact fraction sharp welfare intervals given bounded average co-switch moments.

The law is over K (4 eligible actors), NOT full labeled co-switch masks.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from math import comb
from r66_t8_fraction_linear import solve_square

@dataclass(frozen=True)
class SharpInterval:
    lower:F
    upper:F
    lower_law:tuple
    upper_law:tuple
    vertex_count:int

def _features():
    return {d:tuple(F(comb(k,d),comb(4,d)) for k in range(5)) for d in range(1,5)}

def _constraints(bounds):
    feats=_features()
    cons=[]
    for d,(lo,hi) in bounds.items():
        if d not in feats:raise ValueError('unsupported order')
        lo,hi=F(lo),F(hi)
        if lo<0 or hi>1 or lo>hi:raise ValueError('invalid moment interval')
        v=feats[d]
        cons.append((v,hi,f'm{d}_upper'))
        cons.append((tuple(-x for x in v),-lo,f'm{d}_lower'))
    for k in range(5):
        cons.append((tuple(F(-int(j==k)) for j in range(5)),F(0),f'q{k}_nonnegative'))
    return cons

def _feasible(q,ineq):
    return all(sum((x*y for x,y in zip(a,q)),F(0))<=b for a,b,_ in ineq)

def sharp_interval(cost,bounds):
    if len(cost)!=5:raise ValueError('K=0..4 outcome vector')
    cost=tuple(F(x) for x in cost)
    cons=_constraints(bounds)
    norm=(F(1),)*5
    found={}
    for active in combinations(cons,4):
        q=solve_square([norm]+[x[0] for x in active],[F(1)]+[x[1] for x in active])
        if q is None or not _feasible(q,cons):continue
        if sum(q,F(0))!=1:raise AssertionError('vertex violated normalization')
        found[q]=sum((x*y for x,y in zip(q,cost)),F(0))
    if not found:raise ValueError('moment region infeasible')
    lo=min(found.values());hi=max(found.values())
    lq=min((q for q,v in found.items() if v==lo))
    hq=min((q for q,v in found.items() if v==hi))
    return SharpInterval(lo,hi,lq,hq,len(found))

def verify_certificate(out,cost,bounds):
    cons=_constraints(bounds)
    assert _feasible(out.lower_law,cons) and _feasible(out.upper_law,cons)
    assert sum(out.lower_law,F(0))==sum(out.upper_law,F(0))==1
    assert sum((F(x)*p for x,p in zip(cost,out.lower_law)),F(0))==out.lower
    assert sum((F(x)*p for x,p in zip(cost,out.upper_law)),F(0))==out.upper
    return True
