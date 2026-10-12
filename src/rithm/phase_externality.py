"""P17 exact INTEGER phase-allocation envelopes for a source traffic PROXY.

Assumptions: original per-link 10-minute y0+y1 totals are conserved; mean
sensor speed remains FIXED; pair reassignments are otherwise independent except
for an optional global integer L1 budget. Results are NOT true driver welfare.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Pair:
    y0: int
    y1: int
    speed0: float
    speed1: float

    def __post_init__(self):
        if any(type(x) is not int or x < 0 for x in (self.y0, self.y1)):
            raise ValueError("nonnegative INTEGER source counts required")
        if any(not isinstance(x, (float, int)) or not isfinite(x) or x <= 0
               for x in (self.speed0, self.speed1)):
            raise ValueError("fixed positive finite source speeds required")

    @property
    def source_proxy(self):
        return self.y0/self.speed0 + self.y1/self.speed1


def phase_envelope(pairs, global_budget=None, per_pair_cap=None):
    """Sharp min/max of sum(q0/v0+q1/v1) under source clock & count constraints.

    q0+q1=y0+y1, q0,q1 nonnegative integers; optional global budget
    sum(abs(q0-y0))<=B. Each maximizer may be a different latent allocation.
    O(P log P) time / O(P) memory. Source v0,v1 are HELD FIXED by assumption.
    Unit: vehicle-hours/km when passage counts and km/h are source variables.
    """
    pairs = list(pairs)
    if global_budget is not None and (type(global_budget) is not int or global_budget < 0):
        raise ValueError("global budget must be nonnegative integer")
    if per_pair_cap is not None and (type(per_pair_cap) is not int or per_pair_cap < 0):
        raise ValueError("per-pair bound must be nonnegative integer")
    baseline = 0.
    inc, dec = [], []
    for p in pairs:
        if not isinstance(p, Pair):
            raise ValueError("Pair source type required")
        baseline += p.source_proxy
        slope = 1/p.speed0 - 1/p.speed1
        upcap = p.y1 if per_pair_cap is None else min(p.y1, per_pair_cap)
        downcap = p.y0 if per_pair_cap is None else min(p.y0, per_pair_cap)
        if slope >= 0:
            inc.append((slope, upcap))
            dec.append((slope, downcap))
        else:
            inc.append((-slope, downcap))
            dec.append((-slope, upcap))
    def greedy(envelope_moves):
        gain = 0.
        remaining = global_budget
        moved = 0
        for coefficient, cap in sorted(envelope_moves, reverse=True):
            if coefficient <= 0 or cap <= 0:
                continue
            take = cap if remaining is None else min(cap, remaining)
            if take == 0:
                break
            gain += coefficient*take
            moved += take
            if remaining is not None:
                remaining -= take
        return gain, moved
    hi, hi_moves = greedy(inc)
    lo, lo_moves = greedy(dec)
    return dict(pairs=len(pairs), source_proxy=baseline,
                min_proxy=baseline-lo, max_proxy=baseline+hi,
                min_required_moves=lo_moves, max_required_moves=hi_moves,
                global_budget=global_budget, per_pair_cap=per_pair_cap,
                conditional_only=True, speeds_held_fixed=True,
                not_actual_human_welfare=True)


def balanced_reallocation_proxy(pairs):
    """Closest per-pair near-flat INTEGER hypothetical latent flow witness."""
    before = after = 0.
    moved = 0
    for p in pairs:
        if not isinstance(p, Pair):
            raise ValueError("Pair source type required")
        total = p.y0+p.y1
        q0 = min((total//2, (total+1)//2), key=lambda x: abs(x-p.y0))
        moved += abs(q0-p.y0)
        before += p.source_proxy
        after += q0/p.speed0+(total-q0)/p.speed1
    return dict(source_proxy=before, nearflat_proxy=after,
                minimum_nearflat_integer_reassignments=moved,
                hypothetical_latent_nearflat_only=True)
