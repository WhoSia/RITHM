"""Stylized 4-eligible A->B revisions followed by one-at-a-time return."""
from fractions import Fraction as F
from math import comb
N_ELIGIBLE_A=4

def stage_excess(k):
    if not isinstance(k,int) or not 0<=k<=N_ELIGIBLE_A:raise ValueError('invalid K')
    return F(3*k*k)

def recovery_excess(k):
    if not isinstance(k,int) or not 0<=k<=N_ELIGIBLE_A:raise ValueError('invalid K')
    return F(k*(k+1)*(2*k+1),2)

def resource_fees(k,fee):
    if F(fee)<0:raise ValueError('nonnegative real resource fee')
    if not isinstance(k,int) or not 0<=k<=N_ELIGIBLE_A:raise ValueError('K')
    return F(2*k)*F(fee)

def expected_law(values,probabilities):
    if len(values)!=len(probabilities) or any(F(p)<0 for p in probabilities) or sum(map(F,probabilities),F(0))!=1:
        raise ValueError('not a probability vector')
    return sum((F(c)*F(p) for c,p in zip(values,probabilities)),F(0))

def factorial_moment(probabilities,d):
    if len(probabilities)!=5 or not 0<=d<=4:raise ValueError('K=0..4 only')
    return expected_law([F(comb(k,d),comb(4,d)) for k in range(5)],probabilities)

def exact_recovery_from_moments(m1,m2,m3):
    return F(12)*F(m1)+F(54)*F(m2)+F(24)*F(m3)
