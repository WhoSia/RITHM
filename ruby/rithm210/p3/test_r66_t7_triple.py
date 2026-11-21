import unittest
from fractions import Fraction as F
from r66_t7_triple import triple_interval,law_from_triple
from r66_t7_moments import moments

class TestTriple(unittest.TestCase):
    def test_parity_sharp_interval(self):
        x=(F(1,2),)*3+(F(1,4),)*3
        self.assertEqual(triple_interval(*x),(0,F(1,4)))
        for t in (0,F(1,4)):
            m=moments(law_from_triple(*x,t),3,3)
            self.assertEqual(m[(0,1,2)],t)
    def test_infeasible_triple(self):
        with self.assertRaises(ValueError):
            triple_interval(0,0,0,1,1,1)
    def test_outside_interval_rejected(self):
        with self.assertRaises(ValueError):
            law_from_triple(F(1,2),F(1,2),F(1,2),F(1,4),F(1,4),F(1,4),F(1,3))
