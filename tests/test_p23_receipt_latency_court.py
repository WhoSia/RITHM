import sys,unittest
from pathlib import Path
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"/"traffic_sources"))
from p23_receipt_latency_court import Observation,Receipt,Probe,publication_interval,asof,pair,world,evaluate,court,mean_bound
T=datetime(2025,10,1,tzinfo=timezone.utc)
class P23GitHubSmokes(unittest.TestCase):
 def test_identical_measurement_values(self):
    a,b=world("fast"),world("congestion_delayed")
    self.assertEqual(a[0],b[0]);self.assertNotEqual(a[1],b[1])
 def test_selection_bias(self):
    x=evaluate("congestion_delayed")
    self.assertEqual(x["selection_by_current_traffic"]["congested"]["received"],0)
    self.assertLess(x["available_only_receipt_loss"],x["full_decision_receipt_loss"])
 def test_authority_absent(self):self.assertFalse(court()["authentic_client_receipt_logs"])
 def test_p21_cohort_not_refit(self):self.assertEqual(court()["P21_matched_source_N_reference_ONLY"],2121699)
 def test_fixed_lag_needs_both_components(self):
    a=Observation("a","A","inbound",T+timedelta(minutes=5),1,5)
    b=Observation("b","A","inbound",T+timedelta(minutes=10),1,5)
    rb=Receipt("b",1,b.end+timedelta(minutes=1),b.digest)
    self.assertIsNone(pair([a,b],[rb],T+timedelta(minutes=12),"A","inbound"))
 def test_old_version_does_not_override_new(self):
    a=Observation("a","A","inbound",T,1,5)
    b=Observation("a","A","inbound",T,2,7)
    rs=[Receipt("a",2,T+timedelta(minutes=1),b.digest),
        Receipt("a",1,T+timedelta(minutes=3),a.digest)]
    self.assertEqual(next(iter(asof([a,b],rs,T+timedelta(minutes=4)).values())).count,7)
 def test_cache_negative_not_origin(self):
    x=Observation("a","A","inbound",T,1,1)
    p=Probe("a",T+timedelta(minutes=3),False,True,False,True)
    self.assertEqual(publication_interval(x,[p]),(T,None))
 def test_corrupted_payload_blocks(self):
    x=Observation("a","A","inbound",T,1,5)
    with self.assertRaises(ValueError):
        asof([x],[Receipt("a",1,T+timedelta(minutes=1),"bad")],T+timedelta(minutes=2))
 def test_low_delay_legal_vs_sixty(self):
    a=evaluate("fast");b=evaluate("uniform_60")
    self.assertLess(a["MAE"]["receipt"],b["MAE"]["receipt"])
    self.assertLess(b["MAE"]["lag7"],b["MAE"]["calendar"])
 def test_partial_bound(self):
    self.assertAlmostEqual(mean_bound(32,52,3.125,120)[0],1.9230769230769231)
if __name__=="__main__":unittest.main()
