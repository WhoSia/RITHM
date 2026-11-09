"""R27: exact six-actor occupancy-fiber nonidentification witness.

Synthetic mathematical counterexample, not an empirical estimate or
an identified behavioral/strategic mechanism. Standard library only.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import product
from math import log
from typing import Dict, Tuple

State = Tuple[int, ...]
Law = Dict[State, Fraction]
STATES: Tuple[State, ...] = tuple(product((0, 1), repeat=6))


def _state(actors: tuple[int, ...]) -> State:
    return tuple(int(i in actors) for i in range(1, 7))


def construct_witness() -> tuple[Law, Law]:
    """A four-cell 2x2 switch preserving marginals and occupancy."""
    uniform = {s: Fraction(1, 64) for s in STATES}
    altered = dict(uniform)
    epsilon = Fraction(1, 128)
    for actors, sign in (((1, 2), 1), ((3, 4), 1),
                         ((1, 3), -1), ((2, 4), -1)):
        altered[_state(actors)] += sign*epsilon
    return uniform, altered


def check_law(law: Law) -> None:
    if set(law) != set(STATES) or any(not isinstance(v, Fraction) or v < 0 for v in law.values()):
        raise ValueError('law must be nonnegative Fraction on all 64 states')
    if sum(law.values()) != 1:
        raise ValueError('law not normalized')


def marginals(law: Law) -> tuple[Fraction, ...]:
    check_law(law)
    return tuple(sum(prob for s, prob in law.items() if s[i]) for i in range(6))


def occupancy(law: Law) -> tuple[Fraction, ...]:
    check_law(law)
    return tuple(sum(prob for s, prob in law.items() if sum(s) == k) for k in range(7))


def pair_probability(law: Law, i: int, j: int) -> Fraction:
    if not 0 <= i < j < 6:
        raise ValueError('need two distinct zero-indexed actor labels')
    check_law(law)
    return sum(prob for s, prob in law.items() if s[i] and s[j])


def expected_cost(law: Law) -> Fraction:
    return sum(prob * (24 + 3*(sum(s) - 4)**2) for s, prob in law.items())


def kl_divergence(true_law: Law, forecast_law: Law) -> float:
    check_law(true_law)
    check_law(forecast_law)
    if any(true_law[s] > 0 and forecast_law[s] == 0 for s in STATES):
        return float('inf')
    return sum(float(p)*log(float(p/q)) for s, p in true_law.items() if p > 0
               for q in (forecast_law[s],))


def audit() -> dict:
    p, q = construct_witness()
    return {
        'marginal_parity': marginals(p) == marginals(q),
        'occupancy_parity': occupancy(p) == occupancy(q),
        'cost_P': str(expected_cost(p)),
        'cost_Q': str(expected_cost(q)),
        'pair12_P': str(pair_probability(p, 0, 1)),
        'pair12_Q': str(pair_probability(q, 0, 1)),
        'changed_states': sum(p[s] != q[s] for s in STATES),
        'joint_kl_Q_vs_P_nats': kl_divergence(q, p),
        'occupancy_kl_Q_vs_P_nats': sum(float(a)*log(float(a/b)) for a,b in zip(occupancy(q),occupancy(p)) if a),
    }


if __name__ == '__main__':
    import json
    print(json.dumps(audit(), sort_keys=True, indent=2))
