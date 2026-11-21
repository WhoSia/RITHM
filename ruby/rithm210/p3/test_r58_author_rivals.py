"""Source-free adversarial protocol tests. Real actor rows NEVER enter CI."""
import math
from collections import Counter
from itertools import product
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from r58_author_rivals import (other_route_belief,ewa_path_differences,
    win_from_histogram,ssm_probabilities,ssm_posterior_predictive,
    flow_law_from_actor_flip,score_laws)
from r58_matched_cv import fitted_ewa_lambda,legal_training,legal_predict


def synthetic_history():
    # Previous period A occupancy 4; keep actor ID and information mask fixed.
    routes=[1,1,1,1,0,0]
    info=[1,0,1,0,1,0]
    out=[]
    for t in range(40):
        if t==1: routes=[1,0,1,1,1,0]
        if t==2: routes=[1,0,1,0,1,1]
        a=sum(routes)
        out.append(tuple((routes[i],info[i],a,10.0-(a if routes[i] else 2*(6-a))) for i in range(6)))
    return out


class AppendixALegalBeliefs(unittest.TestCase):
    def test_uninformed_tables_exact_boundary_cases(self):
        self.assertEqual(other_route_belief(1,14.5),(1,0,0,0,0,0))
        self.assertEqual(other_route_belief(1,5.0),(1/6,)*6)
        self.assertEqual(other_route_belief(0,14.0),(0,0,0,0,0,1))
        self.assertEqual(other_route_belief(0,4.0),(1/6,)*6)
        self.assertEqual(other_route_belief(0,-5.0),(1,0,0,0,0,0))
        with self.assertRaises(ValueError):other_route_belief(0,50.0)

    def test_ewa_initial_attractions_and_future_wall(self):
        a=synthetic_history()
        before=ewa_path_differences(a)
        self.assertEqual(before[0],(0,)*6)
        copy=list(a)
        # Change future action and payoff together. Current t=10 prediction
        # must NOT change: it conditions only on completed periods 1..9.
        at=list(copy[9]);at[2]=(0,at[2][1],at[2][2],at[2][3]);copy[9]=tuple(at)
        after=ewa_path_differences(copy)
        self.assertEqual(before[:10],after[:10])
        self.assertNotEqual(before[10],after[10])

    def test_ewa_lambda_train_only_optimizer(self):
        d=[-0.5,-1.0,0.0,2.0,0.3];y=[0,0,1,1,1]
        lam=fitted_ewa_lambda(d,y)
        self.assertTrue(0<=lam<=3)
        shuffled=fitted_ewa_lambda(list(reversed(d)),list(reversed(y)))
        self.assertAlmostEqual(lam,shuffled,places=10)
        with self.assertRaises(ValueError):fitted_ewa_lambda([],[])


class AppendixBSampling(unittest.TestCase):
    def test_exact_fft_samples_vs_bruteforce(self):
        # Single paired payoff difference W = X_A-X_B.
        a=[12,16,21];b=[5,10]
        differences=Counter(x-y for x in a for y in b)
        vals=[x-y for x in a for y in b]
        for q in range(1,5):
            score=0
            for tuple_of_choices in product(vals,repeat=q):
                sign=sum(tuple_of_choices)
                score+=(1.0 if sign>0 else 0.5 if sign==0 else 0.0)
            self.assertAlmostEqual(win_from_histogram(differences,q),
                                   score/len(vals)**q,places=11)
        self.assertEqual(win_from_histogram({5:1},9),1)
        self.assertEqual(win_from_histogram({-5:1},9),0)
        self.assertEqual(win_from_histogram({0:1},9),.5)

    def test_ssm_no_future_choices_in_same_forecast(self):
        history=synthetic_history()
        before=ssm_probabilities(history)
        changed=list(history)
        fr=list(changed[9]);
        fr[0]=(1-fr[0][0],fr[0][1],fr[0][2],fr[0][3])
        changed[9]=tuple(fr)
        after=ssm_probabilities(changed)
        self.assertEqual(before[:10],after[:10])
        self.assertNotEqual(before[10],after[10])
        mixed=ssm_posterior_predictive(before,history,epsilon=.02)
        self.assertTrue(all(.01<=p<=.99 for step in mixed for ps in step.values() for p in ps))
        self.assertEqual(mixed[0]['ssm5'],(.5,)*6)

    def test_joint_law_normalization_and_no_lookahead(self):
        frame=synthetic_history()[0]
        flip=[.1,.2,.3,.4,.5,.6]
        law=flow_law_from_actor_flip(frame,flip)
        self.assertAlmostEqual(sum(law.values()),1)
        self.assertEqual(len(law),(4+1)*(2+1))
        score=score_laws(frame,synthetic_history()[1],tuple(.2 for _ in frame))
        self.assertTrue(all(math.isfinite(s) for s in score))


class ReproducibilityBoundary(unittest.TestCase):
    def test_source_requires_explicit_salt_SHA(self):
        from r58_author_rivals import actor_rows_sealed
        with tempfile.TemporaryDirectory() as dirname:
            bad=Path(dirname)/'fake-approved.zip'
            with ZipFile(bad,'w') as z:z.writestr('data_task_all_switch_230705.csv','session\n')
            with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):
                actor_rows_sealed(bad)

    def test_private_only_baseline_does_not_use_occupancy(self):
        a={'trt':1,'a':2,'actors':((1,3,9.0,0),(0,1,4.0,1)),'flips':(1,0)}
        b={'trt':1,'a':5,'actors':a['actors'],'flips':a['flips']}
        t=legal_training([a,b])
        self.assertEqual(legal_predict(a,t,refined=True),legal_predict(b,t,refined=True))

if __name__=='__main__':unittest.main()
