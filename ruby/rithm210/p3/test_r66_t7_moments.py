import unittest
from fractions import Fraction as F
from r66_t7_moments import moments, invert_all_moments, subsets
from r66_t7_distribution import masks

class TestMoments(unittest.TestCase):
    def test_dimension(self):self.assertEqual(len(subsets(6,2)),22)
    def test_normalization(self):
        m=moments({(0,0):F(1,3),(1,1):F(2,3)},2,2)
        self.assertEqual(m[()],1)
        self.assertEqual(m[(0,1)],F(2,3))
    def test_full_inversion(self):
        law={s:F(i+1,36) for i,s in enumerate(masks(3))}
        # 1+...+8 = 36.
        self.assertEqual(invert_all_moments(moments(law,3,3),3),law)
    def test_missing_moment_error(self):
        with self.assertRaises(ValueError):invert_all_moments({():1},2)
