"""R26 tau=0 must reproduce R25's unchanged calibrated independent law."""
import math
import unittest
from r26_common_shock import forecast
from r25_actor_calibration import Calibrator
from r25_calibration_cv import group_score

class TestR26R25Bridge(unittest.TestCase):
    def test_all_64_outcomes_exact_r25_independent_replay(self):
        probabilities=[.11,.22,.37,.62,.74,.83]
        for mask in range(64):
            ys=[(mask>>i)&1 for i in range(6)]
            rows=[dict(p=p,y=y,prev=(-1 if mask==0 else i%2),period=(1 if mask==0 else 10),
                       session=1,treatment=3,group=1,informed=1)
                  for i,(p,y) in enumerate(zip(probabilities,ys))]
            r25=group_score(rows,Calibrator('identity',{}))
            r26=forecast(probabilities).evaluate(ys)
            self.assertAlmostEqual(r25['logloss'],r26['logloss'],places=11)
            self.assertAlmostEqual(r25['abs_cost_error'],r26['cost_mae'],places=11)
            self.assertAlmostEqual(r25['actor_brier'],r26['actor_brier'],places=11)
            self.assertAlmostEqual(r25['predicted_cost'],forecast(probabilities).expectation_cost(),places=11)
    def test_joint_independence_likelihood_exact(self):
        ps=[.1,.2,.3,.4,.5,.6]
        ys=[1,0,1,0,1,0]
        r=forecast(ps).evaluate(ys)
        expected=-sum(math.log(p if y else 1-p) for p,y in zip(ps,ys))
        self.assertAlmostEqual(expected,r['joint_logloss'],places=11)

if __name__=='__main__':unittest.main()
