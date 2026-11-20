"""Independent full-path witness tests for R53 partial welfare rankings."""
from fractions import Fraction as Q
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from r49_model import from_events
from r49_store import Ledger
from r51_registry import registry
from r53_policy_order import classification, compare_registry
from test_r49 import FixedDraws

CLOCK = (0, 1, 2, 3, 4)


class R53PolicyOrderTests(unittest.TestCase):
    def setUp(self):
        self.db = Path(self.enterContext(TemporaryDirectory())) / "pilot.sqlite3"
        self.ledger = {}
        self.keys = {}

    def allocate(self, key_number, amount, *, move_at_three=False, through=4,
                 clock=CLOCK, final_route=None):
        key = f"{key_number:032x}"
        rng = FixedDraws(amount=amount)
        rng.clock = iter(clock)
        ledger = Ledger(self.db, rng)
        ledger.allocate(key, 5, len(clock))
        self.ledger[key_number] = ledger
        self.keys[key_number] = key
        self.advance(key_number, through=through, move_at_three=move_at_three,
                     final_route=final_route)

    def advance(self, key_number, *, through, move_at_three=False, final_route=None):
        ledger, key = self.ledger[key_number], self.keys[key_number]
        while True:
            state = ledger.view(key)
            if state["phase"] == "complete":
                return
            t, seat = state["round"], state["seat"]
            if t > through:
                return
            if state["phase"] == "handoff":
                ledger.action(key, "open", t, seat=seat)
            elif state["phase"] == "choice":
                route = state["previous"]
                if move_at_three and t == 3 and seat == 2:
                    route = "B"
                if t == 5 and final_route is not None:
                    route = final_route
                ledger.action(key, "choose", t, seat=seat, route=route)
            else:
                ticket = ledger.action(key, "issue", t, seat=seat)
                ledger.action(key, "ack", t, seat=seat, receipt=ticket["receipt"])

    def current(self):
        return registry(Ledger(self.db))

    @staticmethod
    def independent_replay(events, planned):
        config, routes = from_events(events)
        initial = [e for e in events if e["type"] == "choice_committed"]
        excess = sum(3*(e["after_A"]-4)**2 for e in initial)
        focal_switches = sum(e["seat"] == config["focal"] and e["route"] != e["previous"]
                             for e in initial)
        for j, step in enumerate(planned):
            seat = config["clock"][len(initial) + j]
            assert step["seat"] == seat
            assert step["round"] == len(initial) + j + 1
            before = routes[seat]
            assert before in ("A", "B")
            assert step["route"] in ("A", "B")
            switched = step["route"] != before
            assert switched == step["changed"]
            focal_switches += int(switched and seat == config["focal"])
            routes[seat] = step["route"]
            excess += 3*(routes.count("A")-4)**2
        assert len(planned) == config["rounds"]-len(initial)
        return excess, 2*excess + focal_switches

    def test_strict_ranking_even_with_unknown_final_and_known_zero_focal_action(self):
        self.allocate(1, -4)
        self.allocate(2, +4, move_at_three=True)
        bundle = self.current()
        self.assertEqual([r["summary"]["first_focal_switch"] for r in bundle["cohort"]],
                         [False, False])
        out = compare_registry(bundle, witnesses=True)
        entry = out["comparisons"][0]
        self.assertEqual(entry["minus4_minus_plus4_bounds"], [Q(3), Q(9)])
        self.assertEqual(entry["ranking"], "minus4_strictly_higher_cost")
        lookup = {g["study"]: g["events"] for g in bundle["cohort"]}
        for which, bound_index in (("lower", 0), ("upper", 1)):
            outcomes = {}
            for amount_label in ("minus4", "plus4"):
                paths = entry["endpoint_witnesses"][which][amount_label]
                vals = [self.independent_replay(lookup[p["group"]], p["path"])[0]
                        for p in paths]
                outcomes[amount_label] = Q(sum(vals), len(vals))
            self.assertEqual(outcomes["minus4"] - outcomes["plus4"],
                             entry["minus4_minus_plus4_bounds"][bound_index])
        total = compare_registry(bundle, metric="half_points")
        self.assertEqual(total["comparisons"][0]["minus4_minus_plus4_bounds"],
                         [Q(6), Q(18)])

    def test_overlap_both_rankings_and_monitoring_refines_to_strict(self):
        self.allocate(1, -4)
        self.allocate(2, +4)
        before = compare_registry(self.current())["comparisons"][0]
        self.assertEqual(before["minus4_minus_plus4_bounds"], [Q(-3), Q(3)])
        self.assertEqual(before["ranking"], "both_strict_cost_rankings_attainable")

        # Observe the actual final no-change action in the minus arm.
        self.advance(1, through=5, final_route="A")
        middle = compare_registry(self.current())["comparisons"][0]
        self.assertEqual(middle["minus4_minus_plus4_bounds"], [Q(0), Q(3)])
        self.assertEqual(middle["ranking"], "minus4_weakly_higher_cost")

        # Observe the plus-arm final correction (A -> B).
        self.advance(2, through=5, final_route="B")
        after = compare_registry(self.current())["comparisons"][0]
        self.assertEqual(after["minus4_minus_plus4_bounds"], [Q(3), Q(3)])
        self.assertEqual(after["ranking"], "minus4_strictly_higher_cost")
        for earlier, later in ((before, middle), (middle, after)):
            self.assertGreaterEqual(later["minus4_minus_plus4_bounds"][0],
                                    earlier["minus4_minus_plus4_bounds"][0])
            self.assertLessEqual(later["minus4_minus_plus4_bounds"][1],
                                 earlier["minus4_minus_plus4_bounds"][1])

    def test_preassignment_group_is_not_given_a_sign(self):
        self.allocate(1, -4)
        self.allocate(2, +4)
        self.allocate(3, -4, through=1)
        result = compare_registry(self.current())
        self.assertEqual((result["allocated"], result["assigned"]), (3, 2))
        self.assertEqual(result["before_assignment"][0]["count"], 1)
        self.assertEqual(len(result["comparisons"]), 1)

    def test_strict_and_weak_boundaries_are_not_confused(self):
        cases = [
            ((Q(-4), Q(-2)), "minus4_strictly_lower_cost"),
            ((Q(2), Q(4)), "minus4_strictly_higher_cost"),
            ((Q(0), Q(0)), "identical_cost"),
            ((Q(-2), Q(0)), "minus4_weakly_lower_cost"),
            ((Q(0), Q(2)), "minus4_weakly_higher_cost"),
            ((Q(-2), Q(2)), "both_strict_cost_rankings_attainable"),
        ]
        for bounds, label in cases:
            self.assertEqual(classification(*bounds), label)
        with self.assertRaises(ValueError):
            classification(2, 1)

    def test_rejects_invalid_metric_and_duplicated_allocation(self):
        self.allocate(1, -4)
        self.allocate(2, +4)
        with self.assertRaisesRegex(ValueError, "unknown welfare metric"):
            compare_registry(self.current(), metric="revenue")
        bundle = self.current()
        bundle["cohort"].append(bundle["cohort"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            compare_registry(bundle)


if __name__ == "__main__":
    unittest.main()
