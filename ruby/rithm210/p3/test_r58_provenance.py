import unittest
from r58_provenance import (assert_result_cohort,SOURCE_ZIP_SHA256,
        LOSO_SESSIONS,EXPECTED_GROUP_TRANSITIONS,EXPECTED_ACTOR_DECISIONS)

class R58ResultContract(unittest.TestCase):
    def test_exact_denominators_and_no_fake_workflows(self):
        result={'source_sha256':SOURCE_ZIP_SHA256,
                'sessions':LOSO_SESSIONS,
                'period_transitions':EXPECTED_GROUP_TRANSITIONS,
                'individual_one_step_predictions':EXPECTED_ACTOR_DECISIONS}
        self.assertTrue(assert_result_cohort(result))
        for key,bad in [('source_sha256','wrong'),('sessions',23),
                        ('period_transitions',5617),
                        ('individual_one_step_predictions',33695)]:
            wrong=dict(result);wrong[key]=bad
            with self.assertRaises(ValueError):assert_result_cohort(wrong)

if __name__=='__main__':unittest.main()
