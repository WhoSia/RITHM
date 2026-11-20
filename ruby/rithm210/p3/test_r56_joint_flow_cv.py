"""Source-free R56 predictive pipeline tests (never require original human CSV)."""
import unittest
from math import isfinite
from r56_joint_flow_cv import (
    flow_support, independent_flow, joint_flow_smooth,
    loss, train_counts, infer_laws, leave_one_session_out,
)


class R56JointFlowCVTests(unittest.TestCase):
    def test_valid_flow_support_all_occupancies(self):
        for a in range(7):
            states=flow_support(a)
            self.assertEqual(len(states),(a+1)*(7-a))
            self.assertTrue(all(0<=u<=6-a and 0<=d<=a for u,d in states))
        with self.assertRaises(ValueError):flow_support(7)

    def test_binomial_is_a_proper_joint_law_with_zero_exposure_edges(self):
        for a in range(7):
            law=independent_flow(a,0.15,0.40)
            self.assertAlmostEqual(sum(law.values()),1,places=12)
            self.assertTrue(all(p>0 for p in law.values()))
            self.assertAlmostEqual(sum(d*p for (u,d),p in law.items()), a*0.15,places=12)
            self.assertAlmostEqual(sum(u*p for (u,d),p in law.items()), (6-a)*0.40,places=12)
        with self.assertRaises(ValueError):independent_flow(4,0,0.5)

    def test_saturated_smoother_has_support_for_unseen_joint_events(self):
        train={ (4,0,0):100, (4,1,1):2 }
        law=joint_flow_smooth(4,train)
        self.assertAlmostEqual(sum(law.values()),1)
        self.assertGreater(law[(2,2)],0)
        self.assertGreater(law[(0,0)],law[(2,2)])
        self.assertTrue(all(isfinite(v) for v in loss(law,(1,1))))

    @staticmethod
    def toy_data():
        # Session IDs are fictitious; no original observation is ever included.
        rows=[]
        for session in range(1,5):
            for trt in (1,2,3):
                for t in range(1,15):
                    a=(session+t+trt)%5+1
                    d=int(t%3==0 and a>0)
                    u=int(t%4==0 and a<6)
                    rows.append((session,trt,a,u,d))
        return rows

    def test_loso_session_fold_and_exact_same_targets(self):
        rows=self.toy_data()
        count=train_counts(rows)
        self.assertEqual(sum(count.values()),len(rows))
        laws=infer_laws(count,1)
        self.assertEqual(set(laws),{'pooled_independent','state_independent','joint_laplace'})
        for name,m in laws.items():
            for a,dist in m.items():
                self.assertEqual(set(dist),set(flow_support(a)))
                self.assertAlmostEqual(sum(dist.values()),1,places=10)
        res=leave_one_session_out(rows,bootstrap=100,seed=12)
        self.assertEqual(res['session_count'],4)
        self.assertEqual(res['transition_count'],len(rows))
        self.assertEqual(len(res['paired_session_resampling']),6)
        for row in res['models'].values():
            self.assertTrue(all(isfinite(v) for v in row.values()))
        self.assertEqual(res,leave_one_session_out(rows,bootstrap=100,seed=12))

    def test_strict_source_free_fold_boundary_and_validation(self):
        rows=self.toy_data()
        # The first session cannot leak into its own train counts.
        held=1
        training=train_counts([r for r in rows if r[0]!=held])
        held_only=train_counts([r for r in rows if r[0]==held])
        full=train_counts(rows)
        key=next(iter(held_only))
        self.assertEqual(training[key]+held_only[key],full[key])
        with self.assertRaisesRegex(ValueError,'three'):
            leave_one_session_out(rows[:14],bootstrap=2)
        with self.assertRaisesRegex(ValueError,'bootstrap'):
            leave_one_session_out(rows,bootstrap=0)


if __name__=='__main__':unittest.main()
