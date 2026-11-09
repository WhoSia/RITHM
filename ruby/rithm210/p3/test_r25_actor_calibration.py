import math
import unittest
from r25_actor_calibration import CALIBRATORS,Calibrator,cell,epoch,fit,logit,sigmoid

class TestR25ActorCalibration(unittest.TestCase):
    def row(self,p=.3,y=1,prev=1,period=10,informed=1):
        return dict(p=p,y=y,prev=prev,period=period,informed=informed)

    def test_regularized_offset_recovers_known_probability(self):
        p=.3;shift=.8;target=sigmoid(logit(p)+shift)
        n=10000;pos=round(n*target)
        rows=[self.row(p=p,y=1)]*pos+[self.row(p=p,y=0)]*(n-pos)
        fitted=fit(rows,'global',lam=.001)
        self.assertAlmostEqual(shift,fitted.shifts[('global',)],delta=.002)
        self.assertAlmostEqual(target,fitted.probability(rows[0]),delta=.002)

    def test_route_and_informed_cells_do_not_leak(self):
        data=[self.row(p=.4,y=1,prev=1,informed=1)]*100
        data +=[self.row(p=.4,y=0,prev=0,informed=0)]*100
        m=fit(data,'route_informed',lam=5)
        self.assertGreater(m.probability(self.row(p=.4,prev=1,informed=1)),.4)
        self.assertLess(m.probability(self.row(p=.4,prev=0,informed=0)),.4)
        self.assertAlmostEqual(.4,m.probability(self.row(p=.4,prev=1,informed=0)))
        self.assertEqual('early',epoch(10));self.assertEqual('middle',epoch(11))
        self.assertEqual('late',epoch(30))

    def test_identity_and_invalid_training(self):
        r=self.row()
        self.assertEqual(.3,fit([r],'identity').probability(r))
        for bad in ([],):
            with self.assertRaises(ValueError):fit(bad,'global')
        with self.assertRaises(ValueError):fit([r],'bogus')
        with self.assertRaises(ValueError):fit([r],'global',lam=0)
        with self.assertRaises(ValueError):fit([dict(r,p=float('nan'))],'global')
        with self.assertRaises(ValueError):fit([dict(r,y=2)],'global')
        self.assertEqual(6,len(CALIBRATORS))

if __name__=='__main__':unittest.main()
