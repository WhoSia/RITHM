import unittest
from fractions import Fraction as Q
from r66_t10_state_null import (row_independent,transition,validate,joint_moments,binomial_occupancy_law,independent_occupancy_null)
class StateNull(unittest.TestCase):
    def test_no_changes(self):
        for n in range(7):self.assertEqual(row_independent(n,0,0)[n],1)
    def test_certain_flip(self):
        for n in range(7):self.assertEqual(row_independent(n,1,1)[6-n],1)
    def test_independent_state_binomial(self):
        p=Q(2,3)
        for n in range(7):self.assertEqual(row_independent(n,1-p,p),binomial_occupancy_law(p))
    def test_raw_negative_even_without_memory(self):
        self.assertEqual(independent_occupancy_null()['lag_covariance'],-Q(4,3))
    def test_zero_innovation_covariance(self):
        P=transition([Q(1,5)]*7,[Q(2,5)]*7)
        pi=binomial_occupancy_law(Q(1,2))
        self.assertEqual(joint_moments(P,pi)['lag_covariance_of_next_innovation'],0)
    def test_no_changes_zero_covariance(self):
        P=transition([0]*7,[0]*7)
        self.assertEqual(joint_moments(P,binomial_occupancy_law(Q(1,3)))['lag_covariance'],0)
    def test_invalid_probability(self):
        with self.assertRaises(ValueError):row_independent(3,Q(7,6),0)
    def test_invalid_state(self):
        with self.assertRaises(ValueError):row_independent(7,0,0)
    def test_wrong_transition(self):
        with self.assertRaises(ValueError):validate([[1]],[1])
    def test_invalid_distribution(self):
        with self.assertRaises(ValueError):validate(transition([0]*7,[0]*7),[1]*7)
if __name__=='__main__':unittest.main()
