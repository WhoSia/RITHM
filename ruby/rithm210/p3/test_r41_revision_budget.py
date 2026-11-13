import unittest

import numpy as np

from r40_default_horizon import transition
from r41_revision_budget import comparison, kernel, same_marginal_example, switch_account, welfare_bounds


class RevisionBudgetTests(unittest.TestCase):
    def test_frozen_equivalence(self):
        for beta, penalty in ((.6, 0), (1.5, .5), (2, 2)):
            frozen, moves = kernel(beta, penalty, False)
            np.testing.assert_allclose(frozen, transition(beta, penalty), atol=1e-14)
            self.assertTrue(np.all((moves >= 0) & (moves <= 6)))

    def test_refreshed_rows(self):
        matrix, _ = kernel(1.5, .5, True)
        np.testing.assert_allclose(matrix.sum(axis=1), 1)
        self.assertTrue(np.all(matrix >= 0))

    def test_cost_account(self):
        for n in range(7):
            for up in range(7-n):
                for down in range(n+1):
                    separate, interaction = switch_account(n, up, down)
                    self.assertEqual(separate+interaction, 3*((n+up-down-4)**2-(n-4)**2))
        self.assertEqual(switch_account(5, 0, 5), (-15, 60))

    def test_lock_in_at_five(self):
        results = comparison(50, 75)["refreshed"]["5"]["39"]
        self.assertAlmostEqual(results["control"]["cost"], 0., places=6)
        self.assertAlmostEqual(results["treatment"]["cost"], 117., places=6)


    def test_identical_marginals_can_span_cost(self):
        cases = same_marginal_example()
        for result in cases.values():
            self.assertAlmostEqual(result["expected_switches"], 1)
        self.assertAlmostEqual(cases["one_uniform_switcher"]["expected_excess"], 0)
        self.assertAlmostEqual(cases["independent"]["expected_excess"], 2.4)
        self.assertAlmostEqual(cases["all_or_none"]["expected_excess"], 12)


    def test_sharp_bounds_against_linear_program(self):
        from itertools import product
        from scipy.optimize import linprog

        states = np.array(list(product((0, 1), repeat=6)))
        cost = 3*(states.sum(axis=1)-4)**2
        constraints = np.vstack((np.ones(len(states)), states.T))
        for p in ((.8,)*5+(0,), (.01, .1, .2, .45, .7, .9), (1,)*6, (0,)*6):
            exact = welfare_bounds(p)
            for key, sign in (("minimum", 1), ("maximum", -1)):
                result = linprog(sign*cost, A_eq=constraints, b_eq=(1, *p))
                self.assertTrue(result.success)
                self.assertAlmostEqual(exact[key], sign*result.fun)

    def test_dynamic_bounds_include_independent_benchmark(self):
        from r41_revision_budget import dynamic_bounds

        bounds = dynamic_bounds(1.5, .5)
        independent = comparison(1.5, .5)["frozen"]
        for h, row in bounds.items():
            for n in (3, 4, 5):
                self.assertLessEqual(row["minimum"][n], independent[str(n)][h]["treatment"]["cost"])
                self.assertGreaterEqual(row["maximum"][n], independent[str(n)][h]["treatment"]["cost"])
