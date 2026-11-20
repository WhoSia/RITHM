"""R56: two distinct latent explanations induce identical labelled swap law.

A constructive nonidentification witness, NOT a fitted human mechanism.
"""
from collections import defaultdict
from fractions import Fraction


def check(mask):
    if type(mask) is not int or not 0 <= mask < 64:
        raise ValueError('invalid labelled six-seat mask')
    return mask


def coordinated_pair_swap(mask):
    """Joint planner chooses one A seat and one B seat to swap."""
    check(mask)
    on_A=[i for i in range(6) if mask & (1<<i)]
    on_B=[i for i in range(6) if not mask & (1<<i)]
    pairs=[(i,j) for i in on_A for j in on_B]
    if not pairs:
        return {mask:Fraction(1)}
    return {mask ^ (1<<i) ^ (1<<j):Fraction(1,len(pairs))
            for i,j in pairs}


def latent_common_instruction(mask):
    """Unobserved H chooses the pair; actors move independently given H.

    Conditional on H=(i,j), every actor has a degenerate, independent
    Bernoulli toggle rule 1{actor in H}; the mixture is dependent marginally.
    """
    check(mask)
    on_A=[i for i in range(6) if mask & (1<<i)]
    on_B=[i for i in range(6) if not mask & (1<<i)]
    signals=[(i,j) for i in on_A for j in on_B]
    if not signals:
        return {mask:Fraction(1)}
    law=defaultdict(Fraction)
    for hidden in signals:
        next_mask=mask
        for actor in range(6):
            if actor in hidden:
                next_mask ^= (1<<actor)
        law[next_mask]+=Fraction(1,len(signals))
    return dict(law)
