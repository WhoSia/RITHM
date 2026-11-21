"""RITHM-2.10 P3-R63C public-aggregate provenance and falsifier tests.

Runs without the original author ZIP; original actor rows NEVER enter GitHub CI.
"""
from hashlib import sha1
from pathlib import Path
import json
import unittest

BASE=Path(__file__).resolve().parent
NAME="r63c_marginal_results.json"
FROZEN="420272814f4b336dabf2606f6d2f20822dc7f35e"


def git_sha(raw):
    return sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()


def audit_bytes(raw):
    if git_sha(raw)!=FROZEN:raise ValueError("public aggregate Git blob SHA mismatch")
    return json.loads(raw)


class MarginalAggregateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=(BASE/NAME).read_bytes()
        cls.x=audit_bytes(cls.raw)

    def test_original_verified_public_aggregate_byte_identity(self):
        self.assertEqual(git_sha(self.raw), FROZEN)

    def test_cohort_and_no_legal_actor_oracle_claim(self):
        x=self.x
        self.assertEqual(x["target"]["old_A4_partial_transitions"],530)
        self.assertEqual(x["target"]["target_bearing_sessions"],17)
        self.assertIn("analyst-only",x["scope"])
        self.assertIn("NOT actor legal",x["oracle_shift_summary"]["source"])
        self.assertEqual(len(x["source_sha256"]),64)

    def test_exact_partial_frank_bounds_contain_observation(self):
        x=self.x
        b=x["all_zero_sharp_marginal_bounds"]
        actual=x["models"]["bridge"]["P0_empirical"]
        self.assertLess(b["mean_lower"],actual)
        self.assertLess(actual,b["mean_upper"])
        self.assertLess(b["mean_lower"],b["mean_upper"])
        self.assertIn("do NOT certify",b["explanation"])

    def test_researcher_oracle_changes_marginals_not_admissibility(self):
        m=self.x["models"]
        real=m["bridge"]["gross_switches_empirical_per_old_A4"]
        before=m["bridge"]["gross_switches_predicted_per_old_A4"]
        after=m["analyst_A4_marginal_oracle"]["gross_switches_predicted_per_old_A4"]
        self.assertLess(abs(after-real),abs(before-real))
        self.assertLess(abs(m["analyst_A4_marginal_oracle"]["P0_predicted"]-.30),
                        abs(m["bridge"]["P0_predicted"]-.30))
        self.assertGreater(m["analyst_A4_marginal_oracle"]["joint_U_D_logloss_equal_session"],
                           m["bridge"]["joint_U_D_logloss_equal_session"])

    def test_paired_intervals_both_include_zero(self):
        for loss in ("P0_Brier","joint_U_D_logloss"):
            v=self.x["oracle_minus_bridge"][loss]
            self.assertLess(v["descriptive_session_bootstrap95"][0],0)
            self.assertGreater(v["descriptive_session_bootstrap95"][1],0)
            self.assertEqual(v["n_paired_source_sessions"],17)

    def test_public_result_rejects_mutated_byte(self):
        with self.assertRaisesRegex(ValueError,"Git blob SHA mismatch"):
            audit_bytes(self.raw+b" ")

    def test_public_result_has_no_person_level_payload(self):
        for marker in (b'"actor_id"',b'"ID"',b'"subject_id"',b'"individual_rows"',
                       b'"group_trajectories"',b'"Value_t"'):
            self.assertNotIn(marker,self.raw)


if __name__=="__main__":unittest.main()
