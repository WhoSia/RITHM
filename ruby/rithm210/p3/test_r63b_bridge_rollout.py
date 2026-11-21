"""Synthetic-only legal closed-loop checks; NO original human source included."""
import copy
import tempfile
from pathlib import Path
import unittest
from r63b_bridge_rollout import cost, payoff, simulate, original_group_cost, read_private_tapes


def fixture():
    routes=[1,1,1,1,0,0]
    people=[{'actor':i,'info':int(i>=3),'prior_flips':6,'period':2} for i in range(6)]
    tapes=[{t:(r,13.,9.) for t in range(1,41)} for r in routes]
    model={'tau':8,'base':{(inf,r):.2 for inf in (0,1) for r in (0,1)},
           'shifts':{(inf,b):0. for inf in (0,1) for b in range(9)},
           'support':{(inf,b):100 for inf in (0,1) for b in range(9)}}
    coins=[tuple([.999]*6) for t in range(40)]
    return people, {0:model,1:model},tapes,coins


class ClosedLoopSafetyTest(unittest.TestCase):
    def test_source_cost_range_exact(self):
        self.assertEqual([cost(a) for a in range(7)], [48,27,12,3,0,3,12])
        with self.assertRaises(ValueError):cost(-1)
        with self.assertRaises(ValueError):cost(7)

    def test_realized_own_payoff_only(self):
        self.assertEqual(payoff(13,4,1),9)
        self.assertEqual(payoff(13,4,0),9)
        self.assertEqual(payoff(13,5,1),8)
        self.assertEqual(payoff(13,5,0),11)

    def test_no_unnecessary_motion_when_all_uniforms_high(self):
        g,m,t,c=fixture()
        self.assertEqual(simulate(g,m,t,c),(0,0,40,39,39))

    def test_all_six_flip_simultaneously_and_t40_is_last(self):
        g,m,t,c=fixture()
        for i in range(1,40):c[i]=tuple([0.]*6)
        C,G,numberA4,old4,stay=simulate(g,m,t,c)
        self.assertEqual((C,G,numberA4,old4,stay),(240,234,20,20,0))

    def test_mutating_value40_cannot_affect_any_decision(self):
        g,m,t,c=fixture()
        x=simulate(g,m,t,c)
        future=copy.deepcopy(t)
        for item in future:item[40]=(0,9999999.,-9999.)
        self.assertEqual(x,simulate(g,m,future,c))

    def test_future_recorded_routes_cannot_leak_into_simulated_policy(self):
        g,m,t,c=fixture()
        y=copy.deepcopy(t)
        for item in y:
            for n in range(2,41):
                x=item[n];item[n]=(1-x[0],x[1],x[2])
        self.assertEqual(simulate(g,m,t,c),simulate(g,m,y,c))

    def test_original_horizon_consistency(self):
        g,m,t,c=fixture()
        self.assertEqual(original_group_cost(t),(0,0,40,39,39))
        t[0][1]=(1,13.,200.)
        with self.assertRaisesRegex(ValueError,'reward inconsistency'):simulate(g,m,t,c)

    def test_fair_start_changes_initial_state_but_not_information_rule(self):
        g,m,t,c=fixture()
        self.assertEqual(simulate(g,m,t,c,start='fair'),(1920,0,0,0,0))

    def test_memory_clock_contract_and_group_size(self):
        g,m,t,c=fixture()
        with self.assertRaisesRegex(ValueError,'memory-clock'):simulate(g,m,t,c,tau=16)
        with self.assertRaises(ValueError):simulate(g[:5],m,t,c)

    def test_reject_unapproved_original_before_open(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d,'x.zip');p.write_bytes(b'invalid')
            with self.assertRaisesRegex(ValueError,'SHA'):read_private_tapes(p)

if __name__=='__main__':unittest.main()
