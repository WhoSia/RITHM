"""R65 independent source-free original fitted-Sample-q model tests."""
import unittest
from random import Random
from r65_ssm_fitted import choose,one_game,simulate

class SourceFreeSSMFittedTest(unittest.TestCase):
    def test_appendix_b_full_information_advantage_sign(self):
        # A profit - B profit = 11 - 3 * other players choosing A
        self.assertEqual([11-3*n for n in range(6)], [11,8,5,2,-1,-4])

    def test_choice_advantage_and_random_unexperienced(self):
        rng=Random(4)
        self.assertEqual(choose([11,8,5],q=3,rng=rng),1)
        self.assertEqual(choose([-4,-1],q=4,rng=rng),0)
        self.assertIn(choose([],q=3,rng=rng),(0,1))

    def test_fixed_seed_determinism(self):
        a=one_game(3,'fixed',Random(20261121))
        b=one_game(3,'fixed',Random(20261121))
        self.assertEqual(a,b)

    def test_mode_and_q_reject_invalid(self):
        for args in ((0,'fixed'),(31,'fixed'),(3,'bad')):
            with self.assertRaises(ValueError):one_game(*args,rng=Random(1))

    def test_completed_horizon_denominator_and_cost(self):
        counts,cost=one_game(5,'fixed',Random(10))
        self.assertTrue(all(cost[key]>=4 for key in ('cost_early','cost_late')))
        self.assertLessEqual(sum(counts[ep]['previous_A4'] for ep in counts),20)

    def test_fitted_models_not_only_q5_are_simulated(self):
        p=simulate({'fixed3':{'qmax':3,'mode':'fixed'},
                    'hetero4':{'qmax':4,'mode':'heterogeneous'}},reps=500,seed=20)
        self.assertEqual(set(p['models']),{'fixed3','hetero4'})
        for r in p['models'].values():
            self.assertTrue(0 <= r['early']['p_all_stay_A4'] <= 1)
            self.assertTrue(0 <= r['late']['p_all_stay_A4'] <= 1)

    def test_fixed_seed_replicability_of_public_result(self):
        a=simulate({'q3':{'qmax':3,'mode':'fixed'}},reps=100,seed=25)
        b=simulate({'q3':{'qmax':3,'mode':'fixed'}},reps=100,seed=25)
        self.assertEqual(a,b)

if __name__=='__main__':unittest.main()
