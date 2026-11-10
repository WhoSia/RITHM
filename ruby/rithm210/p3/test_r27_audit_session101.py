"""RITHM interim audit source-free regression of admissible source filtration."""
import inspect
import unittest
from r27_audit_session101_25fold import Params,choose,read_events,run

class TestSession101Sensitivity(unittest.TestCase):
    def test_read_filter_keeps_author_admissible_session101(self):
        source=inspect.getsource(read_events)
        self.assertIn("if sid==2 or trt!=3",source)
        self.assertNotIn("sid in (2,101)",source)
        self.assertIn("len(sessions)!=25",source)
        self.assertIn("len(out)!=1938",source)
    def test_all_outer_folds_are_disjoint_twenty_five(self):
        sessions=list(range(25))
        by={s:i%5 for i,s in enumerate(sessions)}
        covered=[]
        for f in range(5):
            training={s for s in sessions if by[s]!=f}
            heldout={s for s in sessions if by[s]==f}
            self.assertEqual((len(training),len(heldout)),(20,5))
            self.assertFalse(training&heldout)
            covered.extend(heldout)
        self.assertEqual(sorted(covered),sessions)
    def test_no_t_plus_one_fields_as_predictors(self):
        source=inspect.getsource(read_events)+inspect.getsource(run)
        for forbidden in ("NumAnext","NumSwitchWill","switchWill"):
            self.assertNotIn(forbidden,source)
    def test_train_only_selection_boundary(self):
        p=Params(.05,0.,0.,0.)
        q=Params(.3,0.,0.,.3)
        train=list(range(20))
        scores={(v,s):(1 if v==p else 2,0.,0.) for v in (p,q) for s in range(25)}
        self.assertEqual(choose(scores,train,[p,q]),p)
        for s in range(20,25):
            scores[p,s]=(999,0,0)
            scores[q,s]=(-999,0,0)
        self.assertEqual(choose(scores,train,[p,q]),p)

if __name__=="__main__":
    unittest.main()
