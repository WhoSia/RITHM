"""Exact finite-spell observational equivalence: selection vs tenure-dependent hazard.

Model A: at *each new spell* an unobserved risk type is sampled; switching is
constant-probability Bernoulli within the spell conditional on that type.
Model B: no latent type, only a deterministic duration-dependent hazard.
Both have EXACTLY the same joint law of binary route-switch sequences.  This
does NOT imply globally permanent individual type heterogeneity is equivalent.
"""
from fractions import Fraction as F
from itertools import product

RISKS=(F(1,20),F(1,2))
WEIGHTS=(F(1,2),F(1,2))


def survival(k):
    if type(k) is not int or k<0:
        raise ValueError('nonnegative completed stay count required')
    return sum(w*(1-p)**k for w,p in zip(WEIGHTS,RISKS))


def duration_hazard(tenure):
    if type(tenure) is not int or tenure<1:
        raise ValueError('positive observed duration')
    return 1-survival(tenure)/survival(tenure-1)


def mixed_spell_probability(flips):
    """Use type-mixture survival for complete runs, and prior for each new run."""
    stays=0
    likelihood=F(1)
    for flip in flips:
        if flip not in (0,1):raise ValueError('binary only')
        if flip:
            likelihood*=survival(stays)-survival(stays+1)
            stays=0
        else:
            stays+=1
    return likelihood*survival(stays)


def duration_spell_probability(flips):
    tenure=1
    likelihood=F(1)
    for flip in flips:
        if flip not in (0,1):raise ValueError('binary only')
        h=duration_hazard(tenure)
        likelihood*=h if flip else 1-h
        tenure=1 if flip else tenure+1
    return likelihood


def exact_check(horizon=9):
    if not 0<=horizon<=12:raise ValueError('restrict exhaustive proof to <=12 choices')
    total=F(0)
    for flips in product((0,1),repeat=horizon):
        a=mixed_spell_probability(flips)
        b=duration_spell_probability(flips)
        if a!=b:raise AssertionError((flips,a,b))
        total+=a
    if total!=1:raise AssertionError('non-normalized spell law')
    return {'horizon':horizon,'cases':2**horizon,'equal':True,
            'hazards':{str(k):str(duration_hazard(k)) for k in (1,2,3,5,10)}}


if __name__=='__main__':
    import json
    print(json.dumps(exact_check(),indent=2))
