"""Read-only, operator-side cohort export for R49 complete and incomplete sessions.

Never publish registry files containing full future seat clocks or per-seat choices.
"""
import argparse
import json
from pathlib import Path

from r49_audit import audit_trace
from r49_model import PAYOUT_ROUND, PROTOCOL, TARGET_A, next_state, outcome

REGISTRY_SCHEMA = "rithm-r51-registry-v1"


def derive(events):
    audit_trace(events, allow_prefix=True)
    cfg = events[0]
    phase = next_state(events)
    finished = phase["phase"] == "complete"
    if finished:
        audit_trace(events)
    assigned = next((e for e in events if e["type"] == "settlement_assigned"), None)
    acknowledged = next((e for e in events if e["type"] == "settlement_acknowledged"), None)
    decisions = [e for e in events if e["type"] == "choice_committed"]
    first = next((e for e in decisions if acknowledged is not None and
                  e["seq"] > acknowledged["seq"] and e["seat"] == cfg["focal"]), None)
    response = None if first is None and not finished else (
        bool(first["route"] != first["previous"]) if first is not None else False
    )
    excess = sum(3 * (e["after_A"] - TARGET_A)**2 for e in decisions)
    focal_switches = sum(e["seat"] == cfg["focal"] and e["previous"] != e["route"] for e in decisions)
    remaining = cfg["rounds"] - len(decisions)
    # Each unobserved stage has excess congestion in [0,48].
    # Only a scheduled focal opportunity can add a further focal switching event.
    future_focal = sum(seat == cfg["focal"] for seat in cfg["clock"][len(decisions):])
    return {
        "start_A": cfg["start"], "horizon": cfg["rounds"], "phase": phase["phase"],
        "completed": finished, "committed_rounds": len(decisions),
        "assigned_arm": None if assigned is None else {
            "frame": assigned["frame"], "amount": assigned["amount"]},
        "acknowledged": acknowledged is not None,
        "first_focal_round": None if first is None else first["round"],
        "first_focal_switch": response,
        "excess_cost_bounds": [excess, excess + 48 * remaining],
        "total_cost_half_points_bounds": [2 * excess + focal_switches,
                                         2 * (excess + 48 * remaining) + focal_switches + future_focal],
    }


def registry(ledger):
    # Snapshot all study streams under a single SQLite transaction: no torn groups.
    with ledger.connect() as db:
        keys = [row[0] for row in db.execute(
            "SELECT DISTINCT study FROM r49_events ORDER BY study")]
        entries = [(key, ledger.load(db, key)) for key in keys]
    rows = []
    for key, events in entries:
        derived = derive(events)
        if derived["completed"] and outcome(events)["first_focal_after_settlement"] is None:
            if derived["first_focal_switch"] is not False:
                raise AssertionError("complete no-opportunity trace must be known zero")
        safe = [{k: v for k, v in e.items() if k != "receipt"} for e in events]
        rows.append({"study": key, "protocol": PROTOCOL, "events": safe, "summary": derived})
    return {"schema": REGISTRY_SCHEMA, "cohort": rows}


def check_registry(bundle):
    if bundle.get("schema") != REGISTRY_SCHEMA or not isinstance(bundle.get("cohort"), list):
        raise ValueError("invalid R51 registry")
    ids = set()
    for row in bundle["cohort"]:
        key = row.get("study")
        if not isinstance(key, str) or len(key) != 32 or any(c not in "0123456789abcdef" for c in key):
            raise ValueError("invalid study identifier")
        if key in ids:
            raise ValueError("duplicate allocated study")
        ids.add(key)
        if row.get("protocol") != PROTOCOL:
            raise ValueError("unknown study protocol")
        if any("receipt" in e for e in row["events"]):
            raise ValueError("receipt exposed in operator export")
        if derive(row["events"]) != row.get("summary"):
            raise ValueError("forged summary or invalid prefix")
    return len(ids)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--db", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    from r49_store import Ledger
    result = registry(Ledger(a.db))
    check_registry(result)
    a.output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"exported {len(result['cohort'])} allocated studies; operator-only")
