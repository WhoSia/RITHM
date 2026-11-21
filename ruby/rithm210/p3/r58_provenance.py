"""Immutable R58 source provenance and deliberately unfitted structural settings."""
SOURCE_ZIP_SHA256 = 'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'
SOURCE_CSV = 'data_task_all_switch_230705.csv'
AUTHOR_APPENDIX_DATE = '2025-09-18'
AUTHOR_MANUSCRIPT_DATE = '2026-07-24'
AUTHOR_PUBLISHER_DOI = '10.1287/mnsc.2023.00056'
LAMBDA_TRAINING_INTERVAL = (0.0,3.0)
SSM_LAPSE_PREDECLARED = 0.02
SSM_SENSITIVITY_LAPSES = (0.005,0.02,0.05)
LOSO_SESSIONS = 24
EXPECTED_GROUP_TRANSITIONS = 5616
EXPECTED_ACTOR_DECISIONS = 33696


def assert_result_cohort(result):
    if result.get('source_sha256') != SOURCE_ZIP_SHA256:
        raise ValueError('R58 cohort did not use the approved raw-byte ZIP')
    if result.get('sessions') != LOSO_SESSIONS:
        raise ValueError('R58 must evaluate all 24 heldout sessions')
    if result.get('period_transitions') != EXPECTED_GROUP_TRANSITIONS:
        raise ValueError('R58 unexpected group transition denominator')
    if result.get('individual_one_step_predictions') != EXPECTED_ACTOR_DECISIONS:
        raise ValueError('R58 unexpected actor outcome denominator')
    return True
