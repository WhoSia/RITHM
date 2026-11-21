import unittest
from fractions import Fraction as F
from r66_marginal_equivalence import (social_excess,exact_joint_moments,
    joint_independent,joint_common_update,mix_revision_clock,analytic_one_direction_delta,demo)

class TestR66ExactBridge(unittest.TestCase):
    def test_costs_original_six_routes(self):
        self.assertEqual([social_excess(i) for i in range(7)],[48,27,12,3,0,3,12])
    def test_identical_switch_marginals_but_different_social_loss(self):
        p=[F(1,5)]*5+[F(0)]
        a=joint_independent(5,p)
        b=mix_revision_clock(5,[1]*5+[0],{F(0):F(4,5),F(1):F(1,5)})
        self.assertEqual(a['marginals'],b['marginals'])
        self.assertEqual(a['expected_gross_switches'],b['expected_gross_switches'])
        self.assertEqual(a['expected_excess'],F(12,5))
        self.assertEqual(b['expected_excess'],F(12))
        self.assertEqual(b['expected_excess']-a['expected_excess'],F(48,5))
    def test_common_update_margins_and_cost(self):
        b=joint_common_update(5,[1]*5+[0],F(1,5))
        self.assertEqual(b['expected_excess'],12)
        self.assertEqual(b['expected_gross_switches'],1)
    def test_heterogeneous_clock_closed_form(self):
        clock={F(1,10):F(1,2),F(3,10):F(1,2)}
        a=joint_independent(5,[F(1,5)]*5+[F(0)])
        b=mix_revision_clock(5,[1]*5+[0],clock)
        self.assertEqual(b['expected_excess']-a['expected_excess'],F(3,5))
        self.assertEqual(analytic_one_direction_delta(5,3,clock),F(3,5))
    def test_mutual_opposite_switches_can_reduce_congestion(self):
        # n=4 with 4 A and 2 B; actor 0 moves A->B, actor 4 B->A
        p=[F(1,2),0,0,0,F(1,2),0]
        independent=joint_independent(4,p)
        zero=(0,)*6
        both=(1,0,0,0,1,0)
        paired=exact_joint_moments(4,(-1,-1,-1,-1,1,1),{zero:F(1,2),both:F(1,2)})
        self.assertEqual(independent['marginals'],paired['marginals'])
        self.assertEqual(independent['expected_gross_switches'],paired['expected_gross_switches'])
        self.assertEqual(independent['expected_excess'],F(3,2))
        self.assertEqual(paired['expected_excess'],F(0))
    def test_fraction_mixture_extreme_vs_independent(self):
        for r in (F(0),F(1,10),F(1,5),F(1,2),F(1)):
            mix=mix_revision_clock(3,[0]*3+[1]*3,{r:F(1)})
            ind=joint_independent(3,[0]*3+[r]*3)
            self.assertEqual(mix['expected_excess'],ind['expected_excess'])
    def test_invalid_joint_normalization(self):
        with self.assertRaises(ValueError):exact_joint_moments(5,(-1,)*5+(1,),{(0,)*6:F(1,2)})
    def test_invalid_route_map(self):
        with self.assertRaises(ValueError):exact_joint_moments(5,(-1,)*6,{(0,)*6:F(1)})
    def test_uncertain_clock_distribution_rejected(self):
        with self.assertRaises(ValueError):mix_revision_clock(5,[1]*5+[0],{F(1,5):F(1,2)})
    def test_demo_contract(self):
        self.assertEqual(demo()['gap'],'48/5')

if __name__=='__main__':unittest.main()
