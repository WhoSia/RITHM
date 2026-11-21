import unittest
from fractions import Fraction as F
from r66_t7_transfer import validate,left,right,J,telescoping

class TestTransfer(unittest.TestCase):
    def setUp(self):
        self.mu=(F(1),F(0))
        self.P=((F(3,4),F(1,4)),(F(1,3),F(2,3)))
        self.Q=((F(1,2),F(1,2)),(F(1,5),F(4,5)))
        self.c=(F(0),F(3))
    def test_40_step_exact_identity(self):
        for H in (1,2,3,5,12,40):
            self.assertEqual(telescoping(self.mu,self.P,self.Q,self.c,H),
                             J(self.mu,self.Q,self.c,H)-J(self.mu,self.P,self.c,H))
    def test_identical_policy(self):
        self.assertEqual(telescoping(self.mu,self.P,self.P,self.c,40),0)
    def test_initial_cost(self):self.assertEqual(J(self.mu,self.P,self.c,1),0)
    def test_invalid_transition(self):
        with self.assertRaises(ValueError):validate(self.mu,((1,0),(1,1)))
