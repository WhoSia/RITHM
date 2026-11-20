"""R53: sharp extrema for realized assigned-arm welfare rankings.

The estimand is a finite cohort's *realized* minus-four minus plus-four
average resource cost, conditional on the frozen operator ledger.
It is NOT an average causal treatment effect or a confidence interval.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path

from r51_registry import check_registry
from r52_welfare_bounds import sharp_bounds

METRICS = {
    "excess": ("full_excess_cost_bounds", "min_excess", "max_excess"),
    "half_points": ("full_total_cost_half_points_bounds", "min_total", "max_total"),
}


def classification(lower, upper):
    """Return an exhaustive sign classification without assuming a continuum."""
    if lower > upper:
        raise ValueError("inverted bounds")
    if lower > 0:
        return "minus4_strictly_higher_cost"
    if upper < 0:
        return "minus4_strictly_lower_cost"
    if lower == upper == 0:
        return "identical_cost"
    if lower < 0 < upper:
        return "both_strict_cost_rankings_attainable"
    if lower == 0:
        return "minus4_weakly_higher_cost"
    if upper == 0:
        return "minus4_weakly_lower_cost"
    raise AssertionError("unclassified sign")


def compare_registry(bundle, *, metric="excess", witnesses=False):
    check_registry(bundle)
    if metric not in METRICS:
        raise ValueError("unknown welfare metric")
    field, minimum, maximum = METRICS[metric]
    groups = defaultdict(list)
    unassigned = defaultdict(int)
    for row in bundle["cohort"]:
        summary = row["summary"]
        start, horizon = summary["start_A"], summary["horizon"]
        arm = summary["assigned_arm"]
        if arm is None:
            unassigned[(start, horizon)] += 1
            continue
        key = (start, horizon, arm["frame"], arm["amount"])
        bounds = sharp_bounds(row["events"], witnesses=witnesses)
        low, high = bounds[field]
        if low > high:
            raise AssertionError("inverted group interval")
        entry = {"group": row["study"], "bounds": [low, high]}
        if witnesses:
            entry["witnesses"] = {minimum: bounds["witnesses"][minimum],
                                  maximum: bounds["witnesses"][maximum]}
        groups[key].append(entry)
    cells = {}
    for key, rows in sorted(groups.items()):
        n = len(rows)
        cells[key] = {
            "start_A": key[0], "horizon": key[1], "frame": key[2],
            "amount": key[3], "assigned": n,
            "mean_bounds": [
                Fraction(sum(g["bounds"][0] for g in rows), n),
                Fraction(sum(g["bounds"][1] for g in rows), n)],
        }
        # Witnesses are kept outside arm cell summaries; never publish private clocks.
    comparisons = []
    for start, horizon, frame in sorted({key[:3] for key in cells}):
        minus_key = (start, horizon, frame, -4)
        plus_key = (start, horizon, frame, 4)
        if minus_key not in cells or plus_key not in cells:
            continue
        lo_minus, hi_minus = cells[minus_key]["mean_bounds"]
        lo_plus, hi_plus = cells[plus_key]["mean_bounds"]
        low, high = lo_minus - hi_plus, hi_minus - lo_plus
        result = {
            "start_A": start, "horizon": horizon, "frame": frame,
            "minus4_minus_plus4_bounds": [low, high],
            "ranking": classification(low, high),
            "cohort_sizes": {"minus4": cells[minus_key]["assigned"],
                             "plus4": cells[plus_key]["assigned"]},
        }
        if witnesses:
            # Each endpoint uses independent feasible continuation paths for
            # disjoint allocated groups in the two signed arms.
            result["endpoint_witnesses"] = {
                "lower": {
                    "minus4": [{"group": g["group"], "path": g["witnesses"][minimum]}
                               for g in groups[minus_key]],
                    "plus4": [{"group": g["group"], "path": g["witnesses"][maximum]}
                              for g in groups[plus_key]]},
                "upper": {
                    "minus4": [{"group": g["group"], "path": g["witnesses"][maximum]}
                               for g in groups[minus_key]],
                    "plus4": [{"group": g["group"], "path": g["witnesses"][minimum]}
                              for g in groups[plus_key]]},
            }
        comparisons.append(result)
    return {
        "metric": metric,
        "allocated": len(bundle["cohort"]),
        "assigned": sum(cell["assigned"] for cell in cells.values()),
        "before_assignment": [
            {"start_A": start, "horizon": horizon, "count": count}
            for (start, horizon), count in sorted(unassigned.items())
        ],
        "arm_cells": list(cells.values()),
        "comparisons": comparisons,
        "interpretation": (
            "Sharp extreme realized arm-mean contrasts over independent "
            "clock-feasible group completions only; NOT causal ATE, "
            "statistical confidence bounds, or proof of continuous interval support."
        )
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("registry", type=Path)
    p.add_argument("--metric", choices=sorted(METRICS), default="excess")
    p.add_argument("--operator-witnesses", action="store_true",
                   help="RESTRICTED: emit future seat clocks and choices")
    a = p.parse_args()
    bundle = json.loads(a.registry.read_text(encoding="utf-8"))
    result = compare_registry(bundle, metric=a.metric,
                              witnesses=a.operator_witnesses)
    print(json.dumps(result, indent=2, default=str))
