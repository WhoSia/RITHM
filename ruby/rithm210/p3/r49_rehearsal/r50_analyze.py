"""Analyze first revision by lag from independently checked R49 exports."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path

from r49_audit import audit
from r49_model import AMOUNTS, FRAMES, PAYOUT_ROUND, outcome


def rate(changes, opportunities):
    return Fraction(changes, opportunities) if opportunities else None


def summarize_exports(exports):
    cells = defaultdict(lambda: {"groups": 0, "missed": 0, "by_lag": Counter(), "changed": Counter()})
    seen = set()
    for export in exports:
        audit(export)
        events = export["events"]
        trace = json.dumps(events, sort_keys=True)
        if trace in seen:
            raise ValueError("duplicate event trace")
        seen.add(trace)
        derived = outcome(events)
        if export.get("outcome") != derived:
            raise ValueError("exported outcome differs from audited choices")
        setup = events[0]
        assignment = next(e for e in events if e["type"] == "settlement_assigned")
        key = (setup["start"], setup["rounds"], assignment["frame"], assignment["amount"])
        cell = cells[key]
        cell["groups"] += 1
        focal = derived["first_focal_after_settlement"]
        if focal is None:
            cell["missed"] += 1
            continue
        delta = focal["round"] - PAYOUT_ROUND
        cell["by_lag"][delta] += 1
        cell["changed"][delta] += int(focal["switched"])

    rows = {}
    for key, cell in sorted(cells.items()):
        start, horizon, frame, amount = key
        observed = sum(cell["by_lag"].values())
        changed = sum(cell["changed"].values())
        by_lag = {
            lag: {"opportunities": cell["by_lag"][lag], "changes": cell["changed"][lag],
                  "switch_rate": rate(cell["changed"][lag], cell["by_lag"][lag])}
            for lag in range(1, horizon - PAYOUT_ROUND + 1)
        }
        rows[key] = {
            "start_A": start, "horizon": horizon, "frame": frame, "amount": amount,
            "groups": cell["groups"], "no_opportunity": cell["missed"], "observed": observed,
            "switch_rate_given_opportunity": rate(changed, observed),
            "observed_first_switches_per_assigned_group": rate(changed, cell["groups"]),
            "by_lag": by_lag,
        }

    contrasts = {}
    for start, horizon, frame in sorted({key[:3] for key in rows}):
        low, high = (rows.get((start, horizon, frame, amount)) for amount in AMOUNTS)
        if low is None or high is None:
            continue
        differences = {}
        for lag, lo in low["by_lag"].items():
            hi = high["by_lag"][lag]
            a, b = lo["switch_rate"], hi["switch_rate"]
            differences[lag] = {
                "minus4_opportunities": lo["opportunities"],
                "plus4_opportunities": hi["opportunities"],
                "rate_difference": None if a is None or b is None else a - b,
            }
        contrasts[start, horizon, frame] = {
            "start_A": start, "horizon": horizon, "frame": frame,
            "minus4_minus_plus4": differences,
        }

    interactions = []
    for start, horizon in sorted({key[:2] for key in contrasts}):
        route, wallet = (contrasts.get((start, horizon, frame)) for frame in FRAMES)
        if route is None or wallet is None:
            continue
        differences = {}
        for lag in route["minus4_minus_plus4"]:
            r = route["minus4_minus_plus4"][lag]["rate_difference"]
            w = wallet["minus4_minus_plus4"][lag]["rate_difference"]
            differences[lag] = None if r is None or w is None else r - w
        interactions.append({"start_A": start, "horizon": horizon,
                             "route_minus_wallet_signed_contrast": differences})
    return {"cells": list(rows.values()), "lag_contrasts": list(contrasts.values()),
            "lag_frame_interactions": interactions}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("exports", nargs="+", type=Path)
    inputs = cli.parse_args()
    print(json.dumps(summarize_exports(json.loads(f.read_text(encoding="utf-8")) for f in inputs.exports),
                     indent=2, default=str))
