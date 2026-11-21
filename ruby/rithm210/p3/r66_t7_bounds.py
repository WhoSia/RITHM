"""Sharp nonparametric welfare identification interval from binary action moments.

Scipy/HiGHS is an optimization oracle. Candidate rational primal and dual
solutions MUST pass exact reconstruction/certificate checks before reporting
as mathematically sharp. No human experiment inference is implied.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from scipy.optimize import linprog
from r66_t7_distribution import masks,validate,expectation

@dataclass(frozen=True)
class ExactOptimum:
    value: F
    law: dict
    dual: dict
    direction: str


def _spec(n,known):
    subsets=sorted(known,key=lambda k:(len(k),k))
    if () not in known or F(known[()])!=1:
        raise ValueError("normalization moment is required")
    if any(not isinstance(k,tuple) or k!=tuple(sorted(set(k))) or any(i<0 or i>=n for i in k) for k in known):
        raise ValueError("invalid moment index")
    return subsets


def _solve(values,n,known,direction):
    states=masks(n)
    if set(values)!=set(states):
        raise ValueError("complete welfare function required")
    subsets=_spec(n,known)
    A=[[int(all(x[i] for i in subset)) for x in states] for subset in subsets]
    b=[float(known[s]) for s in subsets]
    sign=1 if direction=='min' else -1
    obj=[sign*float(values[s]) for s in states]
    r=linprog(obj,A_eq=A,b_eq=b,bounds=(0,None),method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    if not r.success:
        raise ValueError("moment constraints infeasible: "+r.message)
    # Rational reconstruction: exact feasibility and primal-dual value are checked.
    law=validate({s:F(float(p)).limit_denominator(1000000) for s,p in zip(states,r.x) if p>1e-10},n)
    for s in subsets:
        observed=sum((p for x,p in law.items() if all(x[i] for i in s)),F(0))
        if observed!=F(known[s]):
            raise ArithmeticError("LP rationalization violated exact input moment")
    dual={s: F(float(v)).limit_denominator(1000000)*sign for s,v in zip(subsets,r.eqlin.marginals)}
    value=expectation(law,n,lambda x:values[x])
    for x in states:
        envelope=sum((v for s,v in dual.items() if all(x[i] for i in s)),F(0))
        if (direction=='min' and envelope>F(values[x])) or (direction=='max' and envelope<F(values[x])):
            raise ArithmeticError("infeasible rational dual certificate")
    matching=sum((dual[s]*F(known[s]) for s in subsets),F(0))
    if matching!=value:
        raise ArithmeticError("exact primal/dual objective mismatch")
    return ExactOptimum(value,law,dual,direction)


def sharp_interval(values,n,known):
    return _solve(values,n,known,'min'),_solve(values,n,known,'max')
