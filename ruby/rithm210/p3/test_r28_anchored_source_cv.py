"""R28 source-free anchored cohort fold and leakage regression."""
import unittest
from r28_anchored_source_cv import fixed_folds,select,CANDIDATES
from r27_audit_population_contracts import CONTRACTS,included

class TestR28Anchored(unittest.TestCase):
    def test_24_common_sixfold_remains_fixed(self):
        core=[s for s in range(3,27) if s not in (2,101)]
        self.assertEqual(len(core),24)
        a=fixed_folds(core)
        b=fixed_folds(core+[101,2])
        self.assertTrue(all(a[s]==b[s] for s in core))
        self.assertEqual(b[101],0)
        self.assertEqual(b[2],1)
        self.assertTrue(all(sum(a[s]==f for s in core)==4 for f in range(6)))

    def test_author_R_pilot_exception_explicit(self):
        self.assertFalse(included(2,3,3,'published_main_24'))
        self.assertFalse(included(2,3,3,'exclude_pilot2_include101_25'))
        self.assertTrue(included(2,3,3,'literal_author_R_filter_26'))
        self.assertTrue(included(101,3,3,'literal_author_R_filter_26'))
        self.assertFalse(included(1,3,3,'literal_author_R_filter_26'))

    def test_train_selection_immune_to_heldout(self):
        a=CANDIDATES[0]
        b=CANDIDATES[1]
        scores={s:{a:(1.,0.,0.),b:(2.,0.,0.)} for s in range(25)}
        train=list(range(20))
        self.assertEqual(select(scores,train,(a,b)),a)
        for s in range(20,25):
            scores[s][a]=(10000.,0.,0.)
            scores[s][b]=(-10000.,0.,0.)
        self.assertEqual(select(scores,train,(a,b)),a)

    def test_candidate_set_contains_both_joint_families(self):
        self.assertTrue(any(p.tau==0 for p in CANDIDATES))
        self.assertTrue(any(p.tau>0 for p in CANDIDATES))
        self.assertEqual(len(CANDIDATES),48)

    def test_refuse_cohort_without_24_common_sessions(self):
        with self.assertRaises(ValueError):fixed_folds([2,101])
        self.assertEqual(len(CONTRACTS),3)

if __name__=='__main__':unittest.main()
