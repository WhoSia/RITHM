import unittest
from fractions import Fraction as F
from r66_t8_cluster_bounds import union_hoeffding_radius,ratio_interval
class ClusterCoverageTests(unittest.TestCase):
    def test_radius_increasing_moment_count(self):self.assertLess(union_hoeffding_radius(24,20,1),union_hoeffding_radius(24,20,4))
    def test_radius_decreasing_cluster_count(self):self.assertGreater(union_hoeffding_radius(24,20,2),union_hoeffding_radius(96,20,2))
    def test_empty_denominator_uninformative(self):
        lo,hi,e=ratio_interval([0]*24,[0]*24,bmax=20,num_moments=2)
        self.assertEqual((lo,hi),(0,1))
    def test_binary_output(self):
        lo,hi,e=ratio_interval([0]*24,[20]*24,bmax=20,num_moments=1)
        self.assertEqual(lo,0);self.assertGreaterEqual(hi,0)
    def test_invalid_counts(self):
        with self.assertRaises(ValueError):ratio_interval([3],[2],bmax=20)
    def test_invalid_support(self):
        with self.assertRaises(ValueError):union_hoeffding_radius(0,20,1)
    def test_tight_with_many_clusters(self):
        lo,hi,e=ratio_interval([5]*10000,[10]*10000,bmax=20,num_moments=2)
        self.assertTrue(lo<F(1,2)<hi)
        self.assertLess(float(hi-lo),.10)
    def test_bonferroni_alpha(self):
        self.assertGreater(union_hoeffding_radius(24,20,3,F(1,100)),union_hoeffding_radius(24,20,3,F(1,20)))
