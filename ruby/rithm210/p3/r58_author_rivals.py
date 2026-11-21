"""R58: Appendix-faithful *observed-history one-step* EWA-lite/SSM comparisons.

Own value/route/earnings after t enter the information state for t+1 ONLY.
R54 sealed 24-session source is required. Never publish raw groups or actor data.

Notes: an SSM lapse epsilon is an explicit ADDITION to the author's sampling
rule to score zero-probability realizations; do not call it author-estimated.
"""
from collections import defaultdict
from functools import lru_cache
from math import comb, exp, log
from pathlib import Path
from zipfile import ZipFile
from io import StringIO
import csv

from r54_original_batch_clock import audit_zip, SOURCE_NAME
from r57_history_cv import poisson_binomial


def actor_rows_sealed(original):
    """Return tracks entirely in memory. Audit source and guard all six identities."""
    audit_zip(original, require_original=True)
    tracks=defaultdict(lambda: defaultdict(dict))
    meta={}
    with ZipFile(original) as z:
        reader=csv.DictReader(StringIO(z.read(SOURCE_NAME).decode('utf-8-sig')))
        for row in reader:
            session,sec,trt,t=(int(row[k]) for k in ('session','section','trt','Period'))
            if session in (2,101) or trt not in (1,2,3) or t<1:
                continue
            key=(session,sec,int(row['Group']))
            actor=int(row['ID'])
            previous=meta.setdefault(key,trt)
            if previous!=trt:raise ValueError('treatment varies inside group')
            if actor in tracks[key][t]:raise ValueError('duplicate actor')
            route,info,a=(int(row[k]) for k in ('RouteA','Informed','NumA'))
            profit=float(row['profit']); value=float(row['Value']); cost=float(row['Cost'])
            if route not in (0,1) or info not in (0,1) or abs(value-cost-profit)>1e-6:
                raise ValueError('invalid realized profit/informed/route')
            if abs(profit*10-round(profit*10))>1e-7:
                raise ValueError('source earning requires more than 0.1 resolution')
            tracks[key][t][actor]=(route,info,a,profit)
    answer=[]
    for key,by_t in sorted(tracks.items()):
        if set(by_t)!=set(range(1,41)):raise ValueError('not 40 sequential periods')
        ids=sorted(by_t[1]);
        if len(ids)!=6 or any(sorted(by_t[t])!=ids for t in by_t):
            raise ValueError('actor support drift')
        values=[]
        for t in range(1,41):
            frame=[by_t[t][i] for i in ids]
            a=sum(c[0] for c in frame)
            if any(c[2]!=a for c in frame):raise ValueError('mismatched group occupancy')
            values.append(tuple(frame))
        answer.append({'session':key[0], 'treatment':meta[key], 'periods':values})
    if len(answer)!=144:raise ValueError('not 144 actor groups')
    return answer


def other_route_belief(route, earned):
    """Appendix A.2 Tables 2–3: uniform k=other A count consistent with
    privately observed profit and Value in [6,16].

    To match the author's *rounded* table at integer endpoints, use half-open
    intervals for value. Exact boundary values matter for integer
    profits: the source includes values exactly 6 and exactly 16.
    """
    if route not in (0,1):raise ValueError('invalid route')
    candidates=[]
    for k in range(6):
        cost=(k+1) if route==1 else 2*(6-k)
        implied_value=earned+cost
        if 6-1e-9<=implied_value<=16+1e-9:
            candidates.append(k)
    if not candidates:
        raise ValueError('no possible other-player count under private earnings')
    return tuple(1/len(candidates) if k in candidates else 0.0 for k in range(6))


