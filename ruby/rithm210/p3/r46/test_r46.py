from fractions import Fraction
from itertools import product
import unittest

import numpy as np
from scipy.optimize import linprog

from r46_recommendations import solve


BASELINE = [549 / 755] * 5 + [53 / 151]


def full_profile_cost(start, burden, resource, baseline, public, budget):
    """Independent 64-profile reference with explicit assignment and deviations."""
    profiles = np.array(list(product((0, 1), repeat=6)))
    moves = profiles != (np.arange(6) < start)
    count = profiles.sum(axis=1)
    private_gain = np.where(profiles == 1, 14 - 3 * count[:, None],
                            3 * count[:, None] - 11)
    net_gain = private_gain + np.where(moves, -np.array(burden), burden)
    cost = 3 * (count - 4)**2 + moves @ resource
    rows, rhs = [], []
    for i in range(6):
        for action in (0, 1):
            rows.append(np.r_[-net_gain[:, i] * (profiles[:, i] == action), np.zeros(6)])
            rhs.append(0)
        for sign in (1, -1):
            row = np.r_[sign * profiles[:, i], np.zeros(6)]
            row[64 + i] = -1
            rows.append(row)
            rhs.append(sign * baseline[i])
    rows.append(np.r_[np.zeros(64), np.ones(6)])
    rhs.append(budget)
    bounds = [(0, 0) if public and any(gain < 0) else (0, None) for gain in net_gain]
    result = linprog(np.r_[cost, np.zeros(6)], A_eq=[np.r_[np.ones(64), np.zeros(6)]],
                     b_eq=[1], A_ub=rows, b_ub=rhs, bounds=bounds + [(0, None)] * 6)
    if result.status == 2:
        return None
    if not result.success:
        raise AssertionError(result.message)
    return result.fun


class RecommendationTests(unittest.TestCase):
    def test_one_eligible_actor(self):
        result = solve(5, [1, 2, 2, 2, 2, 1], [1] * 6, BASELINE,
                       public=True, target=4, minimize_change=True)
        self.assertAlmostEqual(result["change"], float(Fraction(1638, 755)))
        self.assertEqual(result["marginals"], [0, 1, 1, 1, 1, 0])
        self.assertAlmostEqual(result["cost"], 1)

    def test_all_eligible_reproduces_r45(self):
        result = solve(5, [1] * 6, [0] * 6, BASELINE,
                       public=True, target=4, minimize_change=True)
        self.assertAlmostEqual(result["change"], 2 / 151)

    def test_target_fails_with_no_eligible_actor(self):
        self.assertIsNone(solve(5, [2] * 5 + [1], [0] * 6, BASELINE,
                                target=4, minimize_change=True))

    def test_resource_accounting_can_reverse_policy_rank(self):
        for resource, expected_cost in (([0] * 6, 0), ([4] * 6, 3)):
            result = solve(5, [1, 2, 2, 2, 2, 1], resource, BASELINE, public=True)
            self.assertAlmostEqual(result["cost"], expected_cost)

    def test_full_profile_comparison(self):
        for start, baseline in ((5, BASELINE), (3, [.7] * 3 + [.4] * 3)):
            for public, budget in product((False, True), (0, .4, 3)):
                with self.subTest(start=start, public=public, budget=budget):
                    burden = [1.1, .9, 1.3, .4, 2.5, 1]
                    resource = [1.8, .2, 1, 3, 2, .4]
                    expected = full_profile_cost(start, burden, resource, baseline, public, budget)
                    compressed = solve(start, burden, resource, baseline, public=public,
                                       max_change=budget)
                    if expected is None:
                        self.assertIsNone(compressed)
                    else:
                        self.assertAlmostEqual(compressed["cost"], expected)

    def test_fixed_marginal_resource_component_is_exact(self):
        burden = [.5] * 6
        costs = [.2, .4, .6, .8, 1, 2]
        common = (5, burden)
        free = solve(*common, [0] * 6, BASELINE, max_change=0)
        charged = solve(*common, costs, BASELINE, max_change=0)
        expected = sum(cost * (1 - p) for cost, p in zip(costs[:5], BASELINE[:5])) + costs[5] * BASELINE[5]
        self.assertAlmostEqual(charged["cost"] - free["cost"], expected)


if __name__ == "__main__":
    unittest.main()
