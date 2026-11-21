"""Original private source replay; exports only whole-cohort comparisons."""
import json,sys
from pathlib import Path
from r59_prior_exposure import parse_source_section_histories
from r60_cross_segment import events_from_histories
from r62_legal_feedback import attach_legal_features,score_legal
from r62_legal_joint import legal_joint_cv
from r62_statecal import score_statecal
if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: r62_legal_run.py APPROVED_SOURCE.zip OUTPUT_AGGREGATES.json')
    src,out=sys.argv[1:3]
    events,_=events_from_histories(parse_source_section_histories(src))
    data=attach_legal_features(events,src)
    result={'source':'restricted-author ZIP, identical R60/R61 24-session 3,744 groups',
            'population':{'sessions':24,'group_transitions':3744,'actor_decisions':22464},
            'author_rules':'Only lagged *own* realized payoff and own route tenure enter private actor probability; t outcomes never enter that decision.',
            'post_R61_legal_competitors':{}, 'analyst_oracle_state_conditions':{}}
    for actor in ('current_only','nested_adaptive'):
        result['post_R61_legal_competitors'][actor]={
            'own_legal_history_independent':score_legal(data,base_mode=actor,bootstrap=2000),
            'with_joint_hidden_state':legal_joint_cv(data,base_mode=actor,bootstrap=2000)}
    for state in ('a4','a4_early_late'):
        score,_,_=score_statecal(events,mode=state,actor_model='current_only',bootstrap=2000)
        result['analyst_oracle_state_conditions'][state]=score
    result['scope']='Retrospective same dataset repeatedly examined. No causal policy/strategic interaction/participant occupancy disclosure claims.'
    Path(out).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('sealing original-person-free aggregate',out,'bytes',Path(out).stat().st_size)
