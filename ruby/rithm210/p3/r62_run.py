"""Run exact SHA-gated source cohort R62: anonymized cohort-level results only."""
import json,sys
from pathlib import Path
from hashlib import sha256
from r59_prior_exposure import parse_source_section_histories
from r60_cross_segment import events_from_histories
from r62_batch import full_cv_fast
from r62_collective import aggregate
from r54_original_batch_clock import APPROVED_ZIP_SHA256

def run(source,bootstrap=2000):
    blob=Path(source).read_bytes()
    if sha256(blob).hexdigest()!=APPROVED_ZIP_SHA256:raise ValueError('approved original SHA mismatch')
    people=parse_source_section_histories(source)
    events,groups=events_from_histories(people)
    all_results={}
    for base in ('current_only','nested_adaptive'):
        result,sel=full_cv_fast(events,actor_model=base,selector='joint')
        stability,stability_sel=full_cv_fast(events,actor_model=base,selector='a4_no_switch_brier')
        for name in ('pause_at_four','pause_late_four'):
            new_name=name+'_stability_tuned'
            result[new_name]=stability[name]
            sel[new_name]=stability_sel[name]
        all_results[base]=aggregate(result,sel,bootstrap=bootstrap,seed=20261121)
    return {'version':'R62.0','source_sha256':APPROVED_ZIP_SHA256,
            'cohort':'original 24 sessions target section3/4, period2..40; original cohort SHA-gated',
            'info_boundary':'shared Z is hidden analyst joint-state representation; no occupancy input for uninformed actors',
            'trained':'q selected within 23 other source sessions on joint flow logloss per outer heldout session; actor p recomputed with heldout session excluded',
            'models':all_results,
            'limitations':'Retrospective exploratory: 24 sessions reused in previous work. Marginal-preserving joint fit does not identify cooperation or causal welfare.'}

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: r62_run.py APPROVED_SOURCE_ZIP OUTPUT_AGGREGATE_JSON')
    result=run(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'complete','out':sys.argv[2],'only_aggregates':True,'cohort':result['models']['current_only']['cohort']},indent=2))
