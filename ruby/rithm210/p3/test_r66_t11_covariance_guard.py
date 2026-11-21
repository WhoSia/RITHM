import unittest
from fractions import Fraction as Q
from r66_t11_covariance_guard import covariance,mse,decomposition,source_free_witness
class R66T11SourceFreeTest(unittest.TestCase):
    def test_constant_zero_covariance(self):self.assertEqual(covariance([1,1],[2,3]),0)
    def test_fraction_covariance(self):self.assertEqual(covariance([-1,1],[-2,2]),2)
    def test_mse_exact(self):self.assertEqual(mse([0,2],[1,1]),1)
    def test_constant_zero_mse(self):self.assertEqual(mse([1,2],[1,2]),0)
    def test_decomposition_identity(self):
        x=decomposition([0,1,2],[2,3,0],[1,1,1])
        self.assertEqual(x['raw'],x['fitted']+x['residual'])
    def test_witness(self):self.assertEqual(source_free_witness()[0]['mse'],0)
    def test_empty_rejected(self):
        with self.assertRaises(ValueError):covariance([],[])
    def test_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):decomposition([1],[2,2],[1,1])
if __name__=='__main__':unittest.main()
