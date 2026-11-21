import unittest
from copy import deepcopy
from math import log,exp
import numpy as np
from r62_legal_feedback import stratum,attach_legal_features
from r62_statecal import fit_logit_shift,sigmoid
from r62_legal_rollout import legal_rollout,source_values,MODELS


def fixture():
    routes=[1,1,1,1,0,0]
    actors=[];values=[]
    for i,r in enumerate(routes):
        actors.append([{'actor':i,'treatment':1,'info':0,'previous_route':r,'own_count':7}])
        cost=4 if r else 4
        values.append({t:(13.0,9.0 if t==1 else 0.,r) for t in range(1,41)})
    group={'initial_route':routes,'actors':actors}
    trained={(1,0,1):[24,100],(1,0,0):[24,100],(1,0):[48,200]}
    offset={k:0.1*(k-4) for k in range(9)}
    coins=[(.5,tuple(.1*i for i in range(6))) for _ in range(40)]
    return group,trained,offset,values,coins

class LawfulFeedbackTest(unittest.TestCase):
    def test_only_actual_previous_reward_and_tenure_in_strata(self):
        e={'lagged_own_payoff':3.5,'legal_route_streak':1}
        self.assertEqual(stratum(e,'payoff_tenure_9'),0)
        e['lagged_own_payoff']=5.2;e['legal_route_streak']=3
        self.assertEqual(stratum(e,'payoff_tenure_9'),4)
        e['lagged_own_payoff']=11.0;e['legal_route_streak']=9
        self.assertEqual(stratum(e,'payoff_tenure_9'),8)

    def test_payoff_bins_strict_edges(self):
        e={'lagged_own_payoff':4.,'legal_route_streak':4}
        self.assertEqual(stratum(e,'payoff_3'),1)
        self.assertEqual(stratum(e,'tenure_3'),2)
        e['lagged_own_payoff']=8.
        self.assertEqual(stratum(e,'payoff_3'),2)

    def test_stratum_rejects_unregistered_model(self):
        with self.assertRaises(ValueError):stratum({'lagged_own_payoff':1,'legal_route_streak':1},'other_group_occupancy')

    def test_intercept_calibration_matches_train_target_on_synthetic(self):
        pp=np.array([.1,.2,.3,.4,.5,.6]);yy=np.array([0,0,0,1,1,1]);delta=fit_logit_shift(pp,yy)
        posterior=sigmoid(np.log(pp/(1-pp))+delta)
        self.assertAlmostEqual(np.mean(posterior),(yy.sum()+.5)/(len(yy)+1),places=8)

    def test_generated_future_value_cannot_change_current_decision(self):
        group,b,off,values,coins=fixture()
        a=legal_rollout(group,b,8,off,'legal_independent',0,coins,values)
        new=deepcopy(values)
        for d in new:d[40]=(100000.,d[40][1],d[40][2])
        self.assertEqual(a,legal_rollout(group,b,8,off,'legal_independent',0,coins,new))

    def test_authorized_value_tape_is_required(self):
        with self.assertRaises((ValueError,FileNotFoundError)):
            source_values('/mnt/data/nonexistent_unapproved_source.zip')

    def test_future_recorded_actor_actions_are_not_simulation_input(self):
        group,b,off,values,coins=fixture()
        before=legal_rollout(group,b,8,off,'legal_pause_stability',.1,coins,values)
        for actor in group['actors']:
            actor.append({'RouteA_future':999,'flip_future':999})
        self.assertEqual(before,legal_rollout(group,b,8,off,'legal_pause_stability',.1,coins,values))

    def test_simultaneous_group_choices_match_cost_identity(self):
        group,b,off,values,coins=fixture()
        for m in MODELS:
            C,G,traj=legal_rollout(group,b,8,off,m,.1,coins,values)
            self.assertEqual(C,sum(3*(a-4)**2 for a,sw in traj))
            self.assertEqual(G,sum(sw for a,sw in traj))
            self.assertEqual(len(traj),40)

if __name__=='__main__':unittest.main()
