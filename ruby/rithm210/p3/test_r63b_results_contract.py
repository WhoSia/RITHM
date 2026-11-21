"""Immutable public aggregates only; CI never receives restricted original ZIP."""
from hashlib import sha1
from pathlib import Path
import json
import unittest

BASE=Path(__file__).resolve().parent
FROZEN={
  'r63b_legal_bridge_results.json':'e96ee7f89b840ffbd89c05ac5c15f04b57e96d68',
  'r63b_rollout_observed.json':'360a6aa10a7769e6c23bf96ae1b92ced6087ed58',
  'r63b_rollout_seed2.json':'f76719a7ee1b860a4d6719d2e563f6c589afaa33',
  'r63b_rollout_fair.json':'bfd37cc8c20c6f6dd3dafba7427e667bf5f34424',
}

def git_blob(raw):return sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def load_frozen(name):
    if name not in FROZEN:raise ValueError('non-frozen experiment')
    raw=(BASE/name).read_bytes()
    if git_blob(raw)!=FROZEN[name]:raise ValueError('original replay public aggregate has changed')
    return json.loads(raw)


class OriginalDataFreeResultsTest(unittest.TestCase):
    def test_all_four_aggregate_blobs_exact(self):
        for name in FROZEN:
            with self.subTest(name=name):self.assertIsInstance(load_frozen(name),dict)

    def test_one_step_information_and_session_contract(self):
        x=load_frozen('r63b_legal_bridge_results.json')
        self.assertEqual(x['evaluated']['target_bearing_sessions'],17)
        self.assertEqual(x['evaluated']['group_transitions'],1248)
        self.assertEqual(x['evaluated']['actor_decisions'],7488)
        self.assertEqual(x['contract']['heldout_unit'],'entire original session')
        self.assertEqual(x['contract']['tau'],8)
        for m in ('bridge','partial_invariant'):
            self.assertEqual(x['models'][m]['source_strata_lt30_fraction'],0.)
            self.assertEqual(x['models'][m]['old_A4_no_switch_rate_actual'],.3)

    def test_one_step_margins_are_not_overclaimed(self):
        x=load_frozen('r63b_legal_bridge_results.json')
        self.assertGreater(x['models']['bridge']['actor_logloss'],x['models']['partial_invariant']['actor_logloss'])
        self.assertGreater(x['models']['bridge']['joint_U_D_logloss'],x['models']['partial_invariant']['joint_U_D_logloss'])
        for metric in ('actor_logloss','joint_U_D_logloss','old_A4_no_switch_Brier'):
            interval=x['bridge_minus_partial'][metric]['descriptive_session_bootstrap95']
            self.assertLess(interval[0],0)
            self.assertGreater(interval[1],0)

    def test_long_horizon_reversal_three_scenarios(self):
        for name in ('observed','seed2','fair'):
            x=load_frozen('r63b_rollout_'+name+'.json')
            self.assertEqual(x['design']['horizon'],40)
            self.assertEqual(x['design']['target_partial_groups'],32)
            self.assertEqual(x['design']['repetitions'],64)
            self.assertEqual(x['design']['target_bearing_sessions'],17)
            self.assertLess(x['models']['bridge']['group_total_congestion_MSE'],
                            x['models']['partial_invariant']['group_total_congestion_MSE'])
            self.assertLess(x['models']['bridge']['P0_given_old_A4'],x['historical_partial']['P0_given_old_A4'])
            self.assertLess(x['models']['partial_invariant']['P0_given_old_A4'],x['historical_partial']['P0_given_old_A4'])

    def test_confidence_caution_and_no_individual_record_serialization(self):
        for name in FROZEN:
            raw=(BASE/name).read_text()
            for forbidden in ('"ID"','"Subject"','"participant_id"','"session_id"','"personal_trajectory"','"raw_rows"'):
                self.assertNotIn(forbidden,raw)
        x=load_frozen('r63b_rollout_observed.json')
        ci=x['bridge_minus_partial_MSE']['descriptive_session_bootstrap95']
        self.assertLess(ci[1],0)
        self.assertIn('NOT causal',x['scope'])

if __name__=='__main__':unittest.main()
