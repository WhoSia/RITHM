"""Raw all-one joint moments, exact inversion by inclusion-exclusion."""
from fractions import Fraction
from itertools import combinations
from r66_t7_distribution import validate, masks


def subsets(n, order):
    if not 0 <= order <= n:
        raise ValueError("moment order out of range")
    return [s for d in range(order + 1) for s in combinations(range(n),d)]


def moments(law, n, order):
    d=validate(law,n)
    return {subset:sum((p for x,p in d.items() if all(x[i] for i in subset)),Fraction(0))
            for subset in subsets(n,order)}


def invert_all_moments(m, n):
    """Recover unique binary distribution when ALL 2^n moments are known."""
    all_keys=set(subsets(n,n))
    if set(m)!=all_keys or m[()]!=1:
        raise ValueError("need a complete normalized moment tensor")
    result={}
    for x in masks(n):
        ones=tuple(i for i,v in enumerate(x) if v)
        zeros=tuple(i for i,v in enumerate(x) if not v)
        result[x]=sum(((-1)**len(S)*Fraction(m[tuple(sorted(ones+S))])
                       for k in range(len(zeros)+1) for S in combinations(zeros,k)),Fraction(0))
    return validate(result,n)
