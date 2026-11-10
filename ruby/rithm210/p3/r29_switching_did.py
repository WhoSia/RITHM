"""Descriptive Partial info-group switch rates by period, not causal DID.

Uses original-source actor histories but exports no personal records.
Within-session treatment crossover and group interference mean this is
a descriptive late-minus-early contrast, not a causal treatment effect.
"""
from __future__ import annotations
import csv,hashlib,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from r29_partial_information_cv import SOURCE_SHA

WINDOWS={'early':(2,10),'middle':(11,30),'late':(31,40)}

def run(path):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError('source SHA mismatch')
    by=defaultdict(lambda:defaultdict(dict))
    with open(path,newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            s=int(r['session']);trt=int(r['trt']);p=int(r['Period'])
            if s in (2,101) or trt!=2 or not 1<=p<=40:continue
            key=(s,int(r['section']),int(r['Group']))
            aid=int(r['ID'])
            if aid in by[key][p]:raise ValueError('duplicate actor')
            by[key][p][aid]=(int(r['RouteA']),int(r['Informed']))
    session_stats=defaultdict(lambda:defaultdict(list))
    for (s,section,g),periods in by.items():
        actors=sorted(periods[1])
        if len(actors)!=6 or set(periods)!=set(range(1,41)):
            raise ValueError('bad group structure')
        if any(sorted(periods[p])!=actors for p in range(1,41)):
            raise ValueError('actor drift')
        marks={a:periods[1][a][1] for a in actors}
        if sum(marks.values())!=3 or any(periods[p][a][1]!=marks[a] for p in range(1,41) for a in actors):
            raise ValueError('informed membership changed')
        for window,(lo,hi) in WINDOWS.items():
            for info in (0,1):
                values=[float(periods[p][a][0]!=periods[p-1][a][0])
                        for p in range(lo,hi+1) for a in actors if marks[a]==info]
                session_stats[s][window,info].extend(values)
    sessions=sorted(session_stats)
    if len(sessions)!=24 or len(by)!=48:raise ValueError('not published 24 main sessions')
    per={s:{f'{w}_{i}':float(np.mean(session_stats[s][w,i]))
            for w in WINDOWS for i in (0,1)} for s in sessions}
    keys=[f'{w}_{i}' for w in WINDOWS for i in (0,1)]
    pooled={k:float(np.mean([per[s][k] for s in sessions])) for k in keys}
    did=np.array([(per[s]['late_1']-per[s]['early_1'])-
                  (per[s]['late_0']-per[s]['early_0']) for s in sessions])
    rng=np.random.default_rng(20261110)
    reps=np.array([np.mean(did[rng.integers(0,len(did),len(did))])
                   for _ in range(5000)])
    return {'source_sha256':SOURCE_SHA,
        'population':'Partial, published 24 sessions, 48 groups, fixed 3 informed per 6',
        'windows':WINDOWS,'switch_rate_session_equally_weighted':pooled,
        'late_minus_early_information_difference_in_differences':float(did.mean()),
        'descriptive_session_bootstrap95':np.quantile(reps,[.025,.975]).tolist(),
        'caveat':'Descriptive contrast, NOT causal DID. No treatment order adjustment, no parallel trends and dynamic group interference.'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python r29_switching_did.py PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
