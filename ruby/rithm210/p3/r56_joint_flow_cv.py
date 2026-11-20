"""R56: source-sealed leave-one-session-out joint-flow forecasting diagnostics.

Target: (U B->A, D A->B) before the NEXT period is revealed.
Legal predictors: previous occupancy A and public treatment code only.
These source-level diagnostics are NOT a causal test of strategic interaction.
Source rows are never written to a public artifact.
"""
from collections import Counter, defaultdict
import csv
from io import StringIO
from itertools import product
from math import comb, log
from pathlib import Path
from random import Random
from statistics import mean
from zipfile import ZipFile

from r54_original_batch_clock import SOURCE_NAME, audit_zip


def flow_support(a):
    if type(a) is not int or not 0 <= a <= 6:
        raise ValueError('invalid old occupancy')
    return tuple(product(range(7-a),range(a+1)))  # (U, D)


def independent_flow(a,p_down,p_up):
    if not (0 < p_down < 1 and 0 < p_up < 1):
        raise ValueError('smoothed Bernoulli probabilities required')
    law={}
    for u,d in flow_support(a):
        law[u,d]=(comb(a,d)*p_down**d*(1-p_down)**(a-d)*
                  comb(6-a,u)*p_up**u*(1-p_up)**(6-a-u))
    if abs(sum(law.values())-1)>1e-10:
        raise ArithmeticError('non-normalized independent flow law')
    return law


def joint_flow_smooth(a, training, alpha=1):
    if alpha <= 0:
        raise ValueError('positive Laplace concentration required')
    supp=flow_support(a)
    n=sum(training.get((a,u,d),0) for u,d in supp)
    return {(u,d):(training.get((a,u,d),0)+alpha)/(n+alpha*len(supp)) for u,d in supp}


def loss(law, chosen):
    if chosen not in law:
        raise ValueError('impossible joint transition')
    p=law[chosen]
    if not p>0:
        raise ValueError('zero mass: no artificial clipping')
    return (-log(p), 1-2*p+sum(x*x for x in law.values()))


def load_original_transitions(path):
    original=audit_zip(path,require_original=True)  # original hash and 5,616 NumSwitch parity
    groups=defaultdict(dict)
    treatments={}
    with ZipFile(path) as z:
        csv_text=z.read(SOURCE_NAME).decode('utf-8-sig')
    for row in csv.DictReader(StringIO(csv_text)):
        s, sec, trt, period=(int(row[n]) for n in ('session','section','trt','Period'))
        if s in (2,101) or trt not in (1,2,3) or period<1:
            continue
        key=(s,sec,int(row['Group']))
        if key in treatments and treatments[key]!=trt:
            raise ValueError('inconsistent treatment')
        treatments[key]=trt
        at=groups[key].setdefault(period,{})
        actor=int(row['ID'])
        if actor in at:
            raise ValueError('duplicate actor')
        at[actor]=int(row['RouteA'])
    transitions=[]
    for key,by_period in groups.items():
        s=key[0]
        if sorted(by_period)!=list(range(1,41)):
            raise ValueError('incomplete group history')
        for t in range(2,41):
            before,after=by_period[t-1],by_period[t]
            if set(before)!=set(after) or len(before)!=6:
                raise ValueError('changed actor support')
            a=sum(before.values())
            u=sum(before[i]==0 and after[i]==1 for i in before)
            d=sum(before[i]==1 and after[i]==0 for i in before)
            if (u,d) not in flow_support(a):
                raise AssertionError('invalid flow')
            transitions.append((s,treatments[key],a,u,d))
    if len(transitions)!=original['group_period_transitions']:
        raise AssertionError('source sample changed')
    return transitions


def train_counts(rows):
    count=Counter()
    for session,trt,a,u,d in rows:
        count[trt,a,u,d]+=1
    return count


