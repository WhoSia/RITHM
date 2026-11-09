import math
import unittest
from r23_inertia_memory_cv import (Actor, candidates, label, occupancy_distribution, scores,
                                  cross_validate, evaluate)

class TestR23MemoryInertia(unittest.TestCase):
    def test_actor_prior_history_and_decay(self):
        a=Actor()
        self.assertEqual(.5,a.frequency(1.0))
        self.assertEqual(.5,a.markov(5.0))
        a.update(1)
        self.assertAlmostEqual(2/3,a.frequency(1))
        self.assertAlmostEqual(.8,a.markov(5))
        a.update(0)
        self.assertAlmostEqual(.5,a.frequency(1))
        self.assertAlmostEqual((.5+1)/(.5+1+2),a.frequency(.5))
        self.assertAlmostEqual(.2,a.markov(5))
        a.update(1)
        self.assertAlmostEqual(4/6,a.markov(5))

    def test_mass_and_exact_quadratic_cost(self):
        self.assertEqual(7,len(occupancy_distribution([.5]*6)))
        self.assertAlmostEqual(1.,sum(occupancy_distribution([.3]*6)))
        self.assertAlmostEqual(31.5, sum(p*(n*n+2*(6-n)**2) for n,p in enumerate(occupancy_distribution([.5]*6))))
        self.assertAlmostEqual(-math.log(20/64),scores([.5]*6,3)[0])
        with self.assertRaises(ValueError): occupancy_distribution([.5]*5)

    def test_unique_candidates_and_baseline(self):
        names=[label(c) for c in candidates()]
        self.assertEqual(len(names),len(set(names)))
        self.assertIn('frequency_decay_1',names)
        self.assertIn('markov_strength_5',names)
        self.assertEqual(33,len(names))

    def test_no_same_period_leakage(self):
        groups={}
        for t in (1,2):
            groups[(1,1,t,1)]=[
                {'ID':str(i),'trt':'3','RouteA':str(int(i<=3)), 'NumA':'3'} for i in range(1,7)]
        models=((1.,5.,0.),(.8,5.,0.),(1.,5.,1.))
        payload=evaluate(groups,requested_candidates=models)
        self.assertEqual(2,payload['groups'])
        self.assertEqual(3,payload['candidates'])
        baseline=next(x for x in payload['session_results'] if x['model']=='frequency_decay_1')
        expected_first=scores([.5]*6,3)[0]
        expected_second=scores([2/3]*3+[1/3]*3,3)[0]
        self.assertAlmostEqual((expected_first+expected_second)/2,baseline['logloss'])
        broken=dict(groups)
        broken[(1,1,2,1)]=[dict(r,NumA='5') for r in groups[(1,1,2,1)]]
        with self.assertRaises(ValueError): evaluate(broken,requested_candidates=models)

    def test_select_only_training_fold(self):
        rows=[]
        for s in range(1,25):
            for treatment in (1,2,3):
                for m in ('frequency_decay_1','memory_0.8_markov_5_mix_0.5'):
                    v=0.5 if m=='frequency_decay_1' else (0.3 if s<=20 else 3.0)
                    rows.append(dict(session=s,treatment=treatment,model=m,groups=80,
                                     logloss=v,brier=v,cost_abs_error=v))
        out=cross_validate(dict(session_results=rows,groups=5760),draws=20)
        self.assertEqual(24,out['results'][0]['sessions'])
        self.assertTrue(math.isfinite(out['results'][0]['delta_logloss']))
        bad=rows+[rows[0]]
        with self.assertRaises(ValueError):
            cross_validate(dict(session_results=bad,groups=5760),draws=20)

if __name__=='__main__':unittest.main()
