"""Exact paid-feedback experiment on R47's six-person revision clock."""

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction as Q

from r47.r47_withdrawal import N, TARGET, Design, State, decay_distribution, step


@dataclass(frozen=True)
class Pulse:
    """A signed adjustment to the focal actor's earned reward after a route is used."""
    round: int = 2
    adjustment: Q = Q(0)
    route_credit: Q = Q(1)
    rate: Q = Q(1, 2)
    retention: Q = Q(3, 4)

    def __post_init__(self):
        if not isinstance(self.round, int) or self.round < 1:
            raise ValueError("pulse round must be positive")
        if not all(0 <= p <= 1 for p in (self.route_credit, self.rate, self.retention)):
            raise ValueError("invalid learning or credit parameter")

    def update(self, difference, t, used_a):
        difference *= self.retention
        if t != self.round:
            return difference
        # Public congestion-only reward is the forecast baseline. The observed
        # reward minus that baseline is the signed randomized adjustment.
        surprise = self.adjustment if used_a else -self.adjustment
        return difference + self.rate * self.route_credit * surprise


def run(design, routes, memory, focal, pulse, horizon=40):
    """Carry labelled routes, inherited memory, learned value and first response."""
    if not isinstance(horizon, int) or horizon < 0 or not 0 <= focal < N:
        raise ValueError("invalid horizon or focal actor")
    if not all(0 <= mask < 1 << N for mask in (routes, memory)):
        raise ValueError("six-bit masks required")
    mask = 1 << focal
    start = State(routes, memory, routes.bit_count() == TARGET)
    states = {(start, Q(0), None): Q(1)}
    decay = {m: decay_distribution(m, design.retention, design.decay)
             for m in range(1 << N) if m & memory == m}
    congestion = resource = Q(0)
    rows = []
    for t in range(1, horizon + 1):
        out = defaultdict(Q)
        for (state, value, first), probability in states.items():
            for actor in range(N):
                extra = value if actor == focal else Q(0)
                next_routes, hit, left, cost = step(design, state, actor, learned_a_value=extra)
                response = first
                if first is None and actor == focal and t > pulse.round:
                    response = next_routes != state.routes
                next_value = pulse.update(value, t, bool(next_routes & mask))
                weight = probability / N
                congestion += weight * 3 * (next_routes.bit_count() - TARGET)**2
                resource += weight * cost
                for active, p in decay[state.active]:
                    next_state = State(next_routes, active, hit, left)
                    out[(next_state, next_value, response)] += weight * p
        states = out
        opportunity = sum(p for (_, _, first), p in states.items() if first is not None)
        switched = sum(p for (_, _, first), p in states.items() if first is True)
        rows.append({
            "round": t,
            "hit_by": sum(p for (s, _, _), p in states.items() if s.hit_target),
            "left_by": sum(p for (s, _, _), p in states.items() if s.left_target),
            "at_target": sum(p for (s, _, _), p in states.items() if s.routes.bit_count() == TARGET),
            "congestion": congestion,
            "resource": resource,
            "revised_after_pulse": opportunity,
            "switched_at_first_revision_by_round": switched,
            "switch_given_first_revision": switched / opportunity if opportunity else None,
        })
    return rows


def scenario(start, decay="independent", two=False):
    """Matched focal-only or two-eligible-actor scenarios inherited from R47."""
    if start not in (4, 5):
        raise ValueError("expected 4:2 or 5:1")
    focal = 0 if start == 5 else 4
    eligible = (focal, focal + 1) if two else (focal,)
    burden = tuple(0 if i in eligible else 2 for i in range(N))
    resource = tuple(Q(1, 2) if i in eligible else Q(0) for i in range(N))
    return Design(burden, resource, Q(3, 4), decay), (1 << start) - 1, sum(1 << i for i in eligible), focal
