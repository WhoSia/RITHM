from fractions import Fraction as Q
from itertools import product
import unittest

from r48.r48_credit import Pulse, run, scenario
from r50.r50_delay import exact_signed_comparison, first_opportunity


class ExactDelayTests(unittest.TestCase):
    def test_partitions_each_cumulative_measure(self):
        rows = run(*scenario(5, "shared", True), Pulse(adjustment=Q(-4)))
        bins = first_opportunity(rows)
        self.assertEqual(sum(b["opportunity"] for b in bins), rows[-1]["revised_after_pulse"])
        self.assertEqual(sum(b["switched"] for b in bins), rows[-1]["switched_at_first_revision_by_round"])
        self.assertEqual(bins[0]["rate"], Q(23, 24))

    def test_cutoff_and_horizon_identity(self):
        for start in (4, 5):
            data = exact_signed_comparison(start)
            self.assertEqual([b["minus4_minus_plus4"] for b in data["lag"]],
                             [1, 1, 1] + [0] * 35)
            numerator = 1-Q(5, 6)**3
            for h in (5, 10, 40):
                self.assertEqual(data["horizon"][h]["difference_given_opportunity"],
                                 numerator / (1-Q(5, 6)**(h-2)))
                self.assertEqual(data["horizon"][h]["difference_in_observed_switches_per_assigned_group"],
                                 numerator)

    def test_cutoff_with_two_eligible_seats(self):
        for start, decay in product((4, 5), ("independent", "shared")):
            data = exact_signed_comparison(start, True, decay)
            self.assertTrue(all(b["minus4_minus_plus4"] == 0 for b in data["lag"][3:]))
            self.assertGreater(data["horizon"][3]["difference_given_opportunity"],
                               data["horizon"][10]["difference_given_opportunity"])

    def test_reward_decay_is_an_assumption_of_the_cutoff(self):
        for retention, length in ((Q(1, 4), 1), (Q(9, 10), 7), (Q(1), 38)):
            data = exact_signed_comparison(5, reward_retention=retention)
            self.assertEqual([t["minus4_minus_plus4"] for t in data["lag"]],
                             [1] * length + [0] * (38 - length))

    def test_rejects_nonphysical_cumulative_values(self):
        rows = [{"round": 3, "revised_after_pulse": Q(1, 6),
                 "switched_at_first_revision_by_round": Q(1, 4)}]
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            first_opportunity(rows)


if __name__ == "__main__":
    unittest.main()
