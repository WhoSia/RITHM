import unittest
from fractions import Fraction as F
from r66_t4_frailty_equivalence import (
    survival, hazard, exact_gap, equivalent_evolving_population
)


class FrailtyEquivalenceTests(unittest.TestCase):
    def setUp(self):
        self.types=((F(1,2),F(1,10)),(F(1,2),F(3,5)))

    def test_age_zero_survival(self):
        self.assertEqual(survival(self.types,0),1)

    def test_mixture_initial_exit_probability(self):
        self.assertEqual(hazard(self.types,0),F(7,20))

    def test_one_period_survivors(self):
        self.assertEqual(survival(self.types,1),F(13,20))

    def test_one_period_survival_hazard(self):
        self.assertEqual(hazard(self.types,1),F(33,130))

    def test_monotone_gap_as_exact_fraction(self):
        self.assertGreater(exact_gap(self.types,0),0)
        for age in range(20):
            self.assertGreater(exact_gap(self.types,age),0)

    def test_constant_hazard_zero_gap(self):
        same=((F(1,4),F(1,5)),(F(3,4),F(1,5)))
        for age in range(15):
            self.assertEqual(exact_gap(same,age),0)

    def test_30_period_survivor_equivalence(self):
        rows=equivalent_evolving_population(self.types,30)
        self.assertEqual(len(rows),30)
        for age,(surv,h,exitprob) in enumerate(rows):
            self.assertEqual(surv,survival(self.types,age))
            self.assertEqual(exitprob,survival(self.types,age)-survival(self.types,age+1))
            self.assertEqual(surv*h,exitprob)

    def test_30_period_total_probability(self):
        rows=equivalent_evolving_population(self.types,30)
        self.assertEqual(sum((r[2] for r in rows),F(0))+survival(self.types,30),1)

    def test_invalid_latent_weights_rejected(self):
        with self.assertRaises(ValueError):
            hazard(((F(1,2),F(1,10)),),0)

    def test_invalid_hazard_rejected(self):
        with self.assertRaises(ValueError):
            hazard(((F(1,2),F(1,10)),(F(1,2),F(7,5))),0)

    def test_invalid_age_rejected(self):
        with self.assertRaises(ValueError):
            survival(self.types,-1)

    def test_invalid_horizon_rejected(self):
        with self.assertRaises(ValueError):
            equivalent_evolving_population(self.types,0)


if __name__=="__main__":
    unittest.main()
