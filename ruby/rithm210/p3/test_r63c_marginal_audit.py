"""Source-free exact rational bounds and analyst-oracle information gates."""
import json, tempfile
from fractions import Fraction as F
from pathlib import Path
import math,unittest
from r63c_marginal_audit import (frechet_all_stay_bounds,rational_sharp_coupling,
    apply_oracle_delta,score_group)

class MarginalSupportTest(unittest.TestCase):
    def test_disjoint_switch_lower_endpoint(self):
        ps=[F(1,12)]*6
        v=rational_sharp_coupling(ps,kind='lower')
        self.assertEqual(v['all_zero'],F(1,2))
        self.assertLessEqual(v['joint_masks'],64)

    def test_nested_switch_upper_endpoint(self):
        ps=[F(1,10),F(1,5),F(2,5),F(1,2),F(1,4),F(1,3)]
        v=rational_sharp_coupling(ps,kind='upper')
        self.assertEqual(v['all_zero'],F(1,2))
        self.assertEqual(v['marginals'],tuple(ps))

    def test_covered_union_zero_lower_endpoint(self):
        ps=[F(1,5)]*6
        v=rational_sharp_coupling(ps,kind='lower')
        self.assertEqual(v['all_zero'],0)

    def test_zero_and_full_probabilities_are_valid(self):
        p=[F(1),F(0),F(0),F(0),F(0),F(0)]
        for kind in ('upper','lower'):
            self.assertEqual(rational_sharp_coupling(p,kind=kind)['all_zero'],0)
        zeros=[F(0)]*6
        self.assertEqual(rational_sharp_coupling(zeros,kind='upper')['all_zero'],1)

    def test_invalid_rational_marginals_rejected(self):
        with self.assertRaises(ValueError):rational_sharp_coupling([F(1,2)]*5,kind='upper')
        with self.assertRaises(ValueError):rational_sharp_coupling([F(2)]*6,kind='lower')
        with self.assertRaises(ValueError):frechet_all_stay_bounds([1.5,.2])

    def test_independent_law_lies_between_sharp_bounds(self):
        ps=[.03,.08,.15,.22,.4,.1]
        lower,upper=frechet_all_stay_bounds(ps)
        independent=math.prod(1-p for p in ps)
        self.assertLessEqual(lower,independent)
        self.assertLessEqual(independent,upper)

    def test_analyst_delta_shifts_marginal_without_hidden_input(self):
        self.assertAlmostEqual(apply_oracle_delta(.5,0),.5)
        self.assertLess(apply_oracle_delta(.5,-.2),.5)
        with self.assertRaises(ValueError):apply_oracle_delta(1.,.1)

    def test_joint_probability_uses_group_counts_not_actor_label(self):
        g=[{'flip':0,'previous_route':int(i<4)} for i in range(6)]
        ps=[.1,.2,.3,.4,.5,.6]
        x=score_group(g,ps)
        self.assertAlmostEqual(x['p0'],math.prod(1-p for p in ps))
        self.assertEqual(x['zero'],1)
        self.assertAlmostEqual(x['gross_predict'],sum(ps))
        self.assertEqual(x['gross_observed'],0)

if __name__=='__main__':unittest.main()
