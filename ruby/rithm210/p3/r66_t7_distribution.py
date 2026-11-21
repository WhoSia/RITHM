"""Exact source-free probability laws on binary revision masks."""
from fractions import Fraction
from itertools import product


def masks(n):
    if not isinstance(n, int) or n < 1 or n > 12:
        raise ValueError("number of actors must be 1..12")
    return list(product((0, 1), repeat=n))


def validate(law, n):
    """Return a *complete* normalized Fraction law, raising on invalid input."""
    states = masks(n)
    if not isinstance(law, dict):
        raise TypeError("a revision law is a dict of masks to probabilities")
    if any(key not in states for key in law):
        raise ValueError("mask not in binary cube")
    values = {s: Fraction(law.get(s, 0)) for s in states}
    if any(p < 0 for p in values.values()) or sum(values.values(), Fraction(0)) != 1:
        raise ValueError("probability law must be nonnegative and sum to one")
    return values


def point_mass(mask):
    if not mask or any(x not in (0,1) for x in mask):
        raise ValueError("bad binary mask")
    return {tuple(mask): Fraction(1)}


def expectation(law, n, functional):
    return sum((p * Fraction(functional(s)) for s, p in validate(law, n).items()), Fraction(0))
