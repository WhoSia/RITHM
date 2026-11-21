"""Exact rational, inspectable primal-dual sharp-bounds certificates."""
from fractions import Fraction as F
from r66_t7_distribution import masks, expectation,validate


def certificate(values,n,known,optimum):
    dist=validate(optimum.law,n)
    for s,v in known.items():
        observed=sum((p for x,p in dist.items() if all(x[i] for i in s)),F(0))
        if observed!=F(v):
            return False
    if set(optimum.dual)-set(known):
        return False
    for x in masks(n):
        y=sum((F(v) for s,v in optimum.dual.items() if all(x[i] for i in s)),F(0))
        if optimum.direction=='min' and y>F(values[x]):return False
        if optimum.direction=='max' and y<F(values[x]):return False
    dual_value=sum((F(v)*F(known[s]) for s,v in optimum.dual.items()),F(0))
    primal_value=expectation(dist,n,lambda x:values[x])
    return dual_value==primal_value==optimum.value


def functional_span_bound(values,n,known_order,estimate):
    """Safe coarse certificate if high moments are ignored.

    Given any feasible moment law, the expected value equals the low-order
    contribution plus sum of unknown c_S*m_S. Since each unknown m_S in [0,1],
    an interval is obtained by adding negative/positive coefficients.
    This is generally NOT sharp; use the LP certificate for sharp values.
    """
    from r66_t7_mobius import coefficients
    c=coefficients(values,n)
    lo=F(estimate)+sum((min(0,F(v)) for s,v in c.items() if len(s)>known_order),F(0))
    hi=F(estimate)+sum((max(0,F(v)) for s,v in c.items() if len(s)>known_order),F(0))
    return lo,hi
