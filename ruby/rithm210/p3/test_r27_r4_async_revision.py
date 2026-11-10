"""R27-R4 source-free revision scheduling tests."""
import unittest
from r27_r3_switching_welfare import Params,BITS,transition as r3
from r27_r4_async_revision import Revision,revision_marginals,transition,exact_horizon

class TestAsyncRevision(unittest.TestCase):
    def test_rho_one_exact_r3_nesting(self):
        p=Params(.6,4.,.5,.6)
        for m in range(64):
            for old in range(7):
                a=r3(m,old,p);b=transition(m,old,p,Revision(1.))
                for x,y in zip(a,b):self.assertAlmostEqual(x,y,places=13)

    def test_rho_zero_means_no_switches(self):
        for m in range(64):
            a=transition(m,3,Params(.6,0.),Revision(0.))
            self.assertAlmostEqual(a[m],1.,places=13)
            self.assertAlmostEqual(sum(a),1.,places=13)

    def test_all_448_history_kernels_normalize(self):
        p=Params(.6,2.,.2,.6)
        for m in range(64):
            for old in range(7):
                a=transition(m,old,p,Revision(.3))
                self.assertAlmostEqual(sum(a),1.,places=12)
                self.assertGreaterEqual(min(a),0.)

    def test_shock_preserves_six_individual_marginals(self):
        p=Params(.6,2.,.2,.8)
        for m in range(64):
            for old in range(7):
                ps,_=revision_marginals(m,old,p,Revision(.7))
                law=transition(m,old,p,Revision(.7))
                for i in range(6):
                    self.assertAlmostEqual(sum(law[j] for j in range(64) if BITS[j][i]),ps[i],places=12)

    def test_zero_opportunities_preserves_initial_binomial_cost(self):
        z=exact_horizon(Params(.6,7.25),Revision(0.),40)
        self.assertAlmostEqual(z['mean_switches'],0.)
        self.assertAlmostEqual(z['mean_social_cost'],31.5)

    def test_bounded_adaptive_hazard(self):
        p=Params(.6,1.,.5,.1)
        for m in range(64):
            ps,hs=revision_marginals(m,1,p,Revision(.8,2.,0.))
            self.assertTrue(all(0<=v<=.8 for v in hs))
            self.assertTrue(all(0<=v<=1 for v in ps))

    def test_counterfactual_async_result(self):
        a=exact_horizon(Params(.6,0.),Revision(1.),40)
        b=exact_horizon(Params(.6,0.),Revision(.3,3.,0.),40)
        self.assertAlmostEqual(a['mean_social_cost'],47.559293738,places=6)
        self.assertAlmostEqual(b['mean_social_cost'],24.250374,places=5)
        self.assertLess(b['mean_social_cost'],a['mean_social_cost'])

    def test_invalid_parameters(self):
        for args in [(-1.,0.,0.),(2.,0.,0.),(.5,-1.,0.)]:
            with self.assertRaises(ValueError):Revision(*args)
        with self.assertRaises(ValueError):exact_horizon(Params(.6,0.),Revision(1.),0)

if __name__=='__main__':unittest.main()
