"""Pure P15 operator regression tests, zero original personal/source data."""
import unittest
from tools.traffic_sources.p15_phase_operator import aggregate_ten_min,competing_worlds,audit_worlds

class TwoBinOperatorTest(unittest.TestCase):
    def test_example(self):
        x=competing_worlds(315,557)
        self.assertTrue(audit_worlds(x))
        self.assertEqual(x["identified_ten_min_total"],872)
        self.assertEqual(x["per_bin_reassignment_to_flatten_phase"],121)
    def test_null_direction_invariance(self):
        self.assertEqual(aggregate_ten_min([20,40,30,50]),
                         aggregate_ten_min([24,36,20,60]))
    def test_nonnegative_constraints(self):
        with self.assertRaises(ValueError):competing_worlds(-1,3)
    def test_odd_record_vector(self):
        with self.assertRaises(ValueError):aggregate_ten_min([1,2,3])

if __name__=="__main__":unittest.main()
