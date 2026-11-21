"""R66-T2 public aggregate-only output schema; source-free safe CI."""
import json
import unittest
from pathlib import Path
from math import isclose

REPORT=Path(__file__).with_name('r66_t2_original_results.json')
MODEL=('legal_coarse','legal_tenure','analyst_A4')

class TestR66T2PublicAggregate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=REPORT.read_text()
        cls.j=json.loads(cls.raw)
    def test_contract_and_source_custody(self):
        j=self.j
        self.assertEqual(j['approved_sha256'],
          'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953')
        self.assertTrue(j['no_original_rows_exported'])
        self.assertEqual(j['original_sessions'],24)
        self.assertEqual(j['unique_repeated_six_person_groups'],48)
        self.assertNotIn('"actor":',self.raw)
        self.assertNotIn('"ID":',self.raw)
        self.assertNotIn('"Value":',self.raw)
        self.assertIn('not causal',j['scope'])
    def test_four_conditions_24_session_summary_and_consistent_moments(self):
        self.assertEqual(set(self.j['pooled']),{'No','Partial','Full','Endogenous'})
        for trt in self.j['pooled']:
            for ep in ('early','late'):
                models=self.j['pooled'][trt][ep]
                self.assertEqual(set(models),set(MODEL))
                n={x['n_old_A4_transitions'] for x in models.values()}
                self.assertEqual(len(n),1)
                self.assertGreaterEqual(next(iter(n)),20)
                for m,v in models.items():
                    self.assertTrue(0<=v['all_stay_obs_mean']<=1)
                    self.assertTrue(0<=v['all_stay_pred_mean']<=1)
                    self.assertTrue(isclose(v['welfare_obs_mean'],3*v['net_sq_obs_mean'],abs_tol=1e-9))
                    self.assertTrue(isclose(v['welfare_pred_mean'],3*v['net_sq_pred_mean'],abs_tol=1e-9))
                    self.assertTrue(isclose(v['observed_net_variance'],
                        v['observed_up_variance']+v['observed_down_variance']-2*v['observed_up_down_covariance'],abs_tol=1e-9))
                    self.assertTrue(isclose(v['signed_covariance_plus_miscalibration_welfare_residual'],
                                         v['welfare_obs_mean']-v['welfare_pred_mean'],abs_tol=1e-9))
    def test_r65_consistency_of_A4_counts_and_stay(self):
        expected={('Full','early'):(154,34),('Full','late'):(257,150),
                  ('Partial','early'):(198,49),('Partial','late'):(204,59),
                  ('Endogenous','early'):(219,82),('Endogenous','late'):(224,82)}
        for (trt,ep),(n,stays) in expected.items():
            observed=self.j['pooled'][trt][ep]['legal_coarse']
            self.assertEqual(observed['n_old_A4_transitions'],n)
            self.assertAlmostEqual(observed['all_stay_obs_mean'],stays/n)
    def test_analyst_oracle_not_participant_cognitive_law(self):
        self.assertIn('not actor-legal',self.j['models']['analyst_A4'])
        self.assertIn('marginal-model mismatch',self.j['estimand'])
        self.assertIn('NOT equal to identified',self.j['failure_mode'])

if __name__=='__main__':unittest.main()
