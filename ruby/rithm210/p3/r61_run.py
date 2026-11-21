"""Source-restricted R61 aggregate-only replay, one scenario per invocation.

Separate invocations avoid expensive full-scenario runs timing out and permit
stand-alone verification of every file. Never writes actor/group/session rows.
"""
from hashlib import sha256
from pathlib import Path
import argparse,json
from r54_original_batch_clock import APPROVED_ZIP_SHA256
from r59_prior_exposure import parse_source_section_histories
from r60_cross_segment import events_from_histories
from r61_adaptive_prior import run as adaptive_run,get_predictions
from r61_matched_identity import build_adaptive_cost_matrices,check_identity_null
from r61_three_segment_rival import exact_separation,descriptive_three_sections
from r61_closed_loop import rollout_score
from r61_macro_diagnostics import run_diagnostics
from r61_subgroups import stratified_actor_scores

OUTPUTS=('r61_results.json','r61_identity_null.json','r61_subgroups.json',
         'r61_three_segment_results.json','r61_rollout_observed.json',
         'r61_rollout_fair.json','r61_rollout_seed2.json','r61_macro_diagnostics.json')


def execute(original,destination,only):
    src=Path(original);out=Path(destination)
    if only not in OUTPUTS:raise ValueError('unknown aggregate-only scenario')
    if not out.is_dir():raise ValueError('explicit pre-existing output directory required')
    if sha256(src.read_bytes()).hexdigest()!=APPROVED_ZIP_SHA256:
        raise ValueError('approved original ZIP SHA-256 mismatch; no human rows accessed')
    if only=='r61_results.json':
        value=adaptive_run(src)
    else:
        people=parse_source_section_histories(src)
        if only=='r61_three_segment_results.json':
            value={'synthetic_exact':exact_separation(),'original_descriptive':descriptive_three_sections(people)}
        else:
            events,_=events_from_histories(people)
            pred,selected,_=get_predictions(events)
            if only=='r61_identity_null.json':
                matrices=build_adaptive_cost_matrices(events,selected)
                value={scope:check_identity_null(matrices,scope=scope,reps=2000,seed=20261121)
                       for scope in ('group','same_information','same_information_and_boundary_route')}
            elif only=='r61_subgroups.json':value=stratified_actor_scores(pred)
            elif only=='r61_macro_diagnostics.json':
                value=run_diagnostics(events,selected,reps=64,seed=20261121,start='observed')
            else:
                seed=20261122 if only=='r61_rollout_seed2.json' else 20261121
                start='fair' if only=='r61_rollout_fair.json' else 'observed'
                value=rollout_score(events,selected,reps=64,seed=seed,start=start)
    raw=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode('utf-8')
    (out/only).write_bytes(raw)
    return {'result_name':only,'sha256':sha256(raw).hexdigest(),'bytes':len(raw),
            'privacy':'whole-cohort aggregate only; approved source rows never exported'}


if __name__=='__main__':
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('approved_original_zip')
    args.add_argument('existing_output_directory')
    args.add_argument('--only',choices=OUTPUTS,required=True)
    opts=args.parse_args()
    print(json.dumps(execute(opts.approved_original_zip,opts.existing_output_directory,opts.only),indent=2))
