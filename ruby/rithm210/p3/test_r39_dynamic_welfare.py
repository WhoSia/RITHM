import glob
import os
import unittest

import numpy as np

from r33_within_partial_payoff_learning import personal_online_signals
from r37_ewa_author_cv import attractions
from r37_ssm_source_cv import p_a_from_observed_payoffs, p_a_from_sum_difference, source_groups
from r39_dynamic_welfare import feedback_step, sampled_choice, signals, simulate, summarize


class DynamicWelfareTest(unittest.TestCase):
    def test_ewa_batch_matches_scalar_source(self):
        path = os.environ.get("RITHM_PRIVATE_CSV") or next(iter(glob.glob("chat_files/*/*.csv")), None)
        if not path:
            self.skipTest("optional SHA-verified author CSV")
        groups = source_groups(path)
        for group in groups:
            sid, _, _, actors, periods = group
            expected = np.asarray([d for d, _ in attractions([group])[sid]])
            a = np.ones((6, 2))
            experience = np.ones(6)
            belief = np.zeros((6, 6))
            predicted = []
            for t in range(1, 40):
                choice, info, payoff, count = np.asarray([periods[t][x] for x in actors]).T
                a, experience, belief = feedback_step(a, experience, belief, choice.astype(bool),
                                                       payoff, info.astype(bool), count[0], t)
                predicted.append(a[:, 1]-a[:, 0])
            np.testing.assert_allclose(predicted, expected, atol=1e-13, rtol=0)

    def test_signals_match_r33(self):
        past = [(1, 5), (0, -2), (1, 10), (0, 6)]
        np.testing.assert_allclose(signals(2, 15, 4, 4), personal_online_signals(past))

    def test_ssm_against_exact_distributions(self):
        # Enumerate all 2^4 sample pairs (q=2), with both tie coin outcomes.
        grid = np.asarray([[int((j >> i) & 1)/2 for i in range(5)] for j in range(32)])
        u = grid[:, :2]
        v = grid[:, 2:4]
        coin = grid[:, 4].astype(bool)
        history = np.tile([1, -2, 0, 0], (32, 1))
        a = np.tile([1, 4, 0, 0], (32, 1))
        b = np.tile([2, 3, 0, 0], (32, 1))
        q = n = np.full(32, 2)
        informed = np.ones(32, dtype=bool)
        result = sampled_choice(history, a, b, n, 2, q, (u, v), informed, coin)
        self.assertAlmostEqual(result.mean(), p_a_from_sum_difference([1, -2], 2))
        result = sampled_choice(history, a, b, n, 4, q, (u, v), ~informed, coin)
        self.assertAlmostEqual(result.mean(), p_a_from_observed_payoffs([1, 4], [2, 3], 2))
        result = sampled_choice(history, a, b, n*0, 4, q, (u, v), ~informed, coin)
        np.testing.assert_array_equal(result, coin)

    def test_cost_identity_and_round_boundaries(self):
        counts = np.full((2, 1, 40), 4)
        counts[..., 0] = 0
        switches = np.zeros((2, 1, 39, 6), dtype=bool)
        info = np.zeros((1, 6), dtype=bool)
        stats, _, _ = summarize(counts, switches, info)
        self.assertEqual(stats["excess_per_round"], 0)
        self.assertEqual(stats["first_round_excess"], 48)
        self.assertEqual(stats["efficient_rate"], 1)

    def test_information_firewall(self):
        # Same received payoff but different hidden count must produce same
        # update for the uninformed actor, while informed feedback changes.
        args = (np.ones((6, 2)), np.ones(6), np.zeros((6, 6)),
                np.ones(6, dtype=bool), np.full(6, 8.0))
        info = np.array([False, True, True, True, True, True])
        a = feedback_step(*args, info, 3, 1)[0]
        b = feedback_step(*args, info, 5, 1)[0]
        np.testing.assert_array_equal(a[0], b[0])
        self.assertFalse(np.array_equal(a[1], b[1]))

    def test_end_to_end_neutral_policy(self):
        draws = np.full((2, 1, 40, 6), .4)
        info = np.array([[1, 1, 1, 0, 0, 0]], dtype=bool)
        initial_choice = np.array([[1, 1, 1, 1, 0, 0]], dtype=bool)
        count, switches, mu, var = simulate("ewa", np.zeros((1, 3)), info, initial_choice,
            np.full((1, 6), 7.), draws, np.full_like(draws, 11.), None, 1, True)
        np.testing.assert_array_equal(count[:, :, 0], 4)
        np.testing.assert_array_equal(count[:, :, 1:], 6)
        np.testing.assert_array_equal(mu[:, :, 1:], 3)
        np.testing.assert_array_equal(var[:, :, 1:], 1.5)
        self.assertEqual(switches.sum(), 4)


if __name__ == "__main__":
    unittest.main()
