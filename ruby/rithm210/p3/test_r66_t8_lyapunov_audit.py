import unittest
from fractions import Fraction as F
from r66_t8_lyapunov_audit import lyapunov,identity_map,sign_flip_map,nonincrease_holds,is_attracted_within
class LyapunovGapAuditTests(unittest.TestCase):
    def test_positive_definite(self):
        self.assertEqual(lyapunov(0),0)
        self.assertTrue(all(lyapunov(F(j,10))>0 for j in range(-5,6) if j))
    def test_identity_satisfies_nonincrease(self):
        self.assertTrue(nonincrease_holds([F(j,10) for j in range(-10,11)],identity_map))
    def test_identity_not_attractive(self):
        self.assertFalse(is_attracted_within(identity_map,F(1,10),100))
    def test_sign_flip_satisfies_nonincrease(self):
        self.assertTrue(nonincrease_holds([F(j,10) for j in range(-10,11)],sign_flip_map))
    def test_sign_flip_not_attractive(self):
        self.assertFalse(is_attracted_within(sign_flip_map,F(1,10),100))
