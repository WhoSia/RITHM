"""Synthetic two-period welfare separation from an occupancy-fiber pair.

Given identical N1 laws P,Q, at period 2 define an illustrative transition
using the LABELLED historical event (actors 1 and 2 both chose A):
Y2=(1,1,1,1,1,1) if true, else Y2=(1,1,1,1,0,0).
This is not an empirically fitted transportation-policy mechanism.
"""
from __future__ import annotations
from fractions import Fraction
from r27_occupancy_fiber import construct_witness, expected_cost, pair_probability


def two_period_welfare(law):
    first = expected_cost(law)
    pair = pair_probability(law, 0, 1)
    c6 = 24 + 3*(6-4)**2
    c4 = 24 + 3*(4-4)**2
    second = pair*c6+(1-pair)*c4
    return first, second, first+second


def witness():
    p,q=construct_witness()
    a=two_period_welfare(p)
    b=two_period_welfare(q)
    return a,b,tuple(v-u for u,v in zip(a,b))


if __name__=='__main__':
    print(witness())
