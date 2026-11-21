"""Exact sharp triple-coincident-event Frechet interval from pairwise joint moments."""
from fractions import Fraction


def triple_interval(p1,p2,p3,p12,p13,p23):
    p1,p2,p3,p12,p13,p23=map(Fraction,(p1,p2,p3,p12,p13,p23))
    lo=max(Fraction(0),p12+p13-p1,p12+p23-p2,p13+p23-p3)
    hi=min(p12,p13,p23,1-p1-p2-p3+p12+p13+p23)
    if lo>hi or any(not 0<=p<=1 for p in (p1,p2,p3)):
        raise ValueError("infeasible 1st and 2nd binary joint moments")
    return lo,hi


def law_from_triple(p1,p2,p3,p12,p13,p23,t):
    p1,p2,p3,p12,p13,p23,t=map(Fraction,(p1,p2,p3,p12,p13,p23,t))
    lo,hi=triple_interval(p1,p2,p3,p12,p13,p23)
    if not lo<=t<=hi:
        raise ValueError("infeasible triple mass")
    d={
        (1,1,1):t,
        (1,1,0):p12-t,
        (1,0,1):p13-t,
        (0,1,1):p23-t,
        (1,0,0):p1-p12-p13+t,
        (0,1,0):p2-p12-p23+t,
        (0,0,1):p3-p13-p23+t,
        (0,0,0):1-p1-p2-p3+p12+p13+p23-t,
    }
    from r66_t7_distribution import validate
    return validate(d,3)
