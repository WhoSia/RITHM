"""RITHM R64A aggregate-only source-free scientific guardrail tests."""
import json
import hashlib
from pathlib import Path
import unittest

DATA=Path(__file__).with_name('r64_size_matched_summary.json')
BLOB='f471b60d460fc640aba8b68e5873bf121e312e19'

def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


class MatchedResultGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=DATA.read_bytes()
        if git_blob(cls.raw)!=BLOB:
            raise ValueError('original-author-derived aggregate summary changed without reviewed SHA update')
        cls.o=json.loads(cls.raw)

    def test_sha_fixed_and_approved_original_reference_only(self):
        self.assertEqual(git_blob(self.raw),BLOB)
        self.assertEqual(len(self.o['source_sha256']),64)

    def test_exact_original_cohort_contract(self):
        c=self.o['population']
        self.assertEqual(c['total_sessions'],24)
        self.assertEqual(c['partial_target_sessions'],17)
        self.assertEqual(c['partial_group_sections'],32)
        self.assertEqual(c['partial_joint_transitions'],1248)

    def test_original_source_sample_size_imbalance(self):
        c=self.o['population']
        self.assertEqual(c['actor_decisions_per_mask_original_source_no_or_full'],7488)
        self.assertEqual(c['actor_decisions_per_partial_mask'],3744)
        self.assertEqual(c['actor_decisions_per_mask_original_source_no_or_full'],
                         2*c['actor_decisions_per_partial_mask'])

    def test_stated_information_and_cluster_constraints(self):
        c=self.o['method']
        for k in ('whole_session_holdout','actor_panel_indivisible_length',
                  'matched_source_panel_count_equals_comparator_partial_count',
                  'panel_selection_without_outcomes',
                  'same_mc_uniform_streams',
                  'original_future_values_seen_only_post_choice'):
            self.assertTrue(c[k] if k!='actor_panel_indivisible_length' else c[k]==39)
        self.assertEqual(c['source_subsample_repetitions'],8)

    def test_original_reference_exact(self):
        x=self.o['baseline']
        self.assertAlmostEqual(x['partial_only']['autonomous_40_group_total_mse'],5546.8125)
        self.assertAlmostEqual(x['unthinned_bridge']['autonomous_40_group_total_mse'],4648.13525390625)

    def test_eight_matched_one_step_losses_are_worse(self):
        baseline=self.o['baseline']['partial_only']['one_step_joint_U_D_logloss']
        r=self.o['matched']
        self.assertEqual(len(r),8)
        self.assertEqual(len(set(x['panel_seed'] for x in r)),8)
        self.assertTrue(all(x['one_step_joint_U_D_logloss']>baseline for x in r))

    def test_three_matched_autonomous_group_mse_better_not_confirmed(self):
        r=[x for x in self.o['matched'] if 'autonomous_40_group_total_mse' in x]
        self.assertEqual(len(r),3)
        baseline=self.o['baseline']['partial_only']['autonomous_40_group_total_mse']
        for x in r:
            self.assertLess(x['autonomous_40_group_total_mse'],baseline)
            low,hi=x['cluster_bootstrap95']
            self.assertLess(low,0)
            self.assertGreater(hi,0)

    def test_no_private_identifiers_or_unsupported_claims(self):
        raw=self.raw.decode()
        for marker in ('"actor_id"','"Subject"','"Value_t"','"person_route_trajectory"',
                       '"per_session_results"'):
            self.assertNotIn(marker,raw)
        self.assertIn('NOT established',self.o['verdict'])
        self.assertIn('reused',self.o['scope'])

    def test_fail_closed_for_changed_public_byte(self):
        self.assertNotEqual(git_blob(self.raw+b' '),BLOB)


if __name__=='__main__':unittest.main()
