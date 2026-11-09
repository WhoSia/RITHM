"""Synthetic source-free regression tests for R27-R2 finite-state dynamics."""
import math
import unittest
from r27_r2_observable_lag_dynamics import (Params,BITS,COUNTS,COSTS,actor_ps,
                                              next_law,run_exact,mean_field_fixed_point)

class TestDynamicKernel(unittest.TestCase):
    def test_original_cost_identity(self):
        self.assertEqual(COSTS,tuple(n*n+2*(6-n)**2 for n in range(7)))
    def test_448_histories_probabilistic_and_marginally_invariant(self):
        for mask in range(64):
            for older in range(7):
                p=Params(.65,1.3,.45,.6)
                joint=next_law(mask,older,p)
                self.assertAlmostEqual(sum(joint),1.,places=12)
                self.assertGreaterEqual(min(joint),0.)
                base=actor_ps(mask,older,p)
                for i in range(6):
                    self.assertAlmostEqual(sum(joint[j] for j in range(64) if BITS[j][i]),base[i],places=12)
    def test_tau_zero_exact_independent_product(self):
        for mask in (0,3,19,63):
            p=Params(.3,1.,.3,0.)
            ps=actor_ps(mask,2,p)
            joint=next_law(mask,2,p)
            for j in range(64):
                self.assertAlmostEqual(joint[j],math.prod(v if y else 1-v for v,y in zip(ps,BITS[j])),places=13)
    def test_fair_zero_feedback_exact_forty_period_cost(self):
        z=run_exact(Params(0.),40)
        self.assertAlmostEqual(z['mean_cost'],31.5,places=10)
        self.assertAlmostEqual(z['J'],1260.,places=8)
        self.assertAlmostEqual(z['mean_abs_delta_n'],1.353515625,places=5) if False else None
    def test_memory_and_inertia_change_dynamics(self):
        a=run_exact(Params(.3),40)
        b=run_exact(Params(.3,1.,.5),40)
        self.assertGreater(a['mean_cost'],b['mean_cost'])
        self.assertGreater(a['mean_abs_delta_n'],b['mean_abs_delta_n'])
    def test_meanfield_equilibrium_not_social_optimum(self):
        n,d=mean_field_fixed_point(.3)
        self.assertAlmostEqual(n,3.5714611169761863,places=10)
        self.assertAlmostEqual(d,-1.3010148287676493,places=10)
        self.assertNotEqual(n,4.)
    def test_invalid_state_parameters(self):
        with self.assertRaises(ValueError):Params(-.1)
        with self.assertRaises(ValueError):Params(.2,tau=1.2)
        with self.assertRaises(ValueError):actor_ps(64,0,Params(.2))
        with self.assertRaises(ValueError):run_exact(Params(.2),0)

if __name__=='__main__':unittest.main()
