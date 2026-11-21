import unittest
from fractions import Fraction as F
from r66_t7_distribution import masks
from r66_t7_moments import moments
from r66_t7_sufficiency import required_order,from_moments,upper_order_contributions

class TestSufficiency(unittest.TestCase):
    def test_one_step_second_order(self):
        vals={s:3*sum(s)**2 for s in masks(3)}
        self.assertEqual(required_order(vals,3),2)
        law={s:F(1,8) for s in masks(3)}
        self.assertEqual(from_moments(vals,3,moments(law,3,2),2),9)
    def test_cubic_requires_three(self):
        vals={s:sum(s)**3 for s in masks(3)}
        self.assertEqual(required_order(vals,3),3)
        with self.assertRaises(ValueError):from_moments(vals,3,{():1},2)
    def test_incompatible_low_moments(self):
        vals={s:sum(s) for s in masks(1)}
        with self.assertRaises(ValueError):
            upper_order_contributions(vals,1,{(0,):1},{(1,):1},1)
