"""Unique multilinear representation of welfare on a Boolean action cube."""
from fractions import Fraction
from itertools import combinations
from r66_t7_distribution import masks


def coefficients(values,n):
    """c(S)=sum_{T subset S}(-1)^|S\\T| f(1_T), exactly."""
    all_masks=masks(n)
    if set(values)!=set(all_masks):
        raise ValueError("functional must be specified at every mask")
    coeff={}
    for m in all_masks:
        idx=tuple(i for i,v in enumerate(m) if v)
        c=Fraction(0)
        for k in range(len(idx)+1):
            for subset in combinations(idx,k):
                vector=tuple(int(i in subset) for i in range(n))
                c+=(-1)**(len(idx)-k)*Fraction(values[vector])
        coeff[idx]=c
    return coeff


def evaluate(coeff,x):
    n=len(x)
    return sum((Fraction(c) for s,c in coeff.items() if all(x[i] for i in s)),Fraction(0))


def degree(coeff):
    return max((len(s) for s,c in coeff.items() if c),default=-1)
