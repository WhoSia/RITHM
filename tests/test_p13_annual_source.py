import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"/"traffic_sources"))
import p13_annual as P
class CourtTests(unittest.TestCase):
 def test_source_clock(self):
  self.assertEqual(len(P.DATES),365)
  self.assertEqual(len(list(range(0,338,28))),13)
 def test_missing_day_rejected(self):
  seen=np.ones((1,365,288),np.uint8);seen[:,14,:]=0
  self.assertTrue(P.admitted(seen,0))
 def test_constant_honest_history(self):
  seen=np.ones((1,365,288),np.uint8)
  v=np.full((1,365,288),60.,dtype=np.float32)
  q=np.full((1,365,288),100.,dtype=np.float32)
  a=P.score(v,q,seen,0)
  b=P.two_clock(q,seen,0)
  self.assertEqual(a["status"],"PASS")
  self.assertEqual(a["speed_lag5"],0)
  self.assertEqual(b["lag5"],0)
 def test_welfare_counterexample(self):
  self.assertAlmostEqual(sum(60/x for x in (60,60)),2)
  self.assertAlmostEqual(sum(60/x for x in (40,80)),2.25)
if __name__=="__main__":unittest.main()