def infer_laws(count,trt,*,joint_alpha=1):
    total_A=total_B=sw_A=sw_B=0
    for a in range(7):
        for u,d in flow_support(a):
            n=count[trt,a,u,d]
            total_A+=a*n;total_B+=(6-a)*n
            sw_A+=d*n;sw_B+=u*n
    pooled_down=(sw_A+0.5)/(total_A+1)
    pooled_up=(sw_B+0.5)/(total_B+1)
    models={name:{} for name in ('pooled_independent','state_independent','joint_laplace')}
    for a in range(7):
        at={ (u,d):count[trt,a,u,d] for u,d in flow_support(a) }
        mass=sum(at.values())
        down=sum(d*n for (u,d),n in at.items())
        up=sum(u*n for (u,d),n in at.items())
        by_a_down=(down+0.5)/(a*mass+1)
        by_a_up=(up+0.5)/((6-a)*mass+1)
        models['pooled_independent'][a]=independent_flow(a,pooled_down,pooled_up)
        models['state_independent'][a]=independent_flow(a,by_a_down,by_a_up)
        local=Counter({(a,u,d):n for (u,d),n in at.items()})
        models['joint_laplace'][a]=joint_flow_smooth(a,local,alpha=joint_alpha)
    return models


def leave_one_session_out(rows, *, bootstrap=2000, seed=20261121, joint_alpha=1):
    sessions=sorted({s for s,trt,a,u,d in rows})
    if len(sessions)<3:
        raise ValueError('at least three independent sessions required')
    by_session=defaultdict(list)
    for entry in rows:
        by_session[entry[0]].append(entry)
    results=[]
    for held in sessions:
        other=[row for s,entries in by_session.items() if s!=held for row in entries]
        counts=train_counts(other)
        fitted={trt:infer_laws(counts,trt,joint_alpha=joint_alpha) for trt in (1,2,3)}
        losses=defaultdict(list)
        for s,trt,a,u,d in by_session[held]:
            for model,by_a in fitted[trt].items():
                losses[model].append(loss(by_a[a],(u,d)))
        results.append({**{name:(mean(e[0] for e in points),mean(e[1] for e in points))
                        for name,points in losses.items()},
                        "_session_transition_count":len(by_session[held])})
    models=('pooled_independent','state_independent','joint_laplace')
    summary={name:{'equal_session_logloss_nats':mean(r[name][0] for r in results),
                   'equal_session_multiclass_brier':mean(r[name][1] for r in results),
                   'pooled_transition_logloss_nats':sum(r[name][0]*r['_session_transition_count'] for r in results)/len(rows),
                   'pooled_transition_multiclass_brier':sum(r[name][1]*r['_session_transition_count'] for r in results)/len(rows)}
             for name in models}
    if type(bootstrap) is not int or bootstrap<1:
        raise ValueError('positive bootstrap count required')
    rng=Random(seed)
    comparisons=[]
    for alternative, baseline in (('state_independent','pooled_independent'),
                                  ('joint_laplace','pooled_independent'),
                                  ('joint_laplace','state_independent')):
        for score,label in enumerate(('logloss_nats','multiclass_brier')):
            contrast=[r[alternative][score]-r[baseline][score] for r in results]
            draws=sorted(mean(contrast[rng.randrange(len(sessions))] for _ in sessions)
                         for _ in range(bootstrap))
            comparisons.append({
                'alternative':alternative,
                'baseline':baseline,
                'score':label,
                'mean_difference':mean(contrast),
                'session_resampling_95_percentile':[
                    draws[int(0.025*bootstrap)],draws[min(bootstrap-1,int(0.975*bootstrap))]],
            })
    return {
        'units':'24 session leave-one-out, all 3 treatment codes in each fold',
        'session_count':len(sessions),
        'transition_count':len(rows),
        'joint_laplace_alpha': joint_alpha,
        'conditioning':'previous A occupancy and treatment only; no future occupancy, choices, or same-session train leakage',
        'models':summary,
        'paired_session_resampling':comparisons,
        'scope':'exploratory source fit; no causal strategic coordination identification',
    }


if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('approved_source_zip',type=Path)
    p.add_argument('--bootstrap',type=int,default=2000)
    p.add_argument('--joint-alpha',type=float,default=1.0)
    args=p.parse_args()
    r=leave_one_session_out(load_original_transitions(args.approved_source_zip),
                            bootstrap=args.bootstrap,joint_alpha=args.joint_alpha)
    print(json.dumps(r,indent=2,sort_keys=True))
