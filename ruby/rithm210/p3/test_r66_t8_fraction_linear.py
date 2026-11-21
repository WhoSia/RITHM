import unittest
from fractions import Fraction as F
from r66_t8_fraction_linear import solve_square

class ExactLinearTests(unittest.TestCase):
    def test_identity(self):self.assertEqual(solve_square([[1,0],[0,1]],[F(1,3),F(2,5)]),(F(1,3),F(2,5)))
    def test_invertible(self):self.assertEqual(solve_square([[1,1],[1,-1]],[1,0]),(F(1,2),F(1,2)))
    def test_singular(self):self.assertIsNone(solve_square([[1,2],[2,4]],[3,6]))
    def test_pivot_swap(self):self.assertEqual(solve_square([[0,1],[1,0]],[2,3]),(3,2))
    def test_reject_non_square(self):
        with self.assertRaises(ValueError):solve_square([[1,2,3]],[1])
