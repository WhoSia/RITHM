import unittest
from fractions import Fraction as F
from r66_t7_distribution import masks, validate, point_mass, expectation

class TestDistribution(unittest.TestCase):
    def test_state_count(self):
        self.assertEqual(len(masks(6)), 64)
    def test_point_mass(self):
        self.assertEqual(expectation(point_mass((1,0,1)),3,sum),2)
    def test_partial_support_normalizes(self):
        x=validate({(0,0):F(1,2),(1,1):F(1,2)},2)
        self.assertEqual(x[(0,1)],0)
    def test_invalid_mass(self):
        with self.assertRaises(ValueError):validate({(0,):F(2,3)},1)
    def test_negative_mass(self):
        with self.assertRaises(ValueError):validate({(0,):F(2),(1,):-F(1)},1)
    def test_bad_mask(self):
        with self.assertRaises(ValueError):validate({(0,2):F(1)},2)
