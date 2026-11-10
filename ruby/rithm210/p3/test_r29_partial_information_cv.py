"""R29 source-free guard against hidden public-count leakage in Partial."""
import unittest
import numpy as np
from r29_partial_information_cv import design,fit,metrics_for_group,MODELS

class TestR29(unittest.TestCase):
    def test_no_public_information_changes_uninformed_design(self):
        for model in MODELS:
            for route in (0,1):
                self.assertEqual(design(route,1,6.,0,model),design(route,5,6.,0,model))
    def test_public_information_relevant_to_informed_only(self):
        self.assertNotEqual(design(1,1,6.,1,'route_info_payoff_public'),
                            design(1,5,6.,1,'route_info_payoff_public'))
    def test_no_payoff_in_route_only(self):
        self.assertEqual(design(1,2,3.,1,'route_info'),design(1,2,9.,1,'route_info'))
    def test_symmetric_group_score(self):
        z=metrics_for_group(np.ones(6)*.5,[1,1,1,0,0,0],[1,1,1,0,0,0])
        self.assertAlmostEqual(z[0],np.log(2))
        self.assertAlmostEqual(z[2],np.log(2))
        self.assertAlmostEqual(z[3],np.log(2))
        self.assertAlmostEqual(z[6],-np.log(20/64))
        self.assertAlmostEqual(z[7],4.5)
    def test_training_within_model(self):
        X=[[1.,-1.,0.,0.],[1.,1.,0.,0.]]*40
        y=[0,1]*40
        b=fit(X,y)
        self.assertGreater(b[1],0)
    def test_unsupported_family_rejected(self):
        with self.assertRaises(ValueError):design(1,2,3.,1,'public_for_everyone')
        with self.assertRaises(ValueError):design(1,2,3.,2,'route_info')

if __name__=='__main__':unittest.main()
