"""Conservative randomized-arm effect intervals with incomplete R49 traces."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path

from r51_registry import check_registry


def ratio(a, n):
    return Fraction(a, n) if n else None


def summarize(bundle):
    check_registry(bundle)
    arms = defaultdict(list)
    preassignment = Counter()
    for study in bundle["cohort"]:
        s = study["summary"]
        if s["assigned_arm"] is None:
            preassignment[(s["start_A"], s["horizon"])] += 1
            continue
        arm = s["assigned_arm"]
        arms[(s["start_A"], s["horizon"], arm["frame"], arm["amount"])].append(s)
    cells = {}
    for key, rows in sorted(arms.items()):
        start, horizon, frame, amount = key
        n = len(rows)
        yes = sum(s["first_focal_switch"] is True for s in rows)
        no = sum(s["first_focal_switch"] is False for s in rows)
        missing = sum(s["first_focal_switch"] is None for s in rows)
        if yes + no + missing != n:
            raise AssertionError("missing disposition")
        lower, upper = ratio(yes, n), ratio(yes + missing, n)
        assert lower <= upper
        complete = sum(s["completed"] for s in rows)
        assigned_unack = sum(not s["acknowledged"] for s in rows)
        lo_cost = sum(s["excess_cost_bounds"][0] for s in rows)
        hi_cost = sum(s["excess_cost_bounds"][1] for s in rows)
        cells[key] = {
            "start_A": start, "horizon": horizon, "frame": frame, "amount": amount,
            "assigned": n, "complete": complete, "not_complete": n - complete,
            "assigned_but_unacknowledged": assigned_unack,
            "known_first_switch": yes, "known_first_stay_or_no_opportunity": no,
            "unknown_first_response": missing,
            "complete_case_switch_rate": ratio(yes, yes + no),
            "assigned_group_first_switch_bounds": [lower, upper],
            "assigned_group_excess_cost_mean_bounds": [ratio(lo_cost, n), ratio(hi_cost, n)],
            "phases": dict(Counter(s["phase"] for s in rows)),
        }
    contrasts = []
    for start, horizon, frame in sorted({k[:3] for k in cells}):
        minus = cells.get((start, horizon, frame, -4))
        plus = cells.get((start, horizon, frame, 4))
        if minus is None or plus is None:
            continue
        a, b = minus["assigned_group_first_switch_bounds"], plus["assigned_group_first_switch_bounds"]
        ca = minus["assigned_group_excess_cost_mean_bounds"]
        cb = plus["assigned_group_excess_cost_mean_bounds"]
        contrasts.append({
            "start_A": start, "horizon": horizon, "frame": frame,
            "minus4_minus_plus4_first_switch_bounds": [a[0] - b[1], a[1] - b[0]],
            "minus4_minus_plus4_excess_cost_mean_bounds": [ca[0] - cb[1], ca[1] - cb[0]],
        })
    return {
        "allocated": len(bundle["cohort"]),
        "assigned": sum(c["assigned"] for c in cells.values()),
        "preassignment_no_arm": [
            {"start_A": start, "horizon": horizon, "count": n}
            for (start, horizon), n in sorted(preassignment.items())
        ],
        "arm_cells": list(cells.values()),
        "contrasts": contrasts,
        "interpretation": "Finite-sample worst-case bounds; not confidence intervals or participant effects."
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    a = p.parse_args()
    print(json.dumps(summarize(json.loads(a.input.read_text(encoding="utf-8"))),
                     indent=2, default=str))
