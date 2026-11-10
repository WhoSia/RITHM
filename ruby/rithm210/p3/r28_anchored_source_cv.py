"""RITHM R28: anchored sixfold 24/25/26 source-cohort sensitivity.

Every historical source actor/group row stays in the private input CSV.
No future-derived switches or next-period count are used as features.
Original 24 sessions stay in the same six folds as R27-R2; add 101 to
fold 0 and pilot2 to fold 1. Out-of-fold model choice is train-only.
The 26 cohort follows the literal original R predicate, NOT an
endorsement of pilot2 in the published study population.
"""
from __future__ import annotations
import csv,hashlib,math,json,sys
from collections import defaultdict
from pathlib import Path
from r27_r2_observable_lag_dynamics import Params,COUNTS,COSTS,next_law
from r27_audit_population_contracts import EXPECTED,CONTRACTS, included

SHA="d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb"
BETAS=(.05,.15,.3,.6)
CANDIDATES=tuple(Params(b,k,w,t) for b in BETAS
                 for k in (0.,1.) for w in (0.,.5) for t in (0.,.3,.6))


def all_events(path):
    path=Path(path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=SHA:raise ValueError('source SHA changed')
    groups=defaultdict(lambda:defaultdict(dict))
    with path.open(newline="",encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            s,trt,t=(int(r[x]) for x in ('session','trt','Period'))
            if not included(s,trt,t,'literal_author_R_filter_26'):continue
            key=(s,int(r['section']),int(r['Group']))
            aid=int(r['ID'])
            if aid in groups[key][t]:raise ValueError('duplicate actor')
            groups[key][t][aid]=(int(r['RouteA']),int(r['NumA']))
    out=defaultdict(list)
    for (s,section,group),periods in groups.items():
        if set(periods)!=set(range(1,41)):raise ValueError('missing periods')
        actors=sorted(periods[1])
        if len(actors)!=6 or any(sorted(periods[t])!=actors for t in range(1,41)):
            raise ValueError('unstable actor identity')
        masks=[]
        for t in range(1,41):
            mask=sum(periods[t][aid][0]<<i for i,aid in enumerate(actors))
            if any(periods[t][aid][1]!=COUNTS[mask] for aid in actors):
                raise ValueError('occupancy discrepancy')
            masks.append(mask)
        for i in range(2,40):
            out[s].append((masks[i-1],COUNTS[masks[i-2]],masks[i]))
    if len(out)!=26 or sum(map(len,out.values()))!=2014:raise ValueError('bad source census')
    return dict(out)


def fixed_folds(sessions):
    core=sorted(set(sessions)-{2,101})
    if len(core)!=24:raise ValueError('need 24 common sessions')
    mapping={s:i%6 for i,s in enumerate(core)}
    if 101 in sessions:mapping[101]=0
    if 2 in sessions:mapping[2]=1
    return mapping


def score_events(events):
    cache={}
    result={}
    for p in CANDIDATES:
        total=[0.,0.,0.]
        for last,older,nxt in events:
            key=(p,last,older)
            if key not in cache:
                law=next_law(last,older,p)
                probn=[sum(v for j,v in enumerate(law) if COUNTS[j]==n) for n in range(7)]
                e_cost=sum(probn[n]*COSTS[n] for n in range(7))
                cache[key]=(law,probn,e_cost)
            law,pn,e_cost=cache[key]
            n=COUNTS[nxt]
            total[0]-=math.log(max(law[nxt],1e-300))
            total[1]-=math.log(max(pn[n],1e-300))
            total[2]+=abs(e_cost-COSTS[n])
        result[p]=tuple(v/len(events) for v in total)
    return result


def select(scores,train,family):
    if not train or not family:raise ValueError('empty train/family')
    return min(family,key=lambda p:(sum(scores[s][p][0] for s in train)/len(train),
                                    p.beta,p.inertia,p.memory_weight,p.tau))


def _aggregate(rows):
    if not rows:return None
    return {'sessions':len(rows),
            'independent':[sum(a[j] for a,b in rows)/len(rows) for j in range(3)],
            'latent':[sum(b[j] for a,b in rows)/len(rows) for j in range(3)],
            'delta':[sum(b[j]-a[j] for a,b in rows)/len(rows) for j in range(3)]}


def run(path):
    events=all_events(path)
    folds=fixed_folds(events)
    scores={s:score_events(rows) for s,rows in events.items()}
    families=((p for p in CANDIDATES if p.tau==0),
              (p for p in CANDIDATES if p.tau>0))
    base_family=tuple(families[0]);latent_family=tuple(families[1])
    results={}
    for contract in CONTRACTS:
        avail=sorted(s for s in events if included(s,3,3,contract))
        expect=EXPECTED[contract]
        if len(avail)!=expect[0] or sum(len(events[s]) for s in avail)!=expect[2]:
            raise ValueError('contract census failed')
        tested={};models=[]
        for f in range(6):
            train=[s for s in avail if folds[s]!=f]
            held=[s for s in avail if folds[s]==f]
            if not held or set(train)&set(held):raise ValueError('fold boundary failure')
            a=select(scores,train,base_family)
            b=select(scores,train,latent_family)
            models.append({'fold':f,'n_train':len(train),'n_heldout':len(held),
                           'independent':vars(a),'latent':vars(b)})
            tested.update({s:(scores[s][a],scores[s][b]) for s in held})
        if set(tested)!=set(avail):raise ValueError('holdout missing')
        common=[tested[s] for s in avail if s not in (2,101)]
        extras=[tested[s] for s in avail if s in (2,101)]
        results[contract]={'sessions':len(avail),'scored_group_periods':expect[2],
                           'all_equal_session_weight':_aggregate(list(tested.values())),
                           'same_common24_holdouts':_aggregate(common),
                           'additional_session_holdouts':_aggregate(extras),
                           'selected':models}
    return {'source_sha256':SHA,
            'protocol':'anchored sixfold, fixed 24-session assignment; add101 to fold0, add2 to fold1; each fold train-only selection',
            'metrics':['joint_logloss','occupancy_logloss','cost_mae'],
            'result':results,
            'limitations':'exploratory; folds grow to 21-22 train sessions with additional cases, so equal fold design is NOT equal training-set size; only the original 24 heldout assignments are fixed; no causal attribution'}


if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit('usage: python r28_anchored_source_cv.py PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
