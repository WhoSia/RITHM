"""Check which first-choice outcomes are known in a frozen R49 roster."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path
import re

from r49_audit import audit_trace
from r49_model import AMOUNTS, PAYOUT_ROUND, PROTOCOL
from r51_roster import ROSTER_SCHEMA

STATUSES = ("switched", "stayed", "no_scheduled_opportunity", "unresolved")


def classify(events):
    verified = audit_trace(events, allow_prefix=True)
    setup = events[0]
    completion = verified["choices"] == setup["rounds"]
    allocation = next((e for e in events if e["type"] == "settlement_assigned"), None)
    if allocation is None:
        return {"status": "before_assignment", "complete": False, "cell": None,
                "committed_rounds": verified["choices"]}
    focal = setup["focal"]
    first_round = next((t for t, seat in enumerate(setup["clock"], 1)
                        if t > PAYOUT_ROUND and seat == focal), None)
    first_choice = next((e for e in events if e["type"] == "choice_committed"
                         and e["round"] == first_round), None)
    if first_round is None:
        status = "no_scheduled_opportunity"
    elif first_choice is None:
        status = "unresolved"
    else:
        status = "stayed" if first_choice["route"] == first_choice["previous"] else "switched"
    return {
        "complete": completion, "status": status, "first_scheduled_round": first_round,
        "cell": (setup["start"], setup["rounds"], allocation["frame"], allocation["amount"]),
    }


def analyze_roster(roster):
    if roster.get("schema") != ROSTER_SCHEMA or roster.get("source_protocol") != PROTOCOL:
        raise ValueError("unknown roster schema")
    seen, traces = set(), set()
    before = Counter()
    cells = defaultdict(Counter)
    for entry in roster["groups"]:
        group = entry["group"]
        if not isinstance(group, str) or not re.fullmatch(r"[0-9a-f]{64}", group):
            raise ValueError("invalid roster group reference")
        trace = json.dumps(entry["events"], sort_keys=True)
        if group in seen or trace in traces:
            raise ValueError("duplicate group or event trace")
        seen.add(group)
        traces.add(trace)

        result = classify(entry["events"])
        if result["cell"] is None:
            before[result["committed_rounds"]] += 1
            continue
        counts = cells[result["cell"]]
        status = result["status"]
        counts[status] += 1
        if result["complete"]:
            counts["completed_groups"] += 1
            counts["completed_" + status] += 1
        else:
            counts["incomplete_groups"] += 1
            counts["incomplete_known"] += status != "unresolved"

    rows = {}
    for key, counts in sorted(cells.items()):
        start, horizon, frame, amount = key
        n = sum(counts[s] for s in STATUSES)
        known_switches = counts["switched"]
        completed = counts["completed_groups"]
        rows[key] = {
            "start_A": start, "horizon": horizon, "frame": frame, "amount": amount,
            "assigned": n, "completed": completed, "incomplete": counts["incomplete_groups"],
            "incomplete_known": counts["incomplete_known"],
            "observed_switch_status": {s: counts[s] for s in STATUSES},
            "status_by_completion": {
                "completed": {s: counts["completed_" + s] for s in STATUSES},
                "incomplete": {s: counts[s] - counts["completed_" + s] for s in STATUSES},
            },
            "full_observation_rate_bounds": (
                Fraction(known_switches, n), Fraction(known_switches + counts["unresolved"], n),
            ),
            "complete_case_rate": Fraction(counts["completed_switched"], completed) if completed else None,
        }

    contrasts = []
    for start, horizon, frame in sorted({key[:3] for key in rows}):
        low, high = (rows.get((start, horizon, frame, a)) for a in AMOUNTS)
        if low is None or high is None:
            continue
        l0, l1 = low["full_observation_rate_bounds"]
        h0, h1 = high["full_observation_rate_bounds"]
        lc, hc = low["complete_case_rate"], high["complete_case_rate"]
        contrasts.append({
            "start_A": start, "horizon": horizon, "frame": frame,
            "minus4_minus_plus4_bounds": (l0 - h1, l1 - h0),
            "complete_case_difference": None if lc is None or hc is None else lc - hc,
        })
    missing = sum(before.values())
    return {
        "allocated": len(seen), "before_settlement_assignment": missing,
        "before_assignment_by_committed_rounds": dict(sorted(before.items())),
        "settlement_assigned": len(seen) - missing, "cells": list(rows.values()),
        "contrasts": contrasts,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roster", type=Path)
    args = parser.parse_args()
    print(json.dumps(analyze_roster(json.loads(args.roster.read_text(encoding="utf-8"))),
                     indent=2, default=str))
