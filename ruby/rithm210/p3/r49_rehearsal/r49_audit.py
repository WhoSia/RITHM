"""Independently check the phase sequence of an exported R49 rehearsal."""

import argparse
import json
from pathlib import Path

from r49_model import AMOUNTS, FRAMES, HORIZONS, PAYOUT_ROUND, PROTOCOL, SEATS


def audit(export):
    if export.get("schema") != PROTOCOL:
        raise ValueError("unknown rehearsal schema")
    events = export["events"]
    if not events:
        raise ValueError("missing allocation")
    config = events[0]
    focal = config["focal"]
    clock = config["clock"]
    routes = config["routes"].copy()
    if (config["rounds"] not in HORIZONS or len(clock) != config["rounds"]
            or any(seat not in range(SEATS) for seat in clock)
            or focal not in range(SEATS) or len(routes) != SEATS
            or any(route not in ("A", "B") for route in routes)
            or config["start"] not in (4, 5) or config["start"] != routes.count("A")
            or routes[focal] != ("A" if config["start"] == 5 else "B")):
        raise ValueError("invalid allocation")

    index = 0

    def expect(kind, round_, seat=None):
        nonlocal index
        index += 1
        if index > len(events):
            raise ValueError(f"missing {kind} at round {round_}")
        entry = events[index - 1]
        if (entry["seq"], entry["type"], entry["round"], entry.get("seat")) != (index, kind, round_, seat):
            raise ValueError(f"expected {kind} at round {round_}, sequence {index}")
        if type(entry["server_unix_ns"]) is not int or entry["server_unix_ns"] <= 0:
            raise ValueError("missing server timestamp")
        return entry

    expect("allocated", 0)
    for t, seat in enumerate(clock, start=1):
        opened = expect("opportunity_opened", t, seat)
        committed = expect("choice_committed", t, seat)
        before = routes.count("A")
        other = before - int(routes[seat] == "A")
        values = (opened["previous"], committed["previous"], opened["a"],
                  committed["before_A"], opened["cost_A"], opened["cost_B"])
        if values != (routes[seat], routes[seat], before, before, other+1, 2*(SEATS-other)):
            raise ValueError("recorded opportunity differs from the previous state")
        if committed["route"] not in ("A", "B"):
            raise ValueError("invalid committed route")
        routes[seat] = committed["route"]
        if committed["after_A"] != routes.count("A"):
            raise ValueError("recorded occupancy differs from the choices")
        if t == PAYOUT_ROUND:
            assigned = expect("settlement_assigned", t, focal)
            issued = expect("settlement_issued", t, focal)
            ack = expect("settlement_acknowledged", t, focal)
            if (assigned["frame"] not in FRAMES or assigned["amount"] not in AMOUNTS
                    or assigned["route"] != routes[focal]
                    or assigned["anchor_A"] != routes.count("A")
                    or any(assigned[key] != issued[key] for key in ("frame", "amount", "route"))):
                raise ValueError("settlement differs from recorded assignment or route")
            settlement_order = (committed["seq"], assigned["seq"], issued["seq"], ack["seq"], ack["seq"] + 1)
    if index != len(events):
        raise ValueError("unexpected event after last choice")
    regressions = sum(a["server_unix_ns"] > b["server_unix_ns"] for a, b in zip(events, events[1:]))
    return {"choices": len(clock), "events": index, "settlement_order": settlement_order,
            "wall_clock_regressions": regressions}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(json.loads(args.export.read_text(encoding="utf-8"))), indent=2))
