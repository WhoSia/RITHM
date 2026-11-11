"""RITHM R37: nondegenerate predecision negative controls for hidden travel Value.

All conditioning variables chosen before the current Value draw unless the
postroute special diagnostic is explicitly labelled; test set spans same
24 paper-main Partial sessions and t=2..39 (both switch outcomes exist).
Outcomes are not conditioned on to make an artificially 'passing' placebo.
"""
from __future__ import annotations
import csv,hashlib,json,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'

def original_rows(path):
    if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=SHA:raise ValueError('original author source SHA mismatch')
    records={}
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f):
            s=int(row['session']);trt=int(row['trt']);t=int(row['Period'])
            if s in (2,101) or trt!=2 or not 1<=t<=40:continue
            key=(s,int(row['section']),int(row['Group']),int(row['ID']),t)
            if key in records:raise ValueError('duplicate actor-period')
            y=int(row['RouteA']);info=int(row['Informed']);v=float(row['Value'])
            if y not in (0,1) or info not in (0,1) or not 6<=v<=16:raise ValueError('invalid source')
            if abs(v-float(row['Cost'])-float(row['profit']))>1e-9:raise ValueError('profit identity failed')
            records[key]=(y,info,v)
    rows=[]
    for (s,sec,g,aid,t),(y,info,v) in records.items():
        if not 2<=t<=39:continue
        yp=records.get((s,sec,g,aid,t-1));yn=records.get((s,sec,g,aid,t+1))
        if yp is None or yn is None:raise ValueError('broken longitudinal identity')
        rows.append((s,sec,g,t,aid,yp[0],y,info,v,int(y!=yp[0]),int(yn[0]!=y)))
    return rows

def make_cells(rows,mode):
    if mode not in ('previous','current','both','info_only'):raise ValueError('unknown conditioning')
    grouped=defaultdict(list)
    for s,sec,g,t,aid,prev,current,info,v,before,after in rows:
        key=(s,sec,g,t,info)
        if mode in ('previous','both'):key+=(prev,)
        if mode in ('current','both'):key+=(current,)
        grouped[key].append((v,before,after))
    return [(k,np.asarray(x,float)) for k,x in grouped.items() if len(x)>=2]

def slope(cells,column):
    num=den=0.;data={};n=0;variable=0
    for key,a in cells:
        x=a[:,0]-a[:,0].mean();y=a[:,column]-a[:,column].mean()
        num+=float(x@y);den+=float(x@x);n+=len(a)
        variable+=int(np.any(y!=0) and np.any(x!=0))
    if den<=0:raise ValueError('zero variation in Value')
    return num/den,{'actors':n,'cells':len(cells),'cells_with_both_value_and_outcome_variation':variable,'value_demeaned_sum_squares':den}

def randomization(cells,col,beta,seed=3711,reps=999):
    rng=np.random.default_rng(seed);num=np.zeros(reps);den=0
    for k,a in cells:
        x=a[:,0]-a[:,0].mean();y=a[:,col]-a[:,col].mean()
        perms=np.argsort(rng.random((reps,len(a))),axis=1)
        num+=(x[perms]@y)
        den+=x@x
    return (1+int(np.sum(np.abs(num/den)>=abs(beta))))/(reps+1)

def run(path,reps=999):
    rows=original_rows(path);out={}
    for mode in ('info_only','previous','current','both'):
        cells=make_cells(rows,mode)
        bv,bmeta=slope(cells,1)
        av,ameta=slope(cells,2)
        pairs=[(k,np.column_stack((a[:,0],a[:,2]-a[:,1]))) for k,a in cells]
        dv,dmeta=slope(pairs,1)
        out[mode]={'before':{'beta':bv,'permutation_p':randomization(cells,1,bv,reps=reps),**bmeta},
          'after':{'beta':av,'permutation_p':randomization(cells,2,av,seed=3712,reps=reps),**ameta},
          'after_minus_before':{'beta':dv,'permutation_p':randomization(pairs,1,dv,seed=3713,reps=reps),**dmeta},
          'diagnosis':'DEGENERATE placebo: both choices fixed' if mode=='both' else ('NONDEGENERATE placebo candidate' if bmeta['cells_with_both_value_and_outcome_variation'] else 'NO negative-control variation')}
    return {'source_sha256':SHA,'raw_actor_periods_t2_to39':len(rows),'permutation_reps':reps,
            'estimand':'pooled within-cell slope, t2..39 with both before/after observed, no outcomes used for selecting cells',
            'conditions':out,
            'conclusion':'Use previous-route cells as a candidate nondegenerate negative control, not both-route cells: conditioning on both makes current switch deterministic. No result automatically certifies assignment independence or causal payoffs.'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python r37_negative_control_gates.py PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
