"""Source-free R66-T2 contract tests: do NOT require restricted author ZIP."""
import unittest
from collections import Counter
from itertools import product
from math import isclose
from r66_t2_original_audit import (period_epoch,age_bin,coarse_key,fit_by_session,
  prediction,signed_second_from_independence,event_stats,pooled_summary,paired_bootstrap)


def fake_event(route,flip,*,sid=1,ep='late',age=1,info=1,trt=3):
    return {'session':sid,'treatment':trt,'epoch':ep,'info':info,
     'previous_route':route,'previous_A':4,'tenure_bin':age,'flip':int(flip),
     'up':int(not route and flip),'down':int(route and flip)}


class TestR66T2(unittest.TestCase):
    def test_clock_timing(self):
        self.assertEqual([period_epoch(t) for t in (1,10,11,29,30,39,40)],
                         ['early','early',None,None,'late','late',None])
    def test_age_streak_bins(self):
        self.assertEqual([age_bin(i) for i in (1,2,3,4,5,20)], [1,2,3,3,4,4])
    def test_features_do_not_include_occupancy_or_outcomes(self):
        e=fake_event(1,0)
        key=coarse_key(e)
        self.assertEqual(key,(3,'late',1,1))
        self.assertEqual(len(key),4)
        self.assertEqual(coarse_key({**e,'previous_A':2}),key)
    def test_source_heldout_fold_and_info_support(self):
        e=[fake_event(1,flip=1,sid=1),fake_event(1,flip=0,sid=2),
           fake_event(0,flip=1,sid=2)]
        model=fit_by_session(e,held=1)
        p=prediction(e[0],model,'legal_coarse')
        self.assertEqual(p,0.25)
        self.assertGreater(prediction(e[0],model,'legal_tenure'),0)
        self.assertGreater(prediction(e[0],model,'analyst_A4'),0)
    def test_analyst_state_not_available_to_legal_variant(self):
        e=[fake_event(1,flip=1,sid=1),fake_event(1,flip=0,sid=2)]
        model=fit_by_session(e,held=1)
        candidate={**e[0], 'previous_A':3}
        self.assertEqual(prediction(candidate,model,'legal_coarse'),
                         prediction(e[0],model,'legal_coarse'))
        with self.assertRaises(ValueError):prediction(candidate,model,'analyst_A4')
    def test_expected_signed_second_exact_enumeration(self):
        rows=[fake_event(route,flip=0) for route in (1,1,1,1,0,0)]
        ps=[0.11,0.19,0.07,0.23,0.3,0.2]
        mu,sq=signed_second_from_independence(rows,ps)
        check0=check1=0
        for bits in product((0,1),repeat=6):
            mass=1
            for x,p in zip(bits,ps):mass*=p if x else 1-p
            value=sum(x*(1 if row['previous_route']==0 else -1) for x,row in zip(bits,rows))
            check0+=mass*value;check1+=mass*value**2
        self.assertTrue(isclose(mu,check0,abs_tol=1e-12))
        self.assertTrue(isclose(sq,check1,abs_tol=1e-12))
    def test_directional_cancellation_is_not_full_stay(self):
        rows=[fake_event(route,flip) for route,flip in
              zip((1,1,1,1,0,0),(1,0,0,0,1,0))]
        metrics=event_stats(rows,[.2]*6)
        self.assertEqual(metrics['gross_obs'],2)
        self.assertEqual(metrics['net_obs'],0)
        self.assertEqual(metrics['all_stay_obs'],0)
        self.assertEqual(metrics['cancel_obs'],1)
        self.assertEqual(metrics['nochange_occupancy_obs'],1)
        self.assertEqual(metrics['welfare_obs'],0)
        self.assertEqual(metrics['up_down_obs'],1)
    def test_full_stay_has_no_gross_or_net(self):
        rows=[fake_event(route,0) for route in (1,1,1,1,0,0)]
        m=event_stats(rows,[.1]*6)
        self.assertEqual(m['all_stay_obs'],1)
        self.assertEqual(m['gross_obs'],0)
        self.assertEqual(m['net_sq_obs'],0)
    def test_variance_components_and_output_suppression(self):
        c=Counter({'n':20,'net_obs':10.,'net_sq_obs':15.,'net_pred':8.,
            'net_sq_pred':12.,'welfare_obs':45.,'welfare_pred':36.,
            'up_obs':10.,'up_sq_obs':15.,'down_obs':0.,'down_sq_obs':0.,'up_down_obs':0.})
        v=pooled_summary(c)
        self.assertAlmostEqual(v['observed_net_variance'],.75-.5**2)
        self.assertAlmostEqual(v['signed_covariance_plus_miscalibration_welfare_residual'],.45)
    def test_bad_joint_group_guard(self):
        rows=[fake_event(route,0) for route in (1,1,1,1,0,0)]
        with self.assertRaises(ValueError):signed_second_from_independence(rows[:5],[.2]*6)
        with self.assertRaises(ValueError):event_stats(rows[:5],[.2]*5)

if __name__=='__main__': unittest.main()
