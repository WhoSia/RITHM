from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import tempfile
import unittest

from r49_store import Ledger
from r50_analyze import summarize_exports
from test_r49 import FixedDraws


class LogAnalysisTests(unittest.TestCase):
    def trace(self, amount, clock, switch, key, frame="route"):
        temp = self.enterContext(tempfile.TemporaryDirectory())
        draws = FixedDraws(frame=frame, amount=amount)
        draws.clock = iter(clock)
        ledger = Ledger(Path(temp) / "study.db", draws)
        study = f"{key:032x}"
        ledger.allocate(study, 5, len(clock))
        while (view := ledger.view(study))["phase"] != "complete":
            t, seat = view["round"], view["seat"]
            if view["phase"] == "handoff":
                ledger.action(study, "open", t, seat=seat)
            elif view["phase"] == "choice":
                route = "B" if switch and seat == 0 and t > 2 else view["previous"]
                ledger.action(study, "choose", t, seat=seat, route=route)
            else:
                ticket = ledger.action(study, "issue", t, seat=seat)
                ledger.action(study, "ack", t, seat=seat, receipt=ticket["receipt"])
        return ledger.export(study)

    def test_separates_censoring_and_no_switch_with_matched_lag_support(self):
        exports = [
            self.trace(-4, (0, 1, 0, 2, 3), True, 1),
            self.trace(-4, (0, 1, 2, 0, 3), False, 2),
            self.trace(-4, (0, 1, 2, 3, 4), False, 3),
            self.trace(4, (0, 1, 0, 2, 3), False, 4),
        ]
        result = summarize_exports(exports)
        low, high = result["cells"]
        self.assertEqual((low["observed"], low["no_opportunity"]), (2, 1))
        self.assertEqual(low["switch_rate_given_opportunity"], Q(1, 2))
        self.assertEqual(low["observed_first_switches_per_assigned_group"], Q(1, 3))
        self.assertEqual(high["by_lag"][2]["switch_rate"], None)
        contrast = result["lag_contrasts"][0]["minus4_minus_plus4"]
        self.assertEqual(contrast[1]["rate_difference"], 1)
        self.assertIsNone(contrast[2]["rate_difference"])

    def test_rejects_duplicate_trace_and_forged_outcome(self):
        export = self.trace(-4, (0, 1, 0, 2, 3), True, 1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            summarize_exports((export, deepcopy(export)))
        export["outcome"]["first_focal_after_settlement"]["switched"] = False
        with self.assertRaisesRegex(ValueError, "audited choices"):
            summarize_exports((export,))

    def test_frame_interaction_requires_all_four_lag_cells(self):
        clock = (0, 1, 0, 2, 3)
        exports = [
            self.trace(-4, clock, True, 1),
            self.trace(4, clock, False, 2),
            self.trace(-4, clock, False, 3, "wallet"),
            self.trace(4, clock, False, 4, "wallet"),
        ]
        interaction = summarize_exports(exports)["lag_frame_interactions"][0]
        self.assertEqual(interaction["route_minus_wallet_signed_contrast"],
                         {1: Q(1), 2: None, 3: None})

    def test_uses_committed_event_timing(self):
        export = self.trace(-4, (0, 1, 0, 2, 3), True, 1)
        export["events"][7], export["events"][8] = export["events"][8], export["events"][7]
        with self.assertRaisesRegex(ValueError, "settlement_acknowledged"):
            summarize_exports((export,))


if __name__ == "__main__":
    unittest.main()
