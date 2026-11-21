"""Source-free original-data aggregate contract; NO private ZIP on CI."""
import json
import unittest
from math import isclose
from pathlib import Path

HERE=Path(__file__).parent
R66T3=HERE/'r66_t3_results.json'
R66T2=HERE/'r66_t2_original_results.json'

class R66T3PublicResults(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=R66T3.read_text('utf-8')
        cls.j=json.loads(cls.raw)
        cls.old=json.loads(R66T2.read_text('utf-8'))

    def test_private_source_omitted_from_public_aggregate(self):
        j=self.j
        self.assertEqual(j['original_author_zip_sha256'],
            'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953')
        self.assertEqual(j['source_roster']['original_sessions'],24)
        self.assertEqual(j['source_roster']['distinct_six_person_groups'],48)
        self.assertTrue(j['source_free_contract'])
        for raw_key in ('"ID":','"Subject":','"Value":','"profit":','"RouteA":','"RouteB":','"session_id":','"actor_id":'):
            self.assertNotIn(raw_key,self.raw)
        self.assertIn('not randomized', ' '.join(j['limitations']))

    def test_exact_r66_t2_coarse_tenure_and_A4_reproduction(self):
        mnames=('legal_coarse','legal_tenure','analyst_A4')
        cols=(('welfare_obs_mean','observed_welfare_mean'),
              ('welfare_pred_mean','pred_welfare_mean'),
              ('all_stay_obs_mean','observed_allstay_mean'),
              ('all_stay_pred_mean','pred_allstay_mean'),
              ('zero_switch_brier_mean','brier_allstay_mean'),
              ('actor_logloss_mean','actor_logloss_mean'))
        for trt in ('No','Partial','Full','Endogenous'):
            for ep in ('early','late'):
                for name in mnames:
                    old=self.old['pooled'][trt][ep][name]
                    new=self.j['pooled'][trt][ep][name]
                    self.assertEqual(old['n_old_A4_transitions'],new['n_old_A4_transitions'])
                    for a,b in cols:
                        self.assertTrue(isclose(old[a],new[b],rel_tol=1e-10,abs_tol=1e-10),
                            (trt,ep,name,a,b,old[a],new[b]))

    def test_model_cells_and_welfare_accounting(self):
        modelnames=set(self.j['models'])
        self.assertEqual(len(modelnames),6)
        for trt in self.j['pooled']:
            for ep,models in self.j['pooled'][trt].items():
                self.assertEqual(set(models),modelnames)
                for model,rec in models.items():
                    self.assertGreaterEqual(rec['n_old_A4_transitions'],20)
                    self.assertTrue(isclose(rec['residual_welfare_mean'],
                        rec['observed_welfare_mean']-rec['pred_welfare_mean'],abs_tol=1e-10))
                    self.assertTrue(0<=rec['pred_allstay_mean']<=1)
                    self.assertTrue(0<=rec['observed_allstay_mean']<=1)
                    self.assertGreater(rec['welfare_sqerr_mean'],0)
                    self.assertGreater(rec['actor_logloss_mean'],0)

    def test_session_paired_intervals(self):
        b=self.j['paired_24_session_descriptive_bootstrap']
        self.assertEqual(len(b),8)
        for tag,r in b.items():
            self.assertEqual(r['original_sessions'],24)
            self.assertGreaterEqual(r['accepted'],3600)
            for cmp,metrics in r['differences'].items():
                for m,v in metrics.items():
                    a,c=v['descriptive_95']
                    self.assertLessEqual(a,c)
                    self.assertLessEqual(a+0.,v['delta']+20,tag)
        # Not a hypothesis test: intervals describe repeatedly reused sessions.
        self.assertIn('exploratory',self.j['scope'].lower())

if __name__=='__main__':unittest.main()
