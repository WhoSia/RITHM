"""All R63 tests are public, source-free and prohibit private human records."""
import json
from fractions import Fraction
from pathlib import Path
import tempfile
import unittest
from r63_transport_audit import (INPUTS, MODELS, audit_directory, exact_legal_transport,
                                 git_blob_sha, treatment_contrasts, uniform_tv_welfare_bound,
                                 validate_aggregate)


def aggregate():
    return {'sessions': 24, 'groups': 96, 'reps': 64,
            'seed': 20261121, 'start': 'observed',
            'source_true_group_total_excess_by_treatment': {'1': 114.1875, '2': 112.40625, '3': 112.3125},
            'models': {m: {'group_total_congestion_MSE': 1.,
                           'mean_cost_by_treatment': {'1': 148.97021484375, '2': 155.2119140625,
                                                      '3': 155.6103515625}} for m in MODELS}}


class TransportAuditTest(unittest.TestCase):
    def test_correct_group_cost_range(self):
        self.assertEqual([3*(a-4)**2 for a in range(7)], [48,27,12,3,0,3,12])

    def test_source_laws_exactly_equal_at_all_periods(self):
        for h in (1, 2, 5, 40):
            self.assertEqual(exact_legal_transport('reset', 'No', h),
                             exact_legal_transport('trap', 'No', h))

    def test_target_diverges_only_after_first_entry(self):
        for h in (1, 2):
            self.assertEqual(exact_legal_transport('reset','Full',h)['cost'],
                             exact_legal_transport('trap','Full',h)['cost'])
        self.assertGreater(exact_legal_transport('trap','Full',40)['cost'] -
                           exact_legal_transport('reset','Full',40)['cost'], Fraction(79))

    def test_exact_40_round_dp_cost(self):
        self.assertAlmostEqual(float(exact_legal_transport('reset','Full',40)['cost']), 10.661157024793388, places=12)
        self.assertAlmostEqual(float(exact_legal_transport('trap','Full',40)['cost']), 90.44342648824303, places=12)

    def test_no_off_horizon_move_and_exact_gross(self):
        self.assertEqual(exact_legal_transport('reset', 'Full', 1)['gross_switches'], 0)
        self.assertEqual(exact_legal_transport('trap', 'Full', 1)['gross_switches'], 0)
        self.assertAlmostEqual(float(exact_legal_transport('reset', 'Full', 40)['gross_switches']),
                               7.016528925619835, places=12)
        self.assertAlmostEqual(float(exact_legal_transport('trap', 'Full', 40)['gross_switches']),
                               0.9835767967317394, places=12)

    def test_cost_and_gross_distinct(self):
        a = exact_legal_transport('reset','Full',40)
        b = exact_legal_transport('trap','Full',40)
        self.assertGreater(a['gross_switches'], b['gross_switches'])
        self.assertLess(a['cost'], b['cost'])

    def test_zero_global_tv_means_zero_bound(self):
        self.assertEqual(uniform_tv_welfare_bound(0,40), 0)
        self.assertEqual(uniform_tv_welfare_bound(1,40), 48*39)

    def test_tv_bound_matches_small_epsilon_sum(self):
        self.assertEqual(uniform_tv_welfare_bound(Fraction(1,10),4), Fraction(48*6,10))

    def test_bad_arguments_rejected(self):
        with self.assertRaises(ValueError): exact_legal_transport('reset','other')
        with self.assertRaises(ValueError): exact_legal_transport('reset','No',0)
        with self.assertRaises(ValueError): uniform_tv_welfare_bound(2)

    def test_aggregate_contrast_identity_and_sign(self):
        x = aggregate()
        validate_aggregate(x,start='observed',seed=20261121)
        v = treatment_contrasts(x)
        self.assertEqual(v['historical_full_minus_no'],-1.875)
        self.assertAlmostEqual(v['models']['legal_independent']['contrast_error_full_minus_no'],8.51513671875)

    def test_cohort_mismatch_rejected(self):
        x=aggregate();x['groups']=95
        with self.assertRaises(ValueError):validate_aggregate(x,start='observed',seed=20261121)
        x=aggregate();x['models'].pop('legal_independent')
        with self.assertRaises(ValueError):validate_aggregate(x,start='observed',seed=20261121)

    def test_mutated_source_is_rejected_by_sha_gate(self):
        with tempfile.TemporaryDirectory() as t:
            for filename,_,_,_ in INPUTS.values():
                Path(t,filename).write_text(json.dumps(aggregate()))
            with self.assertRaisesRegex(ValueError,'Git blob SHA mismatch'):audit_directory(t)

    def test_real_public_aggregate_contract_when_checked_out(self):
        # Local standalone tests may omit the repository aggregate files; CI does not.
        root = Path(__file__).parent
        if not (root / INPUTS['observed'][0]).exists():
            self.skipTest('requires public R62 aggregate JSONs from GitHub checkout')
        report = audit_directory(root)
        for name in INPUTS:
            sc = report['scenarios'][name]
            self.assertEqual(sc['historical_full_minus_no'], -1.875)
            self.assertGreater(sc['models']['legal_independent']['contrast_error_full_minus_no'], 0)
            self.assertLess(sc['models']['legal_independent']['40_round_group_total_mse'],
                            sc['models']['r61_current_only']['40_round_group_total_mse'])
        self.assertAlmostEqual(report['scenarios']['observed']['models']['legal_independent']['contrast_error_full_minus_no'],
                               8.51513671875, places=10)

    def test_git_blob_sha_simple_fixture(self):
        self.assertEqual(git_blob_sha(b'hello\n'),'ce013625030ba8dba906f756967f9e9ca394464a')


if __name__ == '__main__': unittest.main()
