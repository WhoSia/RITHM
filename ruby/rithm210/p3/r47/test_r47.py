import unittest
from fractions import Fraction as Q

from r47_withdrawal import Design, benchmarks, checkpoint_selection, decay_distribution, evaluate


class WithdrawalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = benchmarks()

    def test_no_memory_baseline_has_geometric_recovery(self):
        for row in self.rows["correction_no_memory"]:
            t = row["round"]
            self.assertEqual(row["hit_by"], 1 - Q(5, 6)**t)
            self.assertEqual(row["congestion"], 15 * (1 - Q(5, 6)**t))

    def test_delayed_recovery_is_sum_of_two_geometric_waits(self):
        retention, missed = Q(3, 4), Q(5, 6)
        for row in self.rows["correction_memory"]:
            t = row["round"]
            recover = sum(retention**(d-1) * (1-retention) * (1 - missed**(t-d))
                          for d in range(1, t))
            self.assertEqual(row["hit_by"], recover)
            self.assertEqual(row["resource"], recover / 2)

    def test_initially_efficient_arm_has_measurable_exit_without_losing_first_hit(self):
        for row in self.rows["exit_memory"]:
            t = row["round"]
            self.assertEqual(row["hit_by"], 1)
            self.assertEqual(row["left_by"], Q(4, 9) * (1 - Q(5, 8)**t))
        self.assertEqual(self.rows["exit_no_memory"][-1]["congestion"], 0)

    def test_within_round_timing_and_retention_endpoints(self):
        immediate_decay = benchmarks(horizon=3, retention=Q(0))
        never_decay = benchmarks(horizon=3, retention=Q(1))
        self.assertEqual(immediate_decay["correction_memory"][0]["hit_by"], 0)
        self.assertEqual(immediate_decay["correction_memory"][1]["hit_by"], Q(1, 6))
        self.assertEqual(never_decay["correction_memory"][-1]["congestion"], 9)

    def test_shared_and_individual_have_same_marginal_decay(self):
        active, retention = 0b11, Q(3, 4)
        for kind in ("shared", "independent"):
            law = decay_distribution(active, retention, kind)
            self.assertEqual(sum(p for _, p in law), 1)
            for bit in (1, 2):
                self.assertEqual(sum(p for mask, p in law if mask & bit), retention)

    def test_matched_early_cost_paths_separate_on_third_round(self):
        independent, shared = self.rows["two_independent"], self.rows["two_shared"]
        self.assertEqual(independent[:2], shared[:2])
        self.assertEqual(independent[2]["hit_by"] - shared[2]["hit_by"], Q(1, 128))
        self.assertEqual(shared[2]["congestion"] - independent[2]["congestion"], Q(3, 128))

    def test_aggregate_excess_curve_cannot_distinguish_delay_from_exit(self):
        for retention in (Q(0), Q(1, 4), Q(3, 4), Q(9, 10), Q(1)):
            cases = benchmarks(retention=retention)
            delayed, baseline, exit_ = (cases[name] for name in
                                        ("correction_memory", "correction_no_memory", "exit_memory"))
            for d, b, e in zip(delayed, baseline, exit_, strict=True):
                self.assertEqual(d["congestion"] - b["congestion"], e["congestion"])
                self.assertEqual(b["hit_by"] - d["hit_by"], 1 - e["at_target"])
            self.assertLess(delayed[-1]["resource"] - baseline[-1]["resource"],
                            exit_[-1]["resource"])

    def test_checkpoint_matching_can_create_an_effect(self):
        self.assertEqual(checkpoint_selection(), {
            "every_group_difference": Q(0), "natural_checkpoint_difference": Q(1)
        })

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            Design((0,)*6, (0,)*6, Q(2))
        design = Design((0,)*6, (0,)*6, Q(1, 2))
        self.assertEqual(evaluate(design, 0b001111, 0, 0), [])
        with self.assertRaises(ValueError):
            evaluate(design, 64, 0, 1)


if __name__ == "__main__":
    unittest.main()
