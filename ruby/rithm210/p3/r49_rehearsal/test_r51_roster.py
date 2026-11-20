from copy import deepcopy
from fractions import Fraction
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from r49_audit import audit, audit_trace
from r49_store import Ledger
from r51_audit_roster import analyze_roster, classify
from r51_demo import PrescribedDraws, advance, demonstrate
from r51_roster import export_roster, group_ref

KEY = "8"*32


class RosterTests(unittest.TestCase):
    def setUp(self):
        d = self.enterContext(TemporaryDirectory())
        self.path = Path(d) / "r49.sqlite3"

    def ledger(self, clock=(0, 1, 2, 0, 4)):
        ledger = Ledger(self.path, PrescribedDraws(-4, clock))
        ledger.allocate(KEY, 5, 5)
        return ledger

    def snapshot(self):
        return export_roster(self.path)

    def test_roster_preserves_preassignment_and_redacts_session_credentials(self):
        ledger = self.ledger()
        ledger.action(KEY, "open", 1, seat=0)
        result = self.snapshot()
        self.assertEqual(result["groups"][0]["group"], group_ref(KEY))
        self.assertNotIn(KEY, json.dumps(result))
        self.assertEqual(analyze_roster(result)["before_assignment_by_committed_rounds"], {0: 1})

    def test_settlement_prefixes_have_assignment_even_before_ack(self):
        ledger = self.ledger()
        advance(ledger, KEY, 1, False)
        ledger.action(KEY, "open", 2, seat=1)
        ledger.action(KEY, "choose", 2, seat=1, route="A")
        self.assertEqual(classify(self.snapshot()["groups"][0]["events"])["status"], "unresolved")
        ticket = ledger.action(KEY, "issue", 2, seat=0)
        self.assertNotIn(ticket["receipt"], json.dumps(self.snapshot()))
        before = self.snapshot()["groups"][0]["events"]
        self.assertEqual(classify(before)["status"], "unresolved")
        ledger.action(KEY, "ack", 2, seat=0, receipt=ticket["receipt"])
        advance(ledger, KEY, 4, True)
        after = self.snapshot()["groups"][0]["events"]
        self.assertEqual(before, after[:len(before)])
        result = analyze_roster(self.snapshot())["cells"][0]
        self.assertEqual(result["status_by_completion"]["incomplete"]["switched"], 1)
        self.assertEqual(result["full_observation_rate_bounds"], (1, 1))

    def test_no_planned_opportunity_is_known_in_both_complete_and_incomplete_groups(self):
        ledger = self.ledger((0, 1, 2, 3, 4))
        advance(ledger, KEY, 2, False)
        result = analyze_roster(self.snapshot())["cells"][0]
        self.assertEqual(result["status_by_completion"]["incomplete"]["no_scheduled_opportunity"], 1)
        self.assertEqual(result["full_observation_rate_bounds"], (0, 0))
        advance(ledger, KEY, 5, False)
        result = analyze_roster(self.snapshot())["cells"][0]
        self.assertEqual(result["status_by_completion"]["completed"]["no_scheduled_opportunity"], 1)
        self.assertEqual(audit(ledger.export(KEY))["choices"], 5)

    def test_audit_rejects_split_transaction_and_nonprefix(self):
        ledger = self.ledger()
        advance(ledger, KEY, 5, False)
        events = self.snapshot()["groups"][0]["events"]
        with self.assertRaisesRegex(ValueError, "missing settlement_assigned"):
            audit_trace(events[:5], allow_prefix=True)
        with self.assertRaisesRegex(ValueError, "expected"):
            audit_trace(events[:6] + events[7:8], allow_prefix=True)

    def test_unknown_database_and_duplicate_records_are_rejected(self):
        with self.assertRaises(sqlite3.OperationalError):
            self.snapshot()
        self.assertFalse(self.path.exists())
        self.ledger()
        roster = self.snapshot()
        duplicate = deepcopy(roster["groups"][0])
        duplicate["group"] = "a"*64
        roster["groups"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            analyze_roster(roster)

    def test_frozen_prefixes_attain_both_signs_by_actual_rehearsal_completion(self):
        d = self.enterContext(TemporaryDirectory())
        demo = demonstrate(d)
        nominal = demo["frozen_summary"]
        self.assertEqual((nominal["allocated"], nominal["settlement_assigned"]), (14, 12))
        self.assertEqual(nominal["before_assignment_by_committed_rounds"], {0: 1, 1: 1})
        self.assertEqual(demo["complete_case_difference_at_freeze"], 1)
        self.assertEqual(demo["attained_completions"],
                         {"lower": Fraction(-1, 3), "upper": Fraction(1, 3)})


if __name__ == "__main__":
    unittest.main()
