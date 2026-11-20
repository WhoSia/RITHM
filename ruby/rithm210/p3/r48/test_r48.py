from fractions import Fraction as Q
import unittest

from r47.r47_withdrawal import evaluate
from r48.r48_credit import Pulse, run, scenario
from r48.r48_results import results


class PayoffCreditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = results()
        cls.paths = cls.results["paths"]

    def test_credit_is_for_the_route_experienced_before_the_feedback(self):
        p = Pulse(adjustment=Q(4))
        self.assertEqual(p.update(Q(0), 1, True), 0)
        self.assertEqual(p.update(Q(0), 2, True), 2)
        self.assertEqual(p.update(Q(0), 2, False), -2)
        self.assertEqual(p.update(Q(-2), 3, True), Q(-3, 2))

    def test_no_payout_effect_on_any_earlier_or_same_round_action(self):
        for start in (4, 5):
            pos, neg = [run(*scenario(start), Pulse(adjustment=Q(sign*4)), horizon=3)
                        for sign in (1, -1)]
            self.assertEqual(pos[:2], neg[:2])
            self.assertEqual(pos[1]["revised_after_pulse"], 0)
            self.assertIsNone(pos[1]["switch_given_first_revision"])

    def test_wallet_frame_reproduces_original_model_at_every_round(self):
        for start in (4, 5):
            for decay in ("independent", "shared"):
                design, routes, memory, focal = scenario(start, decay, two=True)
                baseline = evaluate(design, routes, memory, 40)
                for sign in (+1, -1):
                    wallet = run(design, routes, memory, focal,
                                 Pulse(adjustment=Q(sign*4), route_credit=Q(0)))
                    for reference, row in zip(baseline, wallet, strict=True):
                        self.assertEqual({k: row[k] for k in reference}, reference)

    def test_first_revision_denominator_is_exogenous(self):
        for rows in self.paths.values():
            for row in rows:
                clocks = row["round"] - 2
                self.assertEqual(row["revised_after_pulse"], 1 - Q(5, 6)**clocks)
                if clocks:
                    self.assertEqual(row["switch_given_first_revision"] *
                                     row["revised_after_pulse"],
                                     row["switched_at_first_revision_by_round"])

    def test_same_behavioral_sign_has_opposite_welfare_sign(self):
        for start, direction in ((4, 1), (5, -1)):
            pos, neg = [self.paths[f"{start}_one_independent_route_{sign}1"] for sign in ("+", "-")]
            self.assertEqual(neg[1]["switch_given_first_revision"], 1)
            self.assertEqual(pos[1]["switch_given_first_revision"], 0)
            self.assertGreater(direction * (neg[-1]["congestion"] - pos[-1]["congestion"]), 0)
            cost_pos = pos[-1]["congestion"] + pos[-1]["resource"]
            cost_neg = neg[-1]["congestion"] + neg[-1]["resource"]
            self.assertGreater(direction * (cost_neg - cost_pos), 0)

    def test_strict_choice_threshold(self):
        for start, at_boundary in ((4, Q(139, 288)), (5, Q(19, 48))):
            key = "first_opportunity_switch_minus_vs_plus_at_3"
            doses = self.results["dose_response"]
            self.assertEqual(doses[f"{start}_1"][key], 0)
            self.assertEqual(doses[f"{start}_2"][key], at_boundary)
            self.assertEqual(doses[f"{start}_9/4"][key], 1)

    def test_imperfect_wallet_control_attenuates_frame_interaction(self):
        first = self.results["wallet_credit_sensitivity"]
        for start in (4, 5):
            self.assertEqual(first[f"{start}_0"], 0)
            self.assertEqual(first[f"{start}_1/4"], 0)
            self.assertLess(0, first[f"{start}_1/2"])
            self.assertLess(first[f"{start}_1/2"], 1)
            self.assertEqual(first[f"{start}_3/4"], 1)

    def test_same_near_term_focal_response_need_not_identify_shared_decay(self):
        for start in (4, 5):
            for sign in ("+", "-"):
                independent, shared = [self.paths[f"{start}_two_{d}_route_{sign}1"]
                                       for d in ("independent", "shared")]
                self.assertEqual(independent[1]["switch_given_first_revision"],
                                 shared[1]["switch_given_first_revision"])
                self.assertNotEqual(independent[-1]["congestion"], shared[-1]["congestion"])


if __name__ == "__main__":
    unittest.main()
