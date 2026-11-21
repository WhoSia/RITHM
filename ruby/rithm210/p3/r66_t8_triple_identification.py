"""Minimum third-order statistic for degree-three hypothetical recovery welfare."""
from fractions import Fraction as F
from math import comb
from r66_t8_moment_polytope import sharp_interval
from r66_t8_welfare import recovery_excess,exact_recovery_from_moments

def triple_range_from_marginal_pair(m1,m2):
    known={1:(F(m1),F(m1)),2:(F(m2),F(m2))}
    triple=[F(comb(k,3),4) for k in range(5)]
    a=sharp_interval(triple,known)
    cost=sharp_interval([recovery_excess(k) for k in range(5)],known)
    lo=exact_recovery_from_moments(m1,m2,a.lower)
    hi=exact_recovery_from_moments(m1,m2,a.upper)
    if (lo,hi)!=(cost.lower,cost.upper):raise AssertionError('degree-3 sufficiency failed')
    return {'triple_lower':a.lower,'triple_upper':a.upper,
            'welfare_lower':lo,'welfare_upper':hi,'width_exact':hi-lo}
