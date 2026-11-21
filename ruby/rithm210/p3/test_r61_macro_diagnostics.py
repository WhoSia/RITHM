"""R61 source-free macro stability diagnostic contract tests."""
import unittest
from r61_macro_diagnostics import observe_trajectory,gather,normalize,run_diagnostics
from r61_closed_loop import collect_groups
from r61_adaptive_prior import get_predictions
from r60_cross_segment import events_from_histories
from test_r61_adaptive_prior import synthetic_people
from collections import defaultdict

class R61MacroDiagnostics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events,_=events_from_histories(synthetic_people())
        _,cls.selected,_=get_predictions(cls.events)

    def test_observed_numerators_are_independently_reconciled(self):
        grp=collect_groups(self.events)[0]
        traj=observe_trajectory(grp)
        self.assertEqual(len(traj),40)
        self.assertEqual(sum(3*(a-4)**2 for a,g in traj),grp['target_congestion'])
        self.assertEqual(sum(g for a,g in traj),grp['target_gross'])

    def test_source_free_counts_denominators(self):
        rows=[(4,0)]*40
        agg=defaultdict(lambda:defaultdict(float))
        gather(agg,rows)
        norm=normalize(agg)
        self.assertEqual(norm['all']['choice_periods'],40)
        self.assertEqual(norm['all']['optimal_occupancy_4_fraction'],1)
        self.assertEqual(norm['all']['p4_to4_with_no_switch_given_prev4'],1)
        self.assertEqual(norm['first_10']['gross_switches_per_internal_transition'],0)
        self.assertEqual(norm['last_10']['n_from_prior_4_transitions'],10)

    def test_synthetic_diagnostics_never_release_actor_level_records(self):
        out=run_diagnostics(self.events,self.selected,reps=1,seed=5)
        self.assertEqual(out['source_groups'],96)
        self.assertEqual(out['whole_cohort_aggregate_no_original_rows']['source_observed']['all']['choice_periods'],3840)
        self.assertTrue(all('actor' not in str(x).lower() and 'session' not in str(x).lower()
                            for x in out['whole_cohort_aggregate_no_original_rows'].keys()))

if __name__=='__main__':unittest.main()
