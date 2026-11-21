"""Source-free R57 invariants: exact R56 baseline, hazard, training wall and privacy."""
from copy import deepcopy
from math import isfinite
from fractions import Fraction
import unittest

from r56_joint_flow_cv import train_counts, infer_laws
from r57_history_cv import (MODELS, actor_cell, fitted_laws, forecast_flow,
                            actor_scores, leave_one_session_out, poisson_binomial,
                            tenure_bin, profit_bin, train_histories)
from r57_duration_equivalence import (duration_hazard, exact_check,
                                      mixed_spell_probability,
                                      duration_spell_probability)


def toy(n_sessions=4):
    result=[]
    for s in range(1,n_sessions+1):
        for trt in (1,2,3):
            for t in range(2,23):
                a=2+(t+s)%3
                actors=tuple((int(i<a),1+(t+i)%5,2+(i+t+s)%11,
                              int(trt==3 or (trt==2 and i%2==0)))
                             for i in range(6))
                flips=tuple(int((t+i+s+trt)%7==0) for i in range(6))
                u=sum(flips[i] for i in range(a,6))
                d=sum(flips[i] for i in range(a))
                result.append({'session':s,'trt':trt,'period':t,'a':a,
                               'actors':actors,'flips':flips,'ud':(u,d)})
    return result


class HistoryRegression(unittest.TestCase):
    def test_fixed_bins_and_no_wrong_features(self):
        self.assertEqual([tenure_bin(k) for k in (1,2,3,4,40)], [0,1,1,2,2])
        self.assertEqual([profit_bin(p) for p in (-5,3.9,4,7.9,8,20)],
                         [0,0,1,1,2,2])
        e=toy()[0];actor=e['actors'][0]
        self.assertEqual(actor_cell(e['a'],actor,'state_independent'),(e['a'],actor[0]))
        with self.assertRaisesRegex(ValueError,'unrecognized'):
            actor_cell(e['a'],actor,'future_profit')
        with self.assertRaises(ValueError):tenure_bin(0)

    def test_baseline_exactly_equals_r56_joint_distribution(self):
        data=toy()
        base=fitted_laws(data)
        fitted=train_histories(data)
        for e in data:
            actual=forecast_flow(e,'state_independent',base,fitted)
            expected=base[e['trt']][e['a']]
            for key in expected:
                self.assertAlmostEqual(actual[key],expected[key],places=13)
            for model in MODELS:
                p=forecast_flow(e,model,base,fitted)
                self.assertAlmostEqual(sum(p.values()),1,places=12)
                self.assertTrue(all(0<x<1 for x in p.values()))
        with self.assertRaises(ValueError):poisson_binomial([1])

    def test_folds_never_train_on_held_session_or_current_observation(self):
        data=toy()
        subset=[r for r in data if r['session']!=1]
        trained=train_histories(subset)
        key=(data[0]['trt'],)+actor_cell(data[0]['a'],data[0]['actors'][0],'tenure')
        local=train_histories([r for r in data if r['session']==1])
        full=train_histories(data)
        self.assertEqual(full['tenure'][key]['n'],
                         trained['tenure'][key]['n']+local['tenure'][key]['n'])
        # The reported predictions are independent of the current flips:
        # altering *future/current* outcome must NOT change law at t.
        base=fitted_laws(subset)
        before=forecast_flow(data[0],'tenure_profit',base,trained)
        copy=deepcopy(data[0]);copy['flips']=tuple(1-x for x in copy['flips']);copy['ud']=(0,0)
        self.assertEqual(before,forecast_flow(copy,'tenure_profit',base,trained))

    def test_group_flow_is_invariant_to_within_route_label_permutation(self):
        e={'a':3, 'actors':((1,1,6,0),(1,5,6,0),(1,8,6,0),
                           (0,1,4,0),(0,5,4,0),(0,8,4,0)),
           'flips':(1,0,0,0,1,0), 'ud':(1,1)}
        q=deepcopy(e);q['flips']=(0,1,0,0,1,0)
        # The target U,D is identical, while actor-resolved scoring changes.
        self.assertEqual(e['ud'],q['ud'])
        p=(0.8,0.2,0.2,0.2,0.8,0.2)
        x=actor_scores(e,p)
        y=actor_scores(q,p)
        self.assertLess(x['actor_logloss'],y['actor_logloss'])
        self.assertEqual(x['route_permutation_expected_actor_logloss'],
                         y['route_permutation_expected_actor_logloss'])
        self.assertAlmostEqual(x['route_permutation_expected_actor_logloss'],
                               sum(actor_scores({**e,'flips':bits},p)['actor_logloss']
                                   for bits in ((1,0,0,0,1,0),(1,0,0,0,0,1),
                                                (0,1,0,0,1,0),(0,1,0,0,0,1),
                                                (0,0,1,0,1,0),(0,0,1,0,0,1),
                                                (1,0,0,1,0,0),(0,1,0,1,0,0),
                                                (0,0,1,1,0,0)))/9,places=12)

    def test_source_free_loso_reproducible_and_nan_free(self):
        a=leave_one_session_out(toy(),bootstrap=40,seed=71)
        b=leave_one_session_out(toy(),bootstrap=40,seed=71)
        self.assertEqual(a,b)
        self.assertEqual(a['session_count'],4)
        self.assertEqual(a['transition_count'],252)
        self.assertEqual(set(a['models']),set(MODELS))
        for item in a['models'].values():
            self.assertTrue(all(isfinite(x) for x in item.values()))
        with self.assertRaises(ValueError):leave_one_session_out(toy(2),bootstrap=3)
        with self.assertRaises(ValueError):leave_one_session_out(toy(),bootstrap=0)
        with self.assertRaises(ValueError):leave_one_session_out(toy(),bootstrap=2,shrink=0)

    def test_fixed_type_mixture_spells_look_like_duration_dependence(self):
        self.assertEqual(duration_hazard(1),Fraction(11,40))
        self.assertLess(duration_hazard(5),duration_hazard(1))
        self.assertLess(duration_hazard(10),duration_hazard(5))
        self.assertEqual(mixed_spell_probability((0,0,1,0,1)),
                         duration_spell_probability((0,0,1,0,1)))
        self.assertTrue(exact_check(9)['equal'])
        self.assertEqual(exact_check(9)['cases'],512)
        with self.assertRaises(ValueError):exact_check(13)

if __name__=='__main__':unittest.main()
