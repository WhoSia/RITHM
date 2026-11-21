import unittest
from fractions import Fraction as F
from r66_t7_distribution import masks
from r66_t7_mobius import coefficients, evaluate, degree

class TestMobius(unittest.TestCase):
    def test_quadratic(self):
        g={s:3*sum(s)**2 for s in masks(4)}
        c=coefficients(g,4)
        self.assertEqual(degree(c),2)
        self.assertEqual(c[(0,1)],6)
        for s in masks(4):self.assertEqual(evaluate(c,s),g[s])
    def test_cubic(self):
        g={s:sum(s)**3 for s in masks(3)}
        c=coefficients(g,3)
        self.assertEqual(c[(0,1,2)],6)
    def test_missing_values(self):
        with self.assertRaises(ValueError):coefficients({(0,0):0},2)
