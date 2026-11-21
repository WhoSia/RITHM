"""Exact (n-1)-wise independent parity and complementary law witnesses."""
from fractions import Fraction
from r66_t7_distribution import masks,expectation


def law(n, parity):
    if n < 2 or parity not in (0,1):
        raise ValueError("n>=2 and parity 0 or 1")
    return {s: Fraction(1,2**(n-1)) for s in masks(n) if sum(s)%2==parity}


def triple_shift():
    # all marginals and pairwise moments match, yet the triple differs by 1/4.
    zero=law(3,0)
    one=law(3,1)
    return expectation(one,3,lambda s: s[0]*s[1]*s[2])-expectation(zero,3,lambda s:s[0]*s[1]*s[2])
