import unittest
from fractions import Fraction as F
from r66_t8_policy_dominance import interval_difference,robust_order,add_switch_resource_fee
class PolicyDominanceTests(unittest.TestCase):
    def test_strict_a_lower(self):self.assertEqual(robust_order((1,2),(3,4)),'A_STRICTLY_LOWER')
    def test_strict_b_lower(self):self.assertEqual(robust_order((3,4),(1,2)),'B_STRICTLY_LOWER')
    def test_overlapping_unidentified(self):self.assertEqual(robust_order((1,4),(3,6)),'UNIDENTIFIED')
    def test_equal_point(self):self.assertEqual(robust_order((3,3),(3,3)),'EQUAL_POINT')
    def test_difference_interval(self):self.assertEqual(interval_difference((1,3),(2,5)),(-4,1))
    def test_fee_shift_does_not_change_width(self):
        x=add_switch_resource_fee((F(43,2),F(47,2)),F(1,2),F(2,3))
        self.assertEqual(x[1]-x[0],2)
        self.assertEqual(x[0]-F(43,2),F(8,3))
    def test_bad_fee(self):
        with self.assertRaises(ValueError):add_switch_resource_fee((0,1),F(1,2),-1)
