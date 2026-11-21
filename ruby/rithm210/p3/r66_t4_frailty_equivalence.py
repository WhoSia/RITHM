"""RITHM-2.10 P3-R66-T4 exact duration/frailty source-free witness.

A latent mixture of fixed exit hazards has the SAME single-spell exit-time
distribution as a homogeneous population with a suitably varying hazard.
Not an independently novel probability theorem; not a causal human explanation.
"""
from fractions import Fraction as F


def survival(types, k):
    if k < 0 or int(k) != k:
        raise ValueError("age")
    if not types or sum((w for w,h in types),F(0)) != 1 or any(
        w < 0 or not 0 <= h <= 1 for w,h in types
    ):
        raise ValueError("frailty mixture probabilities")
    return sum((w*(1-h)**k for w,h in types), F(0))


def hazard(types, k):
    s = survival(types,k)
    if not s:
        return None
    return sum((w*h*(1-h)**k for w,h in types),F(0))/s


def exact_gap(types, k):
    """Hazard(k)-Hazard(k+1)=Var(h | survived k)/(1-H(k))."""
    h=hazard(types,k)
    if h is None or h==1:
        return None
    var=sum((w*(1-rate)**k*(rate-h)**2 for w,rate in types),F(0))/survival(types,k)
    left=h-hazard(types,k+1)
    assert left==var/(1-h)
    return left


def equivalent_evolving_population(types, horizon):
    """Reproduce fixed-frailty survival and exit masses without frailty."""
    if not isinstance(horizon,int) or horizon < 1:
        raise ValueError("horizon")
    s=F(1)
    rows=[]
    for k in range(horizon):
        h=hazard(types,k)
        if h is None:
            break
        assert s==survival(types,k)
        exit_mass=s*h
        assert exit_mass==survival(types,k)-survival(types,k+1)
        rows.append((s,h,exit_mass))
        s*=1-h
    return rows


def main():
    import json
    types=((F(1,2),F(1,10)),(F(1,2),F(3,5)))
    rows=equivalent_evolving_population(types,30)
    assert rows[0][1]==F(7,20)
    assert rows[1][1]==F(33,130)
    assert all(exact_gap(types,k)>0 for k in range(29))
    print(json.dumps({"fixed_type_exit_hazards":["1/10","3/5"],
        "single_population_evolving_hazards":[str(x[1]) for x in rows[:6]],
        "exact_30_period_survival_match":True,
        "interpretation":"single-spell hazard aging alone cannot identify latent heterogeneity versus changing revision hazard"},indent=2))


if __name__=="__main__":
    main()
