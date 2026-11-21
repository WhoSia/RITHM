"""Policy cost interval dominance; observational contrasts are NOT causal."""
from fractions import Fraction as F

def interval_difference(a,b):
    a0,a1=map(F,a);b0,b1=map(F,b)
    if a0>a1 or b0>b1:raise ValueError('invalid interval')
    return a0-b1,a1-b0

def robust_order(a,b):
    lo,hi=interval_difference(a,b)
    if hi<0:return 'A_STRICTLY_LOWER'
    if lo>0:return 'B_STRICTLY_LOWER'
    if lo==hi==0:return 'EQUAL_POINT'
    return 'UNIDENTIFIED'

def add_switch_resource_fee(interval,m1,fee):
    if F(fee)<0 or not 0<=F(m1)<=1:raise ValueError('fee or marginal invalid')
    value=F(8)*F(m1)*F(fee)
    return F(interval[0])+value,F(interval[1])+value
