import unittest
from fractions import Fraction as F
from r66_t7_dual import certificate,functional_span_bound
from r66_t7_bounds import sharp_interval
from r66_t7_parity import law
from r66_t7_moments import moments
from r66_t7_recovery import values
from r66_t7_mobius import coefficients

class TestDual(unittest.TestCase):
    def test_primal_dual_exact(self):
        v=values(3);k=moments(law(3,0),3,2)
        lo,hi=sharp_interval(v,3,k)
        self.assertTrue(certificate(v,3,k,lo))
        self.assertTrue(certificate(v,3,k,hi))
    def test_span_contains_sharp_bounds(self):
        v=values(3);k=moments(law(3,0),3,2)
        coeff=coefficients(v,3)
        estimate=sum((co*k[s] for s,co in coeff.items() if len(s)<=2),F(0))
        lb,ub=functional_span_bound(v,3,2,estimate)
        lo,hi=sharp_interval(v,3,k)
        self.assertLessEqual(lb,lo.value)
        self.assertGreaterEqual(ub,hi.value)
    def test_certificate_rejects_bad_value(self):
        v=values(3);k=moments(law(3,0),3,2)
        lo,_=sharp_interval(v,3,k)
        from dataclasses import replace
        self.assertFalse(certificate(v,3,k,replace(lo,value=F(0))))
