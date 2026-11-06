# No human source required. Test FFT version of SSM iid-with-replacement rule.
import random
import unittest
from r22_ssm_q9_fft_cv import sampled_q_probabilities

class TestR22SSMQ9FFT(unittest.TestCase):
    def test_500_random_pools_against_integer_exact_counts(self):
        rng=random.Random(20261106)
        for _ in range(500):
            pool=[rng.randrange(-20,21) for j in range(rng.randrange(1,6))]
            actual=sampled_q_probabilities(pool)
            dist={0:1}
            for q in range(1,10):
                next_dist={}
                for state,count in dist.items():
                    for value in pool:
                        key=state+value
                        next_dist[key]=next_dist.get(key,0)+count
                dist=next_dist
                numerator=sum(count for state,count in dist.items() if state>0)
                numerator+=0.5*dist.get(0,0)
                expected=numerator/len(pool)**q
                self.assertAlmostEqual(expected,float(actual[q-1]),delta=1e-10)
    def test_empty_and_pure_signs(self):
        self.assertEqual([.5]*9,list(sampled_q_probabilities([])))
        self.assertEqual([1.]*9,list(sampled_q_probabilities([1,2])))
        self.assertEqual([0.]*9,list(sampled_q_probabilities([-1,-2])))

if __name__=='__main__':
    unittest.main()
