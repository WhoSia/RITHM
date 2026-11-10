"""Source-free period-window and raw-source-identity regression."""
import tempfile,unittest
from pathlib import Path
from r29_switching_did import WINDOWS,run

class TestSwitching(unittest.TestCase):
    def test_buckets_cover_rounds_without_anticipation(self):
        values=[t for lo,hi in WINDOWS.values() for t in range(lo,hi+1)]
        self.assertEqual(values,list(range(2,41)))
    def test_untrusted_source_cannot_pass_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'dummy.csv'
            p.write_text('not the real source')
            with self.assertRaises(ValueError):run(p)

if __name__=='__main__':unittest.main()
