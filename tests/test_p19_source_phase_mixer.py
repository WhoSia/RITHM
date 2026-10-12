"""Offline math/source-summary tests. Does not claim CI or raw 2025 evaluation."""
import json
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"/"traffic_sources"))
from p19_train_only_phase_mixer import train_only_weight

class P19SourceContract(unittest.TestCase):
    def test_conserved_pair(self):
        for q0 in range(8):
            for q1 in range(8):
                for delta in range(-q0,q1+1):
                    self.assertEqual(q0+q1,(q0+delta)+(q1-delta))
    def test_phase_reallocated_five_min_not_conserved(self):
        self.assertNotEqual(2*12,2*(12+4))
    def test_stationary_train_prefers_unmixed_lag(self):
        a=np.full((21,144),40,dtype=np.float32)
        self.assertEqual(train_only_weight(a),1.0)
    def test_trending_train_prefers_nearest(self):
        a=np.arange(21*144,dtype=np.float32).reshape(21,144)
        self.assertEqual(train_only_weight(a),1.0)
    def test_alternating_train_prefers_mixing(self):
        a=np.resize(np.array([10,100],dtype=np.float32),21*144).reshape(21,144)
        self.assertLess(train_only_weight(a),1.0)
    def test_source_summary_replicates_existing_p18_baseline(self):
        p=Path(__file__).resolve().parents[1]/"docs"/"data"/"rithm26_p19_mixer_real_2025.json"
        x=json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(x["N"],2136298)
        self.assertAlmostEqual(x["MAE"]["last10"],34.900208,places=5)
        self.assertAlmostEqual(x["MAE"]["twice_last5"],39.269881,places=5)
        self.assertLess(x["MAE"]["fixed_mix75"],x["MAE"]["last10"])
        self.assertLess(x["MAE"]["train_only_adaptive"],x["MAE"]["fixed_mix75"])
    def test_no_unsupported_human_intervention_claim(self):
        p=Path(__file__).resolve().parents[1]/"docs"/"data"/"rithm26_p19_mixer_real_2025.json"
        x=json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual(x["human_welfare"],"NOT_IDENTIFIED")
        self.assertEqual(x["guidance_causality"],"NOT_ESTIMATED")
if __name__=="__main__":
    unittest.main()
