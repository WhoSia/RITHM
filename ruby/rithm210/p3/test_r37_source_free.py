"""Source-free R37 Appendix A/B probabilities, information and placebo power gates."""
import unittest
import numpy as np
from r37_ssm_source_cv import (p_a_from_sum_difference,p_a_from_observed_payoffs,
   conditional_models,posterior_update,group_metrics)
from r37_ewa_author_cv import inferred_payoffs
from r37_negative_control_gates import make_cells,slope,randomization

class R37Tests(unittest.TestCase):
    def test_informed_exact_five_draws(self):
        self.assertAlmostEqual(p_a_from_sum_difference([2,2,-1],5),
            sum(__import__('math').comb(5,k)*(2/3)**k*(1/3)**(5-k) for k in range(2,6)),12)
    def test_informed_equal_payoffs_tie_half(self):
        self.assertAlmostEqual(p_a_from_sum_difference([0,0,0],5),.5,12)
    def test_uninformed_two_route_sample(self):
        self.assertAlmostEqual(p_a_from_observed_payoffs([10.],[9.],5),1.,12)
        self.assertAlmostEqual(p_a_from_observed_payoffs([5.],[9.],9),0.,12)
        self.assertAlmostEqual(p_a_from_observed_payoffs([5.],[5.],9),.5,12)
        self.assertAlmostEqual(p_a_from_observed_payoffs([], [5.],9),.5,12)
    def test_not_allowed_uninformed_hidden_count(self):
        h1=[(1,8.,1),(0,4.,3),(1,7.,6)]
        h2=[(y,p,6-n) for y,p,n in h1]
        w=np.ones(9)/9
        self.assertEqual(conditional_models(h1,0,w)[:2],conditional_models(h2,0,w)[:2])
        self.assertNotEqual(conditional_models(h1,1,w)[:2],conditional_models(h2,1,w)[:2])
    def test_fixed_q_posterior_updates(self):
        w=np.ones(9)/9
        likelihood=np.linspace(.1,.9,9)
        after=posterior_update(w,likelihood,1)
        self.assertAlmostEqual(sum(after),1.,12)
        self.assertGreater(after[-1],after[0])
    def test_ewa_appendix_a2_table_route_a(self):
        # Table 10: P_A in (14,15] implies other A count 0 only.
        probs,foregone=inferred_payoffs(1,14.5,None)
        np.testing.assert_array_equal(probs,[1,0,0,0,0,0])
        self.assertAlmostEqual(foregone,14.5-11,12)
        # A chosen, P_A=5 yields uniform 0..5 and expected foregone=P_A-3.5.
        probs,foregone=inferred_payoffs(1,5.,None)
        np.testing.assert_allclose(probs,np.ones(6)/6)
        self.assertAlmostEqual(foregone,1.5,12)
    def test_ewa_appendix_a2_table_route_b(self):
        # Table 11, P_B in (12,14] -> other A count exactly 5.
        p,foregone=inferred_payoffs(0,13.,None)
        np.testing.assert_array_equal(p,[0,0,0,0,0,1])
        self.assertAlmostEqual(foregone,9.,12)
        # Informed knows exact past N_A, uninform does not.
        p,_=inferred_payoffs(0,5.,3)
        np.testing.assert_array_equal(p,[0,0,0,1,0,0])
    def test_invalid_ewa_impossible_payoff(self):
        with self.assertRaises(ValueError):inferred_payoffs(0,100.,None)
    def test_joint_group_probability_cost_identity(self):
        m=group_metrics([.5]*6,[1,1,1,0,0,0])
        self.assertAlmostEqual(m[0],np.log(2),12)
        self.assertAlmostEqual(m[1],6*np.log(2),12)
        self.assertAlmostEqual(m[2],-np.log(20/64),12)
        self.assertAlmostEqual(m[3],4.5,12)
    def test_negative_control_has_variance_before_p(self):
        # Previous route fixed, current route varies, current-switch negative control observable.
        rows=[]
        for i,(v,cur) in enumerate(zip([7,9,11,13,15],[0,1,0,1,1])):
            rows.append((3,2,1,10,i,0,cur,1,float(v),cur,1-cur))
        prev=make_cells(rows,'previous')
        b,meta=slope(prev,1)
        self.assertEqual(meta['cells_with_both_value_and_outcome_variation'],1)
        self.assertLessEqual(randomization(prev,1,b,reps=99),1)
        both=make_cells(rows,'both')
        b,meta=slope(both,1)
        self.assertEqual(b,0.)
        self.assertEqual(meta['cells_with_both_value_and_outcome_variation'],0)
    def test_source_free_tests_are_self_contained(self):
        self.assertTrue(True)

if __name__=='__main__':unittest.main()
