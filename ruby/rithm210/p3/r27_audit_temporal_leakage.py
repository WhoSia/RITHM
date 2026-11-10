"""RITHM interim audit: t->t+1 future-label quarantine.

The original-author R script '0 data preparation.R' constructs switchWill,
NumAnext, NumBnext, NumSwitchWill from period t+1 ACTUAL route choices.
These are allowed as targets/retrospective labels, never as predictors
for a decision at t. No participant rows or raw data are committed.
"""
from __future__ import annotations
from collections import defaultdict

FUTURE_LABELS=frozenset({
    "switchWill","switchAtoBWill","switchBtoAWill",
    "NumSwitchWill","NumAnext","NumBnext",
})

def assert_no_future_predictors(predictor_names):
    names=set(predictor_names)
    unsafe=sorted(names & FUTURE_LABELS)
    if unsafe:
        raise ValueError(f"t+1 derived outcomes cannot be used as predictors: {unsafe}")
    return tuple(sorted(names))

def audit_rows(rows):
    """Rows have (group, actor, period, RouteA, NumA, switchWill, NumAnext).

    Verify the original author's derivations without exposing individual rows.
    Does not assert that a labelled future field represents a stated intention.
    """
    by_actor=defaultdict(dict)
    for group,actor,period,route,n,will,next_n in rows:
        if route not in (0,1) or not 0<=n<=6:
            raise ValueError("invalid group observation")
        if period in by_actor[group,actor]:
            raise ValueError("duplicate group-actor-period")
        by_actor[group,actor][period]=(route,n,will,next_n)
    checked=0;future_agree=0;last_sentinels=0
    for by_t in by_actor.values():
        for t,(route,n,will,next_n) in by_t.items():
            if t+1 in by_t:
                future_route,future_n,*_=by_t[t+1]
                checked+=1
                future_agree+=int(will==int(route!=future_route) and next_n==future_n)
            elif t==max(by_t):
                last_sentinels+=int(will==-1 and next_n==-1)
    return dict(checked_pairs=checked,matching_pairs=future_agree,
                last_period_sentinels=last_sentinels,
                all_pairs_match=(checked==future_agree))
