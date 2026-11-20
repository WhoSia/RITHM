"""Regression tests for R51 cohort inclusion and worst-case bounds."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import tempfile
import unittest

from r49_store import Ledger
from r51_registry import check_registry, registry
from r51_bounds import summarize
from test_r49 import FixedDraws


class R51RegistryTests(unittest.TestCase):
    def setUp(self):
        temp = self.enterContext(tempfile.TemporaryDirectory())
        self.db = Path(temp) / "rehearsal.sqlite3"

    def play(self, key, amount, clock, *, stopping="complete", first_switch=False):
        rng = FixedDraws(amount=amount)
        rng.clock = iter(clock)
        ledger = Ledger(self.db, rng)
        study = f"{key:032x}"
        ledger.allocate(study, 5, len(clock))
        while True:
            view = ledger.view(study)
            events = self.events(ledger, study)
            if stopping == "before_assignment" and view == {"phase": "handoff", "round": 2, "seat": clock[1]}:
                return
            if stopping == "before_issue" and events[-1]["type"] == "settlement_assigned":
                return
            if stopping == "before_ack" and events[-1]["type"] == "settlement_issued":
                return
            if stopping == "before_focal" and view == {"phase": "handoff", "round": 3, "seat": clock[2]}:
                return
            if view["phase"] == "complete":
                return
            t, seat = view["round"], view["seat"]
            if view["phase"] == "handoff":
                ledger.action(study, "open", t, seat=seat)
            elif view["phase"] == "choice":
                move = first_switch and t > 2 and seat == 0 and not any(
                    e["type"] == "choice_committed" and e["round"] > 2 and
                    e["seat"] == 0 for e in events)
                route = "B" if move else view["previous"]
                ledger.action(study, "choose", t, seat=seat, route=route)
            else:
                ticket = ledger.action(study, "issue", t, seat=seat)
                ledger.action(study, "ack", t, seat=seat, receipt=ticket["receipt"])

    @staticmethod
    def events(ledger, study):
        with ledger.connect() as db:
            return ledger.load(db, study)

    def fixture(self):
        self.play(1, -4, (0, 1, 0, 2, 3), first_switch=True)
        self.play(2, +4, (0, 1, 0, 2, 3))
        self.play(3, -4, (0, 1, 2, 0, 3), stopping="before_focal")
        self.play(4, +4, (0, 1, 2, 0, 3), stopping="before_issue")
        self.play(5, +4, (0, 1, 2, 3, 4))
        self.play(6, -4, (0, 1, 2, 3, 4), stopping="before_assignment")
        return registry(Ledger(self.db))

    def test_registry_includes_all_assigned_and_partial_states(self):
        b = self.fixture()
        self.assertEqual(check_registry(b), 6)
        states = {r["study"]: r["summary"] for r in b["cohort"]}
        self.assertEqual(states[f"{6:032x}"]["assigned_arm"], None)
        self.assertFalse(states[f"{4:032x}"]["acknowledged"])
        self.assertEqual(states[f"{3:032x}"]["first_focal_switch"], None)
        self.assertIs(states[f"{5:032x}"]["first_focal_switch"], False)
        self.assertEqual(states[f"{1:032x}"]["first_focal_switch"], True)
        self.assertTrue(states[f"{2:032x}"]["completed"])
        self.assertNotIn("receipt", str(b))

    def test_bounds_include_unknown_outcomes_without_imputation(self):
        result = summarize(self.fixture())
        self.assertEqual((result["allocated"], result["assigned"]), (6, 5))
        self.assertEqual(result["preassignment_no_arm"][0]["count"], 1)
        arm = {(r["frame"], r["amount"]): r for r in result["arm_cells"]}
        neg, pos = arm["route", -4], arm["route", 4]
        self.assertEqual(neg["assigned_group_first_switch_bounds"], [Q(1, 2), Q(1)])
        self.assertEqual(pos["assigned_group_first_switch_bounds"], [Q(0), Q(1, 3)])
        self.assertEqual(neg["unknown_first_response"], 1)
        self.assertEqual(pos["assigned_but_unacknowledged"], 1)
        self.assertEqual(result["contrasts"][0]["minus4_minus_plus4_first_switch_bounds"],
                         [Q(1, 6), Q(1)])
        self.assertGreater(neg["assigned_group_excess_cost_mean_bounds"][1],
                           neg["assigned_group_excess_cost_mean_bounds"][0])

    def test_reject_duplicate_and_forged_partial_summary(self):
        bundle = self.fixture()
        duplicate = deepcopy(bundle)
        duplicate["cohort"].append(deepcopy(duplicate["cohort"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate allocated"):
            check_registry(duplicate)
        tampered = deepcopy(bundle)
        tampered["cohort"][2]["summary"]["completed"] = True
        with self.assertRaisesRegex(ValueError, "forged summary"):
            check_registry(tampered)

    def test_audit_rejects_incomplete_atomic_reward_assignment(self):
        bundle = self.fixture()
        tampered = deepcopy(bundle)
        row = next(r for r in tampered["cohort"] if r["study"] == f"{4:032x}")
        row["events"] = row["events"][:-1]  # Between round-two choice and mandatory draw
        with self.assertRaisesRegex(ValueError, "missing settlement_assigned"):
            check_registry(tampered)

    def test_bounds_do_not_claim_significance(self):
        r = summarize(self.fixture())
        self.assertIn("not confidence intervals", r["interpretation"])
        self.assertTrue(all(lo <= hi for c in r["arm_cells"]
                            for lo, hi in [c["assigned_group_excess_cost_mean_bounds"]]))


if __name__ == "__main__":
    unittest.main()
