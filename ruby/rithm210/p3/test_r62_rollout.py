import unittest
from collections import defaultdict
from r62_rollout import forecast_step,rollout,MODELS


def fixture():
    group={'initial_route':[1,1,1,1,0,0],
           'actors':[[{'treatment':1,'info':0,'own_count':8,'previous_route':1 if i<4 else 0}]
                     for i in range(6)]}
    base={(1,0,1):[30,100],(1,0,0):[25,100],(1,0):[55,200]}
    uniforms=[(.5,(.1,.2,.3,.4,.5,.6))]*40
    return group,base,uniforms

class AutonomousSourceFree(unittest.TestCase):
    def test_hidden_state_freezes_all_six_when_seed_within_q(self):
        g,b,c=fixture()
        p=forecast_step(g['initial_route'],[0]*6,[x[0] for x in g['actors']],b,2,'at_four_stability',.2,(.02,(.0,)*6))
        self.assertEqual(p,[0]*6)

    def test_pause_at_four_inactive_off_state(self):
        g,b,c=fixture();old=[1,1,1,0,0,0]
        a=forecast_step(old,[0]*6,[x[0] for x in g['actors']],b,2,'independent',0,(.02,(.1,)*6))
        d=forecast_step(old,[0]*6,[x[0] for x in g['actors']],b,2,'at_four_stability',.3,(.02,(.1,)*6))
        self.assertEqual(a,d)

    def test_late_pause_has_no_early_effect(self):
        g,b,c=fixture()
        for t in (2,10,20):
            self.assertEqual(forecast_step(g['initial_route'],[0]*6,[x[0] for x in g['actors']],b,t,'independent',0,(.01,(.3,)*6)),
                forecast_step(g['initial_route'],[0]*6,[x[0] for x in g['actors']],b,t,'late_four_stability',.4,(.01,(.3,)*6)))

    def test_closed_loop_ignores_future_observed_human_history(self):
        g,b,c=fixture()
        expected=rollout(g,b,'at_four_stability',.2,c)
        for hist in g['actors']:hist.extend([{'flip':1,'secret_future_route':1}]*39)
        self.assertEqual(expected,rollout(g,b,'at_four_stability',.2,c))

    def test_40_period_route_and_gross_consistency(self):
        g,b,c=fixture()
        for m in MODELS:
            C,G,traj=rollout(g,b,m,.2,c)
            self.assertEqual(len(traj),40)
            self.assertEqual(C,sum(3*(a-4)**2 for a,_ in traj))
            self.assertEqual(G,sum(ch for _,ch in traj[1:]))
            self.assertGreaterEqual(G,0)

    def test_fair_start_is_disjoint_from_observed(self):
        g,b,c=fixture()
        c[0]=(.5,(.1,)*6)
        self.assertNotEqual(rollout(g,b,'independent',0,c,start='fair')[2][0][0],
                            rollout(g,b,'independent',0,c,start='observed')[2][0][0])

    def test_invalid_future_uniforms_rejected(self):
        g,b,c=fixture()
        with self.assertRaises(ValueError):rollout(g,b,'independent',0,c[:-1])
        with self.assertRaises(ValueError):forecast_step(g['initial_route'],[0]*6,[x[0] for x in g['actors']],b,2,'independent',0,(.2,(2.,)*6))

if __name__=='__main__':unittest.main()
