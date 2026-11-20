"""Build a synthetic roster and replay both extremal choices from its prefixes."""

import argparse
from fractions import Fraction
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from r49_model import AMOUNTS, FRAMES
from r49_store import Ledger
from r51_audit_roster import analyze_roster
from r51_roster import export_roster, group_ref


class PrescribedDraws:
    def __init__(self, amount, clock):
        self.amount = amount
        self.clock = iter(clock)

    def shuffle(self, routes):
        pass

    def choice(self, values):
        if values == AMOUNTS:
            return self.amount
        if values == FRAMES:
            return "route"
        return values[0]

    def randrange(self, n):
        return next(self.clock)


def advance(ledger, group, through, move):
    """Replay this fixture's choices up to a chosen round, including the receipt."""
    while (view := ledger.view(group))["phase"] != "complete":
        t, seat = view["round"], view["seat"]
        if t > through:
            break
        if view["phase"] == "handoff":
            ledger.action(group, "open", t, seat=seat)
        elif view["phase"] == "choice":
            route = "B" if move and seat == 0 and t > 2 else view["previous"]
            ledger.action(group, "choose", t, seat=seat, route=route)
        else:
            ticket = ledger.action(group, "issue", t, seat=seat)
            ledger.action(group, "ack", t, seat=seat, receipt=ticket["receipt"])


def demonstrate(directory):
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    path = root / "frozen.sqlite3"
    early = (0, 1, 0, 2, 3)
    late = (0, 1, 2, 3, 0)
    none = (0, 1, 2, 3, 4)
    design = [
        (-4, early, 5, True), (-4, early, 5, True),
        (-4, early, 3, False), (-4, none, 3, False),
        (-4, late, 3, False), (-4, late, 2, False),
        (4, early, 5, False), (4, early, 5, False),
        (4, early, 3, True), (4, early, 4, True),
        (4, late, 3, False), (4, late, 2, False),
        (None, late, 0, False), (None, late, 1, False),
    ]
    assigned = {}
    for index, (amount, clock, through, move) in enumerate(design, 1):
        key = f"{index:032x}"
        ledger = Ledger(path, PrescribedDraws(amount, clock))
        ledger.allocate(key, 5, 5)
        advance(ledger, key, through, move)
        if amount is not None:
            assigned[key] = amount

    frozen = export_roster(path)
    summary = analyze_roster(frozen)
    bounds = summary["contrasts"][0]["minus4_minus_plus4_bounds"]
    endpoints = {}
    for label, switching_arm in (("lower", 4), ("upper", -4)):
        endpoint = root / f"{label}.sqlite3"
        shutil.copyfile(path, endpoint)
        ledger = Ledger(endpoint)
        for key, amount in assigned.items():
            advance(ledger, key, 5, amount == switching_arm)
        full = export_roster(endpoint)
        frozen_by_id = {g["group"]: g["events"] for g in frozen["groups"]}
        for entry in full["groups"]:
            prefix = frozen_by_id[entry["group"]]
            if entry["events"][:len(prefix)] != prefix:
                raise ArithmeticError("completion rewrote the frozen prefix")
        assigned_refs = {group_ref(key) for key in assigned}
        replay = analyze_roster(full)
        diff = replay["contrasts"][0]
        endpoints[label] = diff["complete_case_difference"]
        if replay["settlement_assigned"] != len(assigned_refs):
            raise ArithmeticError("assignments changed during completion")

    if (endpoints["lower"], endpoints["upper"]) != bounds:
        raise ArithmeticError("endpoint replay differs from the calculated bounds")
    return {"frozen_summary": summary, "attained_completions": endpoints,
            "complete_case_difference_at_freeze": summary["contrasts"][0]["complete_case_difference"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    with TemporaryDirectory() as d:
        print(json.dumps(demonstrate(d), indent=2, default=str))
