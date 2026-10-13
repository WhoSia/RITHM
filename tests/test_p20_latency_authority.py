"""Synthetic source-clock and convexity tests, not CI real-2025 row reproduction."""
import unittest,sys,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"/"traffic_sources"))
from p20_conditional_authority import required_source_lag, conditional_vehicle_time_bounds,admit_independent_detector
class P20Court(unittest.TestCase):
    def test_0(self): self.assertEqual(required_source_lag(0),1)
    def test_5(self): self.assertEqual(required_source_lag(5),2)
    def test_10(self):self.assertEqual(required_source_lag(10),2)
    def test_15(self):self.assertEqual(required_source_lag(15),3)
    def test_30(self):self.assertEqual(required_source_lag(30),4)
    def test_40(self):self.assertEqual(required_source_lag(40),5)
    def test_60(self):self.assertEqual(required_source_lag(60),7)
    def test_bad_negative(self):
        with self.assertRaises(ValueError):required_source_lag(-1)
    def test_bad_fraction(self):
        with self.assertRaises(ValueError):required_source_lag(0.5)
    def test_two_car_sharp(self):
        low,hi=conditional_vehicle_time_bounds(2,1,60,40,80)
        self.assertAlmostEqual(low*60,2)
        self.assertAlmostEqual(hi*60,2.25)
    def test_three_cars_grid(self):
        for mean in range(10,31,5):
            lo,hi=conditional_vehicle_time_bounds(3,1,mean,10,30)
            cases=[sum(1/v for v in speeds) for speeds in itertools.product(range(10,31),repeat=3) if sum(speeds)==3*mean]
            self.assertLessEqual(lo,min(cases)+1e-12)
            self.assertGreaterEqual(hi,max(cases)-1e-12)
    def test_source_is_not_independent(self):
        self.assertFalse(admit_independent_detector({"instrument":"VOL"}))
    def test_conditional_certificate_required(self):
        with self.assertRaises(ValueError):conditional_vehicle_time_bounds(2,1,60,70,90)
if __name__=="__main__":unittest.main()
