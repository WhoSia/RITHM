"""R66-T3 source-free tests: no original participant ZIP in CI."""
import math
import unittest
from collections import defaultdict
from fractions import Fraction
from r66_t3_payoff_streak import (payoff_bin,build_tables,predict,group_scores,
                                   public_mean,session_bootstrap,_percentile_interval,
                                   coarse_key,MODELS)


def actor(session,*,flip=0,route=1,pay=0,tenure=1,group_age=1,oldA=4,trt=3,ep='late',info=1):
    return dict(session=session,group=1,treatment=trt,epoch=ep,
                previous_A=oldA,previous_route=route,info=info,
                tenure_bin=tenure,payoff_bin=pay,joint_age_bin=group_age,
                info_count_analyst=6,flip=flip,
                up=int(route==0 and flip),down=int(route==1 and flip))

class R66T3Synthetic(unittest.TestCase):
    def test_payoff_buckets_boundary_and_nan(self):
        self.assertEqual([payoff_bin(x) for x in (-100,0,3.9999,4,7.999,8,300)], [0,0,0,1,1,2,2])
        for x in (float('nan'),float('inf'),float('-inf')):
            with self.assertRaises(ValueError):payoff_bin(x)

    def test_leave_whole_session_out_even_when_held_has_adversarial_flips(self):
        a=[actor(1,flip=0,route=1,pay=1),actor(2,flip=0,route=1,pay=1),
           actor(99,flip=1,route=1,pay=1)]
        t=build_tables(a,99)
        self.assertEqual(t['coarse'][coarse_key(a[2])],[0,2])
        self.assertEqual(t['A4'][coarse_key(a[2])],[0,2])
        self.assertEqual(t['tenure_payoff'][coarse_key(a[2])+(1,1)],[0,2])
        self.assertEqual(t['A4_age_payoff'][coarse_key(a[2])+(1,1,1)],[0,2])

    def test_previous_self_payoff_changes_only_payoff_aware_probabilities(self):
        a=[actor(s,route=1,pay=(s%2),flip=(s%2)) for s in range(1,21)]
        t=build_tables(a,99)
        p0=predict(actor(99,route=1,pay=0),t)
        p1=predict(actor(99,route=1,pay=1),t)
        for k in ('legal_coarse','legal_tenure','analyst_A4','analyst_A4_age'):
            self.assertAlmostEqual(p0[k],p1[k])
        self.assertNotEqual(p0['legal_payoff_tenure'],p1['legal_payoff_tenure'])
        self.assertNotEqual(p0['analyst_A4_age_payoff'],p1['analyst_A4_age_payoff'])

    def test_old_A4_age_never_enters_legal_models(self):
        a=[actor(s,group_age=(1 if s<=10 else 3),flip=int(s>10)) for s in range(1,21)]
        t=build_tables(a,99)
        e1=actor(99,group_age=1)
        e2=actor(99,group_age=3)
        x,y=predict(e1,t),predict(e2,t)
        for k in ('legal_coarse','legal_tenure','legal_payoff_tenure','analyst_A4'):
            self.assertAlmostEqual(x[k],y[k],msg=k)
        self.assertNotEqual(x['analyst_A4_age'],y['analyst_A4_age'])

    def test_old_occupancy_not_legal(self):
        a=[actor(s,flip=(s%2)) for s in range(1,21)]
        t=build_tables(a,99)
        old4=actor(99,oldA=4);old3=actor(99,oldA=3)
        p4,p3=predict(old4,t),predict(old3,t)
        for k in ('legal_coarse','legal_tenure','legal_payoff_tenure'):
            self.assertEqual(p4[k],p3[k])
        self.assertNotIn('analyst_A4',p3)
        self.assertIn('analyst_A4',p4)

    def test_group_score_exact_independent_welfare(self):
        group=[actor(1,route=r,flip=0) for r in (1,1,1,1,0,0)]
        r=group_scores(group,[0.5]*6)
        self.assertEqual(r['observed_welfare'],0)
        self.assertAlmostEqual(r['pred_welfare'],7.5) # signed E[net]=-1, Var(net)=1.5; 3*(1+1.5)=7.5
        self.assertAlmostEqual(r['pred_allstay'],1/64)
        self.assertAlmostEqual(r['pred_gross'],3)

    def test_never_pretend_observed_outcomes_are_probabilities(self):
        group=[actor(1,route=r,flip=int(j<2)) for j,r in enumerate((1,1,1,1,0,0))]
        r=group_scores(group,[.2]*6)
        self.assertEqual(r['observed_welfare'],12)
        self.assertGreater(r['welfare_sqerr'],0)
        self.assertGreater(r['actor_logloss'],0)

    def test_scores_require_six_oldA4(self):
        g=[actor(1) for _ in range(5)]
        with self.assertRaises(ValueError):group_scores(g,[.5]*5)
        g=[actor(1,oldA=3) for _ in range(6)]
        with self.assertRaises(ValueError):group_scores(g,[.5]*6)

    def test_public_cell_minimum(self):
        with self.assertRaises(ValueError):public_mean({'n':19})

    def test_bootstrap_requires_24_original_sessions(self):
        with self.assertRaises(ValueError):session_bootstrap({(1,3,'early','legal_coarse'):{'n':100}})

    def test_bootstrap_roundtrip_on_artificial_24_session_law(self):
        # All models identical, therefore contrasts must be exactly zero.
        agg={}
        for s in range(24):
            for t in (1,2,3,4):
                for ep in ('early','late'):
                    for model in MODELS:
                        agg[s,t,ep,model]={k:5 for k in ('n','residual_welfare','welfare_sqerr','brier_allstay','actor_logloss')}
        r=session_bootstrap(agg,draws=30,seed=123)
        for cell in r.values():
            self.assertEqual(cell['accepted'],30)
            for cmp in cell['differences'].values():
                for metric in cmp.values():
                    self.assertEqual(metric['delta'],0)
                    self.assertEqual(metric['descriptive_95'],[0,0])

    def test_incomplete_model_support_refused(self):
        with self.assertRaises(ValueError):predict(actor(1),build_tables([],1))

    def test_aggregate_metrics_not_force_identity(self):
        r=group_scores([actor(1,route=x,flip=0) for x in (1,1,1,1,0,0)],[.2]*6)
        self.assertEqual(r['observed_allstay'],1)
        self.assertGreater(r['brier_allstay'],0)
        self.assertGreater(r['pred_welfare'],0)

if __name__=='__main__':unittest.main()
