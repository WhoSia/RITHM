import unittest
from fractions import Fraction as F
from r66_t7_recovery import full_recovery,truncated_recovery,one_step_excess,expected,values
from r66_t7_parity import law
from r66_t7_sufficiency import required_order

class TestRecovery(unittest.TestCase):
    def test_first_four_costs(self):
        self.assertEqual([full_recovery(i) for i in range(4)],[0,3,15,42])
    def test_one_period_quadratic(self):
        self.assertEqual(required_order(values(3,horizon=1),3),2)
    def test_complete_recovery_cubic(self):
        self.assertEqual(required_order(values(3),3),3)
    def test_parity_gap(self):
        self.assertEqual(expected(law(3,0),3),F(45,4))
        self.assertEqual(expected(law(3,1),3),F(51,4))
    def test_truncation_reduces(self):
        self.assertEqual(truncated_recovery(3,2),3*(9+4))
    def test_invalid_horizon(self):
        with self.assertRaises(ValueError):truncated_recovery(2,0)
