import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"tools"/"traffic_sources"))
from p24_human_source_gate import audit

class SourceAudit(unittest.TestCase):
    def test_original_human_route_ambiguity(self):
        root=Path(__file__).resolve().parents[1]
        a=audit(root/"data"/"rithm23_wijayaratna2017_routes.csv")
        self.assertEqual((a["sessions"],a["panels"],a["group_rounds"]),(6,24,480))
        self.assertEqual((a["q8_z0_n"],a["q8_z0_cost_range"]),(101,[200,256]))
        self.assertEqual(a["within_panel_ambiguous_strata"],82)
if __name__=="__main__":
    unittest.main()
