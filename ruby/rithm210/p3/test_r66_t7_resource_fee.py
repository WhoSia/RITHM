import unittest
from fractions import Fraction as F
from r66_t7_resource_fee import total_cost,breakeven,rank

class TestResourceFee(unittest.TestCase):
    def test_equal_switch_count_cancels(self):
        self.assertEqual(total_cost(F(45,4),3,7)-total_cost(F(51,4),3,7),-F(3,2))
    def test_breakeven(self):
        a=(F(20),F(3));b=(F(21),F(2))
        self.assertEqual(breakeven(a,b),F(1))
        self.assertEqual(rank(a,b,0),'a')
        self.assertEqual(rank(a,b,2),'b')
    def test_no_intersection(self):self.assertIsNone(breakeven((0,1),(1,1)))
    def test_negative_fee(self):
        with self.assertRaises(ValueError):total_cost(10,3,-1)
