"""R29 exact Poisson-binomial expected congestion identity tests."""
import unittest
from r29_welfare_components import components

class TestR29Welfare(unittest.TestCase):
    def test_symmetric_poisson_binomial_cost(self):
        z=components([.5]*6)
        self.assertAlmostEqual(z['occupancy_mean'],3)
        self.assertAlmostEqual(z['occupancy_variance'],1.5)
        self.assertAlmostEqual(z['expected_congestion'],31.5)
    def test_deterministic_optimum(self):
        z=components([1]*4+[0]*2)
        self.assertEqual(z['expected_congestion'],24)
        self.assertEqual(z['occupancy_variance'],0)
    def test_extreme_unanimity(self):
        self.assertEqual(components([1]*6)['expected_congestion'],36)
        self.assertEqual(components([0]*6)['expected_congestion'],72)
    def test_invalid_vector_rejection(self):
        for v in ([.5]*5,[.5]*7,[.3]*5+[1.2],[-.1]+[.3]*5):
            with self.assertRaises(ValueError):components(v)

if __name__=='__main__':unittest.main()
