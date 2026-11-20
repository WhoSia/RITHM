"""Exact six-person route-choice dynamics after withdrawal of guidance."""

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import product

N = 6
TARGET = 4


@dataclass(frozen=True)
class Design:
    burden: tuple
    resource: tuple
    retention: Q
    decay: str = "independent"
    memory_value: Q = Q(2)

    def __post_init__(self):
        if len(self.burden) != N or len(self.resource) != N:
            raise ValueError("six individually labelled actors are required")
        if any(value < 0 for value in (*self.burden, *self.resource, self.memory_value)):
            raise ValueError("costs, burdens and memory value must be nonnegative")
        if not 0 <= self.retention <= 1 or self.decay not in ("independent", "shared"):
            raise ValueError("invalid memory decay")


@dataclass(frozen=True)
class State:
    routes: int
    active: int
    hit_target: bool
    left_target: bool = False


def decay_distribution(active, retention, kind):
    """Resolve a memory shock after the current actor has made their choice."""
    if not active or retention == 1:
        return ((active, Q(1)),)
    if retention == 0:
        return ((0, Q(1)),)
    if kind == "shared":
        return ((active, retention), (0, 1 - retention))
    bits = [1 << i for i in range(N) if active & (1 << i)]
    distribution = []
    for survives in product((False, True), repeat=len(bits)):
        mask = sum(bit for bit, keep in zip(bits, survives) if keep)
        retained = mask.bit_count()
        weight = retention**retained * (1 - retention)**(len(bits) - retained)
        distribution.append((mask, weight))
    return tuple(distribution)


def step(design, state, actor, *, learned_a_value=Q(0)):
    """A selected actor observes the current count and compares staying with moving."""
    bit = 1 << actor
    on_a = bool(state.routes & bit)
    count = state.routes.bit_count()
    # R45/R46 gain evaluated at the post-move count.
    gain = (3 * count - 14) if on_a else (11 - 3 * count)
    if state.active & bit:
        gain += -design.memory_value if on_a else design.memory_value
    gain += -learned_a_value if on_a else learned_a_value
    switched = gain > design.burden[actor]
    routes = state.routes ^ bit if switched else state.routes
    at_target = routes.bit_count() == TARGET
    hit = state.hit_target or at_target
    left = state.left_target or (state.hit_target and not at_target)
    cost = design.resource[actor] if switched else Q(0)
    return routes, hit, left, cost


def evaluate(design, initial_routes, initial_memory, horizon):
    """Integrate over the same exogenous revision and decay clocks in each arm."""
    if horizon < 0 or not all(0 <= mask < (1 << N) for mask in (initial_routes, initial_memory)):
        raise ValueError("nonnegative horizon and six-bit masks required")
    p = {State(initial_routes, initial_memory, initial_routes.bit_count() == TARGET): Q(1)}
    congestion = resource = Q(0)
    rows = []
    decay_cache = {active: decay_distribution(active, design.retention, design.decay)
                   for active in range(1 << N) if active & initial_memory == active}
    for t in range(1, horizon + 1):
        out = defaultdict(Q)
        for state, probability in p.items():
            for actor in range(N):
                routes, hit, left, cost = step(design, state, actor)
                weight = probability / N
                congestion += weight * 3 * (routes.bit_count() - TARGET)**2
                resource += weight * cost
                for active, mass in decay_cache[state.active]:
                    out[State(routes, active, hit, left)] += weight * mass
        p = out
        rows.append({
            "round": t,
            "hit_by": sum(q for s, q in p.items() if s.hit_target),
            "left_by": sum(q for s, q in p.items() if s.left_target),
            "at_target": sum(q for s, q in p.items() if s.routes.bit_count() == TARGET),
            "congestion": congestion,
            "resource": resource,
        })
    return rows


def checkpoint_selection():
    """Random histories, equal potential outcomes, and a biased checkpoint subset."""
    selected = defaultdict(list)
    outcomes = defaultdict(list)
    for history, latent in product((0, 1), repeat=2):
        outcomes[history].append(latent)
        if history == latent:
            selected[history].append(latent)
    mean = lambda values: Q(sum(values), len(values))
    return {
        "every_group_difference": mean(outcomes[1]) - mean(outcomes[0]),
        "natural_checkpoint_difference": mean(selected[1]) - mean(selected[0]),
    }


def benchmarks(horizon=40, retention=Q(3, 4)):
    correction = Design((0, 2, 2, 2, 2, 2), (Q(1, 2), 0, 0, 0, 0, 0), retention)
    exit_ = Design((2, 2, 2, 2, 0, 2), (0, 0, 0, 0, Q(1, 2), 0), retention)
    two = (0, 0, 2, 2, 2, 2), (Q(1, 2), Q(1, 2), 0, 0, 0, 0)
    return {
        "correction_no_memory": evaluate(correction, 0b011111, 0, horizon),
        "correction_memory": evaluate(correction, 0b011111, 1, horizon),
        "exit_no_memory": evaluate(exit_, 0b001111, 0, horizon),
        "exit_memory": evaluate(exit_, 0b001111, 1 << 4, horizon),
        "two_independent": evaluate(Design(*two, retention), 0b011111, 3, horizon),
        "two_shared": evaluate(Design(*two, retention, "shared"), 0b011111, 3, horizon),
    }
