"""Mathematically exact minimal joint-moment order for a fixed welfare functional."""
from fractions import Fraction
from r66_t7_mobius import coefficients, degree
from r66_t7_moments import moments
from r66_t7_distribution import validate


def required_order(values,n):
    return max(0,degree(coefficients(values,n)))


def from_moments(values,n,moment_map,known_order):
    c=coefficients(values,n)
    if any(v and len(s)>known_order for s,v in c.items()):
        raise ValueError("unknown higher moments affect welfare")
    return sum((v*moment_map[s] for s,v in c.items() if v),Fraction(0))


def upper_order_contributions(values,n,law_a,law_b,known_order):
    c=coefficients(values,n)
    a=moments(validate(law_a,n),n,n)
    b=moments(validate(law_b,n),n,n)
    if any(a[s]!=b[s] for s in a if len(s)<=known_order):
        raise ValueError("two laws do not match the stated low moments")
    return {s:v*(b[s]-a[s]) for s,v in c.items() if len(s)>known_order and v}
