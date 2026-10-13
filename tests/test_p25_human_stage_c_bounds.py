"""P25 offline source contract: real 2017 route counts, finite bounds only."""
import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "traffic_sources"))
from p25_human_stage_c_bounds import source_states, local_gain_bounds, summary, network_cost


class StageCBounds(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = source_states(ROOT / "data" / "rithm23_wijayaratna2017_routes.csv")

    def test_original_population(self):
        self.assertEqual((len(self.source), len({x["session"] for x in self.source})),(480,6))

    def test_original_cost_formula(self):
        self.assertTrue(all(x["C"]==network_cost(x["n1"],x["n2"],x["z"]) for x in self.source))

    def test_one_switch_both_signs(self):
        a=summary(self.source)["bounds"]["1"]
        self.assertEqual((a["both_signs_feasible"],a["harm_feasible"],a["benefit_feasible"]),(369,472,376))

    def test_no_stage_c_entry(self):
        q={"n1":12,"n2":0,"n3":0,"z":0,"C":network_cost(12,0,0)}
        self.assertEqual(local_gain_bounds(q,1),(0,0))

    def test_more_possible_switches_never_tightens_bounds(self):
        for x in self.source:
            a=local_gain_bounds(x,1)
            b=local_gain_bounds(x,2)
            self.assertLessEqual(b[0],a[0])
            self.assertGreaterEqual(b[1],a[1])

if __name__=="__main__":
    unittest.main()
