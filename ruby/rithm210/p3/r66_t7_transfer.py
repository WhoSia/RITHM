"""Exact finite-horizon Markov welfare difference via telescoping kernels."""
from fractions import Fraction as F


def validate(mu,P):
    n=len(mu)
    if n==0 or len(P)!=n or any(len(row)!=n for row in P):
        raise ValueError("matrix/state dimensions mismatch")
    if any(F(p)<0 for p in mu) or sum(map(F,mu),F(0))!=1:
        raise ValueError("initial distribution must be stochastic")
    for row in P:
        if any(F(p)<0 for p in row) or sum(map(F,row),F(0))!=1:
            raise ValueError("every transition row must be stochastic")


def left(v,P):
    return tuple(sum((F(v[i])*F(P[i][j]) for i in range(len(v))),F(0)) for j in range(len(v)))


def right(P,c):
    return tuple(sum((F(a)*F(b) for a,b in zip(row,c)),F(0)) for row in P)


def J(mu,P,c,H):
    validate(mu,P)
    if len(c)!=len(mu) or not isinstance(H,int) or H<1:
        raise ValueError("invalid welfare horizon")
    v=tuple(map(F,mu));result=F(0)
    for _ in range(H):
        result+=sum((a*F(b) for a,b in zip(v,c)),F(0))
        v=left(v,P)
    return result


def telescoping(mu,P,Q,c,H):
    validate(mu,P);validate(mu,Q)
    if H<1 or len(c)!=len(mu):
        raise ValueError("invalid welfare horizon")
    n=len(mu)
    # B_m = sum_{j=0}^m P^j c; inverse suffix Bellman recursion.
    B=[tuple(map(F,c))]
    for _ in range(H-2):
        pc=right(P,B[-1])
        B.append(tuple(F(c[i])+pc[i] for i in range(n)))
    state=tuple(map(F,mu));diff=F(0)
    for k in range(H-1):
        x=right(Q,B[H-2-k]);y=right(P,B[H-2-k])
        diff+=sum((state[i]*(x[i]-y[i]) for i in range(n)),F(0))
        state=left(state,Q)
    assert diff==J(mu,Q,c,H)-J(mu,P,c,H)
    return diff
