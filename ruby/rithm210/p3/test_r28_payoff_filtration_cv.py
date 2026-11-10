"""R28 source-free filtration, ridge and geometry tests."""
import unittest
import numpy as np
from r28_payoff_filtration_cv import design,fit,group_metrics,FAMILIES

class R28FeedbackTests(unittest.TestCase):
    def test_no_treatment_public_count_noninterference(self):
        for fam in ("choice","choice_payoff"):
            self.assertEqual(design(1,0,6.,fam),design(1,6,6.,fam))
            self.assertEqual(design(0,0,-2.,fam),design(0,6,-2.,fam))

    def test_full_count_can_affect_design(self):
        self.assertNotEqual(design(1,0,6.,"choice_public"),
                            design(1,6,6.,"choice_public"))

    def test_payoff_helps_change_design_without_future_fields(self):
        self.assertNotEqual(design(1,3,2.,"choice_payoff"),
                            design(1,3,9.,"choice_payoff"))
        self.assertEqual(len(FAMILIES),4)
        for name in FAMILIES:
            self.assertFalse(any("future" in s.lower() or "next" in s.lower() for s in FAMILIES[name]))

    def test_uniform_probability_group_central_cost(self):
        p=[.5]*6
        score=group_metrics(p,[1,1,1,0,0,0])
        self.assertAlmostEqual(score[0],np.log(2),places=12)
        self.assertAlmostEqual(score[1],.25,places=12)
        self.assertAlmostEqual(score[2],-np.log(20/64),places=12)
        self.assertAlmostEqual(score[3],31.5-27,places=12)

    def test_optimizer_baseline_synthetic(self):
        X=[[1.,-1.],[1.,1.]]*60
        y=[0,1]*60
        b=fit(X,y,ridge=.02)
        self.assertEqual(len(b),2)
        self.assertGreater(b[1],0)

    def test_invalid_feature_family(self):
        with self.assertRaises(ValueError):design(1,3,5.,"private_cost_oracle")
        with self.assertRaises(ValueError):fit([[1.,0.]],[],ridge=.02)

if __name__=="__main__":unittest.main()
