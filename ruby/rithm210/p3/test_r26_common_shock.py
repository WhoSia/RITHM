import math
import random
import unittest
from itertools import product
from r26_common_shock import forecast,candidates,convolve

class TestR26Latent(unittest.TestCase):
    def test_exact_marginal_and_independence_nested(self):
        r=random.Random(20261109)
        for _ in range(200):
            p=[r.uniform(.01,.99) for _ in range(6)]
            prev=[r.randrange(-1,2) for _ in range(6)]
            baseline=forecast(p)
            for family,tau in candidates():
                f=forecast(p,tau,family,prev)
                self.assertTrue(all(abs(a-b)<1e-12 for a,b in zip(f.marginal(),p)))
                self.assertAlmostEqual(sum(f.occupancy),1.,places=10)
                self.assertAlmostEqual(f.expectation_cost()-baseline.expectation_cost(),6*f.covariance_sum(),places=9)
                self.assertTrue(all(0<=q<=1 for q in f.plus+f.minus))
                if tau==0:self.assertEqual(baseline.occupancy,f.occupancy)
    def test_outcome_mixture_and_marginal_brier_invariant(self):
        p=[.2,.3,.4,.6,.7,.8];prev=[1,1,1,0,0,0]
        f=forecast(p,.8,'previous_route_signed',prev)
        base=forecast(p)
        for outcomes in product((0,1),repeat=6):
            a=f.evaluate(outcomes);b=base.evaluate(outcomes)
            self.assertAlmostEqual(a['actor_brier'],b['actor_brier'],places=12)
        self.assertLess(f.covariance_sum(),0)
    def test_common_shock_positive_covariance(self):
        p=[.5]*6
        f=forecast(p,1.,'common')
        self.assertAlmostEqual(22.5,6*f.covariance_sum(),places=12)
        self.assertAlmostEqual(f.occupancy[0],.5)
        self.assertAlmostEqual(f.occupancy[6],.5)
        self.assertAlmostEqual(0, sum(f.occupancy[1:6]),places=12)
    def test_synthetic_independent_select_zero_and_correlated_select_shock(self):
        # Expected proper log score, exact enumeration, no Monte Carlo uncertainty.
        p=[.5]*6
        true_ind=forecast(p)
        true_com=forecast(p,.6,'common')
        grid=candidates()
        # Occupancy-level cross entropy (only seven states, exact).
        def crossentropy(true,model):
            return -sum(a*math.log(max(b,1e-300)) for a,b in zip(true.occupancy,model.occupancy))
        best_ind=min(grid,key=lambda x:crossentropy(true_ind,forecast(p,x[1],x[0],[1]*6)))
        best_com=min(grid,key=lambda x:crossentropy(true_com,forecast(p,x[1],x[0],[1]*6)))
        self.assertEqual(('common',0.0),best_ind)
        self.assertGreater(best_com[1],0)
    def test_invalid(self):
        with self.assertRaises(ValueError):forecast([.5]*5)
        with self.assertRaises(ValueError):forecast([.5]*6,1.2)
        with self.assertRaises(ValueError):forecast([.5]*6,.2,'previous_route_signed')
