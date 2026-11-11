"""P3-R35 source-free contract and false-positive controls."""
import unittest
import numpy as np
from r35_value_randomization import statistic,after_minus_before,randomization_p

class R35Tests(unittest.TestCase):
    def data(self):
        return [((s,2,1,8,1,0),np.array([
            [6.,0.,0.],[10.,1.,1.],[14.,1.,0.]],float))
            for s in (3,4)]
    def test_exact_within_group_slope(self):
        slope,sess,n=statistic(self.data())
        self.assertAlmostEqual(slope,4/32)
        self.assertEqual(n,6)
        self.assertEqual(len(sess),2)
    def test_before_vs_after_are_not_same(self):
        self.assertNotEqual(statistic(self.data(),1)[0],
                            statistic(self.data(),2)[0])
    def test_matched_difference_only_has_both_observed(self):
        d=after_minus_before(self.data())
        self.assertAlmostEqual(statistic(d,1)[0],
                               statistic(self.data(),1)[0]-statistic(self.data(),2)[0])
        a=np.array([[6.,0.,np.nan],[10.,1.,np.nan]])
        self.assertEqual(len(after_minus_before(self.data()+[((5,2,1,1,1,0),a)])),2)
    def test_permutation_is_reproducible(self):
        x=self.data();b=statistic(x)[0]
        self.assertEqual(randomization_p(x,1,b,9,99),
                         randomization_p(x,1,b,9,99))
    def test_source_free_unit_does_not_require_private_csv(self):
        self.assertEqual(len(self.data()),2)

if __name__=='__main__':unittest.main()
