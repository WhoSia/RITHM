"""R56 report generator never accepts an unsealed original dataset."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from r56_results import ALPHAS, generate


class R56ReportGateTests(unittest.TestCase):
    def test_sensitivity_grid_fixed_and_ordered(self):
        self.assertEqual(ALPHAS,(0.25,0.5,1.0,2.0,4.0,8.0))

    def test_reject_unapproved_original_blob_before_parsing(self):
        with TemporaryDirectory() as d:
            p=Path(d)/'fabricated.zip'
            p.write_bytes(b'a fake historical source must not be accepted')
            with self.assertRaisesRegex(ValueError,'wrong original source hash'):
                generate(p)


if __name__=='__main__':unittest.main()
