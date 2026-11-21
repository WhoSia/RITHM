"""Source-free stylized deterministic single-switch-per-step congestion recovery."""
from fractions import Fraction
from r66_t7_distribution import masks,expectation


def one_step_excess(k):
    if not isinstance(k,int) or k < 0:
        raise ValueError("nonnegative integer K")
    return 3*k*k


def full_recovery(k):
    """3*sum_{j=1..k} j² = k(k+1)(2k+1)/2, a degree-3 cost."""
    one_step_excess(k)
    return Fraction(k*(k+1)*(2*k+1),2)


def truncated_recovery(k,horizon):
    if not isinstance(horizon,int) or horizon<1:
        raise ValueError("positive horizon")
    one_step_excess(k)
    return sum((one_step_excess(max(k-t,0)) for t in range(horizon)),0)


def values(n,horizon=None):
    if horizon is None:
        return {s:full_recovery(sum(s)) for s in masks(n)}
    return {s:truncated_recovery(sum(s),horizon) for s in masks(n)}


def expected(law,n,horizon=None):
    vals=values(n,horizon)
    return expectation(law,n,lambda s:vals[s])
