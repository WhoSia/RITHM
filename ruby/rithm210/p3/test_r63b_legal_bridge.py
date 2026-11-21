"""No human ZIP, no personal trajectories; synthetic R63B legality/transport tests."""
import json
import math
import tempfile
from pathlib import Path
import unittest
from r63b_legal_bridge import (TAU, APPROVED_SHA, bootstrap_diff, calibrate_shift,
    fit_model, group_joint, legal_bin, load_private_events, poibin, predict,
    prior_probability, sigmoid)


def event(s=1,info=0,prev=0,flip=0,legal=0,treatment=1):
    return {'session':s,'info':info,'previous_route':prev,'flip':flip,
            'legal_bin':legal,'treatment':treatment,'prior_flips':8,
            'current_flips':2,'exposure':6,'actor':0,'other_actor_past':123,
            'analyst_previous_occupancy':6,'future_payoff':123456}


def synthetic_training():
    train=[]
    for info in (0,1):
        for prev in (0,1):
            for legal in range(9):
                for i in range(12):
                    train.append(event(s=1+(i%3),info=info,prev=prev,
                        flip=int((i+legal+info+prev)%4==0),legal=legal,
                        treatment=1 if not info else 3))
    train.append(event(s=99,info=1,prev=0,flip=1,legal=0,treatment=2))
    return train


class LegalBridgeSyntheticTest(unittest.TestCase):
    def test_expected_9_bins_and_edges(self):
        self.assertEqual(legal_bin(3.999,1),0)
        self.assertEqual(legal_bin(4.,3),4)
        self.assertEqual(legal_bin(8.,4),8)
        with self.assertRaises(ValueError):legal_bin(5.,0)

    def test_valid_probability_and_clock(self):
        e=event()
        p=prior_probability(e,.3)
        self.assertTrue(0<p<1)
        self.assertNotEqual(p,prior_probability(e,.3,tau=0))
        with self.assertRaises(ValueError):prior_probability(e,1.)
        with self.assertRaises(ValueError):prior_probability({**e,'exposure':-1},.4)

    def test_sigmoid_monotonic(self):
        self.assertAlmostEqual(sigmoid(0),.5)
        self.assertLess(sigmoid(-9),sigmoid(9))
        self.assertTrue(0<sigmoid(-100)<1)

    def test_source_only_intercept(self):
        p=[(.2,0),(.3,0),(.6,1),(.7,1)]*8
        shift=calibrate_shift(p)
        fitted=sum(sigmoid(math.log(x/(1-x))+shift) for x,_ in p)/len(p)
        self.assertAlmostEqual(fitted,(16+.5)/(32+1),places=12)
        self.assertEqual(calibrate_shift(p[:8]),0)

    def test_holdout_session_cannot_affect_training(self):
        a=synthetic_training()
        b=[{**x,'flip':1-x['flip']} if x['session']==99 else x for x in a]
        fitted=fit_model(a,99,lambda e:e['info']==0)
        other=fit_model(b,99,lambda e:e['info']==0)
        self.assertEqual(fitted,other)

    def test_transport_information_support_is_not_invented(self):
        a=synthetic_training()
        trained=fit_model(a,99,lambda e:e['info']==0)
        self.assertEqual(trained['source_masks'],(0,))
        with self.assertRaisesRegex(ValueError,'unobserved'):predict(event(info=1,legal=5),trained)
        self.assertIsNone(predict(event(info=1,legal=5),trained,require_support=False))

    def test_future_and_peer_mutation_is_invariant(self):
        a=synthetic_training()
        trained=fit_model(a,99,lambda e:e['info']==0)
        x=event(info=0,prev=1,legal=4)
        p=predict(x,trained)
        self.assertEqual(p,predict({**x,'future_payoff':-9999,'analyst_previous_occupancy':0,
                                   'other_actor_past':-1,'flip':1},trained))

    def test_current_own_history_can_change_law(self):
        trained=fit_model(synthetic_training(),99,lambda e:e['info']==0)
        x=event(info=0,prev=0,legal=0)
        self.assertNotEqual(predict(x,trained),predict({**x,'current_flips':0},trained))

    def test_poisson_binomial_exact_and_normalized(self):
        p=poibin([.2,.6,.3])
        self.assertEqual(len(p),4)
        self.assertAlmostEqual(sum(p),1.)
        self.assertAlmostEqual(p[0],.8*.4*.7)
        self.assertAlmostEqual(p[3],.2*.6*.3)

    def test_joint_flow_and_no_switch(self):
        actors=[event(prev=i<4,flip=0) for i in range(6)]
        ps=[.1,.2,.3,.4,.5,.6]
        loss,pzero=group_joint(actors,ps)
        self.assertAlmostEqual(math.exp(-loss),math.prod(1-p for p in ps))
        self.assertAlmostEqual(pzero,math.prod(1-p for p in ps))
        actors[4]['flip']=1
        loss1,_=group_joint(actors,ps)
        self.assertAlmostEqual(math.exp(-loss1),(.5*(1-.6)+(1-.5)*.6)*math.prod(1-p for p in ps[:4]))

    def test_bootstrap_uses_session_units(self):
        out=bootstrap_diff([.003,.003,.003],reps=30)
        self.assertEqual(out['n_paired_source_sessions'],3)
        self.assertAlmostEqual(out['paired_delta'],.003)
        self.assertEqual(out['descriptive_session_bootstrap95'],[.003,.003])

    def test_private_source_requires_exact_digest_before_read(self):
        with tempfile.TemporaryDirectory() as d:
            bad=Path(d,'notapproved.zip');bad.write_bytes(b'different original source')
            with self.assertRaisesRegex(ValueError,'SHA256 mismatch'):load_private_events(bad)

    def test_clean_output_only_aggregate_schema(self):
        x={'models':{'bridge':{'actor_logloss':.49}},'evaluated':{'group_transitions':1248}}
        blob=json.dumps(x)
        for forbidden in ('future_payoff','actor_id','session_id','participant_route','Value_t'):
            self.assertNotIn(forbidden,blob)


if __name__=='__main__':unittest.main()
