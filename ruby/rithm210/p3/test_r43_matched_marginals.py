import unittest
from fractions import Fraction
from math import ceil, floor

from r43_matched_marginals import rounded_law


class MatchedMarginalsTest(unittest.TestCase):
    def test_mass_marginals_and_balanced_totals(self):
        cases = ((0, 1, 2, 3, 4, 5), (1, 1, 1, 1, 1, 0), (5,)*6, (0,)*6)
        for numerators in cases:
            p = [Fraction(x, 5) for x in numerators]
            law = rounded_law(p)
            self.assertEqual(sum(law.values()), 1)
            self.assertEqual([sum(x[i]*w for x,w in law.items()) for i in range(6)], p)
            self.assertTrue({sum(x) for x in law} <= {floor(sum(p)), ceil(sum(p))})
