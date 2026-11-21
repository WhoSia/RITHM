import unittest
from fractions import Fraction as F
from r66_t8_triple_identification import triple_range_from_marginal_pair
class TripleIdentificationTests(unittest.TestCase):
    def test_four_fair_actor_width(self):
        x=triple_range_from_marginal_pair(F(1,2),F(1,4))
        self.assertEqual((x['welfare_lower'],x['welfare_upper']),(F(43,2),F(47,2)))
        self.assertEqual(x['width_exact'],2)
        self.assertEqual(x['triple_upper']-x['triple_lower'],F(1,12))
    def test_zero_actors(self):
        x=triple_range_from_marginal_pair(0,0)
        self.assertEqual((x['welfare_lower'],x['welfare_upper']),(0,0))
    def test_three_way_not_needed_for_stage(self):
        x=triple_range_from_marginal_pair(F(1,2),F(1,4))
        self.assertGreater(x['triple_upper'],x['triple_lower'])
