"""Report assertions on original-source-derived *aggregate only* fixture, not source replay."""
from pathlib import Path
import json,unittest

ROOT=Path(__file__).parent

class R60ResultContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'r60_results.json').read_text())
        cls.placebo=json.loads((ROOT/'r60_identity_placebo.json').read_text())

    def test_original_sha_and_closed_population(self):
        x=self.data
        self.assertEqual(x['original_zip_sha256'],'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953')
        self.assertEqual((x['sessions'],x['linked_actor_section_pairs'],x['target_actor_decisions'],x['target_group_transitions']),(24,576,22464,3744))

    def test_identity_specific_predictability_and_null_gate(self):
        x=self.data['model_scores']
        self.assertLess(x['own_prior']['equal_session_actor_logloss'],x['base']['equal_session_actor_logloss'])
        self.assertGreater(x['other_five_prior']['equal_session_actor_logloss'],x['base']['equal_session_actor_logloss'])
        for control in ('group','same_information','same_information_and_boundary_route'):
            p=self.placebo[control]
            self.assertGreater(p['permutation_null_exact_mean'],p['observed_actor_logloss'])
            self.assertEqual(p['actor_decisions'],22464)

    def test_temporal_rank_reversal_and_no_overclaim(self):
        x=self.data['early_late_paired_compared_to_current']
        earlier=x['early_2_6']['own_prior_plus_current']['actor_logloss']
        later=x['late_21_40']['own_prior_plus_current']['actor_logloss']
        self.assertLess(earlier['session_resampling_95_descriptive'][1],0)
        self.assertGreater(later['session_resampling_95_descriptive'][0],0)
        full=self.data['against_current_only']['own_prior_plus_current']['actor_logloss']
        self.assertLess(full['session_resampling_95_descriptive'][0],0)
        self.assertGreater(full['session_resampling_95_descriptive'][1],0)
        self.assertIn('not',self.data['caveats'].lower())

    def test_private_source_and_id_rows_absent_from_published_results(self):
        for name in ('r60_results.json','r60_identity_placebo.json'):
            s=(ROOT/name).read_text()
            for forbidden in ('"actor_id"','"participant_id"','"individual_rows"','"source_csv_rows"','"session_id"','"human_route_vector"'):
                self.assertNotIn(forbidden,s)
        self.assertEqual(len(self.placebo['exact_rival']['pairs']),4)

if __name__=='__main__':unittest.main()
