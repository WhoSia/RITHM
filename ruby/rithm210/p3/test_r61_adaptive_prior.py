"""R61 synthetic-only falsification tests: no original human data needed."""
import math,copy,unittest
from collections import defaultdict
from r61_adaptive_prior import (TAUS,prior_weight,adaptive_probability,
    summarize_session_bases,base_without,get_pbase,inner_select,get_predictions,
    score_predictions,bootstrap_comparison,run)
from r60_cross_segment import events_from_histories,fit_training_base,pbase,prob


def synthetic_people():
    people={}
    for sess in range(1,25):
        for group in (1,2):
            for actor in range(6):
                ident=100*group+actor
                for section in (2,3,4):
                    hist={};route=(actor+section+group+sess)%2
                    for t in range(1,41):
                        if t>1 and ((t*7+actor*11+section*3+sess)%[3,5,11,19,13,7][actor]==0):
                            route=1-route
                        hist[t]=(route,int(section!=2 and actor%2==0),section-1,group)
                    people[sess,section,ident]=hist
    return people


class R61Gates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.people=synthetic_people()
        cls.events,cls.groups=events_from_histories(cls.people)
        cls.bys=defaultdict(list)
        for e in cls.events:cls.bys[e['session']].append(e)
        cls.totals=summarize_session_bases(cls.events)
        cls.predictions,cls.selected,_=get_predictions(cls.events)

    def test_legal_exact_source_shape(self):
        self.assertEqual(len(self.events),22464)
        self.assertEqual(len(self.groups),3744)
        self.assertEqual(len(self.selected),24)

    def test_tau_limits_and_invalid_exposure(self):
        self.assertEqual(prior_weight(0,2),1)
        self.assertEqual(prior_weight(30,0),0)
        self.assertEqual(prior_weight(200,math.inf),1)
        self.assertLess(prior_weight(12,8),prior_weight(2,8))
        for x in (-1,1.5):
            with self.assertRaises(ValueError):prior_weight(x,8)
        with self.assertRaises(ValueError):prior_weight(1,9)

    def test_fixed_memory_equivalence_to_r60(self):
        s=1;e=self.bys[s][12];f=fit_training_base(self.events,s)
        b=get_pbase(e,base_without(self.totals,{s}))
        self.assertAlmostEqual(b,pbase(e,f),places=14)
        self.assertAlmostEqual(adaptive_probability(e,b,0),prob(e,f,'current_only'),places=14)
        self.assertAlmostEqual(adaptive_probability(e,b,math.inf),prob(e,f,'own_prior_plus_current'),places=14)

    def test_inner_excludes_both_sessions(self):
        s=1;v=base_without(self.totals,{1,2})
        self.assertNotEqual(v,base_without(self.totals,{2}))
        self.assertEqual(v,base_without(self.totals,{2,1}))
        with self.assertRaises(ValueError):base_without(self.totals,{999})

    def test_inner_hyperparameter_has_no_outer_outcome_access(self):
        original=self.selected[1]
        changed=[dict(e,flip=1-e['flip']) if e['session']==1 else e for e in self.events]
        by=defaultdict(list)
        for e in changed:by[e['session']].append(e)
        modified,inner=inner_select(by,summarize_session_bases(changed),1)
        self.assertEqual(original,modified)
        self.assertEqual(set(inner),{str(x) for x in TAUS})

    def test_current_label_mutation_never_changes_own_prediction(self):
        e=self.bys[1][0];b=get_pbase(e,base_without(self.totals,{1}))
        for t in TAUS:
            self.assertEqual(adaptive_probability(e,b,t),adaptive_probability(dict(e,flip=1-e['flip']),b,t))

    def test_inner_validation_excludes_outer_features_and_labels(self):
        changed=[dict(e,own_count=(e['own_count']+1)%40,flip=1-e['flip'],
                      current_count=0) if e['session']==1 else e for e in self.events]
        by=defaultdict(list)
        for e in changed:by[e['session']].append(e)
        fixed,inner=inner_select(by,summarize_session_bases(changed),1)
        self.assertEqual(fixed,self.selected[1])

    def test_same_synthetic_run_reproduces_all_predictions(self):
        pred,selected,_=get_predictions(self.events)
        self.assertEqual(selected,self.selected)
        self.assertEqual(pred,self.predictions)

    def test_probability_is_valid_for_all_realistic_taus(self):
        for e,models in self.predictions[::43]:
            self.assertTrue(all(0<p<1 for p in models.values()))
        with self.assertRaises(ValueError):adaptive_probability(self.events[0],.5,2,shrink=0)

    def test_scoring_uses_session_level_means_and_legal_groups(self):
        scores,loss=score_predictions(self.predictions)
        self.assertEqual(len(loss),24)
        self.assertEqual(sum(x['current_only'][3] for x in loss.values()),3744)
        self.assertGreater(scores['nested_adaptive']['equal_session_group_joint_logloss'],0)

    def test_outcomes_after_test_period_do_not_change_scored_feature(self):
        sample=[(e,p) for e,p in self.predictions if e['period'] in range(2,7)]
        scores,_=score_predictions(sample)
        full,_=score_predictions(self.predictions,periods=range(2,7))
        self.assertEqual(scores,full)

    def test_session_bootstrap_paired_is_deterministic(self):
        _,loss=score_predictions(self.predictions)
        a=bootstrap_comparison(loss,alternative='nested_adaptive',reps=32)
        b=bootstrap_comparison(loss,alternative='nested_adaptive',reps=32)
        self.assertEqual(a,b)
        self.assertEqual(a['n_sessions'],24)
        with self.assertRaises(ValueError):bootstrap_comparison(loss,alternative='foobar',reps=3)

    def test_sha_gate_rejects_missing_human_zip(self):
        with self.assertRaises(Exception):run('/private/source_not_provided.zip',reps=3)

if __name__=='__main__':unittest.main()

class R61SourceFreeStrata(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        events,_=events_from_histories(synthetic_people())
        cls.predictions,_,_=get_predictions(events)

    def test_strata_sum_to_full_cohort(self):
        from r61_subgroups import stratified_actor_scores
        strata=stratified_actor_scores(self.predictions,reps=16)
        self.assertEqual(strata['information_status_changed']['actor_decisions']+
                         strata['information_status_unchanged']['actor_decisions'],22464)
        self.assertEqual(strata['target_section_3']['actor_decisions'],11232)
        self.assertEqual(strata['target_section_4']['actor_decisions'],11232)

    def test_strata_only_emit_aggregate_without_actor_ids(self):
        from r61_subgroups import stratified_actor_scores
        strata=stratified_actor_scores(self.predictions,reps=16)
        for v in strata.values():
            self.assertEqual(set(v),{'actor_decisions','equal_session_actor_logloss',
                                     'adaptive_minus_online_nats','session_resampling_95_descriptive'})
