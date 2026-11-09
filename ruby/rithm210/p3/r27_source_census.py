"""R27 source-only audit: R23/R26 inclusion and observed occupancy replay.

The original author-approved participant CSV is read LOCALLY and SHA-checked.
No individual participant outcomes or IDs are serialized. This is NOT a
R26 fitted nested model-selection / heldout numerical replication.
"""
from __future__ import annotations
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'


def census(path):
    p=Path(path)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError('source byte mismatch')
    groups=defaultdict(list)
    with p.open(newline='', encoding='utf-8-sig') as stream:
        for row in csv.DictReader(stream):
            s,trt,t=int(row['session']),int(row['trt']),int(row['Period'])
            if s in (2,101) or trt not in (1,2,3) or not 1<=t<=40:
                continue
            groups[(s,int(row['section']),t,int(row['Group']))].append(row)
    if len(groups)!=5760 or any(len(g)!=6 for g in groups.values()):
        raise ValueError('bad groups')
    session={k[0] for k in groups}
    if len(session)!=24:raise ValueError('bad sessions')
    hist={trt:[0]*7 for trt in (1,2,3)}
    sumcost={trt:0 for trt in hist}
    periods=Counter();unique=Counter()
    for (s,section,t,group),people in groups.items():
        ids=[r['ID'] for r in people]
        if len(set(ids))!=6:raise ValueError('duplicate actor')
        trts={int(r['trt']) for r in people}
        if len(trts)!=1:raise ValueError('mixed treatments')
        trt=next(iter(trts))
        n=sum(int(r['RouteA']) for r in people)
        if not all(int(r['NumA'])==n for r in people):raise ValueError('occupancy mismatch')
        hist[trt][n]+=1
        sumcost[trt]+=24+3*(n-4)**2
        periods[t]+=1
        unique[(s,trt)]+=1
    if any(sum(v)!=1920 for v in hist.values()):raise ValueError('treatment count')
    return {'verified_source_sha256':SOURCE_SHA,'sessions':len(session),'groups':len(groups),'actor_decisions':len(groups)*6,
            'groups_by_treatment':{str(trt):sum(v) for trt,v in hist.items()},
            'occupancy_histogram_by_treatment':{str(k):v for k,v in hist.items()},
            'mean_one_period_cost_by_treatment':{str(k):sumcost[k]/sum(hist[k]) for k in hist},
            'groups_per_period':dict(sorted(periods.items())),
            'min_groups_per_session_treatment':min(unique.values()),'max_groups_per_session_treatment':max(unique.values()),
            'source_replay_scope':'R23/R26 inclusion + observed occupancy/cost census only; NO R26 fitted heldout model replay'}


if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r27_source_census.py original.csv')
    print(json.dumps(census(sys.argv[1]),sort_keys=True,indent=2))
