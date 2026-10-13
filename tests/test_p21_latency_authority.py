import sys, unittest
from pathlib import Path
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"/"traffic_sources"))
from p21_latency_authority import lag_from_certified_bound,pair_available_by
from p21_trainval_switch import seasonal,mix
import numpy as np

class P21SourceAuthority(unittest.TestCase):
    def test_delay_edges(self):
        for delta,lag in [(0,1),(5,2),(10,2),(11,3),(20,3),(30,4),(40,5),(60,7)]:
            self.assertEqual(lag_from_certified_bound(delta,verified=True),lag)
    def test_uncertified_refused(self):
        with self.assertRaises(ValueError):lag_from_certified_bound(30)
    def test_boolean_delay_refused(self):
        with self.assertRaises(TypeError):lag_from_certified_bound(True,verified=True)
    def test_bad_negative(self):
        with self.assertRaises(ValueError):lag_from_certified_bound(-1,verified=True)
    def test_one_unpublished_half_blocks_pair(self):
        t=datetime(2025,10,13,12,tzinfo=timezone.utc)
        self.assertFalse(pair_available_by(t,t-timedelta(minutes=5),
            t-timedelta(minutes=1),t,t+timedelta(minutes=1)))
    def test_both_published_pair_allowed(self):
        t=datetime(2025,10,13,12,tzinfo=timezone.utc)
        self.assertTrue(pair_available_by(t,t-timedelta(minutes=5),
            t-timedelta(minutes=5),t,t))
    def test_noncontiguous_block(self):
        t=datetime(2025,10,13,12,tzinfo=timezone.utc)
        with self.assertRaises(ValueError):
            pair_available_by(t,t-timedelta(minutes=10),t-timedelta(minutes=10),t,t)
    def test_calendar_two_week_fit(self):
        x=np.arange(14*144.,dtype=float).reshape(14,144)
        self.assertEqual(len(seasonal(x)),1008)
    def test_mixture_real_weight(self):
        x=np.array([10.,20.,40.,80.])
        self.assertAlmostEqual(mix(x,np.array([3]),1)[0],37.5)

if __name__=="__main__":unittest.main()
