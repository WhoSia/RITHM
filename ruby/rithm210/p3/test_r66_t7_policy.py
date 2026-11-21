import unittest
from r66_t7_policy import total_congestion,extra_congestion,deterministic_single_step_recovery,welfare_from_initial
from r66_t7_transfer import validate

class TestSevenStates(unittest.TestCase):
    def test_original_cost(self):
        self.assertEqual([total_congestion(n) for n in range(7)],[72,51,36,27,24,27,36])
    def test_optimal_occupancy(self):self.assertEqual(extra_congestion(4),0)
    def test_transition_stochastic(self):
        P=deterministic_single_step_recovery()
        validate(tuple([1]+[0]*6),P)
        self.assertEqual(P[4][4],1)
        self.assertEqual(P[6][5],1)
    def test_finite_horizon(self):
        self.assertEqual(welfare_from_initial(6,1),12)
        self.assertEqual(welfare_from_initial(6,40),15)
    def test_stationary_optimum(self):self.assertEqual(welfare_from_initial(4,40),0)
