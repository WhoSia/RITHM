"""R34 source-free contract tests for payoff permutation falsification and R30 API."""
import unittest
import numpy as np
from r33_within_partial_payoff_learning import personal_online_signals,design
from r34_payoff_selection_placebo import (swap_conditional_payoffs,features,
                                            bootstrap,eval_session)
from r30_partial_dynamic_joint import joint_scores


def fake_group():
    rows=[]
    for i in range(6):
        y=int(i>=3)
        rows.append((y,3,float(1+i),int(i%2),int((i+1)%2)))
    return tuple(rows)


def fake_source():
    group=fake_group()
    mem=[[] for _ in range(6)]
    vals=[]
    contexts=[(0.,0.,0.,0.)]*6
    traits=[(0.,0.)]*6
    for t in range(2,41):
        # Change the actual previous payoff across periods so sham has a nontrivial effect.
        rows=tuple((r[0],r[1],r[2]+(t-2)/10,r[3],r[4]) for r in group)
        for i,r in enumerate(rows):mem[i].append((r[0],r[2]))
        online=[personal_online_signals(x) for x in mem]
        vals.append((t,rows,contexts,traits,online))
    return {111:vals}


class R34UnitTests(unittest.TestCase):
    def test_sham_payoff_preserves_choice_and_group_route_cost(self):
        orig=fake_source();sham,meta=swap_conditional_payoffs(orig,34001)
        self.assertGreater(meta['changed_actor_periods'],0)
        for a,b in zip(orig[111],sham[111]):
            self.assertEqual(a[0],b[0]);self.assertEqual(a[1],b[1])
            for h_old,h_sham in zip(a[4],b[4]):
                self.assertAlmostEqual(h_old[0],h_sham[0])
        self.assertNotEqual(orig[111][-1][4],sham[111][-1][4])
    def test_sham_future_payoff_never_changes_earlier_states(self):
        orig=fake_source();altered=fake_source()
        # At t=40 only, alter prior period's source payoff; t<40 must stay untouched.
        t,rows,ctx,traits,online=altered[111][-1]
        edited=tuple((r[0],r[1],r[2]+100,r[3],r[4]) for r in rows)
        altered[111][-1]=(t,edited,ctx,traits,online)
        s1,_=swap_conditional_payoffs(orig,34002)
        s2,_=swap_conditional_payoffs(altered,34002)
        for a,b in zip(s1[111][:-1],s2[111][:-1]):
            self.assertEqual(a[4],b[4])
    def test_sham_determinism_and_seed_variation(self):
        data=fake_source()
        a,ma=swap_conditional_payoffs(data,34001)
        b,mb=swap_conditional_payoffs(data,34001)
        c,mc=swap_conditional_payoffs(data,34002)
        self.assertEqual(a[111][-1][4],b[111][-1][4])
        self.assertEqual(ma,mb)
        self.assertNotEqual(a[111][-1][4],c[111][-1][4])
    def test_no_hidden_count_in_uninformed_design(self):
        context=(0.,0.,0.,0.);trait=(.1,1.);online=(.3,.08)
        row=(1,1,4.,0,0)
        other=(1,5,4.,0,1)
        for family in ('within_choice','both'):
            self.assertEqual(design(row,21,family,context,trait,online),
                             design(other,21,family,context,trait,online))
    def test_features_no_current_outcome_column(self):
        data=fake_source();original=features(data,'both')[111][0].copy()
        new=fake_source()
        for i,record in enumerate(new[111]):
            t,rows,ctx,tr,online=record
            edited=tuple((r[0],r[1],r[2],r[3],1-r[4]) for r in rows)
            new[111][i]=(t,edited,ctx,tr,online)
        modified=features(new,'both')[111][0]
        np.testing.assert_allclose(original,modified)
    def test_r30_r31_public_joint_score_api(self):
        # This imported symbol was missing from the posted R30 version before R34.
        v=joint_scores([.3]*6,[0]*6,[0]*6,.2)
        self.assertEqual(len(v),9)
        self.assertTrue(np.all(np.isfinite(v)))
    def test_session_bounded_bootstrap(self):
        diff=np.array([[-.01,-.02]]*24)
        ci=bootstrap(diff)
        self.assertAlmostEqual(ci[0][0],-.01)
        self.assertAlmostEqual(ci[1][1],-.02)
    def test_sham_restricts_group_size(self):
        x=fake_source();t,rows,ctx,tr,online=x[111][0]
        x[111][0]=(t,rows[:5],ctx,tr,online)
        with self.assertRaises(ValueError):swap_conditional_payoffs(x,34001)

if __name__=='__main__':unittest.main()