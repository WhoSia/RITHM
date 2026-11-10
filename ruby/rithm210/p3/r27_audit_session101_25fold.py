"""RITHM interim audit 2026-11-10: 25-session fivefold sensitivity to session 101.

The authors' 2026-07-24 experiment protocol (section 4.1) confirms ALL Full
information participants received previous-period route counts. The second lag
was previously disclosed but actual retention/use is unobserved. The lag
forecast is information-admissible for this treatment, NOT identified cognition
or policy effect.
Only treatment 3 (full information); 25 sessions including source-admissible session 101; t>=3.
No original participant rows leave the local machine or enter git/CI.
"""
from __future__ import annotations
import csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path
from random import Random
from r27_r2_observable_lag_dynamics import Params,COUNTS,COSTS,next_law

SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'
BETAS=(.05,.15,.3,.6);INERTIA=(0.,1.);MEMORY=(0.,.5);TAUS=(0.,.3,.6)

def read_events(path):
    path=Path(path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=SHA:
        raise ValueError('original source SHA256 mismatch')
    records=defaultdict(lambda:defaultdict(dict))
    with path.open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            sid,trt,t=(int(r[k]) for k in ('session','trt','Period'))
            if sid==2 or trt!=3 or not 1<=t<=40:continue
            group=(sid,int(r['section']),int(r['Group']))
            aid=int(r['ID'])
            if aid in records[group][t]:raise ValueError('duplicate actor')
            records[group][t][aid]=(int(r['RouteA']),int(r['NumA']))
    out=[];sessions=set()
    for (sid,section,group),by_t in records.items():
        if set(by_t)!=set(range(1,41)):raise ValueError('missing observation periods')
        ids=sorted(by_t[1])
        if len(ids)!=6 or any(sorted(by_t[t])!=ids for t in range(1,41)):
            raise ValueError('unstable actor group')
        masks=[]
        for t in range(1,41):
            choices=[by_t[t][aid][0] for aid in ids]
            if any(y not in (0,1) for y in choices):raise ValueError('nonbinary outcome')
            mask=sum(y<<j for j,y in enumerate(choices))
            if any(by_t[t][aid][1]!=COUNTS[mask] for aid in ids):
                raise ValueError('reported occupancy not actual')
            masks.append(mask)
        for t in range(2,40):
            out.append((sid,masks[t-1],COUNTS[masks[t-2]],masks[t]))
        sessions.add(sid)
    if len(sessions)!=25 or len(out)!=1938:raise ValueError('expected 25 sessions and 1938 group-periods (session 101 has three groups)')
    return out

def metrics(event,params):
    _,last,older,observed=event
    law=next_law(last,older,params)
    joint=-math.log(max(law[observed],1e-300))
    occupancy=-math.log(max(sum(v for j,v in enumerate(law) if COUNTS[j]==COUNTS[observed]),1e-300))
    estimate=sum(v*COSTS[COUNTS[j]] for j,v in enumerate(law))
    return joint,occupancy,abs(estimate-COSTS[COUNTS[observed]])

def choose(scores,train,candidates):
    """Selection only sees the twenty training sessions, not heldout."""
    return min(candidates,key=lambda p:(sum(scores[p,s][0] for s in train)/len(train),
                                        p.beta,p.inertia,p.memory_weight,p.tau))

def run(path):
    groups=read_events(path)
    versions=tuple(Params(b,k,w,t) for b in BETAS for k in INERTIA for w in MEMORY for t in TAUS)
    by=defaultdict(list)
    for g in groups:by[g[0]].append(g)
    sessions=sorted(by)
    fold={s:i%5 for i,s in enumerate(sessions)}
    stats={}
    for p in versions:
        for s in sessions:
            rows=[metrics(e,p) for e in by[s]]
            stats[p,s]=tuple(sum(row[j] for row in rows)/len(rows) for j in range(3))
    chosen=[];deltas=[]
    for f in range(5):
        train=[s for s in sessions if fold[s]!=f]
        test=[s for s in sessions if fold[s]==f]
        if len(train)!=20 or len(test)!=5:raise ValueError('bad train/test split')
        base=choose(stats,train,[p for p in versions if p.tau==0])
        latent=choose(stats,train,[p for p in versions if p.tau>0])
        chosen.append({'fold':f,'train_sessions':20,'test_sessions':5,
                       'independent_params':vars(base),'latent_params':vars(latent)})
        deltas.extend(tuple(stats[latent,s][j]-stats[base,s][j] for j in range(3)) for s in test)
    if len(deltas)!=25:raise ArithmeticError('not 25 heldout sessions')
    rng=Random(20261110);intervals=[]
    for j in range(3):
        boots=sorted(sum(deltas[rng.randrange(25)][j] for _ in range(25))/25 for _ in range(4000))
        intervals.append([boots[100],boots[3900]])
    return {'original_sha256':SHA,'sessions':25,'scored_groups':1938,
            'treatment':'trt=3 Full; author paper §4.1 confirms prior-period occupancy disclosed to all; older lag recall not established',
            'metrics':['six_actor_joint_logloss','seven_count_occupancy_logloss','one_period_cost_mae'],
            'latent_minus_train_selected_independent':[sum(d[j] for d in deltas)/25 for j in range(3)],
            'exploratory_whole_session_bootstrap95':intervals,
            'selected_models':chosen,
            'scope':'historical-source reuse; 25-session fivefold sensitivity after source-code exclusion audit; source treatment 101 trt3 retained; NOT independent confirmatory significance; memory/use unmeasured'}
if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r27_r2_source_cv.py ORIGINAL_PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
