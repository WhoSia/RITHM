"""Run private source-sealed original replay; PUBLIC output aggregate only."""
import sys,json
from pathlib import Path
from hashlib import sha256
from r54_original_batch_clock import APPROVED_ZIP_SHA256
from r59_prior_exposure import parse_source_section_histories
from r60_cross_segment import events_from_histories
from r62_rollout import run_rollouts
if __name__=='__main__':
    if len(sys.argv) not in (3,4,5):raise SystemExit('usage: r62_rollout_run.py APPROVED_ZIP OUT_AGGREGATE_JSON [observed|fair] [seed]')
    source,out=sys.argv[1:3];start=sys.argv[3] if len(sys.argv)>3 else 'observed';seed=int(sys.argv[4]) if len(sys.argv)>4 else 20261121
    if sha256(Path(source).read_bytes()).hexdigest()!=APPROVED_ZIP_SHA256:raise ValueError('original ZIP SHA failed')
    e,_=events_from_histories(parse_source_section_histories(source))
    r=run_rollouts(e,reps=64,bootstrap=2000,start=start,seed=seed)
    Path(out).write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print('saved source-free aggregate',out,r['source_groups'],r['reps_per_group'])
