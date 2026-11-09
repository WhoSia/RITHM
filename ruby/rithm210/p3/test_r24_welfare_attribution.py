import random
import unittest
from r24_welfare_attribution import decompose,cost,distribution

class TestR24WelfareAttribution(unittest.TestCase):
    def test_exhaustive_64_patterns(self):
        p=[.17,.29,.48,.61,.73,.82]
        previous=[1,1,0,0,1,0]
        for mask in range(64):
            y=[(mask>>i)&1 for i in range(6)]
            r=decompose(y,p,previous)
            self.assertAlmostEqual(r['welfare_error'],
                r['linear']+r['diagonal']+r['same_pair']+r['opposite_pair'],places=9)
            self.assertEqual(cost(sum(y)),r['observed_cost'])
        self.assertEqual(7,len(distribution(p)))

    def test_first_period_pairs_not_given_false_cohort_label(self):
        r=decompose([1,0,1,0,1,0],[.5]*6)
        self.assertEqual(0.,r['same_pair'])
        self.assertEqual(0.,r['opposite_pair'])
        self.assertAlmostEqual(r['welfare_error'],r['linear']+r['diagonal']+r['unknown_pair'])

    def test_negative_controls_conditional_independence_and_common_shock(self):
        p=[.15,.3,.45,.55,.7,.85]
        previous=[1,1,1,0,0,0]
        rng=random.Random(93)
        independent=[]
        for _ in range(20000):
            y=[int(rng.random()<q) for q in p]
            r=decompose(y,p,previous)
            independent.append(r['same_pair']+r['opposite_pair'])
        self.assertLess(abs(sum(independent)/len(independent)),.15)
        rng=random.Random(99)
        shock=[]
        for _ in range(3000):
            y=[int(rng.random()<.5)]*6
            r=decompose(y,[.5]*6,previous)
            shock.append(r['same_pair']+r['opposite_pair'])
        self.assertGreater(sum(shock)/len(shock),10.)

    def test_independent_but_miscalibrated_actors_produce_pair_residuals(self):
        # Even fully independent true choices can generate nonzero cross
        # residuals if the fitted individual probabilities are wrong.
        true_p = [.7]*6
        fitted_p = [.5]*6
        previous = [1,1,1,0,0,0]
        mean_pair = 0.
        for mask in range(64):
            y = [(mask>>i)&1 for i in range(6)]
            weight = 1.
            for choice,p in zip(y,true_p):
                weight *= p if choice else (1-p)
            row = decompose(y,fitted_p,previous)
            mean_pair += weight*(row['same_pair']+row['opposite_pair'])
        # 6*C(6,2)*(.7-.5)^2 = 3.6, WITHOUT ANY peer dependence.
        self.assertAlmostEqual(3.6,mean_pair,places=10)

    def test_reject_invalid_probabilities_and_actors(self):
        with self.assertRaises(ValueError):decompose([1]*5,[.5]*6)
        with self.assertRaises(ValueError):decompose([1]*6,[.5]*5)
        with self.assertRaises(ValueError):decompose([1]*6,[.5]*6,[1]*5)
        with self.assertRaises(ValueError):decompose([1]*6,[float('nan')]*6)

if __name__=='__main__':
    unittest.main()
