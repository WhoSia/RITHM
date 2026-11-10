"""Source-free R27-R5 budget matching and reversal regression."""
import unittest
import numpy as np
from r27_r3_switching_welfare import Params
from r27_r4_async_revision import Revision,exact_horizon
from r27_r5_opportunity_budget import (
    Policy,compile_kernel,evaluate,match_uniform,match_switches)


class TestR27R5(unittest.TestCase):
    def test_448_histories_nonnegative_and_normalized(self):
        for p in (Params(.6,0.),Params(.6,2.,.5,.6)):
            mat,*_=compile_kernel(p,Policy(.3,3.))
            np.testing.assert_allclose(mat.sum(axis=1),np.ones(448),atol=1e-12)
            self.assertGreaterEqual(float(mat.min()),0.)

    def test_r4_source_model_parity(self):
        p=Params(.6,0.)
        for rho,slope in ((.3,0.),(.3,3.),(.1,3.)):
            old=exact_horizon(p,Revision(rho,slope),40)
            new=evaluate(p,Policy(rho,slope),40)
            self.assertAlmostEqual(old['mean_congestion'],new['mean_congestion'],places=8)
            self.assertAlmostEqual(old['mean_switches'],new['mean_actual_switches'],places=8)

    def test_no_review_stays_put(self):
        for friction in (0.,4.):
            z=evaluate(Params(.6,friction),Policy(0.),40)
            self.assertAlmostEqual(z['mean_review_opportunities'],0.)
            self.assertAlmostEqual(z['mean_actual_switches'],0.)
            self.assertAlmostEqual(z['mean_congestion'],31.5)

    def test_opportunity_budget_exactly_matched_not_switch_count(self):
        z=match_uniform(Params(.6,0.),Policy(.3,3.),40)
        self.assertAlmostEqual(z['adaptive']['mean_review_opportunities'],
                               z['matched_uniform']['mean_review_opportunities'],places=8)
        self.assertGreater(abs(z['delta_adaptive_minus_matched']['mean_actual_switches']),.001)
        self.assertAlmostEqual(z['adaptive']['mean_congestion'],24.2503738959,places=7)
        self.assertAlmostEqual(z['matched_uniform']['mean_congestion'],27.5267844544,places=7)

    def test_actual_switches_matched_different_review_budget(self):
        z=match_switches(Params(.6,0.),Policy(.3,3.),40)
        self.assertAlmostEqual(z['adaptive']['mean_actual_switches'],
                               z['matched_uniform']['mean_actual_switches'],places=5)
        self.assertLess(z['adaptive']['mean_congestion'],
                        z['matched_uniform']['mean_congestion'])

    def test_reversal_when_high_opportunity(self):
        a=match_uniform(Params(.6,0.),Policy(1.,3.),40)
        b=match_switches(Params(.6,0.),Policy(1.,3.),40)
        self.assertGreater(a['adaptive']['mean_congestion'],
                           a['matched_uniform']['mean_congestion'])
        self.assertGreater(b['adaptive']['mean_congestion'],
                           b['matched_uniform']['mean_congestion'])
        self.assertAlmostEqual(a['adaptive']['mean_congestion'],43.0779652995,places=7)

    def test_quadratic_drift_not_everywhere_negative(self):
        from r27_r5_opportunity_budget import (
            occupancy_quadratic_drift,PREV_COUNT)
        drift=occupancy_quadratic_drift(Params(.6,0.),Policy(.3,3.))
        self.assertTrue((drift[PREV_COUNT==4]>=0).all())
        self.assertTrue((drift[PREV_COUNT==4]>0).any())
        self.assertTrue((drift[PREV_COUNT==0]<0).all())

    def test_invalid_policies_and_nonadaptive_target(self):
        for v in ((-1.,0.,0.),(1.1,0.,0.),(.3,-1.,0.),(float('nan'),0.,0.)):
            with self.assertRaises(ValueError):Policy(*v)
        with self.assertRaises(ValueError):evaluate(Params(.6,0.),Policy(.3),0)
        with self.assertRaises(ValueError):match_uniform(Params(.6,0.),Policy(.3,0.),40)


if __name__=='__main__':
    unittest.main()
