import unittest
from fractions import Fraction as F
from r66_t7_parity import law,triple_shift
from r66_t7_moments import moments

class TestParity(unittest.TestCase):
    def test_kwise_equal(self):
        for n in (3,4,6):
            self.assertEqual(moments(law(n,0),n,n-1),moments(law(n,1),n,n-1))
    def test_triple_difference(self):self.assertEqual(triple_shift(),F(1,4))
    def test_support_count(self):self.assertEqual(len(law(6,0)),32)
    def test_invalid_parity(self):
        with self.assertRaises(ValueError):law(3,2)
