import unittest
from fractions import Fraction as F
from r66_t3_survivor_frailty import (hazard_at_age,decline_identity,
                                        posterior_after_survival,demo)

class FrailtySelectionSynthetic(unittest.TestCase):
    def setUp(self):self.m=((F(1,2),F(1,10)),(F(1,2),F(3,5)))
    def test_first_period_hazard_is_mean_35_percent(self):
        self.assertEqual(hazard_at_age(self.m,1),F(7,20))
    def test_decreasing_mixture_hazard_with_fixed_person_rules(self):
        hs=[hazard_at_age(self.m,k) for k in range(1,20)]
        self.assertTrue(all(a>b for a,b in zip(hs,hs[1:])))
        self.assertTrue(all(h>F(1,10) for h in hs))
    def test_exact_variance_ratio_identity(self):
        for age in (1,2,3,4,8,15):
            self.assertEqual(decline_identity(self.m,age)['exact_identity'],True)
    def test_no_heterogeneity_no_spurious_duration_dependence(self):
        same=((F(1,4),F(1,5)),(F(3,4),F(1,5)))
        for k in range(1,12):
            self.assertEqual(hazard_at_age(same,k),F(1,5))
            self.assertEqual(decline_identity(same,k)['decline'],0)
    def test_posterior_enriches_stable_type(self):
        self.assertEqual(posterior_after_survival(self.m,1),[F(1,2),F(1,2)])
        self.assertGreater(posterior_after_survival(self.m,8)[0],F(9,10))
    def test_reject_invalid_distribution(self):
        with self.assertRaises(ValueError):posterior_after_survival(((F(1,2),F(1,5)),),1)
        with self.assertRaises(ValueError):posterior_after_survival(self.m,0)
        with self.assertRaises(ValueError):posterior_after_survival(((F(1),F(1)),),1)
    def test_demo_only_reports_aggregate_and_not_cognition(self):
        x=demo()
        self.assertEqual(x['observed_hazard_by_age']['1'],'7/20')
        self.assertIn('not fitted',x['research_boundary'])

if __name__=='__main__':unittest.main()
