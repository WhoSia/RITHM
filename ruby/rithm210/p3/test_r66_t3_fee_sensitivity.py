"""R66-T3B source-free fee-sensitivity contracts: no original human rows."""
import json
from pathlib import Path
import unittest
from r66_t3_fee_sensitivity import paired_interval,load_alternative_rewards

HERE=Path(__file__).parent
CASH=json.loads((HERE/'r66_t3_results.json').read_text())
FEE=json.loads((HERE/'r66_t3_fee_sensitivity_results.json').read_text())

class FeeAudit(unittest.TestCase):
    def test_invalid_raw_source_never_parsed(self):
        with self.assertRaises(ValueError):load_alternative_rewards(__file__,{})

    def test_only_endogenous_has_source_fee_delta(self):
        for trt in ('No','Partial','Full'):
            self.assertEqual(FEE['source_adjustments_aggregate'][trt]['total_rows'],11520)
            self.assertEqual(FEE['source_adjustments_aggregate'][trt].get('nonzero_adjustment',0),0)
        end=FEE['source_adjustments_aggregate']['Endogenous']
        self.assertEqual(end['total_rows'],11520)
        self.assertEqual(end['nonzero_adjustment'],3960)
        self.assertEqual(end['payoff_bin_changed'],491)

    def test_fee_included_original_profit_reproduces_r66_t3(self):
        for trt in CASH['pooled']:
            for ep in ('early','late'):
                ref=CASH['pooled'][trt][ep]['legal_payoff_tenure']
                cur=FEE['pooled'][trt][ep]['received_profit']
                for k in ('n_old_A4_transitions','actor_logloss_mean','brier_allstay_mean','pred_welfare_mean'):
                    self.assertAlmostEqual(ref[k],cur[k],places=12)

    def test_fee_reconstruction_changes_only_endogenous_predictions(self):
        for trt in ('No','Partial','Full'):
            for ep in ('early','late'):
                a=FEE['pooled'][trt][ep]
                self.assertEqual(a['received_profit'],a['route_reward_reconstructed'])
        a=FEE['pooled']['Endogenous']['late']
        self.assertNotEqual(a['received_profit']['actor_logloss_mean'],a['route_reward_reconstructed']['actor_logloss_mean'])

    def test_all_paired_intervals_present_and_ordered(self):
        for r in FEE['descriptive_24_session_paired'].values():
            for v in r.values():
                self.assertLessEqual(v['descriptive_95'][0],v['descriptive_95'][1])

    def test_reconstructed_payoff_is_analyst_only(self):
        self.assertIn('NOT independently verified',FEE['definition_reconstructed'])
        self.assertIn('no causal',FEE['scope'])
        self.assertNotIn('"ID":',(HERE/'r66_t3_fee_sensitivity_results.json').read_text())

if __name__=='__main__':unittest.main()
