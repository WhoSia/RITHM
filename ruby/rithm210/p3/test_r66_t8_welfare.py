import unittest
from fractions import Fraction as F
from r66_t8_welfare import stage_excess,recovery_excess,resource_fees,expected_law,factorial_moment,exact_recovery_from_moments

class WelfareTests(unittest.TestCase):
    def test_stage(self):self.assertEqual([stage_excess(k) for k in range(5)],[0,3,12,27,48])
    def test_recovery(self):self.assertEqual([recovery_excess(k) for k in range(5)],[0,3,15,42,90])
    def test_expected_switch_fee(self):self.assertEqual(resource_fees(3,F(2,3)),4)
    def test_point_mass(self):self.assertEqual(expected_law([2,3],[F(1,4),F(3,4)]),F(11,4))
    def test_factorial_moments(self):
        q=(F(1,16),F(4,16),F(6,16),F(4,16),F(1,16))
        self.assertEqual(factorial_moment(q,1),F(1,2))
        self.assertEqual(factorial_moment(q,2),F(1,4))
        self.assertEqual(factorial_moment(q,3),F(1,8))
    def test_recovery_polynomial(self):
        for k in range(5):
            q=tuple(F(int(i==k)) for i in range(5))
            self.assertEqual(exact_recovery_from_moments(*[factorial_moment(q,d) for d in (1,2,3)]),recovery_excess(k))
    def test_reject_bad_probability(self):
        with self.assertRaises(ValueError):expected_law([1,2],[F(2,3),F(2,3)])
    def test_reject_negative_fee(self):
        with self.assertRaises(ValueError):resource_fees(2,-1)
