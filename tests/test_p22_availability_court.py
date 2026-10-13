import sys,unittest
from pathlib import Path
from datetime import datetime as D,timedelta as T,timezone as Z
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"/"traffic_sources"))
from p22_availability_court import Evidence,source_pair_legal,allowed_latest_pair,lag_from_bound,scenario_court
t=D(2025,10,13,tzinfo=Z.utc)
def E(end=0,pos=4,neg=None,auth=False,trusted=True):
    return Evidence(t+T(minutes=end),None if pos is None else t+T(minutes=pos),
                    None if neg is None else t+T(minutes=neg),auth,trusted)
class P22SourceClock(unittest.TestCase):
    def test_no_positive(self):self.assertEqual(E(pos=None,trusted=False).provider_status(t+T(minutes=10)),"ambiguous")
    def test_positive_source(self):self.assertEqual(E().provider_status(t+T(minutes=4)),"certain")
    def test_before_end(self):self.assertEqual(E().provider_status(t-T(seconds=1)),"impossible")
    def test_trusted_negative(self):self.assertEqual(E(pos=20,neg=10,auth=True).provider_status(t+T(minutes=10)),"impossible")
    def test_straddled_decision(self):self.assertEqual(E(pos=20,neg=10,auth=True).provider_status(t+T(minutes=15)),"ambiguous")
    def test_weak_negative(self):self.assertEqual(E(pos=20,neg=10).provider_status(t+T(minutes=15)),"ambiguous")
    def test_untrusted_positive(self):
        x=E(pos=4,trusted=False)
        self.assertFalse(x.operationally_receipted(t+T(minutes=10)))
        self.assertEqual(x.provider_status(t+T(minutes=10)),"ambiguous")
    def test_receipt_future(self):self.assertFalse(E(pos=20).operationally_receipted(t+T(minutes=15)))
    def test_receipt_at_decision(self):self.assertTrue(E(pos=20).operationally_receipted(t+T(minutes=20)))
    def test_half_missing(self):self.assertFalse(source_pair_legal(E(pos=6),E(end=5,pos=16),t+T(minutes=10)))
    def test_pair_yes(self):self.assertTrue(source_pair_legal(E(pos=6),E(end=5,pos=9),t+T(minutes=10)))
    def test_gap(self):
        with self.assertRaises(ValueError):source_pair_legal(E(),E(end=10),t+T(minutes=20))
    def test_naive_time(self):
        with self.assertRaises(ValueError):Evidence(D(2025,10,13))
    def test_early_receipt(self):
        with self.assertRaises(ValueError):E(end=9,pos=5)
    def test_poll_after_receipt(self):
        with self.assertRaises(ValueError):E(pos=8,neg=9,auth=True)
    def test_untrusted_missing_positive(self):
        with self.assertRaises(ValueError):E(pos=None,trusted=True)
    def test_no_auth_poll(self):
        with self.assertRaises(ValueError):E(auth=True)
    def test_latest(self):
        before=(E(end=0,pos=6),E(end=5,pos=9))
        after=(E(end=10,pos=11),E(end=15,pos=25))
        self.assertEqual(allowed_latest_pair([after,before],t+T(minutes=20)),before)
    def test_no_pair(self):self.assertIsNone(allowed_latest_pair([(E(pos=25),E(end=5,pos=25))],t+T(minutes=20)))
    def test_early_no(self):self.assertFalse(source_pair_legal(E(pos=25),E(end=5,pos=25),t+T(minutes=24)))
    def test_poll_not_trusted_lower(self):self.assertEqual(E(pos=25,neg=15).provider_window()[0],t)
    def test_lag_edges(self):self.assertEqual([lag_from_bound(x) for x in (0,5,10,11,30,40,60)],[1,2,2,3,4,5,7])
    def test_bool(self):
        with self.assertRaises(ValueError):lag_from_bound(True)
    def test_negative_delay(self):
        with self.assertRaises(ValueError):lag_from_bound(-1)
    def test_source_n(self):self.assertEqual(scenario_court()["source_P21_matched_mask_N"],2121699)
    def test_lag2_defeat(self):self.assertGreater(scenario_court()["scenarios"][1]["link_switch"],scenario_court()["scenarios"][1]["fixed"])
    def test_calendar_gain(self):self.assertAlmostEqual(scenario_court()["conditional_D60_gate_gain_vs_calendar"],4.8)
    def test_max_regret(self):self.assertAlmostEqual(scenario_court()["max_scenario_aggregate_regret_across_these_replayed_options"]["frozen_lag7_gate"],27.6)
    def test_not_certified(self):self.assertFalse(scenario_court()["client_max_delay_60min_CERTIFIED"])
    def test_no_optimality_claim(self):self.assertTrue(scenario_court()["not_minimax_optimality_or_operational_claim"])
