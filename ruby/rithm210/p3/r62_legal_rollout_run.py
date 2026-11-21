"""Run approved source-verified, observed-initial own-payoff legal feedback rollouts."""
import json,sys
from pathlib import Path
from r59_prior_exposure import parse_source_section_histories
from r60_cross_segment import events_from_histories
from r62_legal_feedback import attach_legal_features
from r62_legal_rollout import run_legal_rollouts
if __name__=='__main__':
    if len(sys.argv) not in (3,4,5):raise SystemExit('usage: r62_legal_rollout_run.py APPROVED_PRIVATE_ZIP OUT_AGGREGATES [observed|fair] [seed]')
    src,out=sys.argv[1:3]
    start=sys.argv[3] if len(sys.argv)>3 else 'observed'
    seed=int(sys.argv[4]) if len(sys.argv)>4 else 20261121
    events,_=events_from_histories(parse_source_section_histories(src))
    events=attach_legal_features(events,src)
    result=run_legal_rollouts(events,src,reps=64,bootstrap=2000,start=start,seed=seed)
    Path(out).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('APPROVED DATA AGGREGATE ONLY:',out,'24 sessions',result['groups'],'group sections')
