import math
import unittest
from r23_epoch_effects import epoch, assess

class TestR23EpochEffects(unittest.TestCase):
    def test_epoch_edges(self):
        self.assertEqual('early', epoch(1))
        self.assertEqual('early', epoch(10))
        self.assertEqual('middle',epoch(11))
        self.assertEqual('middle',epoch(29))
        self.assertEqual('late',epoch(30))
        self.assertEqual('late',epoch(40))
        with self.assertRaises(ValueError):epoch(41)

    def test_source_free_full_history_without_leakage(self):
        groups={}
        for session in range(1,25):
            for treatment in (1,2,3):
                for period in range(1,41):
                    groups[(session,treatment,period,1)]=[
                        {'ID':str(a),'RouteA':str(int(a<=3)),
                         'NumA':'3','trt':str(treatment)} for a in range(1,7)]
        result=assess(groups)
        self.assertEqual(9,len(result))
        self.assertTrue(all(entry['sessions']==24 for entry in result))
        self.assertTrue(all(math.isfinite(entry['delta_logloss']) for entry in result))
        groups[(1,1,20,1)][0]['NumA']='4'
        with self.assertRaises(ValueError):assess(groups)

if __name__=='__main__':unittest.main()
