import unittest

from r42_correction_diagnostics import first_block, outcomes


class CorrectionDiagnostics(unittest.TestCase):
    def test_cost_ledger(self):
        for n in (3, 5):
            for live in (False, True):
                row = first_block(n, 1.5, .5, live)
                groups = row["final_occupancy_classes"]
                self.assertAlmostEqual(sum(g["probability"] for g in groups.values()), 1)
                self.assertAlmostEqual(sum(g["weighted_cost"] for g in groups.values()), row["end_excess"])
                self.assertAlmostEqual(sum(row["first_target_turn_counts_probability"]), 1)
                self.assertAlmostEqual(1-row["first_target_turn_counts_probability"][0],
                                       row["hit_then_lost"]+groups["target"]["probability"])

    def test_crossing_depends_on_start_side(self):
        distribution = [.1, 0, 0, 0, .5, .4, 0]
        self.assertAlmostEqual(outcomes(3, distribution)["past_target"]["probability"], .4)
        self.assertAlmostEqual(outcomes(5, distribution)["past_target"]["probability"], .1)
