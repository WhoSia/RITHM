import unittest
from fractions import Fraction as F
from r66_t7_bounds import sharp_interval
from r66_t7_moments import moments
from r66_t7_parity import law
from r66_t7_recovery import values

class TestSharpBounds(unittest.TestCase):
    def test_three_actor_parity_extrema(self):
        known=moments(law(3,0),3,2)
        a,b=sharp_interval(values(3),3,known)
        self.assertEqual((a.value,b.value),(F(45,4),F(51,4)))
        self.assertEqual(a.direction,'min')
        self.assertEqual(b.direction,'max')
    def test_one_period_pairwise_point_identification(self):
        known=moments(law(3,0),3,2)
        a,b=sharp_interval(values(3,horizon=1),3,known)
        self.assertEqual(a.value,b.value)
        self.assertEqual(a.value,9)
    def test_infeasible_constraints(self):
        with self.assertRaises(ValueError):
            sharp_interval(values(2),2,{():1,(0,):2})
