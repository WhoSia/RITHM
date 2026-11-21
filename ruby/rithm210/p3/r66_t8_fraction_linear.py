"""Exact Gauss-Jordan solution of small square rational systems; no NumPy."""
from fractions import Fraction as F

def solve_square(a,b):
    n=len(a)
    if n<1 or len(b)!=n or any(len(row)!=n for row in a):
        raise ValueError('square linear system expected')
    m=[[F(x) for x in row]+[F(y)] for row,y in zip(a,b)]
    for j in range(n):
        pivot=next((k for k in range(j,n) if m[k][j]!=0),None)
        if pivot is None:return None
        m[j],m[pivot]=m[pivot],m[j]
        scale=m[j][j]
        m[j]=[v/scale for v in m[j]]
        for k in range(n):
            if k==j:continue
            coef=m[k][j]
            if coef:m[k]=[u-coef*v for u,v in zip(m[k],m[j])]
    return tuple(row[-1] for row in m)
