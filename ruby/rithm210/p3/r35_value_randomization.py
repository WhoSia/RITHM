"""RITHM-2.10 P3-R35 — randomized value shock and predecision negative control.

Source SHA verified; 24 main-paper Partial sessions, author independent Value draws,
but travel Value is HIDDEN at route-choice time. It may be used ONLY as an
experimenter-side design diagnostic, never as a lawful actor input.

Conditional exchangeability test groups within session/section/group/period/
chosen-route/informed. Actor identities are never published. Value is
permuted within this fixed preexisting group. The negative-control comparison
uses *the same current Value* against a switch already decided at time t,
and the matched difference is explicitly NOT a causal treatment effect.
"""
from __future__ import annotations
import csv,hashlib,json
from collections import defaultdict
from pathlib import Path
import numpy as np

SOURCE_SHA='d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb'

def construct_cells(path):
    data=Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest()!=SOURCE_SHA:
        raise ValueError('private original author CSV SHA mismatch')
    record={}
    with Path(path).open('r',encoding='utf-8-sig',newline='') as f:
        for z in csv.DictReader(f):
            sid=int(z['session']); trt=int(z['trt']); t=int(z['Period'])
            if sid in (2,101) or trt!=2 or not 1<=t<=40:continue
            key=(sid,int(z['section']),int(z['Group']),int(z['ID']),t)
            if key in record:raise ValueError('duplicate actor-period')
            y=int(z['RouteA']);info=int(z['Informed'])
            value=float(z['Value']);profit=float(z['profit']);cost=float(z['Cost'])
            if y not in (0,1) or info not in (0,1) or not 6<=value<=16 or abs(value-cost-profit)>1e-9:
                raise ValueError('author value/payoff identity or bound mismatch')
            record[key]=(y,info,value)
    groups=defaultdict(list)
    for (sid,sec,g,aid,t),(y,info,value) in record.items():
        if t==40:continue
        future=record.get((sid,sec,g,aid,t+1))
        past=record.get((sid,sec,g,aid,t-1))
        if future is None:raise ValueError('missing next route choice')
        negative=float('nan') if past is None else float(y!=past[0])
        groups[(sid,sec,g,t,y,info)].append((value,float(y!=future[0]),negative))
    cells=[(k,np.asarray(vals,float)) for k,vals in groups.items() if len(vals)>1]
    if len({k[0] for k,a in cells})!=24:raise ValueError('main 24-session coverage broken')
    census={'all_actor_periods':sum(len(v) for v in groups.values()),
            'all_cells':len(groups),'eligible_cells':len(cells),
            'eligible_actor_periods':sum(len(a) for k,a in cells),
            'singleton_cells':sum(len(v)==1 for v in groups.values())}
    return cells,census

def statistic(cells,column=1):
    numer=denom=0.
    session=defaultdict(lambda:np.zeros(2))
    count=0
    for key,a in cells:
        if np.isnan(a[:,column]).any():continue
        x=a[:,0]-a[:,0].mean()
        y=a[:,column]-a[:,column].mean()
        n=float(x@y);d=float(x@x)
        numer+=n;denom+=d;count+=len(a)
        session[key[0]]+=np.array([n,d])
    if denom<=0:raise ArithmeticError('no within-cell value variation')
    return numer/denom,session,count

def randomization_p(cells,column,slope,seed,reps=2999):
    rng=np.random.default_rng(seed)
    nums=np.zeros(reps);den=0.
    for key,a in cells:
        if np.isnan(a[:,column]).any():continue
        x=a[:,0]-a[:,0].mean()
        y=a[:,column]-a[:,column].mean()
        den+=float(x@x)
        perm=np.argsort(rng.random((reps,len(a))),axis=1)
        nums+=x[perm]@y
    null=nums/den
    p=(1+int(np.sum(np.abs(null)>=abs(slope))))/(reps+1)
    return p,np.quantile(null,[.025,.975]).tolist()

def after_minus_before(cells):
    valid=[(k,np.column_stack((a[:,0],a[:,1]-a[:,2]))) for k,a in cells
           if not np.isnan(a[:,2]).any()]
    return valid

def run(path,reps=2999,seed=20261111):
    cells,census=construct_cells(path)
    after,asess,n=statistic(cells,1)
    before,bsess,nb=statistic(cells,2)
    diff=after_minus_before(cells)
    differential,dsess,nd=statistic(diff,1)
    pA,nullA=randomization_p(cells,1,after,seed,reps)
    pB,nullB=randomization_p(cells,2,before,seed+1,reps)
    pD,nullD=randomization_p(diff,1,differential,seed+2,reps)
    rng=np.random.default_rng(seed)
    ses=sorted(dsess);s=np.asarray([dsess[i] for i in ses])
    samples=s[rng.integers(0,len(s),(3000,len(s)))].sum(axis=1)
    ci=np.quantile(samples[:,0]/samples[:,1],[.025,.975]).tolist()
    info={}
    for i in (0,1):
        sub=[(k,a) for k,a in cells if k[-1]==i]
        value,_,count=statistic(sub,1)
        info[str(i)]={'next_switch_value_slope':value,'eligible_actor_periods':count}
    return {'study':'P3-R35 randomized experimenter Value, predecision placebo and matched differential',
      'source_sha256':SOURCE_SHA,'population':'24 official-main Partial sessions, period t=1..39',
      'census':census,'source_protocol':'V_i,t drawn independently uniform 6..16; not known before route decision, after-period payoff = V-C, so V cannot enter lawful choice forecast',
      'primary_after':{'beta':after,'n':n,'conditional_randomization_p':pA,'null95':nullA},
      'negative_control_before':{'beta':before,'n':nb,'conditional_randomization_p':pB,'null95':nullB},
      'matched_after_minus_before':{'beta':differential,'n':nd,'cells':len(diff),'conditional_randomization_p':pD,'null95':nullD,'exploratory_session_bootstrap95':ci},
      'informed_subgroups':info,'randomization_repetitions':reps,'seed':seed,
      'interpretive_boundary':'Negative control itself shows a nonzero association; cannot promote association with next switch to causal reward-learning. Difference diagnostic is not itself a causal effect estimator. Conditional value exchangeability and author RNG mechanism are not independently verified.'}

if __name__=='__main__':
    import sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r35_value_randomization.py ORIGINAL_PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
