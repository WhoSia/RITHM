"""P24 tests: synthetic costs and receipt checks, not human intervention evidence."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "traffic_sources"))
from p24_receipt_to_welfare_bridge import Group, ObservationAccess, policy_world, witness


class P24FiniteBridge(unittest.TestCase):
    def setUp(self):
        self.base = Group(4, 4, 4)
        self.ok = ObservationAccess(0, 1, 2)

    def test_baseline_cost(self):
        self.assertEqual(self.base.group_cost(), 212)

    def test_beneficial_stage_c_switch(self):
        self.assertEqual(self.base.switch_at_c("ACB", "ACD").group_cost(), 206)

    def test_harmful_stage_c_switch(self):
        self.assertEqual(self.base.switch_at_c("ACD", "ACB").group_cost(), 220)

    def test_same_upstream_sensor(self):
        self.assertEqual(witness()["upstream_sensor_all_worlds"], 8)

    def test_sharp_restricted_gain_range(self):
        self.assertEqual(witness()["sharp_improvement_interval"], [-8, 6])

    def test_no_receipt_requires_no_advice(self):
        self.assertEqual(set(witness()["when_not_received"]["possible_policy_costs"].values()), {212})

    def test_future_receipt_is_forbidden(self):
        self.assertEqual(policy_world(self.base, ObservationAccess(0, 5, 3), "to_acd"), self.base)

    def test_invalid_version_is_forbidden(self):
        self.assertFalse(ObservationAccess(0, 1, 2, False).authorized())

    def test_receipt_before_measurement_forbidden(self):
        self.assertFalse(ObservationAccess(2, 1, 3).authorized())

    def test_invalid_route_count(self):
        with self.assertRaises(ValueError):
            Group(4, 4, 5)

    def test_incident_cost_is_not_measured(self):
        g = Group(4, 4, 4, incident=1)
        self.assertEqual(g.group_cost(), 212 + 19*4)
        self.assertEqual(g.switch_at_c("ACB", "ACD").group_cost(), 206 + 19*3)

    def test_no_upstream_branch_change(self):
        for response in ("to_acd", "to_acb"):
            x = policy_world(self.base, self.ok, response)
            self.assertEqual((x.ab, x.upstream_ac_sensor()), (4, 8))


if __name__ == "__main__":
    unittest.main()
