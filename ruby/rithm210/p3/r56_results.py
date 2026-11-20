"""R56 reproducible source-verified aggregate results; no raw source rows emitted."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from r54_original_batch_clock import APPROVED_ZIP_SHA256
from r56_joint_flow_cv import load_original_transitions, leave_one_session_out

ALPHAS=(0.25,0.5,1.0,2.0,4.0,8.0)


def generate(source):
    if sha256(Path(source).read_bytes()).hexdigest() != APPROVED_ZIP_SHA256:
        raise ValueError('wrong original source hash')
    rows=load_original_transitions(source)
    primary=leave_one_session_out(rows,bootstrap=4000,seed=20261121,joint_alpha=1)
    sensitivity=[]
    for alpha in ALPHAS:
        r=leave_one_session_out(rows,bootstrap=1,seed=20261121,joint_alpha=alpha)
        state=r['models']['state_independent']
        joint=r['models']['joint_laplace']
        sensitivity.append({
            'laplace_alpha':alpha,
            'state_independent_session_equal_logloss':state['equal_session_logloss_nats'],
            'joint_laplace_session_equal_logloss':joint['equal_session_logloss_nats'],
            'joint_minus_state_logloss':joint['equal_session_logloss_nats']-state['equal_session_logloss_nats'],
        })
    return {
        'study':'RITHM-2.10-P3-R56',
        'input_sha256':APPROVED_ZIP_SHA256,
        'privacy':'No participant/group/session rows or identifiers published; all scores cohort aggregates.',
        'primary_loso':primary,
        'non_nested_alpha_sensitivity':sensitivity,
        'assumption_boundary':'Smoothing sensitivity is descriptive, NOT a prespecified nested tuning experiment or a proof of strategic independence.'
    }


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_zip',type=Path)
    a=p.parse_args()
    print(json.dumps(generate(a.original_zip),indent=2,sort_keys=True))
