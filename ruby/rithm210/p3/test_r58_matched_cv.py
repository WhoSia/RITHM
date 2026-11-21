"""Independent, no-human-data contract tests for R58 matched evaluation."""
from collections import Counter
from math import exp, log
import math
import unittest

from r58_author_rivals import (ewa_path_differences,ssm_probabilities,
        ssm_posterior_predictive,flow_law_from_actor_flip)
from r58_matched_cv import (fitted_ewa_lambda,legal_training,legal_predict)


def static_frame(route_mask=(1,1,1,1,0,0), info_mask=(1,1,1,1,0,0), value=10.0):
    a=sum(route_mask)
    return tuple((route_mask[i], info_mask[i], a,
                  value-(a if route_mask[i] else 2*(6-a)))
                 for i in range(6))


class CorrectAppendixDynamics(unittest.TestCase):
    def test_ewa_t2_manual_observation_equivalent_and_attractions(self):
        data=[static_frame() for _ in range(40)]
        ewa=ewa_path_differences(data)
        # First period group A=4. An informed A chooser has actual payoff 6,
        # unchosen B payoff 4 < 6, so N1=2, A(A)=3.5, A(B)=0.5.
        # An informed B chooser has actual 6 and hypothetical A payoff 5,
        # and is equally one-sided in the other direction.
        self.assertEqual(ewa[0],(0,)*6)
        self.assertAlmostEqual(ewa[1][0],3.0)
        self.assertAlmostEqual(ewa[1][1],3.0)
        self.assertNotEqual(ewa[1][4],-3.0)  # uninformed prior belief differs

    def test_informed_ssm_all_paired_trials_favor_A_uninformed_coins(self):
        # At A=4, actual other A count for A chooser=3, paired advantage 2.
        # For B chooser, other A=4, paired advantage -1.
        fr=static_frame(info_mask=(1,1,1,1,0,0))
        data=[fr for _ in range(40)]
        pred=ssm_probabilities(data)
        self.assertEqual(pred[0][0],(.5,)*9)
        self.assertEqual(pred[1][0],(1.0,)*9)
        self.assertEqual(pred[1][4],(.5,)*9)

    def test_q_is_a_fixed_actor_type_updated_from_observed_own_choice(self):
        row=(1,1,4,6.0)
        f=[(0.5,)*9 for _ in range(6)]
        t2=[(0.0,1.0)+(.5,)*7 for _ in range(6)]
        t3=[(0.0,1.0)+(.5,)*7 for _ in range(6)]
        probs=ssm_posterior_predictive([f,t2,t3],
            [tuple(row for _ in range(6)) for _ in range(3)],epsilon=.02)
        prior_p=sum((.01,.99)+(.5,)*7)/9
        self.assertAlmostEqual(probs[1]['ssm1_9'][0],prior_p)
        self.assertGreater(probs[2]['ssm1_9'][0],probs[1]['ssm1_9'][0])
        self.assertEqual(probs[1]['ssm5'][0],.5)

    def test_legal_participant_rival_ignores_excluded_macro_occupancy(self):
        row=(1,4,6.0,0)
        records=[{'trt':1,'a':a,'actors':(row,), 'flips':(flip,)}
                 for a,flip in ((2,0),(3,1),(4,0))]
        trained=legal_training(records)
        results=[legal_predict(x,trained,refined=True)[0] for x in records]
        self.assertEqual(len(set(results)),1)
        self.assertTrue(0<results[0]<1)

    def test_logistic_optimizer_boundary_and_folds_are_deterministic(self):
        # A model predicting A when A=0 should use lambda=0 if possible.
        self.assertEqual(fitted_ewa_lambda([2.0]*5,[0]*5),0.0)
        self.assertAlmostEqual(fitted_ewa_lambda([2.0]*5,[1]*5),3.0)
        self.assertTrue(0<fitted_ewa_lambda([1,-1],[1,1])<3 or
                        fitted_ewa_lambda([1,-1],[1,1])==0)


class FiniteLawGuarantees(unittest.TestCase):
    def test_count_support_for_all_64_label_masks(self):
        for mask in range(64):
            frame=static_frame(tuple((mask>>i)&1 for i in range(6)),
                               (1,)*6)
            law=flow_law_from_actor_flip(frame,[.2]*6)
            a=sum(x[0] for x in frame)
            self.assertEqual(len(law),(a+1)*(7-a))
            self.assertAlmostEqual(sum(law.values()),1.0,places=12)

    def test_model_rejects_malformed_folds_and_prior_probabilities(self):
        with self.assertRaises(ValueError):fitted_ewa_lambda([],[])
        fr=static_frame()
        with self.assertRaises(ValueError):ssm_posterior_predictive([[(.5,)*9]*6],
                                                                    [fr],epsilon=1.1)

if __name__=='__main__':unittest.main()
