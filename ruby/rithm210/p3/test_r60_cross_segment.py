"""Source-free R60 regression gates; no original participant rows are included."""
import copy
import math
import unittest
from fractions import Fraction as F
from r60_cross_segment import (events_from_histories,fit_training_base,pbase,prob,
                               poisson_binomial,group_flow_law,score_events,run)
from r60_latent_rival import fixed_type_law,history_learning_law,exact_nonidentification


def synthetic_people():
    people={}
    for sess in range(1,25):
        for group in (1,2):
            for ident in range(6):
                actor=100*group+ident
                for section in (2,3,4):
                    # Actor 0 has a distinctive HIGH prior flipping rate, actor
                    # 1 low flipping rate: same-group-other null is not actor ID.
                    routes={}
                    for t in range(1,41):
                        if ident==0: r=(t+section)%2
                        elif ident==1:r=1
                        else:r=(ident+group+sess)%2
                        routes[t]=(r,int(section>=3 and ident%2==0),section-1,group)
                    people[sess,section,actor]=routes
    return people


class ExactMechanismRival(unittest.TestCase):
    def test_two_segment_joint_laws_match_cell_by_cell(self):
        x=fixed_type_law();y=history_learning_law()
        self.assertEqual(x,y)
        self.assertEqual(x, {(0,0):F(17,50),(0,1):F(4,25),
                             (1,0):F(4,25),(1,1):F(17,50)})
        self.assertEqual(exact_nonidentification()['match_probability'],'17/25')

    def test_only_two_segment_summary_claimed(self):
        self.assertIn('three segments',exact_nonidentification()['not_equivalent'])


class SourceFreeHistory(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.people=synthetic_people()
        cls.events,cls.groups=events_from_histories(cls.people)

    def test_exact_matched_group_and_actor_support(self):
        self.assertEqual(len(self.events),22464)
        self.assertEqual(len(self.groups),3744)
        self.assertTrue(all(len(g)==6 for g in self.groups.values()))
        self.assertEqual(len({e['session'] for e in self.events}),24)
        self.assertTrue(all(e['section'] in (3,4) and 2<=e['period']<=40
                            for e in self.events))

    def test_prior_actor_excludes_future_target_labels(self):
        e=next(e for e in self.events if e['period']==2 and e['actor']==100)
        self.assertEqual(e['own_count'],39)
        self.assertEqual(e['current_count'],0)
        self.assertEqual(e['current_exposure'],0)
        later=next(e for e in self.events if e['period']==11 and e['actor']==100 and
                   e['session']==e['session'] and e['section']==e['section'] and e['group']==e['group'])
        self.assertEqual(later['current_exposure'],9)
        self.assertEqual(later['own_count'],39)

    def test_other_five_excludes_actor_history(self):
        e=next(e for e in self.events if e['period']==2 and e['actor']==100)
        self.assertEqual(e['other_count'],0)
        self.assertEqual(e['own_count'],39)

    def test_session_holdout_training_independent_of_held_labels(self):
        fit=fit_training_base(self.events,1)
        changed=[dict(e, flip=1-e['flip']) if e['session']==1 else e for e in self.events]
        self.assertEqual(dict(fit_training_base(changed,1)),dict(fit))
        self.assertNotEqual(dict(fit_training_base(changed,2)),dict(fit_training_base(self.events,2)))

    def test_next_outcome_does_not_enter_current_prediction(self):
        e=self.events[0];train=fit_training_base(self.events,e['session'])
        before={n:prob(e,train,n,20) for n in ('base','own_prior','current_only','own_prior_plus_current')}
        after=dict(e,flip=1-e['flip'])
        self.assertEqual(before,{n:prob(after,train,n,20) for n in before})

    def test_period_t_current_exposure_does_not_include_t(self):
        actor=next(e for e in self.events if e['period']==2 and e['actor']==100)
        next_e=next(e for e in self.events if e['period']==3 and e['actor']==100 and
                    e['session']==actor['session'] and e['section']==actor['section'] and e['group']==actor['group'])
        self.assertEqual(next_e['current_count'],actor['flip'])

    def test_six_person_count_law_matches_direct_combinatorics(self):
        g=next(iter(self.groups.values()));p=[.3]*6
        law=group_flow_law(g,p)
        self.assertAlmostEqual(sum(law.values()),1,places=12)
        self.assertEqual(len(law),(1+sum(e['previous_route']==0 for e in g))*(1+sum(e['previous_route']==1 for e in g)))
        for (u,d),m in law.items():
            a=sum(e['previous_route'] for e in g)
            expected=math.comb(6-a,u)*(.3**u)*(.7**(6-a-u))*math.comb(a,d)*(.3**d)*(.7**(a-d))
            self.assertAlmostEqual(m,expected,places=12)

    def test_shrinkage_fail_closed(self):
        train=fit_training_base(self.events,1);e=self.events[0]
        for k in (-1,0,1.5):
            with self.assertRaises(ValueError):prob(e,train,'own_prior',k)
        with self.assertRaises(ValueError):prob(e,train,'unknown',20)

    def test_route_only_base_is_not_using_actor_id(self):
        e=self.events[0];train=fit_training_base(self.events,e['session'])
        alternate=dict(e,actor=999,own_count=0,recent_count=0,other_count=0,current_count=0)
        self.assertEqual(pbase(e,train),pbase(alternate,train))

    def test_source_gate_rejects_missing_private_original(self):
        with self.assertRaises(Exception):run('/nonexistent/author_approved.zip')

    def test_both_scores_positive_and_reproducible_on_synthetic(self):
        first,_=score_events(self.events,strength=20,test_periods=range(2,7))
        second,_=score_events(self.events,strength=20,test_periods=range(2,7))
        self.assertEqual(first,second)
        self.assertTrue(all(v['equal_session_actor_logloss']>0 and
                            v['equal_session_group_joint_logloss']>0 for v in first.values()))


if __name__=='__main__':unittest.main()
