"""R57 author-approved source replay: print only cluster-aggregated CV scores."""
from hashlib import sha256
from pathlib import Path
import json

from r54_original_batch_clock import APPROVED_ZIP_SHA256, audit_zip
from r57_history_cv import load_history_events, leave_one_session_out
from r57_duration_equivalence import exact_check

PRIMARY_SHRINK = 20
SENSITIVITY_SHRINKS = (5, 80)


def generate(source):
    source = Path(source)
    digest = sha256(source.read_bytes()).hexdigest()
    if digest != APPROVED_ZIP_SHA256:
        raise ValueError('not the original authorized source SHA256')
    audited = audit_zip(source, require_original=True)
    events=load_history_events(source)
    main=leave_one_session_out(events,bootstrap=4000,seed=20261121,shrink=PRIMARY_SHRINK)
    # Exact R56 baseline parity: no new baseline or fold selection allowed.
    if abs(main['models']['state_independent']['equal_session_logloss_nats']-
           1.9996137836789747)>1e-12:
        raise AssertionError('R56 frozen baseline changed')
    sensitivity=[]
    for pseudo in SENSITIVITY_SHRINKS:
        item=leave_one_session_out(events,bootstrap=1,seed=20261121,shrink=pseudo)
        sensitivity.append({'pseudo_exposure':pseudo,
                            'equal_session_logloss_nats':{
                                name:values['equal_session_logloss_nats']
                                for name,values in item['models'].items()}})
    return {
        'study':'RITHM-2.10-P3-R57',
        'original_zip_sha256':digest,
        'population':{'sessions':audited['sessions'],
                      'individual_choice_rows':audited['individual_choices'],
                      'group_period_transitions':audited['group_period_transitions'],
                      'declared_switch_mismatches':audited['source_declared_switch_mismatches']},
        'primary_loso':main,
        'retrospective_non_nested_smoothing_sensitivity':sensitivity,
        'exact_latent_spell_hazard_counterexample':exact_check(),
        'privacy':'Aggregate scores and prior source SHA only; no participant, group, session IDs or raw rows.',
        'limits':'Within-task tenure is left-censored by prior practice; prior A occupancy is an analyst predictor, not known to No-information participants. Model comparisons were explored retrospectively; no causal inertia or external-validity claims.'
    }

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('approved_source_zip',type=Path)
    x=p.parse_args()
    print(json.dumps(generate(x.approved_source_zip),indent=2,sort_keys=True))
