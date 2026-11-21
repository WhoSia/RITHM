import unittest
from fractions import Fraction as F
from math import comb
from r62_exact_fiber import exact_law,exact_expectations,covariance_identity
from r62_collective import pause_distribution,positive_shock_distribution,joint_law,fast_group_proba,FROZEN

class ExactFalsifier(unittest.TestCase):
    def setUp(self):
        self.p=[F(1,4)]*6
        self.old=(1,1,1,1,0,0)

    def test_one_period_marginals_exactly_fixed(self):
        q=F(1,5)
        a,ap=exact_expectations(self.old,exact_law(self.p,0))
        b,bp=exact_expectations(self.old,exact_law(self.p,q))
        self.assertEqual(ap,bp)
        self.assertEqual(ap,self.p)
        self.assertEqual(a['gross'],b['gross'])
        self.assertEqual(a['nA'],b['nA'])
        self.assertGreater(b['p_no_switch'],a['p_no_switch'])

    def test_exact_covariance_welfare_formula(self):
        independent=exact_expectations(self.old,exact_law(self.p,0))[0]['excess']
        paused=exact_expectations(self.old,exact_law(self.p,F(1,5)))[0]['excess']
        self.assertEqual(paused-independent,covariance_identity(self.old,self.p,F(1,5)))
        self.assertEqual(paused-independent,F(-3,32))

    def test_welfare_sign_can_flip_despite_same_marginals(self):
        old=(1,1,1,1,1,0)
        self.assertGreater(covariance_identity(old,self.p,F(1,5)),0)
        self.assertLess(covariance_identity(self.old,self.p,F(1,5)),0)

    def test_inadmissible_zero_and_boundary_input(self):
        with self.assertRaises(ValueError): exact_law(self.p,F(4,5))
        with self.assertRaises(ValueError): exact_law([F(0)]*6,0)
        with self.assertRaises(ValueError): exact_law([F(1,4)]*5,0)

    def test_64_mask_sum_and_marginal_exact(self):
        p=[F(1,7),F(2,7),F(3,7),F(1,6),F(1,2),F(1,8)]
        law=exact_law(p,F(1,4))
        self.assertEqual(len(law),64)
        self.assertEqual(sum(law.values()),1)
        self.assertEqual(exact_expectations(self.old,law)[1],p)

    def test_float_64_mass_poisson_support(self):
        p=[.1,.2,.3,.4,.2,.3]
        for model in FROZEN:
            for q in (.0,.25):
                if model=='common_positive':law=positive_shock_distribution(p,q)
                else:law=pause_distribution(p,q)
                self.assertAlmostEqual(sum(law.values()),1,places=12)
                out=joint_law(self.old,p,law)
                self.assertEqual(set(out),{(u,d) for u in range(3) for d in range(5)})
                for (u,d),v in out.items():
                    self.assertGreaterEqual(v,0)

    def test_64_mask_marginals_hold_for_heterogeneous_ps(self):
        p=[.07,.23,.18,.11,.30,.45]
        for q in (0,.05,.2,.4):
            law=pause_distribution(p,q)
            for i,pi in enumerate(p):
                self.assertAlmostEqual(sum(prob for mask,prob in law.items() if mask&(1<<i)),pi)

    def test_reject_bad_probability_and_unsupported_model(self):
        with self.assertRaises(ValueError): pause_distribution([.2]*5,0)
        with self.assertRaises(ValueError): pause_distribution([0]*6,.1)
        with self.assertRaises(ValueError): pause_distribution([.5]*6,.8)
        with self.assertRaises(ValueError): positive_shock_distribution([.2]*6,1)

if __name__=='__main__':unittest.main()
