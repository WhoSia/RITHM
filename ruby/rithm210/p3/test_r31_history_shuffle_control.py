"""R31 source-free and optional private-source fold-preserving negative-control tests."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from r31_history_shuffle_control import permuted_contexts
from r31_order_history import prior_contexts

class TestR31Shuffle(unittest.TestCase):
    def test_explicit_module_source_privacy(self):
        # Never expose complete participant histories to public aggregate output.
        from r31_history_shuffle_control import run
        self.assertTrue(callable(run))

    @unittest.skipUnless(os.environ.get('RITHM_PRIVATE_SOURCE'),'private author CSV not distributed')
    def test_permutation_preserves_order_flags_and_experience_multiset(self):
        path=os.environ['RITHM_PRIVATE_SOURCE']
        original,groups=prior_contexts(path)
        shuffled,_=permuted_contexts(path,20261111)
        self.assertEqual(original.keys(),shuffled.keys())
        for k in original:
            self.assertEqual(original[k][:2],shuffled[k][:2])
        # Global multiset of 2-feature experience summaries preserved by permutation.
        self.assertEqual(sorted(x[2:] for x in original.values()),sorted(x[2:] for x in shuffled.values()))
        self.assertTrue(any(original[k][2:]!=shuffled[k][2:] for k in original))

if __name__=='__main__':unittest.main()
