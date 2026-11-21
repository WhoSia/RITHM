"""Exact source-free RITHM R66-T5 tests, no confidential participant data."""
import unittest
from fractions import Fraction as Q
from r66_t5_public_reference import cost,rates,row,transition,total,local_effect

class R66T5SourceFree(unittest.TestCase):
    def test_original_exact_social_cost(self):
        self.assertEqual([cost(n) for n in range(7)],[48,27,12,3,0,3,12])
    def test_best_response_gains(self):
        self.assertEqual(rates(4),(Q(1,50),Q(1,50)))
        self.assertEqual(rates(5),(Q(2,5),Q(1,50)))
    def test_7_state_row_mass(self):
        for mode in (False,True):
            P,G=transition(mode)
            for n in range(7):
                self.assertEqual(sum(P[n]),1)
                a,b=rates(n)
                self.assertEqual(G[n],Q(1,2)*(n*a+(6-n)*b))
    def test_one_step_covariance_formula_all_states(self):
        for n in range(7):
            self.assertEqual(total(n,2,True)[0]-total(n,2,False)[0],local_effect(n))
    def test_one_step_clock_advantage_n4(self):
        self.assertEqual(local_effect(4),-Q(3,5000))
    def test_40_period_sign_reverse_n4(self):
        d=total(4,40,True)[0]-total(4,40,False)[0]
        self.assertGreater(d,24);self.assertLess(d,26)
    def test_state_dependent_revision_effort(self):
        self.assertLess(total(4,40,effort=Q(1,10))[0],total(4,40,effort=1)[0])
        self.assertLess(total(5,40,effort=Q(2,5))[0],total(5,40,effort=Q(1,10))[0])
        self.assertLess(total(5,40,effort=Q(2,5))[0],total(5,40,effort=1)[0])
    def test_fee_changes_ranking(self):
        self.assertLess(total(5,40,effort=Q(2,5))[2],total(5,40,effort=Q(3,10))[2])
        self.assertGreater(total(5,40,effort=Q(2,5),fee=2)[2],total(5,40,effort=Q(3,10),fee=2)[2])
    def test_clock_extremes(self):
        for t in (Q(0),Q(1)):
            for n in range(7):
                self.assertEqual(sum(transition(True,theta=t)[0][n]),1)
                self.assertEqual(transition(True,theta=t),transition(False,theta=t))
    def test_validation(self):
        with self.assertRaises(ValueError):cost(-1)
        with self.assertRaises(ValueError):total(4,0)
        with self.assertRaises(ValueError):total(4,3,fee=-2)
        with self.assertRaises(ValueError):transition(effort=Q(2))

if __name__=='__main__':unittest.main()
