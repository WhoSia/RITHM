"""P26 pure-math smoke tests. No human advice receipt or policy effect claimed."""
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"/"traffic_sources"))
from p26_exposure_identification import worlds, CB_NORMAL, CB_INCIDENT

class P26Attention(unittest.TestCase):
    def test_two_distinct_latent_worlds_same_observed_rates(self):
        r=worlds()
        a=r["all_read_compatible"];b=r["partial_read_compatible"]
        self.assertEqual(a["attention"],1)
        self.assertLess(b["attention"],1)
        self.assertGreater(b["attention"],0)
        for v in (a,b):
            x=v["attention"]
            self.assertAlmostEqual((1-x)*v["nonreader"]+x*v["reader_normal"],CB_NORMAL)
            self.assertAlmostEqual((1-x)*v["nonreader"]+x*v["reader_incident"],CB_INCIDENT)

    def test_no_false_readership_claim(self):
        r=worlds()
        self.assertIn("unverified",r["CAUTION"])
        self.assertAlmostEqual(r["hypothetical_nonreader_invariant_bounds"]["min"],CB_NORMAL-CB_INCIDENT)

    def test_input_probabilities(self):
        self.assertGreater(CB_NORMAL,CB_INCIDENT)
        self.assertTrue(0<CB_INCIDENT<1)

if __name__=="__main__":
    unittest.main()
