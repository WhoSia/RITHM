"""Actual real switching-cost welfare versus subjective inertia."""
from fractions import Fraction as F


def total_cost(congestion_excess,switch_count,resource_fee):
    if F(switch_count)<0 or F(resource_fee)<0:
        raise ValueError("nonnegative expected counts and real fee")
    return F(congestion_excess)+F(switch_count)*F(resource_fee)


def breakeven(a,b):
    """a=(excess congestion,expected switches), b likewise.

    Returns exact nonnegative real fee at which total costs tie, or None
    if no nonnegative fee makes them tie; raises on identical switching counts
    but differing congestion costs (never intersects).
    """
    ca,ma=map(F,a);cb,mb=map(F,b)
    if ma==mb:
        return F(0) if ca==cb else None
    f=(cb-ca)/(ma-mb)
    return f if f>=0 else None


def rank(a,b,resource_fee):
    x=total_cost(*a,resource_fee);y=total_cost(*b,resource_fee)
    return 'a' if x<y else 'b' if y<x else 'tie'
