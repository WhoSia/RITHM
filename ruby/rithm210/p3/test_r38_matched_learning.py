"""Regression checks for the matched forecast and conditional null."""
import itertools
import unittest

import numpy as np

from r38_matched_learning import fit_compact, ridge_edf
from r38_negative_control import permutation_audit


class R38Tests(unittest.TestCase):
    def test_session_weights_are_respected(self):
        x = np.ones((4, 1))
        y = np.array([0, 1, 1, 1])
        weights = np.array([.5, 1/6, 1/6, 1/6])
        np.testing.assert_allclose(fit_compact(x, y, weights), [0.0])

    def test_effective_dimension_accounts_for_penalty(self):
        x = np.array([[1, -1], [1, 1]])
        self.assertAlmostEqual(ridge_edf(x, np.zeros(2), .25), 1.5)

    def test_null_variance_matches_all_permutations(self):
        values = np.array([[6, 0, 0], [10, 0, 1], [14, 1, 1]], float)
        x = values[:, 0] - values[:, 0].mean()
        before = values[:, 1]
        slopes = [np.dot(p, before)/(x @ x) for p in itertools.permutations(x)]
        audit = permutation_audit([((), values)], reps=99)["before"]
        self.assertAlmostEqual(audit["exact_conditional_null_sd"], np.std(slopes))

    def test_degenerate_before_has_no_p_and_matches_after_draws(self):
        values = np.array([[6, 1, 0], [10, 1, 1], [14, 1, 1]], float)
        audit = permutation_audit([((), values)], reps=99)
        self.assertIsNone(audit["before"]["permutation_p"])
        self.assertEqual(audit["after"], audit["after_minus_before"])


if __name__ == "__main__":
    unittest.main()
