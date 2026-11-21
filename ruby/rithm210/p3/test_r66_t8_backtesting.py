import unittest
from fractions import Fraction as F
from r66_t8_backtesting import point_identification_from_histogram
class AggregateBacktestingTests(unittest.TestCase):
    def test_binomial_four(self):
        x=point_identification_from_histogram({0:1,1:4,2:6,3:4,4:1})
        self.assertEqual(x['m1'],F(1,2))
        self.assertEqual(x['m2'],F(1,4))
        self.assertEqual(x['observed'],F(45,2))
        self.assertEqual((x['sharp_lower'],x['sharp_upper']),(F(43,2),F(47,2)))
    def test_single_source_early(self):
        x=point_identification_from_histogram({0:2,1:1,2:0,3:0,4:0})
        self.assertEqual(x['n'],3)
        self.assertTrue(x['sharp_lower']<=x['observed']<=x['sharp_upper'])
    def test_non_aggregate_rejected(self):
        with self.assertRaises(ValueError):point_identification_from_histogram({0:1,1:1})
    def test_bad_count_rejected(self):
        with self.assertRaises(ValueError):point_identification_from_histogram({0:-1,1:0,2:0,3:0,4:2})
