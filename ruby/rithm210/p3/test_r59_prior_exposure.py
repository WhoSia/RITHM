"""Adversarial source-free original-cohort and actor-specific continuity tests."""
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import unittest
from math import isfinite

from r59_prior_exposure import _cov,summarize_section_pairs,section_pairs
from r59_independent_replay import _selection,source_parity_aggregate


def fake_pairs():
    people=[]
    for s in range(1,25):
        for sec in ((2,3),(3,4)):
            for g in (1,2):
                for actor in range(6):
                    rate=(actor+1)/10+((s%4)-2)*.002
                    people.append({
                        'session':s,'boundary':sec,'group':g,
                        'prior_rate':rate,
                        'later_rate':max(0,min(1,rate*.8+.02*(g%2))),
                        'prior_terminal':actor%2,'later_initial':actor%2,
                        'prior_last_flip':0,'later_first_flip':0,
                        'info_changed':int(sec==(2,3)),
                        'treatment_changed':1})
    return people


class CohortSourceWalls(unittest.TestCase):
    def test_exact_author_row_selector_and_pilot_distinction(self):
        row={'trt':'1','session':'1','section':'2','Period':'1'}
        self.assertTrue(_selection(row))
        for key,value in (('Period','0'),('trt','4'),('section','1'),
                          ('session','2'),('session','101')):
            bad=dict(row);bad[key]=value
            self.assertFalse(_selection(bad))

    def test_independent_source_refuses_forged_zip(self):
        with TemporaryDirectory() as folder:
            path=Path(folder)/'not_author.zip'
            with ZipFile(path,'w') as z:
                z.writestr('data_task_all_230705.csv','fake')
            with self.assertRaisesRegex(ValueError,'SHA256'):
                source_parity_aggregate(path)

    def test_stable_actor_identity_rises_above_within_six_seat_group_null(self):
        result=summarize_section_pairs(fake_pairs(),permutations=100,seed=22)
        self.assertEqual(result['linked_actor_section_transitions'],576)
        self.assertEqual(result['adjacent_section_pairs'],48)
        self.assertAlmostEqual(result['observed_adjacent_section_actor_rate_pearson'],1,places=2)
        self.assertGreater(result['observed_adjacent_section_actor_rate_pearson'],
                           result['identity_permutation_stable_group_95_descriptive'][1])
        self.assertTrue(all(isfinite(x) for x in result['whole_session_resampling_95_descriptive']))
        self.assertEqual(result['informed_mask_changed_fraction'],.5)

    def test_invalid_permutation_convention_rejected(self):
        with self.assertRaisesRegex(ValueError,'positive permutation'):
            summarize_section_pairs(fake_pairs(),permutations=0)
        with self.assertRaises(ValueError):_cov([0,0],[1,1])


if __name__=='__main__':unittest.main()
