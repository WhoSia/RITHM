"""Independent formal checks for the source-free quadratic welfare forecast."""
import unittest
from statistics import mean

from r58_author_rivals import macro_cost_moments,flow_law_from_actor_flip
from r58_matched_cv import welfare_mse_at_k,globally_better_mse


class R58WelfareForecast(unittest.TestCase):
    def test_exact_quadratic_identity_without_any_price_assumption(self):
        errors=[(2,-1),(-3,2),(0,4),(1,-2)]
        summary={
            'excess_congestion_mse':mean(c*c for c,g in errors),
            'gross_excess_cross_error':mean(c*g for c,g in errors),
            'gross_mse':mean(g*g for c,g in errors)}
        for k in (0,0.01,1,3,50):
            direct=mean((c+k*g)**2 for c,g in errors)
            self.assertAlmostEqual(welfare_mse_at_k(summary,k),direct,places=11)
        with self.assertRaises(ValueError):welfare_mse_at_k(summary,-1)

    def test_fair_coin_six_seat_occupancy_moments(self):
        # P(A)=1/2 for each of 6; next A count is Binomial(6,1/2).
        # Var(N_A)=1.5; E[(N_A-4)^2]=1.5+(3-4)^2=2.5.
        old=(1,1,1,1,0,0)
        frame=tuple((x,0,4,0) for x in old)
        law=flow_law_from_actor_flip(frame,[.5]*6)
        moments=macro_cost_moments(4,law)
        self.assertAlmostEqual(moments['gross_changes'],3)
        self.assertAlmostEqual(moments['end_period_excess_congestion'],7.5)

    def test_mse_uniform_ranking_on_kappa_halfline(self):
        legal={'excess_congestion_mse':1.0,'gross_excess_cross_error':.4,'gross_mse':.1}
        worse={'excess_congestion_mse':3.0,'gross_excess_cross_error':.9,'gross_mse':.7}
        self.assertTrue(globally_better_mse(legal,worse))
        self.assertFalse(globally_better_mse(worse,legal))
        # Difference = 1-4*k + k*k; it dips below zero at k=2.
        not_uniform={'excess_congestion_mse':2.0,
                     'gross_excess_cross_error':-1.6,'gross_mse':1.1}
        self.assertFalse(globally_better_mse(legal,not_uniform))
        self.assertTrue(welfare_mse_at_k(legal,0)<welfare_mse_at_k(not_uniform,0))
        self.assertTrue(welfare_mse_at_k(legal,2)>welfare_mse_at_k(not_uniform,2))

    def test_nonnegative_boundaries_and_no_midperiod_claim(self):
        same={'excess_congestion_mse':1,'gross_excess_cross_error':0,'gross_mse':1}
        self.assertFalse(globally_better_mse(same,same,strict=True))
        self.assertTrue(globally_better_mse(same,same,strict=False))
        with self.assertRaises(ValueError):macro_cost_moments(-1,{(0,0):1})
        with self.assertRaises(ValueError):macro_cost_moments(4,{(0,0):.2})
        # Two distinct labelled internal swap assignments with identical U,D
        # generate exactly the same *period-end* group cost.
        self.assertEqual(macro_cost_moments(5,{(1,1):1})['end_period_excess_congestion'],3)

if __name__=='__main__':unittest.main()
