"""R66-T3: exact frailty-selection rival for apparent configuration-age stability.

This is a classical duration-selection arithmetic identity, NOT a new theorem.
Each latent type j has a constant configuration-exit hazard h_j each round.
Survivors are progressively enriched for low-hazard types, so the observed
mixture hazard can decrease WITH NO individual's hazard changing.
"""
from fractions import Fraction as F


def posterior_after_survival(types,k):
    """types: sequence of (prior weight, constant exit hazard). k>=1 is age
    of the existing configuration, after surviving k-1 transitions."""
    if not isinstance(k,int) or k<1:raise ValueError('age must be positive integer')
    if not types or any(w<0 or not 0<=h<1 for w,h in types):
        raise ValueError('finite nonnegative mixture with hazard <1 required')
    if sum((w for w,h in types),F(0))!=F(1):
        raise ValueError('type weights sum to one')
    numerator=[F(w)*(1-F(h))**(k-1) for w,h in types]
    z=sum(numerator)
    if z<=0:raise ValueError('zero survivors')
    return [w/z for w in numerator]


def hazard_at_age(types,k):
    posterior=posterior_after_survival(types,k)
    return sum((post*F(h) for post,(_,h) in zip(posterior,types)),F(0))


def decline_identity(types,k):
    probs=posterior_after_survival(types,k)
    mean=hazard_at_age(types,k)
    variance=sum((p*(F(h)-mean)**2 for p,(_,h) in zip(probs,types)),F(0))
    old,new=mean,hazard_at_age(types,k+1)
    if new-old != -variance/(1-mean):
        raise AssertionError('frailty survivor-tilt identity')
    return {'age':k,'exit_hazard':old,'next_exit_hazard':new,
            'decline':old-new,'posterior_variance':variance,
            'exact_identity':True}


def demo():
    types=((F(1,2),F(1,10)),(F(1,2),F(3,5)))
    result={str(k):str(hazard_at_age(types,k)) for k in (1,2,3,5,10)}
    return {'latent_types_constant_exit_hazards':('1/10','3/5'),
            'equal_initial_prior':True,
            'observed_hazard_by_age':result,
            'research_boundary':'pure synthetic heterogeneous-survivor mechanism; not fitted to original human data'}

if __name__=='__main__':
    import json
    print(json.dumps(demo(),indent=2))