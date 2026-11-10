"""Source-free RITHM future-field quarantine regression."""
import unittest
from r27_audit_temporal_leakage import assert_no_future_predictors,audit_rows,FUTURE_LABELS

class TemporalLeakageGuard(unittest.TestCase):
    def test_historical_inputs_allowed(self):
        self.assertEqual(assert_no_future_predictors(["RouteA","NumA","Cost","Period"]),
                         ("Cost","NumA","Period","RouteA"))

    def test_every_future_label_rejected(self):
        for field in FUTURE_LABELS:
            with self.assertRaises(ValueError):
                assert_no_future_predictors(["RouteA",field])

    def test_raw_generated_future_outcome_not_declared_intention(self):
        rows=[("g",1,1,0,1,1,2),("g",1,2,1,2,-1,-1),
              ("g",2,1,1,1,0,2),("g",2,2,1,2,-1,-1)]
        audit=audit_rows(rows)
        self.assertEqual(audit["checked_pairs"],2)
        self.assertTrue(audit["all_pairs_match"])
        self.assertEqual(audit["last_period_sentinels"],2)

    def test_tampered_future_label_detected(self):
        rows=[("g",1,1,0,1,0,2),("g",1,2,1,2,-1,-1)]
        self.assertFalse(audit_rows(rows)["all_pairs_match"])

    def test_duplicates_rejected(self):
        with self.assertRaises(ValueError):
            audit_rows([("g",1,1,0,1,1,2),("g",1,1,0,1,1,2)])

if __name__=="__main__":
    unittest.main()
