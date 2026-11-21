"""Aggregate-only moment hull contract; never imports private actor trajectories."""
from fractions import Fraction as F
from math import comb
from r66_t8_moment_polytope import sharp_interval
from r66_t8_welfare import recovery_excess

def point_identification_from_histogram(hist):
    if set(hist)!=set(range(5)) or any(not isinstance(v,int) or v<0 for v in hist.values()):
        raise ValueError('only five public aggregate K-counts permitted')
    n=sum(hist.values())
    if n<1:raise ValueError('empty risk set')
    m1=F(sum(k*v for k,v in hist.items()),4*n)
    m2=F(sum(comb(k,2)*v for k,v in hist.items()),6*n)
    m3=F(sum(comb(k,3)*v for k,v in hist.items()),4*n)
    fx=[recovery_excess(k) for k in range(5)]
    point=F(sum(v*fx[k] for k,v in hist.items()),n)
    sharp=sharp_interval(fx,{1:(m1,m1),2:(m2,m2)})
    if not sharp.lower<=point<=sharp.upper:raise AssertionError('out of hull')
    return {'n':n,'m1':m1,'m2':m2,'m3':m3,'observed':point,
            'sharp_lower':sharp.lower,'sharp_upper':sharp.upper}