def ewa_path_differences(periods):
    """EWA-lite difference A_A(t-1) - A_B(t-1) before every period t.
    Appendix A.1 self-tuning phi and delta; Appendix A.2 uniform earning
    inference for UInf, no use of unobserved simultaneous choices by UInf.
    """
    if len(periods)!=40:raise ValueError('expected 40-period sequence')
    seen=[[0.0]*6 for _ in range(6)]
    n=[1.0]*6; attractions=[[1.0,1.0] for _ in range(6)]
    output=[]
    for t,frame in enumerate(periods,1):
        output.append(tuple(x[1]-x[0] for x in attractions))
        next_attr=[]
        for seat,(route,info,group_a,profit) in enumerate(frame):
            k=group_a-route
            if not 0<=k<=5:raise ValueError('impossible other players')
            belief=(tuple(float(j==k) for j in range(6)) if info else
                    other_route_belief(route, profit))
            for j in range(6):seen[seat][j]+=belief[j]
            avg=[x/t for x in seen[seat]]
            surprise=sum((avg[j]-belief[j])**2 for j in range(6))
            phi=1-0.5*surprise
            if not -1e-10<=phi<=1+1e-10:raise ValueError('illegal EWA retention')
            phi=max(0.0,min(1.0,phi))
            expected_k=sum(j*b for j,b in enumerate(belief))
            # Foregone earnings under the *same* private value. With no info,
            # infer rather than read the actual others' choices.
            alt_profit=profit + ((3*expected_k-11) if route else (11-3*expected_k))
            addon=[0.0,0.0]; addon[route]=profit
            if alt_profit>=profit-1e-10:addon[1-route]=alt_profit
            n_next=phi*n[seat]+1
            next_attr.append([(phi*n[seat]*attractions[seat][r]+addon[r])/n_next for r in (0,1)])
            n[seat]=n_next
        attractions=next_attr
    return output


def win_from_histogram(diffs, q):
    """Exact probability a sum of q iid sample draws exceeds 0 (tie=1/2).
    Each dict key is an integer reward difference (0.1 profit units).
    FFT accelerates long prefixes; no pseudo-choices or fitted parameters.
    """
    if not 1<=q<=9 or not diffs:raise ValueError('illegal q/diffs')
    import numpy as np
    keys=list(diffs)
    minimum, maximum=min(keys),max(keys)
    width=maximum-minimum
    nfft=1
    while nfft<=q*width:nfft*=2
    base=np.zeros(nfft,dtype=float)
    total=sum(diffs.values())
    for k,v in diffs.items():base[k-minimum]=v/total
    power=np.fft.rfft(base,nfft)**q
    distribution=np.fft.irfft(power,nfft)[:q*width+1]
    # remove floating FFT ripples O(1e-15), never deliberately clip model risk
    distribution=np.maximum(distribution,0.0)
    distribution/=distribution.sum()
    tie=-q*minimum
    if tie<0:return 1.0
    if tie>=len(distribution):return 0.0
    return float(distribution[tie+1:].sum()+0.5*distribution[tie])


def ssm_probabilities(periods):
    """For each t and actor, return 9 conditional p(A|q) for q=1..9.

    Informed sample paired payoff difference per past trial.
    Uninformed sample q iid past A payoffs and q iid past B payoffs,
    if both routes attempted; otherwise a coin per Appendix B.
    """
    if len(periods)!=40:raise ValueError('wrong period count')
    past_a=[[] for _ in range(6)]
    past_b=[[] for _ in range(6)]
    known_differences=[[] for _ in range(6)]
    output=[]
    for frame in periods:
        p=[]
        for i,(route,info,a,profit) in enumerate(frame):
            if info:
                hist=known_differences[i]
                dist=defaultdict(int)
                for d in hist:dist[d]+=1
            elif past_a[i] and past_b[i]:
                # One draw from each action's experienced payoff distribution
                # is independent of another; q repetitions give the sampled
                # average difference, with identical positive sign.
                dist=defaultdict(int)
                for x in past_a[i]:
                    for y in past_b[i]:dist[x-y]+=1
            else:
                dist=None
            if not dist:
                ps=[0.5]*9
            else:
                ps=[win_from_histogram(dist,q) for q in range(1,10)]
            p.append(tuple(ps))
        output.append(tuple(p))
        for i,(route,info,a,profit) in enumerate(frame):
            k=a-route
            known_differences[i].append(10*(11-3*k))
            (past_a if route else past_b)[i].append(int(round(profit*10)))
    return output


