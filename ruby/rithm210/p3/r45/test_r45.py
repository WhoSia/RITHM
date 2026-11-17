import json
import unittest
from fractions import Fraction as F
from pathlib import Path

from r45_certificate import CEILINGS, exact_cost, restore_four_at_five, verify
from r45_frontier import problem, publicly_disclosed_feasible, solve
from r45_selten import reinforcement, session, strategy_route
from random import Random


class FrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve()
        fixture = here.with_name("r43_results.json")
        if not fixture.exists():
            fixture = here.parents[2]/"r43_results.json"
        cls.rows = json.loads(fixture.read_text())

    def test_exact_primal_dual_certificates(self):
        for key, row in self.rows.items():
            n = int(key)
            data = problem(n, row["marginals"])
            self.assertTrue(verify(data, n, row["marginals"]))
            for i in range(21):
                burden = CEILINGS[n]*i/20
                self.assertAlmostEqual(solve(data, burden).fun, float(exact_cost(n, burden)))
            self.assertFalse(solve(data, CEILINGS[n]+F(1, 100)).success)
            self.assertIsNone(exact_cost(n, CEILINGS[n]+F(1, 10**12)))

    def test_public_final_count_prevents_obedience_at_original_marginals(self):
        for key, row in self.rows.items():
            data = problem(int(key), row["marginals"])
            for burden in (0, F(9, 10), CEILINGS[int(key)], 2, 4):
                self.assertFalse(publicly_disclosed_feasible(data, burden))

    def test_minimal_marginal_relaxation_at_five(self):
        restored = restore_four_at_five(F(1))
        delta = F(restored["minimum_total_absolute_marginal_change"])
        p = [F(restored["initial_A_probability"])]*5+[F(restored["initial_B_probability"])]
        original = list(map(F, self.rows["5"]["marginals"]))
        self.assertEqual(sum(p), 4)
        self.assertEqual(sum(abs(a-b) for a,b in zip(p, original)), delta)
        self.assertTrue(publicly_disclosed_feasible(problem(5, p), 1))
        with self.assertRaises(ValueError):
            restore_four_at_five(F(101, 100))

    def test_selten_response_and_negative_reward(self):
        rng = Random(1)
        self.assertEqual(strategy_route(2, 0, 1, [1, 2], rng), 1)
        self.assertEqual(strategy_route(3, 0, 1, [1, 2], rng), 0)
        self.assertEqual(strategy_route(3, 0, 2, [1, 2], rng), 1)
        weights = [4, 3, 3, 2]
        reinforcement(weights, 0, -2)
        self.assertEqual(weights, [4, 5, 5, 4])
        reinforcement(weights, 0, 2)
        self.assertEqual(weights, [6, 5, 5, 4])
        self.assertEqual(session(Random(42), 10), session(Random(42), 10))
