"""R52: sharp remaining-horizon cost bounds on a frozen six-seat revision clock.

Uses no assumed learning, utility, or obedience rule. Every action is feasible.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path

from r49_audit import audit_trace
from r49_model import TARGET_A, from_events
from r51_registry import check_registry


def sharp_bounds(events, *, witnesses=False):
    audit_trace(events, allow_prefix=True)
    setup, routes = from_events(events)
    choices = [e for e in events if e["type"] == "choice_committed"]
    before = sum(3 * (e["after_A"] - TARGET_A)**2 for e in choices)
    before_focal = sum(e["seat"] == setup["focal"] and e["route"] != e["previous"]
                       for e in choices)
    mask = sum(1 << i for i, r in enumerate(routes) if r == "A")
    pending_clock = setup["clock"][len(choices):]
    focal = setup["focal"]

    @lru_cache(None)
    def dp(index, current):
        if index == len(pending_clock):
            return (0, 0, 0, 0)
        seat = pending_clock[index]
        choices_at_node = []
        for following in (current, current ^ (1 << seat)):
            n = following.bit_count()
            excess = 3 * (n - TARGET_A)**2
            switch = int(following != current and seat == focal)
            child = dp(index + 1, following)
            choices_at_node.append((excess + child[0], excess + child[1],
                                    2 * excess + switch + child[2],
                                    2 * excess + switch + child[3]))
        return (min(c[0] for c in choices_at_node), max(c[1] for c in choices_at_node),
                min(c[2] for c in choices_at_node), max(c[3] for c in choices_at_node))

    future = dp(0, mask)
    report = {
        "committed_rounds": len(choices), "horizon": setup["rounds"],
        "future_excess_cost_bounds": [future[0], future[1]],
        "full_excess_cost_bounds": [before + future[0], before + future[1]],
        "full_total_cost_half_points_bounds": [
            2 * before + before_focal + future[2],
            2 * before + before_focal + future[3]],
        "reachable_dynamic_states": dp.cache_info().currsize,
    }
    if witnesses:
        def path_for(column):
            state = mask
            future_path = []
            for index, seat in enumerate(pending_clock):
                candidates = []
                for next_mask in (state, state ^ (1 << seat)):
                    n = next_mask.bit_count()
                    excess = 3 * (n - TARGET_A)**2
                    switch = int(next_mask != state and seat == focal)
                    subtotal = (excess if column < 2 else 2 * excess + switch)
                    subtotal += dp(index + 1, next_mask)[column]
                    candidates.append((subtotal, next_mask))
                target = dp(index, state)[column]
                new_mask = next(next_mask for cost, next_mask in candidates if cost == target)
                future_path.append({
                    "round": len(choices) + index + 1, "seat": seat,
                    "route": "A" if new_mask & (1 << seat) else "B",
                    "changed": new_mask != state})
                state = new_mask
            return future_path
        report["witnesses"] = {
            "min_excess": path_for(0), "max_excess": path_for(1),
            "min_total": path_for(2), "max_total": path_for(3)}
    return report


def evaluate_registry(bundle):
    check_registry(bundle)
    import collections
    cells = collections.defaultdict(list)
    for study in bundle["cohort"]:
        s = study["summary"]
        if s["assigned_arm"] is None:
            continue
        arm = s["assigned_arm"]
        key = (s["start_A"], s["horizon"], arm["frame"], arm["amount"])
        result = sharp_bounds(study["events"])
        coarse = s["excess_cost_bounds"]
        if not (coarse[0] <= result["full_excess_cost_bounds"][0]
                <= result["full_excess_cost_bounds"][1] <= coarse[1]):
            raise AssertionError("sharp bound escaped the conservative R51 envelope")
        cells[key].append(result)
    rows = []
    for key, value in sorted(cells.items()):
        n = len(value)
        lo = sum(r["full_excess_cost_bounds"][0] for r in value)
        hi = sum(r["full_excess_cost_bounds"][1] for r in value)
        total_lo = sum(r["full_total_cost_half_points_bounds"][0] for r in value)
        total_hi = sum(r["full_total_cost_half_points_bounds"][1] for r in value)
        rows.append({
            "start_A": key[0], "horizon": key[1], "frame": key[2], "amount": key[3],
            "assigned": n, "mean_excess_cost_bounds": [lo/n, hi/n],
            "mean_total_cost_half_points_bounds": [total_lo/n, total_hi/n],
        })
    differences = []
    for key in sorted({(r["start_A"],r["horizon"],r["frame"]) for r in rows}):
        neg = next((r for r in rows if (r["start_A"],r["horizon"],r["frame"],r["amount"]) == (*key,-4)),None)
        pos = next((r for r in rows if (r["start_A"],r["horizon"],r["frame"],r["amount"]) == (*key,4)),None)
        if neg is None or pos is None:
            continue
        a,b=neg["mean_excess_cost_bounds"],pos["mean_excess_cost_bounds"]
        differences.append({"start_A":key[0],"horizon":key[1],"frame":key[2],
                            "minus4_minus_plus4_excess_bounds":[a[0]-b[1],a[1]-b[0]]})
    return {"cells": rows, "contrasts": differences,
            "scope":"Sharp clock-feasible synthetic completion bounds; not causal or statistical intervals."}


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("registry",type=Path)
    a=p.parse_args()
    print(json.dumps(evaluate_registry(json.loads(a.registry.read_text(encoding="utf-8"))),
                     indent=2))