def ssm_posterior_predictive(ssm_q_probs,periods,*,epsilon=0.02):
    """Produce SSM5 vs SSM1–9 (latent fixed q_i, Bayesian posterior) p(A).

    A *predeclared lapse* epsilon makes SSM predictive log-score finite even
    where pure best-sample rules assign an observed choice exactly zero mass.
    """
    if not 0<=epsilon<=1:raise ValueError('invalid lapse')
    posterior=[[1/9]*9 for _ in range(6)]
    results=[]
    for f,frame in zip(ssm_q_probs,periods):
        p5=[]; pm=[]
        for i,(qprobs,(route,info,a,profit)) in enumerate(zip(f,frame)):
            qsm=[epsilon/2+(1-epsilon)*p for p in qprobs]
            m=sum(p*w for p,w in zip(qsm,posterior[i]))
            p5.append(qsm[4]);pm.append(m)
            likelihood=[p if route else (1-p) for p in qsm]
            updated=[w*l for w,l in zip(posterior[i],likelihood)]
            evidence=sum(updated)
            if evidence<=0:
                raise ArithmeticError('zero posterior evidence; set epsilon>0')
            posterior[i]=[v/evidence for v in updated]
        results.append({'ssm5':tuple(p5),'ssm1_9':tuple(pm)})
    return results


def flip_probs_from_a(choices, frame):
    return [p if row[0]==0 else 1-p for p,row in zip(choices,frame)]


def flow_law_from_actor_flip(frame, flip):
    down=poisson_binomial([p for p,f in zip(flip,frame) if f[0]==1])
    up=poisson_binomial([p for p,f in zip(flip,frame) if f[0]==0])
    return {(u,d):up[u]*down[d] for u in range(len(up)) for d in range(len(down))}


def macro_cost_moments(old_a, law):
    """Expected gross individual changes and new-period congestion excess.

    No assumed within-period move order: score only the post-simultaneous
    decision occupancy. Resource prices κ are a symbolic external parameter.
    """
    if type(old_a) is not int or not 0<=old_a<=6:
        raise ValueError('invalid old occupancy')
    norm=sum(law.values())
    if abs(norm-1)>1e-10:
        raise ValueError('non-normalized joint flow distribution')
    gross=0.0; excess=0.0
    for (up,down),prob in law.items():
        n=old_a+up-down
        if not 0<=n<=6:raise ValueError('illegal transition law')
        gross+=(up+down)*prob
        excess+=3*(n-4)**2*prob
    return {'gross_changes':gross,'end_period_excess_congestion':excess}


def logistic_probs_from_diffs(diffs,lam):
    import numpy as np
    diffs=np.asarray(diffs,float)
    z=np.clip(lam*diffs,-700,700)
    return 1/(1+np.exp(-z))


def score_laws(frame, nextframe, choices):
    from math import log
    old=sum(x[0] for x in frame)
    u=sum(frame[i][0]==0 and nextframe[i][0]==1 for i in range(6))
    d=sum(frame[i][0]==1 and nextframe[i][0]==0 for i in range(6))
    flip=flip_probs_from_a(choices, frame)
    law=flow_law_from_actor_flip(frame,flip)
    if abs(sum(law.values())-1)>1e-10:raise ArithmeticError('bad joint normalization')
    p=law[(u,d)]
    if p<=0:return (float('inf'),float('inf'),float('inf'))
    flow_score=-log(p)
    actor_score=-sum(log(choices[i] if nextframe[i][0] else (1-choices[i])) for i in range(6))/6
    return flow_score,actor_score, 1-2*p+sum(v*v for v in law.values())
