"""R53 supplement: exact discrete support, not merely sharp min/max bounds.

This potentially expensive routine is intended for tiny operator-side examples.
It rejects oversized support sets instead of silently approximating them.
"""
from functools import lru_cache
from fractions import Fraction

from r49_audit import audit_trace
from r49_model import from_events
from r51_registry import check_registry
from r53_policy_order import METRICS, compare_registry


def group_cost_support(events, *, metric="excess", max_values=50000):
    if metric not in METRICS:
        raise ValueError("unknown welfare metric")
    audit_trace(events, allow_prefix=True)
    cfg, routes = from_events(events)
    done = [e for e in events if e["type"] == "choice_committed"]
    previous_excess = sum(3 * (e["after_A"] - 4)**2 for e in done)
    previous_focal = sum(e["seat"] == cfg["focal"] and e["route"] != e["previous"]
                         for e in done)
    mask = sum((1 << i) for i, r in enumerate(routes) if r == "A")
    rest = cfg["clock"][len(done):]

    @lru_cache(None)
    def possible(index, state):
        if index == len(rest):
            return frozenset({0})
        seat = rest[index]
        values = set()
        for new in (state, state ^ (1 << seat)):
            excess = 3 * (new.bit_count() - 4)**2
            stage = excess if metric == "excess" else 2 * excess + int(
                new != state and seat == cfg["focal"])
            values.update(stage + child for child in possible(index + 1, new))
            if len(values) > max_values:
                raise ValueError("support exceeds the declared exact-computation limit")
        return frozenset(values)

    already = previous_excess if metric == "excess" else (
        2 * previous_excess + previous_focal)
    return frozenset(already + x for x in possible(0, mask))


def _sum_supports(supports, max_values):
    totals = {0}
    for choices in supports:
        totals = {x + y for x in totals for y in choices}
        if len(totals) > max_values:
            raise ValueError("cohort support exceeds exact-computation limit")
    return totals


def compare_support(bundle, *, metric="excess", max_values=50000):
    if type(max_values) is not int or max_values < 1:
        raise ValueError("invalid exact-computation limit")
    check_registry(bundle)
    from collections import defaultdict
    arms = defaultdict(list)
    for row in bundle["cohort"]:
        s = row["summary"]
        a = s["assigned_arm"]
        if a is None:
            continue
        key = (s["start_A"], s["horizon"], a["frame"], a["amount"])
        arms[key].append(group_cost_support(row["events"], metric=metric,
                                            max_values=max_values))
    aggregate = {key: _sum_supports(sets, max_values) for key, sets in arms.items()}
    bounded = {
        (r["start_A"], r["horizon"], r["frame"]): r
        for r in compare_registry(bundle, metric=metric)["comparisons"]}
    results = []
    for key, report in sorted(bounded.items()):
        minus, plus = aggregate[(*key, -4)], aggregate[(*key, 4)]
        n_minus, n_plus = len(arms[(*key, -4)]), len(arms[(*key, 4)])
        exact = {Fraction(a, n_minus) - Fraction(b, n_plus)
                 for a in minus for b in plus}
        if len(exact) > max_values:
            raise ValueError("contrast support exceeds exact-computation limit")
        sorted_values = sorted(exact)
        bounds = report["minus4_minus_plus4_bounds"]
        if [sorted_values[0], sorted_values[-1]] != bounds:
            raise AssertionError("R52 interval endpoints differ from exact support")
        results.append({
            "start_A": key[0], "horizon": key[1], "frame": key[2],
            "number_of_attainable_cost_differences": len(sorted_values),
            "attainable_cost_differences": sorted_values,
            "zero_is_attainable": Fraction(0) in exact,
            "both_strict_signs_are_attainable": min(exact) < 0 < max(exact),
            "bounds": bounds,
        })
    return {"metric": metric, "comparisons": results,
            "interpretation": "Discrete finite-cohort completion support, not a causal identified set."}
