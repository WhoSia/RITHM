"""R61 source-free identity, rollout and 3-observation causal rival boundaries."""
import copy,math,unittest
from fractions import Fraction as F
from r61_three_segment_rival import (type_3_law,markov_3_law,
                                     exact_separation,descriptive_three_sections)
from r61_closed_loop import collect_groups,rollout_one,rollout_score
from r61_matched_identity import build_adaptive_cost_matrices,check_identity_null
from r61_adaptive_prior import get_predictions,events_from_histories,summarize_session_bases,base_without
from test_r61_adaptive_prior import synthetic_people

class R61MacroAndRival(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.people=synthetic_people()
        cls.events,_=events_from_histories(cls.people)
        cls.pred,cls.selected,_=get_predictions(cls.events)
        cls.groups=collect_groups(cls.events)

    def test_finite_exact_all_3_segment_laws_sum_one(self):
        self.assertEqual(sum(type_3_law().values()),F(1))
        self.assertEqual(sum(markov_3_law().values()),F(1))
        self.assertNotEqual(type_3_law(),markov_3_law())

    def test_two_adjacent_equal_but_skipped_third_differs(self):
        o=exact_separation()
        self.assertEqual(o['p_first_equals_third_fixed_type'],'17/25')
        self.assertEqual(o['p_first_equals_third_markov_learning'],'353/625')
        self.assertEqual(o['total_variation_full_three_joint'],'72/625')

    def test_original_style_triples_preserve_24_session_support(self):
        x=descriptive_three_sections(self.people,reps=20)
        self.assertEqual(x['participant_triples'],288)
        self.assertEqual(x['sessions'],24)
        self.assertTrue(all(-1<=p<=1 for p in x['pairwise_pearson'].values()))

    def test_closed_loop_96_group_source_structure(self):
        self.assertEqual(len(self.groups),96)
        self.assertTrue(all(len(g['actors'])==6 for g in self.groups))
        self.assertTrue(all(0<=g['target_gross']<=234 for g in self.groups))

    def test_rollout_fixed_coin_path_is_reproducible(self):
        g=self.groups[0]
        fitting=base_without(summarize_session_bases(self.events),{g['session']})
        coins=[[.75 for _ in range(6)] for _ in range(40)]
        x=rollout_one(g,fitting,self.selected[g['session']],'nested_adaptive',coins)
        y=rollout_one(g,fitting,self.selected[g['session']],'nested_adaptive',coins)
        self.assertEqual(x,y)
        self.assertTrue(x[0]>=0)

    def test_current_generated_selection_ignores_original_future_labels(self):
        g=self.groups[0];fit=base_without(summarize_session_bases(self.events),{g['session']})
        coins=[[.20 for _ in range(6)] for _ in range(40)]
        x=rollout_one(g,fit,self.selected[g['session']],'nested_adaptive',coins)
        copied=copy.deepcopy(g)
        for h in copied['actors']:
            for e in h:e['flip']=1-e['flip']
        self.assertEqual(x,rollout_one(copied,fit,self.selected[g['session']],'nested_adaptive',coins))

    def test_all_coin_zero_ensures_all_flip_and_max_gross(self):
        g=self.groups[0];fit=base_without(summarize_session_bases(self.events),{g['session']})
        coins=[[0. for _ in range(6)] for _ in range(40)]
        c,s=rollout_one(g,fit,self.selected[g['session']],'nested_adaptive',coins)
        self.assertEqual(s,234)
        self.assertTrue(c>=0)

    def test_fair_start_may_diverge_from_observed_start(self):
        g=self.groups[0];fit=base_without(summarize_session_bases(self.events),{g['session']})
        coins=[[.10 for _ in range(6)] for _ in range(40)]
        x=rollout_one(g,fit,self.selected[g['session']],'nested_adaptive',coins,first='fair')
        y=rollout_one(g,fit,self.selected[g['session']],'nested_adaptive',coins,first='observed')
        self.assertEqual(x[1],y[1])
        self.assertNotEqual(x[0],y[0])

    def test_short_rollout_has_96_groups_and_no_published_actor_rows(self):
        report=rollout_score(self.events,self.selected,reps=2,seed=19)
        self.assertEqual(report['group_sections'],96)
        self.assertNotIn('actors',report)
        self.assertEqual(report['model_scores']['nested_adaptive']['resource_mse_kappa_polynomial']['A'],
                         report['model_scores']['nested_adaptive']['congestion_group_total_mse'])

    def test_strict_matched_label_null_is_reproducible(self):
        mats=build_adaptive_cost_matrices(self.events,self.selected)
        report=check_identity_null(mats,reps=16,seed=11)
        self.assertEqual(report,check_identity_null(mats,reps=16,seed=11))
        self.assertEqual(report['num_target_actor_decisions'],22464)
        self.assertNotIn('session',report)

    def test_identity_permutation_two_by_two_expected_mean_exact(self):
        M={'attrs':[(0,0,0,0),(0,0,0,0),(1,1,0,0),(1,1,1,0),(1,1,0,1),(1,1,1,1)],
           'loss_matrix':[[1,3,0,0,0,0],[4,2,0,0,0,0]]+[[10]*6 for _ in range(4)]}
        z=check_identity_null([M],reps=3,seed=1)
        # exact mean for first pair is (1+3+4+2)/2=5; four constants 10 each.
        self.assertEqual(z['exact_null_mean_logloss'],(5+40)/(6*39))

if __name__=='__main__':unittest.main()
