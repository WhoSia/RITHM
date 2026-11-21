"""RITHM-2.10 P3-R63: source-free condition-contrast audit and exact counterexample.

All inputs are *existing aggregate-only* R62 JSON; NEVER ingest private actor rows.
This is retrospective descriptive validation, not causal information-policy welfare.
"""
from fractions import Fraction
from hashlib import sha1
import json
from pathlib import Path

INPUTS = {
    'observed': ('r62_legal_rollout_observed.json', '7969de70be8f11a2b081e77471b1e8086067bb17', 'observed', 20261121),
    'fair': ('r62_legal_rollout_fair.json', '0399f0009aac60046949249c0e56243e11d3812a', 'fair', 20261121),
    'seed2': ('r62_legal_rollout_seed2.json', '4ad844efec4a73b28f5f63445d8b3f5b0e249867', 'observed', 20261123),
}
MODELS = ('r61_current_only', 'legal_independent', 'legal_pause_stability', 'legal_common_shock_joint')
CONDITIONS = ('1', '2', '3')  # R62: No, Partial, Full


def git_blob_sha(raw):
    return sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def validate_aggregate(doc, *, start, seed):
    if doc.get('sessions') != 24 or doc.get('groups') != 96 or doc.get('reps') != 64:
        raise ValueError('R62 cohort/replication contract changed')
    if doc.get('start') != start or doc.get('seed') != seed:
        raise ValueError('scenario labels do not match data')
    if set(doc['models']) != set(MODELS):
        raise ValueError('missing or unexpected model')
    true = doc['source_true_group_total_excess_by_treatment']
    if set(true) != set(CONDITIONS):
        raise ValueError('unknown treatment coding')
    if any(set(doc['models'][m]['mean_cost_by_treatment']) != set(CONDITIONS) for m in MODELS):
        raise ValueError('model treatment coding changed')
    return true


def treatment_contrasts(doc):
    true = doc['source_true_group_total_excess_by_treatment']
    truth_contrast = true['3'] - true['1']
    models = {}
    for m in MODELS:
        block = doc['models'][m]
        predicted = block['mean_cost_by_treatment']
        contrast = predicted['3'] - predicted['1']
        models[m] = {
            '40_round_group_total_mse': block['group_total_congestion_MSE'],
            'mean_bias_no': predicted['1'] - true['1'],
            'mean_bias_partial': predicted['2'] - true['2'],
            'mean_bias_full': predicted['3'] - true['3'],
            'predicted_full_minus_no': contrast,
            'contrast_error_full_minus_no': contrast - truth_contrast,
        }
    return {'historical_full_minus_no': truth_contrast, 'models': models}


def audit_directory(root):
    root = Path(root)
    out = {'status': 'AGGREGATE_ONLY_EXPLORATORY_NOT_CAUSAL', 'scenarios': {}}
    true_ref = None
    for label, (filename, expected_sha, start, seed) in INPUTS.items():
        raw = (root / filename).read_bytes()
        if git_blob_sha(raw) != expected_sha:
            raise ValueError(f'{filename}: exact R62 Git blob SHA mismatch')
        doc = json.loads(raw)
        true = validate_aggregate(doc, start=start, seed=seed)
        if true_ref is not None and true != true_ref:
            raise ValueError('historical treatment reference changed between scenarios')
        true_ref = true
        out['scenarios'][label] = {'source_blob_sha': expected_sha, **treatment_contrasts(doc)}
    return out


def exact_legal_transport(world, treatment, horizon=40):
    """One flexible actor; 4 fixed A + 1 fixed B. Only own route and treatment.

    At A4 the flexible actor switches B->A with probability 1/10.
    At A5 it switches A->B certainly, except for world='trap' under Full.
    The other five actors do not switch. All six choices are simultaneous.
    The source No law is IDENTICAL across worlds at every time and state.
    Each step's congestion cost is 3*(number_of_A-4)**2.
    """
    if world not in ('reset', 'trap') or treatment not in ('No', 'Full'):
        raise ValueError('unknown world or observable treatment')
    if not isinstance(horizon, int) or horizon < 1:
        raise ValueError('positive integer horizon required')
    p5, cost, gross = Fraction(0), Fraction(0), Fraction(0)
    per_period = []
    for _ in range(horizon):
        per_period.append(p5)
        cost += 3 * p5
        leaving_four = (1 - p5) / 10
        returning_four = p5 * (0 if world == 'trap' and treatment == 'Full' else 1)
        gross += leaving_four + returning_four
        p5 = p5 + leaving_four - returning_four
    return {'cost': cost, 'gross_switches': gross, 'p5_by_period': tuple(per_period)}


def uniform_tv_welfare_bound(epsilon, horizon=40, max_period_cost=48):
    """Classical coupling upper bound; common initial augmented state and reward.

    Requires sup_x TV(K_t(x,.),L_t(x,.))<=epsilon over ALL reachable
    augmented states, not merely states in observed source data.
    """
    eps = Fraction(epsilon)
    if not 0 <= eps <= 1 or horizon < 1:
        raise ValueError('invalid global TV condition')
    return Fraction(max_period_cost) * sum((min(Fraction(1), t * eps) for t in range(horizon)), Fraction(0))


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', nargs='?', default=str(Path(__file__).parent))
    args = p.parse_args()
    output = audit_directory(args.directory)
    a = exact_legal_transport('reset', 'Full')['cost']
    b = exact_legal_transport('trap', 'Full')['cost']
    output['synthetic_full_40'] = {'reset_cost': float(a), 'trap_cost': float(b), 'difference': float(b-a), 'fraction_difference': str(b-a)}
    print(json.dumps(output, indent=2, sort_keys=True))
