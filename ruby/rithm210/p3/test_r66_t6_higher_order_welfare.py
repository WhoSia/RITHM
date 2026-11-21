"""T6: source-free tests for exact higher-order action-correlation witness."""
import unittest
from fractions import Fraction as F
from r66_t6_higher_order_welfare import (
    joint,marginal,pair,triple,one_step_excess,horizon_40_excess,
    integrated_excess_given_initial_k,gross_switches,check
)


class ParityJointWelfare(unittest.TestCase):
    def setUp(self):
        self.a,self.b=joint(0),joint(1)

    def test_both_laws_normalized(self):
        self.assertEqual(sum(self.a.values()),1)
        self.assertEqual(sum(self.b.values()),1)

    def test_four_outcomes_each(self):
        self.assertEqual(len(self.a),4)
        self.assertEqual(len(self.b),4)

    def test_all_marginals_identical(self):
        self.assertEqual(tuple(marginal(self.a,i) for i in range(3)),(F(1,2),)*3)
        self.assertEqual(tuple(marginal(self.b,i) for i in range(3)),(F(1,2),)*3)

    def test_all_pairwise_probabilities_identical(self):
        for i in range(3):
            for j in range(i+1,3):
                self.assertEqual(pair(self.a,i,j),F(1,4))
                self.assertEqual(pair(self.b,i,j),F(1,4))

    def test_all_pairwise_covariances_zero(self):
        for i in range(3):
            for j in range(i+1,3):
                self.assertEqual(pair(self.a,i,j)-marginal(self.a,i)*marginal(self.a,j),0)
                self.assertEqual(pair(self.b,i,j)-marginal(self.b,i)*marginal(self.b,j),0)

    def test_distinct_higher_order(self):
        self.assertEqual(triple(self.a),0)
        self.assertEqual(triple(self.b),F(1,4))

    def test_cubic_integrated_cost(self):
        self.assertEqual([integrated_excess_given_initial_k(k) for k in range(4)],[0,3,15,42])

    def test_identical_one_step(self):
        self.assertEqual(one_step_excess(self.a),one_step_excess(self.b))
        self.assertEqual(one_step_excess(self.a),9)

    def test_long_run_even(self):
        self.assertEqual(horizon_40_excess(self.a),F(45,4))

    def test_long_run_odd(self):
        self.assertEqual(horizon_40_excess(self.b),F(51,4))

    def test_long_run_gap(self):
        self.assertEqual(horizon_40_excess(self.b)-horizon_40_excess(self.a),F(3,2))

    def test_gap_is_six_times_triple_delta(self):
        self.assertEqual(horizon_40_excess(self.b)-horizon_40_excess(self.a),
                         6*(triple(self.b)-triple(self.a)))

    def test_same_total_switch_count(self):
        self.assertEqual(gross_switches(self.a),gross_switches(self.b))
        self.assertEqual(gross_switches(self.a),3)

    def test_same_gross_resource_fee_any_nonnegative_fee(self):
        for fee in (0,1,F(3,2),15,100):
            d=(horizon_40_excess(self.b)+fee*gross_switches(self.b)
              -horizon_40_excess(self.a)-fee*gross_switches(self.a))
            self.assertEqual(d,F(3,2))

    def test_invalid_parity(self):
        with self.assertRaises(ValueError):joint(3)

    def test_invalid_switch_count(self):
        with self.assertRaises(ValueError):integrated_excess_given_initial_k(4)

    def test_summary_reproducible(self):
        self.assertEqual(check()["long_horizon_odd_minus_even"],"3/2")


if __name__=="__main__":
    unittest.main()
