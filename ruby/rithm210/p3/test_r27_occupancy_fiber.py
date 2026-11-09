"""Source-free exact checks for R27 occupancy-fiber witness."""
import math
import unittest
from fractions import Fraction
from itertools import product
from r27_occupancy_fiber import (STATES, construct_witness, check_law, marginals,
                                 occupancy, pair_probability, expected_cost,
                                 kl_divergence, audit)


class TestR27OccupancyFiber(unittest.TestCase):
    def setUp(self):
        self.p, self.q = construct_witness()

    def test_64_state_normalization_and_exact_probability(self):
        self.assertEqual(len(STATES), 64)
        check_law(self.p)
        check_law(self.q)
        self.assertEqual(sum(self.q.values()), Fraction(1))
        self.assertEqual(sum(self.p[s] != self.q[s] for s in STATES), 4)
        self.assertEqual(min(self.q.values()), Fraction(1, 128))

    def test_six_exact_marginals_preserved(self):
        self.assertEqual(marginals(self.p), marginals(self.q))
        self.assertEqual(marginals(self.q), (Fraction(1,2),)*6)

    def test_all_seven_occupancy_probabilities_preserved(self):
        self.assertEqual(occupancy(self.p), occupancy(self.q))
        self.assertEqual(occupancy(self.p), tuple(Fraction(math.comb(6,k), 64) for k in range(7)))

    def test_same_congestion_cost_but_different_joint(self):
        self.assertEqual(expected_cost(self.p), Fraction(63,2))
        self.assertEqual(expected_cost(self.p), expected_cost(self.q))
        self.assertEqual(pair_probability(self.q, 0, 1)-pair_probability(self.p, 0, 1), Fraction(1,128))
        self.assertGreater(kl_divergence(self.q, self.p), 0)
        self.assertAlmostEqual(kl_divergence(self.q, self.p), .008175754, places=8)

    def test_all_occupancy_only_cost_functions_invariant(self):
        for cost_per_occupancy in product((0, 1), repeat=7):
            left = sum(self.p[s]*cost_per_occupancy[sum(s)] for s in STATES)
            right = sum(self.q[s]*cost_per_occupancy[sum(s)] for s in STATES)
            self.assertEqual(left, right)

    def test_dynamic_relevance_requires_explicit_transition(self):
        # Actor-pair-dependent future functional, not a fitted traffic policy.
        actor_pair_next_cost_p = sum(prob*(1 if s[0] and s[1] else 0) for s, prob in self.p.items())
        actor_pair_next_cost_q = sum(prob*(1 if s[0] and s[1] else 0) for s, prob in self.q.items())
        self.assertEqual(actor_pair_next_cost_q - actor_pair_next_cost_p, Fraction(1,128))

    def test_invalid_law_rejected(self):
        with self.assertRaises(ValueError): check_law({(0,)*6: Fraction(1)})
        invalid = dict(self.q); invalid[(0,)*6] = Fraction(-1,64)
        with self.assertRaises(ValueError): check_law(invalid)


if __name__ == '__main__':
    unittest.main()
