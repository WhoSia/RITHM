"""R27-R3 source-free exact six-actor switching-welfare regression."""
import unittest
from r27_r3_switching_welfare import (Params,BITS,COUNTS,COST,private_improvement,
    social_improvement,state_marginals,transition,exact_horizon)

class TestR27R3(unittest.TestCase):
    def test_stage_cost_identity(self):
        self.assertEqual(COST,tuple(n*n+2*(6-n)**2 for n in range(7)))

    def test_private_social_incentive_wedges(self):
        self.assertEqual((private_improvement(3,0),social_improvement(3,0)),(2,3))
        self.assertEqual((private_improvement(5,1),social_improvement(5,1)),(1,3))
        for n in range(7):
            if n<6:
                self.assertEqual(private_improvement(n,0),11-3*n)
                self.assertEqual(social_improvement(n,0),21-6*n)
            if n>0:
                self.assertEqual(private_improvement(n,1),3*n-14)
                self.assertEqual(social_improvement(n,1),6*n-27)

    def test_every_448_state_marginal_preservation(self):
        p=Params(.3,2.,.5,.75)
        for mask in range(64):
            for old in range(7):
                law=transition(mask,old,p)
                ps=state_marginals(mask,old,p)
                self.assertAlmostEqual(sum(law),1.,places=12)
                self.assertGreaterEqual(min(law),0.)
                for i in range(6):
                    self.assertAlmostEqual(sum(law[k] for k in range(64) if BITS[k][i]),ps[i],places=12)

    def test_more_friction_increases_fixed_history_stickiness(self):
        a=state_marginals(7,3,Params(.3,0.))
        b=state_marginals(7,3,Params(.3,2.))
        for i in range(6):
            if BITS[7][i]: self.assertGreater(b[i],a[i])
            else: self.assertLess(b[i],a[i])

    def test_zero_sensitivity_symmetric_initial_cost(self):
        self.assertAlmostEqual(exact_horizon(Params(0,0),40)['mean_social_cost'],31.5,places=9)

    def test_expected_switching_resource_cost_counted_once(self):
        z=exact_horizon(Params(.3,1.),3)
        self.assertAlmostEqual(z['mean_social_cost'],z['mean_congestion']+z['mean_switches'])

    def test_positive_interior_friction_can_reduce_total_cost(self):
        a=exact_horizon(Params(.6,0.),40)
        b=exact_horizon(Params(.6,7.25),40)
        c=exact_horizon(Params(.6,10.),40)
        self.assertGreater(a['mean_social_cost'],b['mean_social_cost'])
        self.assertGreater(c['mean_social_cost'],b['mean_social_cost'])
        self.assertAlmostEqual(a['mean_social_cost'],47.559293738,places=6)
        self.assertAlmostEqual(b['mean_social_cost'],25.458064849,places=6)
        self.assertAlmostEqual(c['mean_social_cost'],26.227599199,places=6)

    def test_invalid_parameters_and_unavailable_switches(self):
        for args in [(-.1,0.),(.3,-1.)]:
            with self.assertRaises(ValueError):Params(*args)
        with self.assertRaises(ValueError):private_improvement(6,0)
        with self.assertRaises(ValueError):private_improvement(0,1)
        with self.assertRaises(ValueError):exact_horizon(Params(.3,1.),0)

if __name__=='__main__':unittest.main()
