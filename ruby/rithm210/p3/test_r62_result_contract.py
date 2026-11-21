"""Public aggregate-only artifact contract; NEVER needs or opens private ZIP."""
import json
import math
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent

class R62PublishedAggregate(unittest.TestCase):
    def load(self,name):
        text=(ROOT/name).read_text()
        obj=json.loads(text)
        self.assertFalse(any(s in text for s in ('"personal_route_sequence"','"subject_id"','"actor_id"','"individual_Value_tape"')))
        return obj

    def test_original_cohort_and_legal_information_boundary(self):
        r=self.load('r62_one_step_results.json')
        self.assertEqual(r['source_sha256'],'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953')
        self.assertEqual(r['models']['current_only']['cohort']['sessions'],24)
        self.assertEqual(r['models']['current_only']['cohort']['group_transitions'],3744)
        self.assertEqual(r['models']['current_only']['cohort']['individual_decisions'],22464)

    def test_fixed_individual_marginals_have_identical_gross_expectation(self):
        r=self.load('r62_one_step_results.json')
        for base in ('current_only','nested_adaptive'):
            scores=r['models'][base]['scores']
            x=scores['independent']['predicted_mean_gross_switches']
            for name,model in scores.items():
                self.assertAlmostEqual(model['predicted_mean_gross_switches'],x)

    def test_original_target_stability_gap_is_not_deceptively_closed(self):
        r=self.load('r62_legal_one_step_results.json')
        a=r['post_R61_legal_competitors']['nested_adaptive']['with_joint_hidden_state']['scored']
        observed=a['independent']['at_four_no_switch_observed']
        self.assertTrue(.30<observed<.35)
        self.assertLess(a['independent']['at_four_no_switch_predicted'],observed)
        self.assertEqual(a['legal_pause_joint']['train_only_q_counts'],{'0.0':24})

    def test_closed_loop_source_population_separate_from_one_step(self):
        r=self.load('r62_legal_rollout_observed.json')
        self.assertEqual(r['groups'],96)
        self.assertEqual(r['sessions'],24)
        self.assertEqual(r['reps'],64)
        self.assertLess(r['models']['legal_independent']['group_total_congestion_MSE'],r['models']['r61_current_only']['group_total_congestion_MSE'])

    def test_alternative_seed_reverses_small_common_shock_advantage(self):
        a=self.load('r62_legal_rollout_observed.json')['models']
        b=self.load('r62_legal_rollout_seed2.json')['models']
        self.assertLess(a['legal_common_shock_joint']['group_total_congestion_MSE'],a['legal_independent']['group_total_congestion_MSE'])
        self.assertGreater(b['legal_common_shock_joint']['group_total_congestion_MSE'],b['legal_independent']['group_total_congestion_MSE'])

    def test_forecast_MSE_polynomial_is_finite(self):
        r=self.load('r62_legal_rollout_observed.json')
        for model in r['models'].values():
            coeff=model['resource_cost_forecast_MSE_A_B_D']
            for k in ('A','B','D'):
                self.assertTrue(math.isfinite(coeff[k]))
            self.assertGreaterEqual(coeff['A'],0)
            self.assertGreaterEqual(coeff['D'],0)

if __name__=='__main__':unittest.main()
