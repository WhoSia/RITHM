"""RITHM-2.10 R62: exact rational common-pause covariance/welfare identity.

A *constructed* latent all-stay gate does not imply participant coordination.
Every individual transition marginal is held exactly fixed. No original rows.
"""
from fractions import Fraction as F
from itertools import combinations


def exact_law(probabilities,q):
    p=tuple(map(F,probabilities));q=F(q)
    if len(p)!=6 or any(not 0<x<1 for x in p):raise ValueError('strict six actor marginals')
    if not 0<=q<1-max(p):raise ValueError('inadmissible common pause')
    active=[x/(1-q) for x in p]
    out={}
    for mask in range(64):
        mass=F(1)
        for i,x in enumerate(active):mass*=x if mask&(1<<i) else 1-x
        out[mask]=(1-q)*mass+(q if mask==0 else 0)
    assert sum(out.values())==1
    return out


def exact_expectations(old_routes,law):
    if len(old_routes)!=6 or any(x not in (0,1) for x in old_routes):raise ValueError('six routes')
    old=sum(old_routes)
    values={'p_no_switch':F(0),'gross':F(0),'nA':F(0),'excess':F(0)}
    marg=[F(0)]*6
    for mask,mass in law.items():
        changes=[(mask>>i)&1 for i in range(6)]
        gross=sum(changes);nA=old+sum((1-2*r)*x for r,x in zip(old_routes,changes))
        values['p_no_switch']+=mass*(mask==0)
        values['gross']+=mass*gross
        values['nA']+=mass*nA
        values['excess']+=mass*3*(nA-4)**2
        for i,x in enumerate(changes):marg[i]+=mass*x
    return values,marg


def covariance_identity(old_routes,probabilities,q):
    """EXACT delta expected excess cost relative to independent P(flip)=p_i.

    Sign s_i = +1 when previously B (B->A), -1 when previously A.
    Delta welfare=6 Σ_{i<j}s_i s_j Cov(X_i,X_j),
    Cov under group pause is q p_i p_j/(1-q).
    """
    p=tuple(map(F,probabilities));q=F(q)
    if len(old_routes)!=6 or len(p)!=6 or not 0<=q<1-max(p):raise ValueError('bad inputs')
    sign=[1-2*r for r in old_routes]
    return 6*q/(1-q)*sum((sign[i]*sign[j]*p[i]*p[j] for i,j in combinations(range(6),2)),F(0))


if __name__=='__main__':
    p=[F(1,4)]*6;old=(1,1,1,1,0,0);q=F(1,5)
    independent=exact_expectations(old,exact_law(p,0))
    freeze=exact_expectations(old,exact_law(p,q))
    assert freeze[1]==independent[1]==p
    assert freeze[0]['excess']-independent[0]['excess']==covariance_identity(old,p,q)==F(-3,32)
    print('EXACT noncausal group common-pause identity:',freeze[0]['excess']-independent[0]['excess'])
