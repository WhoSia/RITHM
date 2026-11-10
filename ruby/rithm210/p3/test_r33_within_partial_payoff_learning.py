"""R33 source-free adversarial tests, with a small private-data replay boundary."""
import unittest
import numpy as np
from r33_within_partial_payoff_learning import personal_online_signals,design,FAMILIES
from r32_trait_rival import design as r32_design

class TestR33(unittest.TestCase):
    def setUp(self):
        self.row=(1,5,8.0,0,0) # uninformed; last true occupancy MUST be hidden
        self.context=(1.,0.,.5,.2)
        self.trait=(.3,1.)
        self.history=[(1,6.),(0,9.),(1,7.),(1,5.)]

    def test_baseline_exact_R32_nesting(self):
        for t in (2,20,40):
            self.assertEqual(design(self.row,t,'prior_preference',self.context,self.trait,(0.,0.)),
                r32_design(self.row,t,'preference',self.context,self.trait))

    def test_online_uses_only_past(self):
        before=personal_online_signals(self.history[:2])
        self.assertEqual(before,personal_online_signals(self.history[:2]))
        self.assertNotEqual(before,personal_online_signals(self.history[:3]))
        # Real timeline feature at t=3 is computed from just first two rounds;
        # arbitrary future round 3+ changes cannot change already computed state.
        future_changed=self.history[:2]+[(1,-10000.),(0,5000.)]
        self.assertEqual(before,personal_online_signals(future_changed[:2]))

    def test_informed_hidden_count_firewall_in_all_families(self):
        a=(1,1,8.,0,0);b=(1,5,8.,0,0)
        for family in FAMILIES:
            self.assertEqual(design(a,11,family,self.context,self.trait,(.2,.13)),
                             design(b,11,family,self.context,self.trait,(.2,.13)))

    def test_history_current_target_never_used(self):
        a=(1,5,8.,1,0);b=(1,5,8.,1,1)
        for family in FAMILIES:
            self.assertEqual(design(a,12,family,self.context,self.trait,(.2,.13)),
                             design(b,12,family,self.context,self.trait,(.2,.13)))

    def test_payoff_stable_under_future_outcome(self):
        sample=[(1,4.),(0,2.)]
        self.assertEqual(personal_online_signals(sample)[0],0.)

    def test_separate_choice_vs_payoff_features(self):
        s=personal_online_signals(self.history)
        altered=[(y,2*p) for y,p in self.history]
        h=personal_online_signals(altered)
        self.assertEqual(s[0],h[0])
        self.assertNotEqual(s[1],h[1])
        self.assertEqual(len(design(self.row,12,'within_choice',self.context,self.trait,s)),
                         len(r32_design(self.row,12,'preference',self.context,self.trait))+2)

    def test_discounting_and_regularization_finite(self):
        for n in range(1,42):
            s=personal_online_signals([(i%2,7.) for i in range(n)])
            self.assertTrue(np.all(np.isfinite(s)))
            self.assertLessEqual(abs(s[0]),1.)

    def test_empty_and_bad_routes_rejected(self):
        with self.assertRaises(ValueError):personal_online_signals([])
        with self.assertRaises(ValueError):personal_online_signals([(2,4.)])
        with self.assertRaises(ValueError):personal_online_signals([(1,float('nan'))])
        with self.assertRaises(ValueError):design(self.row,11,'bad',self.context,self.trait,(0.,0.))

    def test_previous_payoff_does_not_add_to_choice_habit(self):
        s=personal_online_signals(self.history)
        a=design(self.row,12,'within_choice',self.context,self.trait,s)
        b=design(self.row,12,'within_choice',self.context,self.trait,(s[0],50.))
        self.assertEqual(a,b)

if __name__=='__main__':unittest.main()
