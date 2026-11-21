"""Source-free adversarial tests for R59 autonomous replay and information walls."""
import unittest
from math import isclose
from random import Random
from copy import deepcopy
from fractions import Fraction

from r58_author_rivals import ewa_path_differences, ssm_probabilities
from r59_closed_loop import (EWAState,SSMState,simulate,source_value_tape,
                             historical_outcome,MODELS)
from r59_transport_counterexample import (M0,M1,transition,exact_rollout,
                                          observed_one_step_loss)


def synthetic_record():
    frames=[]
    for t in range(40):
        # Alternate several legal choices to stress individual EWA state.
        routes=([1,1,1,1,0,0] if t%3==0 else
                [1,0,1,0,1,0] if t%3==1 else
                [0,1,1,1,1,0])
        n=sum(routes)
        frame=tuple((r,int(i%2==0),n,10+(t%5)/10-(n if r else 2*(6-n)))
                    for i,r in enumerate(routes))
        frames.append(frame)
    return {'session':3,'treatment':1,'periods':frames}


class ExactStateUpdates(unittest.TestCase):
    def test_streaming_ewa_equals_retrospective_author_appendix_at_all_40_steps(self):
        rec=synthetic_record()
        offline=ewa_path_differences(rec['periods'])
        online=EWAState([x[1] for x in rec['periods'][0]])
        for t,frame in enumerate(rec['periods']):
            for i in range(6):
                d=online.attractions[i][1]-online.attractions[i][0]
                self.assertAlmostEqual(d,offline[t][i],places=11)
            online.update(frame)
        self.assertEqual(online.period,40)
        with self.assertRaises(ValueError):online.update(rec['periods'][0][:3])

    def test_ssm_informed_and_uninformed_distinct_legal_histories(self):
        rng=Random(9)
        s=SSMState([1,0,1,0,1,0],fixed_q=5,rng=rng,lapse=0)
        self.assertTrue(all(not v for v in s.a+s.b+s.diff))
        routes=[1,1,1,1,0,0]
        frame=tuple((routes[i],int(i%2==0),4,7) for i in range(6))
        s.update(frame)
        self.assertEqual(s.diff[0],[10*(11-3*(4-1))])
        self.assertEqual(s.a[1],[70]);self.assertEqual(s.b[1],[])
        # Although informed has a known counterfactual, uninformed has no
        # B observations. Its decision must remain a fair coin.
        self.assertIn(s.choose(1),(0,1))
        self.assertEqual(s.q,(5,)*6)
        with self.assertRaises(ValueError):SSMState([0]*6,fixed_q=0,rng=rng)
        qmix=SSMState([0]*6,fixed_q='1_9',rng=Random(1))
        self.assertEqual(len(qmix.q),6)
        self.assertTrue(all(1<=q<=9 for q in qmix.q))

    def test_same_current_choice_when_future_shocks_change(self):
        rec=synthetic_record()
        changed=deepcopy(rec)
        # Set a distinct but legal Value at t=10 on actor 0 only. Decisions
        # made through period 10 cannot depend on that exogenous shock.
        t=9;i=0
        r,info,n,profit=changed['periods'][t][i]
        changed['periods'][t]=tuple((rr,ii,nn,(p+.4 if j==0 else p))
                    for j,(rr,ii,nn,p) in enumerate(changed['periods'][t]))
        self.assertNotEqual(source_value_tape(rec),source_value_tape(changed))
        for model in ('ewa_lite','ssm5','ssm1_9'):
            a=simulate(rec,model=model,seed=18)
            b=simulate(changed,model=model,seed=18)
            self.assertEqual(a['routes'][:10],b['routes'][:10])

    def test_no_actual_first_period_routes_in_fair_initialization(self):
        rec=synthetic_record()
        observed=simulate(rec,model='ssm5',init='observed',seed=6)
        self.assertEqual(observed['routes'][0],tuple(x[0] for x in rec['periods'][0]))
        fair=simulate(rec,model='ssm5',init='fair',seed=6)
        self.assertEqual(len(fair['routes']),40)
        self.assertIn(sum(fair['routes'][0]),range(7))
        self.assertEqual(sum(x[1] for x in fair['costs']),fair['total_gross'])
        self.assertEqual(fair['costs'][0][1],0)

    def test_historical_40_period_cost_is_an_actual_terminal_period_score(self):
        rec=synthetic_record();hist=historical_outcome(rec)
        self.assertEqual(hist['total_excess'],sum(3*(sum(r[0] for r in frame)-4)**2
                                                     for frame in rec['periods']))
        self.assertEqual(hist['total_gross'],sum(
            sum(x[0]!=y[0] for x,y in zip(rec['periods'][t-1],rec['periods'][t]))
            for t in range(1,40)))
        self.assertEqual(hist['early_excess'],sum(3*(sum(r[0] for r in frame)-4)**2
                                                     for frame in rec['periods'][:10]))


class TransportObstruction(unittest.TestCase):
    def test_same_teacher_forced_score_opposite_autonomous_congestion(self):
        a=exact_rollout(mechanism='reset');b=exact_rollout(mechanism='trap')
        self.assertEqual(observed_one_step_loss('reset'),observed_one_step_loss('trap'))
        self.assertEqual(transition(M0,mechanism='reset'),transition(M0,mechanism='trap'))
        self.assertLess(a['expected_total_excess'],b['expected_total_excess'])
        self.assertGreater(b['expected_total_excess']-a['expected_total_excess'],60)
        self.assertTrue(0<a['final_5A_probability']<Fraction(1,10))
        self.assertGreater(b['final_5A_probability'],Fraction(9,10))
        self.assertEqual(a['periods'][0],b['periods'][0])

    def test_exact_40_round_markov_mass_and_switching(self):
        for model in ('reset','trap'):
            z=exact_rollout(mechanism=model,periods=40)
            self.assertEqual(z['expected_total_excess'],sum(x['mean_excess'] for x in z['periods']))
            self.assertEqual(z['expected_total_gross'],sum(x['gross_changes'] for x in z['periods']))
            self.assertTrue(all(0<=x['prob_5A']<=1 for x in z['periods']))
        with self.assertRaises(ValueError):exact_rollout(mechanism='unknown')


if __name__=='__main__':unittest.main()
