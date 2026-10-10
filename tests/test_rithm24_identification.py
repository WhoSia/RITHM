import unittest
from fractions import Fraction
from rithm24_identification import (traffic_cost,exact_rank,identification_rank,
                                    execution_equivalence,joint_cost_counterexample,opening_contract)
class RITHM24Math(unittest.TestCase):
 def test_all_feasible_flow_identities(self):
  for n1 in range(13):
   for n2 in range(13-n1):
    for z in (0,1):
     n3=12-n1-n2
     self.assertEqual(traffic_cost(n1,n2,z),n1*(10+n1+n2)+n2*(13+n2+19*z)+n3*(22-n1))
 def test_invalid_flow_rejected(self):
  with self.assertRaises(ValueError): traffic_cost(11,4,0)
 def test_rank_nonidentification_and_repair(self):
  x=identification_rank()
  self.assertEqual(x["natural_rank"],3)
  self.assertEqual(x["random_private_feedback_rank"],4)
 def test_intention_execution_not_identified(self):
  self.assertEqual(execution_equivalence()["identical_final_route1_probability"],"7/10")
 def test_fixed_marginal_joint_welfare(self):
  r=joint_cost_counterexample()
  self.assertEqual([r[x]["expected_cost"] for x in ("balanced","independent","synchronized")],["192","198","264"])
 def test_no_spurious_human_promotion(self):
  self.assertIn("DESIGN_ONLY",opening_contract()["study_status"])
if __name__=="__main__":unittest.main()
