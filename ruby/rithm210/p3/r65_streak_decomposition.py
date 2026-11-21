"""RITHM R65C: descriptive A4 stay-hazard composition vs within-bin change.

This is symmetric Kitagawa/Oaxaca arithmetic, NOT a causal mechanism.
Two age stratifications yield different attributions; do not crown one.
Load the same SHA-approved original cohort through r65_endogenous_stability.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from random import Random
from r65_endogenous_stability import load_private


def chronological_streak_counts(groups, treatment):
    if treatment not in (3,4):raise ValueError('Full or Endogenous only')
    bins={'1':lambda age:age==1,'2':lambda age:age==2,
          '3-4':lambda age:3<=age<=4,'5+':lambda age:age>=5}
    stats=defaultdict(Counter)
    for (sid,g,trt),hist in groups.items():
        if trt!=treatment:continue
        prev=None; age=0
        for t in range(1,41):
            v=hist[t]
            route=tuple(v[k][0] for k in sorted(v))
            age=age+1 if prev is not None and prev==route else 1
            if t<40 and sum(route)==4 and (t<=10 or t>=30):
                ep='early' if t<=10 else 'late'
                nxt=tuple(hist[t+1][k][0] for k in sorted(hist[t+1]))
                b=next(k for k,check in bins.items() if check(age))
                stats[sid,ep,b]['n']+=1
                stats[sid,ep,b]['stay']+=int(route==nxt)
            prev=route
    return stats


def pooled(stats,selected,epoch,agebin,coarse):
    c=Counter()
    for s in selected:
        for b in ('1',) if agebin=='1' else (('2','3-4','5+') if coarse else (agebin,)):
            c.update(stats[s,epoch,b])
    return c


def symmetric_decomposition(stats, selected, *, coarse=False, zero_mode='error'):
    bnames=('1','2+') if coarse else ('1','2','3-4','5+')
    v={}
    for ep in ('early','late'):
        cells=[pooled(stats,selected,ep,b,coarse) for b in bnames]
        if any(not c['n'] for c in cells):
            if zero_mode=='skip':return None
            raise ValueError('age-bin outcome not observed; no invented rate')
        total=sum(c['n'] for c in cells)
        v[ep]=({'weights':[c['n']/total for c in cells],
                'rates':[c['stay']/c['n'] for c in cells],
                'counts':[{'n':c['n'],'stay':c['stay']} for c in cells],
                'P0':sum(c['stay'] for c in cells)/total})
    e,l=v['early'],v['late']
    composition=sum((l['weights'][i]-e['weights'][i])*(e['rates'][i]+l['rates'][i])/2 for i in range(len(bnames)))
    within=sum((l['rates'][i]-e['rates'][i])*(e['weights'][i]+l['weights'][i])/2 for i in range(len(bnames)))
    difference=l['P0']-e['P0']
    if abs(composition+within-difference)>1e-12:raise AssertionError('decomposition failed')
    return {'bins':bnames,'early':v['early'],'late':v['late'],
            'composition':composition,'within_age_bin':within,'total_change':difference}


def resampling(stats,sessions,*,draws=3000,seed=20261121):
    rng=Random(seed);vals=[];invalid=0
    for _ in range(draws):
        selected=[sessions[rng.randrange(len(sessions))] for _ in sessions]
        z=symmetric_decomposition(stats,selected,coarse=True,zero_mode='skip')
        if z is None:invalid+=1;continue
        vals.append((z['composition'],z['within_age_bin'],z['total_change']))
    def interval(arr):
        y=sorted(arr);return [y[int(.025*len(y))],y[min(len(y)-1,int(.975*len(y)))]]
    if len(vals)<draws*.95:raise ValueError('too much bootstrap support loss')
    return {'bootstrap_draws':draws,'valid':len(vals),'zero_bin_skipped':invalid,
            **{k:{'descriptive_95':interval([row[i] for row in vals])} for i,k in enumerate(('composition','within_age_bin','total_change'))}}


def run(source):
    groups=load_private(source)
    ss=sorted({s for s,g,trt in groups})
    if len(ss)!=24:raise ValueError('24 original sessions required')
    out={}
    for trt,name in [(3,'Full'),(4,'Endogenous')]:
        d=chronological_streak_counts(groups,trt)
        out[name]={'four_age_bins':symmetric_decomposition(d,ss,coarse=False),
                   'two_age_bins':symmetric_decomposition(d,ss,coarse=True),
                   'two_age_bin_cluster_bootstrap':resampling(d,ss,draws=3000,seed=20261121+trt)}
    return {'scope':'REUSED PRIVATE ORIGINAL; HISTORICAL DESCRIPTIVE ONLY; post-treatment A4/age selection, NOT causal',
            'original_sessions':24,'original_approved_sha256':'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953',
            'definition':'early previous t=1..10; late previous t=30..39; only oldA4; configuration streak age since last joint route-label change',
            'method':'symmetric Kitagawa mean composition vs within-bin rate decomposition; depends on age grouping',
            'models':out}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('approved_zip');p.add_argument('aggregates_json');args=p.parse_args()
    out=run(args.approved_zip)
    Path(args.aggregates_json).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'aggregate_only':True,'model_contrast':{k:v['four_age_bins']['composition'] for k,v in out['models'].items()}}))

if __name__=='__main__':main()
