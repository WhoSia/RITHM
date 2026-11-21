import unittest
from fractions import Fraction as F
from r66_t8_moment_polytope import sharp_interval,verify_certificate
from r66_t8_welfare import recovery_excess,stage_excess
C=[recovery_excess(k) for k in range(5)]
M12={1:(F(1,2),F(1,2)),2:(F(1,4),F(1,4))}

class SharpMomentTests(unittest.TestCase):
    def test_four_actor_recovery_sharp(self):
        x=sharp_interval(C,M12)
        self.assertEqual((x.lower,x.upper),(F(43,2),F(47,2)))
        self.assertTrue(verify_certificate(x,C,M12))
    def test_one_step_point_identification(self):
        s=sharp_interval([stage_excess(k) for k in range(5)],M12)
        self.assertEqual(s.lower,s.upper)
        self.assertEqual(s.lower,15)
    def test_fix_triple_recovery(self):
        fixed={**M12,3:(F(1,8),F(1,8))}
        s=sharp_interval(C,fixed)
        self.assertEqual((s.lower,s.upper),(F(45,2),F(45,2)))
    def test_intervals_include_point(self):
        im={1:(F(2,5),F(3,5)),2:(F(1,5),F(3,10))}
        x=sharp_interval(C,im);y=sharp_interval(C,M12)
        self.assertLessEqual(x.lower,y.lower)
        self.assertGreaterEqual(x.upper,y.upper)
    def test_fully_unknown(self):
        x=sharp_interval(C,{})
        self.assertEqual((x.lower,x.upper),(0,90))
    def test_infeasible_input(self):
        with self.assertRaises(ValueError):sharp_interval(C,{1:(F(1),F(1)),2:(0,0)})
    def test_reject_negative_bound(self):
        with self.assertRaises(ValueError):sharp_interval(C,{1:(-1,1)})
    def test_reject_invalid_dimension(self):
        with self.assertRaises(ValueError):sharp_interval([1,2],M12)
    def test_finite_vertices(self):
        self.assertGreater(sharp_interval(C,M12).vertex_count,0)
