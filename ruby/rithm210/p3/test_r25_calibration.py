import math
import random
import unittest
from r25_actor_calibration import CALIBRATORS,fit,cell,Calibrator,epoch
from r25_calibration_cv import choose_calibration,event_rows,run
from r23_inertia_memory_cv import Actor
from r24_welfare_attribution import decompose as residual

class R25Tests(unittest.TestCase):
    def example(self,p=.5,y=1,prev=1,period=5,informed=1):
        return dict(p=p,y=y,prev=prev,period=period,informed=informed,session=1,treatment=3)
    def test_calibration_newton_recovers_known_logit_shift(self):
        p=.3;shift=.8;real=1/(1+math.exp(-(math.log(p/(1-p))+shift)))
        rows=[self.example(p=p,y=1)]*int(real*10000)+[self.example(p=p,y=0)]*(10000-int(real*10000))
        fitted=fit(rows,'global',lam=.001)
        self.assertAlmostEqual(shift,fitted.shifts[('global',)],delta=.002)
        self.assertAlmostEqual(real,fitted.probability(self.example(p=p)),delta=.002)
    def test_directional_and_information_cells_not_reused(self):
        rows=[self.example(p=.4,y=1,prev=1,informed=1)]*100
        rows += [self.example(p=.4,y=0,prev=0,informed=0)]*100
        fitobj=fit(rows,'route_informed',lam=5)
        a=fitobj.probability(self.example(p=.4,prev=1,informed=1))
        b=fitobj.probability(self.example(p=.4,prev=0,informed=0))
        self.assertGreater(a,.4)
        self.assertLess(b,.4)
        unknown=fitobj.probability(self.example(p=.4,prev=1,informed=0))
        self.assertAlmostEqual(.4,unknown)
    def test_exhaustive_group_welfare_identity_after_shift(self):
        xs=[self.example(p=.2+.1*i) for i in range(6)]
        model=fit([x for x in xs]*2,'global')
        ps=[model.probability(x) for x in xs]
        for mask in range(64):
            y=[(mask>>i)&1 for i in range(6)]
            r=residual(y,ps,[1,0,1,0,1,0])
            self.assertAlmostEqual(r['welfare_error'],r['linear']+r['diagonal']+r['same_pair']+r['opposite_pair'],places=9)
    def test_calibration_choice_requires_only_group_training(self):
        groups=[]
        for sid in range(1,21):
            for g in range(2):
                groups.append([self.example(p=.5,y=(sid+g+i)%2) | dict(session=sid,period=1,prev=-1) for i in range(6)])
        winner,values=choose_calibration(groups,list(range(1,21)))
        self.assertIn(winner,CALIBRATORS)
        self.assertEqual(set(values),set(CALIBRATORS))
        with self.assertRaises(ValueError):choose_calibration(groups,list(range(1,20)))
    def test_identity_and_invalid_rows(self):
        row=self.example(p=.7)
        self.assertAlmostEqual(.7,fit([row],'identity').probability(row))
        self.assertEqual('early',epoch(1));self.assertEqual('late',epoch(40))
        with self.assertRaises(ValueError):fit([row],'invalid')
        with self.assertRaises(ValueError):fit([], 'global')

if __name__=='__main__':unittest.main()
