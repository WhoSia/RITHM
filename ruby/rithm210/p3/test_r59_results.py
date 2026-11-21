"""Publication contract and risk-neutral welfare sensitivity gates."""
import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

from r59_results import SOURCE,root_on_nonnegative_axis
from r59_closed_loop import fit_folds,simulate

BASE=Path(__file__).parent


class FixedPublicationContract(unittest.TestCase):
    def test_kappa_crossover_is_an_error_ranking_not_resource_value(self):
        base={'A':10,'B':0,'D':0}
        alt={'A':4,'B':5,'D':1}
        self.assertAlmostEqual(root_on_nonnegative_axis(alt,base),1)
        self.assertAlmostEqual(root_on_nonnegative_axis(base,alt),1)
        self.assertIsNone(root_on_nonnegative_axis({'A':12,'B':2,'D':1},base))

    def test_scenario_source_and_actual_treatment_contrasts_unchanged(self):
        result=json.loads((BASE/'r59_results.json').read_text())
        self.assertEqual(result['source_sha256'],SOURCE)
        self.assertEqual((result['cohort']['sessions'],result['cohort']['group_sections'],
                          result['cohort']['group_period_transitions']),(24,144,5616))
        self.assertEqual(len(result['scenarios']),6)
        for s,scenario in result['scenarios'].items():
            self.assertAlmostEqual(scenario['historical_full_minus_no']['total_excess'],-4.75)
            self.assertEqual(scenario['repetitions_per_group'],32)
        self.assertEqual(result['independent_author_table_parity']['un_enriched_extra_20_period_pilot_rows'],360)
        self.assertEqual(result['previous_section_actor_reuse']['linked_actor_section_transitions'],576)

    def test_published_output_has_no_raw_actor_ids_or_participant_rows(self):
        result=json.loads((BASE/'r59_results.json').read_text())
        data=json.dumps(result)
        for key in ('"actor_id"','"session_id"','"participant_id"',
                    '"original_routes"','"private_value_tape"','"session_keys"'):
            self.assertNotIn(key,data)
        self.assertIn('synthetic simulations',result['study_type'])
        self.assertIn('simultaneous six-person',result['filtration'])

    def test_original_raw_sha_gate_rejects_substitute_zip(self):
        with TemporaryDirectory() as dirname:
            file=Path(dirname)/'fake.zip'
            with ZipFile(file,'w') as archive:
                archive.writestr('data_task_all_switch_230705.csv','invalid')
            with self.assertRaisesRegex(ValueError,'SHA256'):
                fit_folds(file)

    def test_simulation_rejects_untrained_or_unknown_models(self):
        from test_r59_closed_loop import synthetic_record
        rec=synthetic_record()
        with self.assertRaisesRegex(ValueError,'missing trained'):
            simulate(rec,model='private_history')
        with self.assertRaisesRegex(ValueError,'unknown simulation model'):
            simulate(rec,model='future_planner')
        with self.assertRaisesRegex(ValueError,'invalid shocks'):
            simulate(rec,model='ewa_lite',shocks='peek_future')


if __name__=='__main__':unittest.main()
