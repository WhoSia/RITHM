"""RITHM R30: no hidden public count, no future outcome, group law identity."""
import unittest
import numpy as np
from r30_partial_dynamic_joint import design,poisson_binomial,score,FAMILIES,TAUS

class TestR30(unittest.TestCase):
    def test_uninformed_public_count_invariance(self):
        for fam in FAMILIES:
            for y in (0,1):
                for t in (2,21,40):
                    self.assertEqual(design((y,0,5.,0,0),t,fam),
                                     design((y,6,5.,0,1),t,fam))
    def test_informed_public_count_changes_design(self):
        for fam in FAMILIES:
            self.assertNotEqual(design((1,1,5.,1,0),22,fam),
                                design((1,5,5.,1,0),22,fam))
    def test_period_available_and_future_target_excluded(self):
        a=(0,3,4.,1,0);b=(0,3,4.,1,1)
        self.assertEqual(design(a,40,'payoff_public_late'),design(b,40,'payoff_public_late'))
        self.assertEqual(design(a,2,'payoff_public'),design(a,40,'payoff_public'))
        self.assertNotEqual(design(a,2,'payoff_public_late'),design(a,40,'payoff_public_late'))
    def test_probability_and_conditional_mean_preserved(self):
        p=np.array([.14,.25,.31,.55,.73,.86])
        previous=np.array([0,1,0,1,0,1])
        obs=np.array([1,0,1,0,1,0])
        baseline=score(p,previous,obs,0.)
        for tau in TAUS:
            r=score(p,previous,obs,tau)
            self.assertAlmostEqual(r[0],baseline[0],12)
            self.assertAlmostEqual(r[5],r[6]+r[7],11)
            self.assertAlmostEqual(r[4],24+3*((sum(p)-4)**2+r[5]),11)
            d=tau*(2*previous-1)*np.minimum(p,1-p)
            law=(poisson_binomial(p+d)+poisson_binomial(p-d))/2
            self.assertAlmostEqual(float(law.sum()),1.,12)
            self.assertAlmostEqual(float(law@np.arange(7)),sum(p),12)
    def test_invalid_shape_and_tau(self):
        with self.assertRaises(ValueError):
            score([.5]*5,[0]*5,[0]*5,0.)
        with self.assertRaises(ValueError):
            score([.5]*6,[0]*6,[0]*6,2.)
    def test_no_unrecognized_family(self):
        with self.assertRaises(ValueError):
            design((1,4,7.,1,0),20,'current_period_future_cost')
if __name__=='__main__':unittest.main()
