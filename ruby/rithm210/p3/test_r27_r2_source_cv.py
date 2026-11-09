"""Source-free holdout firewall tests for R27-R2 source benchmark."""
import unittest
from r27_r2_observable_lag_dynamics import Params
from r27_r2_source_cv import choose,metrics

class TestR27R2Source(unittest.TestCase):
    def test_holdout_outcomes_cannot_change_train_selection(self):
        p=Params(.05);q=Params(.3)
        train=list(range(20));heldout=list(range(20,24))
        scores={(v,s):((1 if v==p else 2),0,0) for v in (p,q) for s in train+heldout}
        self.assertEqual(choose(scores,train,[p,q]),p)
        for s in heldout:
            scores[p,s]=(99999,0,0)
            scores[q,s]=(-99999,0,0)
        self.assertEqual(choose(scores,train,[p,q]),p)
    def test_full_joint_logloss_is_not_occupancy_logloss(self):
        # Synthetic past state and outcome, no private human rows.
        val=metrics((1,0,2,3),Params(.15,1.,0.,0.))
        self.assertEqual(len(val),3)
        self.assertGreaterEqual(val[0],val[1])
    def test_empty_candidates_refused(self):
        with self.assertRaises(ValueError):
            choose({},[1],[])
if __name__=='__main__':unittest.main()
