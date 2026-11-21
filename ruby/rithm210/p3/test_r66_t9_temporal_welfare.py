import unittest
from fractions import Fraction as Q
from r66_t9_temporal_welfare import welfare,serial_covariance_bound,iid_occupancy_differencing_null

class TemporalWelfareTests(unittest.TestCase):
    def test_initial_updated_date(self):
        for mode in ("iid","common","alternating"):
            self.assertEqual(welfare(2,Q(1,2),Q(1,5),mode),Q(1,25))
    def test_positive_feedback_common_worse(self):
        self.assertGreater(welfare(mode="common"),welfare(mode="iid"))
    def test_negative_feedback_common_better(self):
        self.assertLess(welfare(rho=Q(-1,2),mode="common"),welfare(rho=Q(-1,2),mode="iid"))
    def test_no_memory_equal(self):
        self.assertEqual(welfare(rho=0,mode="common"),welfare(rho=0,mode="iid"))
    def test_alternating_negative_worse(self):
        self.assertGreater(welfare(rho=Q(-1,2),mode="alternating"),welfare(rho=Q(-1,2),mode="iid"))
    def test_feedback_phase_isomorphism(self):
        self.assertEqual(welfare(rho=Q(-1,2),mode="alternating"),welfare(rho=Q(1,2),mode="common"))
    def test_bound_attained_positive(self):
        self.assertEqual(welfare(mode="common")-welfare(mode="iid"),serial_covariance_bound(40,Q(1,2),Q(1,5)))
    def test_bound_attained_negative_alternation(self):
        self.assertEqual(welfare(rho=Q(-1,2),mode="alternating")-welfare(rho=Q(-1,2),mode="iid"),serial_covariance_bound(40,Q(-1,2),Q(1,5)))
    def test_zero_memory_bound(self):self.assertEqual(serial_covariance_bound(40,0,1),0)
    def test_differencing_artifact(self):self.assertEqual(iid_occupancy_differencing_null(),-Q(4,3))
    def test_no_variance_null(self):self.assertEqual(iid_occupancy_differencing_null(p=0),0)
    def test_invalid_feedback(self):
        with self.assertRaises(ValueError):welfare(rho=Q(3,2))
    def test_invalid_horizon(self):
        with self.assertRaises(ValueError):welfare(horizon=1)
    def test_invalid_delta(self):
        with self.assertRaises(ValueError):serial_covariance_bound(5,Q(1,2),1,3)
if __name__=="__main__":unittest.main()
