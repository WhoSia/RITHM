from fractions import Fraction
import unittest
from r27_two_period_welfare import witness

class TestTwoPeriod(unittest.TestCase):
    def test_exact_dynamic_separation(self):
        p,q,d=witness()
        self.assertEqual(p[0],q[0])
        self.assertEqual(p[0],Fraction(63,2))
        self.assertEqual(d,(Fraction(0),Fraction(3,32),Fraction(3,32)))
        self.assertEqual(p[2],Fraction(117,2))
        self.assertEqual(q[2],Fraction(117,2)+Fraction(3,32))

if __name__=='__main__':unittest.main()
