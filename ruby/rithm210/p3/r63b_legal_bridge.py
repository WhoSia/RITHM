"""RITHM-2.10 P3-R63B: permissioned original-data, aggregate-only legal-feedback bridge test.

The original author ZIP is SHA-gated; actor IDs and histories live only in RAM.
Only aggregate, non-disclosive outputs are emitted. Every fold holds out its
ENTIRE original session. No future payoff, actor oracle occupancy or private
row is emitted. Reused original sessions imply exploratory validation only.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from hashlib import sha256
from math import exp, log, log1p
from pathlib import Path
from random import Random
from statistics import mean
import argparse
import csv
import io
import json
import zipfile

APPROVED_SHA = 'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'
SOURCE_CSV = 'data_task_all_switch_230705.csv'
EXCLUDED = frozenset((2, 101))
TAU = 8  # previously studied R61 comparator; NOT reselected on heldout target
SHRINK = 20


def legal_bin(payoff, tenure):
    if tenure < 1: raise ValueError('own route tenure must be >=1')
    a = 0 if payoff < 4 else (1 if payoff < 8 else 2)
    b = 0 if tenure == 1 else (1 if tenure <= 3 else 2)
    return 3*a + b


def load_private_events(source):
    """Exact previous R60 population; private identifiers never leave function outputs."""
    if sha256(Path(source).read_bytes()).hexdigest() != APPROVED_SHA:
        raise ValueError('original-author ZIP SHA256 mismatch; refuse to open')
    people = defaultdict(dict)
    with zipfile.ZipFile(source) as z:
        with io.TextIOWrapper(z.open(SOURCE_CSV), encoding='utf-8-sig') as fp:
            for row in csv.DictReader(fp):
                sid,sec,t = int(row['session']),int(row['section']),int(row['Period'])
                if sid in EXCLUDED or sec not in (2,3,4) or t not in range(1,41):
                    continue
                actor=int(row['ID']); key=(sid,sec,actor)
                if t in people[key]: raise ValueError('duplicate actor/period')
                people[key][t]=(int(row['RouteA']),int(row['Informed']),int(row['trt']),
                                 int(row['Group']),float(row['profit']))
    sessions=sorted({k[0] for k in people})
    if len(sessions)!=24:raise ValueError('24 sessions expected')
    if any(set(h)!=set(range(1,41)) for h in people.values()):
        raise ValueError('source person incomplete')
    events=[]; bygroup=defaultdict(list)
    for (sid,sec,actor),h in people.items():
        if sec==2:continue
        before=people.get((sid,sec-1,actor))
        if before is None:raise ValueError('prior section person absent')
        prior_count=sum(before[t][0]!=before[t-1][0] for t in range(2,41))
        group=h[1][3];info=h[1][1];trt=h[1][2]
        if any((v[1],v[2],v[3])!=(info,trt,group) for v in h.values()):
            raise ValueError('mid-section design changes')
        if before[40][3]!=group:raise ValueError('cross-section group mismatch')
        current_count=0;tenure=1
        for t in range(2,41):
            last=h[t-1];now=h[t]
            flip=int(last[0]!=now[0]);
            e={'session':sid,'section':sec,'group':group,'period':t,'actor':actor,
               'info':info,'treatment':trt,'previous_route':last[0],
               'flip':flip,'prior_flips':prior_count,'current_flips':current_count,
               'exposure':t-2,'legal_bin':legal_bin(last[4],tenure)}
            events.append(e)
            bygroup[(sid,sec,group,t)].append(e)
            current_count+=flip
            tenure=1 if flip else tenure+1
    if len(events)!=22464 or len(bygroup)!=3744 or any(len(g)!=6 for g in bygroup.values()):
        raise ValueError('wrong matched 24-session 6-person source cohort')
    for group in bygroup.values():
        trts={e['treatment'] for e in group}
        if len(trts)!=1:raise ValueError('treatment not group-constant')
        if next(iter(trts))==1 and any(e['info']!=0 for e in group):raise ValueError('No mask mismatch')
        if next(iter(trts))==3 and any(e['info']!=1 for e in group):raise ValueError('Full mask mismatch')
    return events,bygroup


def prior_probability(e, baseline, tau=TAU, shrink=SHRINK):
    if not 0<baseline<1 or tau<0 or shrink<=0 or e['exposure']<0:
        raise ValueError('invalid probability/information clock')
    w=0 if tau==0 else exp(-e['exposure']/tau)
    p=(e['current_flips']+w*e['prior_flips']+shrink*baseline)/(e['exposure']+39*w+shrink)
    if not 0<p<1:raise ValueError('probability not open')
    return p


def sigmoid(x):
    if x>=0:
        z=exp(-x);return 1/(1+z)
    z=exp(x);return z/(1+z)


def calibrate_shift(pairs):
    """Pseudocount-calibrated source-only logit correction; no scipy needed."""
    if len(pairs)<10:return 0.
    logits=[log(p/(1-p)) for p,y in pairs]
    goal=(sum(y for p,y in pairs)+.5)/(len(pairs)+1)
    lo,hi=-12.,12.
    for _ in range(55):
        mid=(lo+hi)/2
        if sum(sigmoid(z+mid) for z in logits)/len(logits)<goal:lo=mid
        else:hi=mid
    return (lo+hi)/2


def fit_model(events,held,source_selector,*,tau=TAU):
    """Condition-stratified fitted law with information-mask nonoverlap explicit."""
    selected=[e for e in events if e['session']!=held and source_selector(e)]
    if len(selected)<100: raise ValueError('source treatment has inadequate training observations')
    # All source model predictors depend only on previous own route and own info mask;
    # no analyst-level old occupancy or other persons' received payoffs.
    bins=defaultdict(lambda:[0,0]); total=defaultdict(lambda:[0,0]);samples=defaultdict(list)
    for e in selected:
        key=e['info'],e['previous_route']
        bins[key][0]+=e['flip'];bins[key][1]+=1
        total[e['info']][0]+=e['flip'];total[e['info']][1]+=1
    base={key:(y+.5)/(n+1) for key,(y,n) in bins.items()}
    for e in selected:
        key=e['info'],e['previous_route']; b=base[key]
        p=prior_probability(e,b,tau=tau)
        samples[(e['info'],e['legal_bin'])].append((p,e['flip']))
    shifts={k:calibrate_shift(v) for k,v in samples.items()}
    support=Counter((e['info'],e['legal_bin']) for e in selected)
    return {'base':base,'shifts':shifts,'support':support,'n_source':len(selected),
            'source_masks':tuple(sorted(total)), 'tau':tau}


def predict(e,model,require_support=True):
    key=e['info'],e['previous_route']
    if key not in model['base'] or (e['info'],e['legal_bin']) not in model['support']:
        if require_support:raise ValueError('legal state unobserved in source training')
        return None
    p=prior_probability(e,model['base'][key],tau=model['tau'])
    return sigmoid(log(p/(1-p))+model['shifts'].get((e['info'],e['legal_bin']),0.))


def poibin(ps):
    out=[1.]
    for p in ps:
        next=[0.]*(len(out)+1)
        for i,x in enumerate(out):
            next[i]+=x*(1-p);next[i+1]+=x*p
        out=next
    return out


def group_joint(ge, probs):
    up=poibin([p for e,p in zip(ge,probs) if e['previous_route']==0]);
    down=poibin([p for e,p in zip(ge,probs) if e['previous_route']==1])
    u=sum(e['flip'] and e['previous_route']==0 for e in ge)
    d=sum(e['flip'] and e['previous_route']==1 for e in ge)
    mass=up[u]*down[d]
    if mass<=0:raise ValueError('joint probability invalid')
    pzero=1.
    for p in probs:pzero*=(1-p)
    return -log(mass), pzero


def bootstrap_diff(diff, seed=20261121, reps=4000):
    """Whole-original-session bootstrap; descriptive, not external confirmation."""
    if not diff:raise ValueError('empty paired sessions')
    vals=list(diff);rng=Random(seed)
    draws=sorted(mean(vals[rng.randrange(len(vals))] for _ in vals) for _ in range(reps))
    return {'paired_delta':mean(vals),'descriptive_session_bootstrap95':
            [draws[int(reps*.025)],draws[min(reps-1,int(reps*.975))]],
            'n_paired_source_sessions':len(vals)}


def bridge_cv(events,groups,*,tau=TAU):
    """Outer 24-fold held-out session, only held-out Partial group-sections evaluated."""
    sessions=sorted({e['session'] for e in events})
    bysession=defaultdict(list)
    for key,grp in groups.items():
        if grp[0]['treatment']==2:bysession[key[0]].append(grp)
    if not bysession:raise ValueError('no Partial groups')
    totals={name:defaultdict(lambda:[0.,0.,0.,0.,0.,0.,0.,0]) for name in ('bridge','partial_invariant')}
    mask_scores={name:defaultdict(lambda:defaultdict(lambda:[0.,0.,0])) for name in totals}
    support={name:Counter() for name in totals}
    byheld={name:{} for name in totals}
    for held in sessions:
        if not bysession.get(held):continue
        # BRIDGE: fit No-uninformed and Full-informed only; never read any Partial outcomes.
        no=fit_model(events,held,lambda e:e['treatment']==1 and e['info']==0,tau=tau)
        full=fit_model(events,held,lambda e:e['treatment']==3 and e['info']==1,tau=tau)
        partial=fit_model(events,held,lambda e:e['treatment']==2,tau=tau)
        for m in ('bridge','partial_invariant'):
            accum=[0.,0.,0.,0.,0.,0.,0.,0]
            for grp in bysession[held]:
                if sum(e['info'] for e in grp)!=3 or len({e['actor'] for e in grp})!=6:
                    raise ValueError('Partial 3+3 actor-information design changed')
                ps=[]
                for e in grp:
                    model=(no if e['info']==0 else full) if m=='bridge' else partial
                    sup=model['support'].get((e['info'],e['legal_bin']),0)
                    support[m]['total_actor']+=1
                    if sup<10:support[m]['source_less_10']+=1
                    if sup<30:support[m]['source_less_30']+=1
                    pred=predict(e,model,require_support=False)
                    if pred is None:raise ValueError('cross treatment strata non-overlap; DO NOT silently substitute')
                    ps.append(pred)
                    accum[0]+=-(log(pred) if e['flip'] else log1p(-pred))
                    accum[1]+=(pred-e['flip'])**2
                    by_info=mask_scores[m][held][e['info']]
                    by_info[0]+=-(log(pred) if e['flip'] else log1p(-pred))
                    by_info[1]+=(pred-e['flip'])**2
                    by_info[2]+=1
                ll,p0=group_joint(grp,ps)
                accum[2]+=ll;accum[3]+=1
                old4=sum(e['previous_route'] for e in grp)==4
                if old4:
                    actual0=int(not any(e['flip'] for e in grp))
                    accum[4]+=(p0-actual0)**2
                    accum[5]+=1
                    accum[6]+=actual0
                    accum[7]+=p0
            byheld[m][held]=accum
            for i,v in enumerate(accum):totals[m][held][i]+=v
    output={'contract':{'approved_zip_sha256':APPROVED_SHA,'total_original_sessions':24,
        'total_original_actor_decisions':22464,'total_original_group_transitions':3744,
        'target':'Partial mixed-information group-sections; no target data in source model training',
        'heldout_unit':'entire original session','tau':tau,'shrink':SHRINK,
        'source_bridge':'No for info0 + Full for info1; no Partial used in training of bridge',
        'comparator':'Partial-only same-mask training on 23 other sessions',
        'claim':'exploratory retrospective prediction only; information-mask invariance NOT causal identification'},
        'evaluated':{'target_bearing_sessions':sum(bool(x) for x in bysession.values()),
                    'outer_training_sessions':24, 'group_transitions':sum(len(x) for x in bysession.values()),
                    'actor_decisions':sum(6*len(x) for x in bysession.values())}}
    scores={}
    for name,d in byheld.items():
        sessions_used=len(d)
        scores[name]={'actor_logloss':mean(v[0]/(6*v[3]) for v in d.values()),
            'actor_brier':mean(v[1]/(6*v[3]) for v in d.values()),
            'joint_U_D_logloss':mean(v[2]/v[3] for v in d.values()),
            'old_A4_no_switch_Brier':mean(v[4]/v[5] for v in d.values() if v[5]),
            'old_A4_no_switch_rate_actual':sum(v[6] for v in d.values())/sum(v[5] for v in d.values()),
            'old_A4_no_switch_mean_predicted':sum(v[7] for v in d.values())/sum(v[5] for v in d.values()),
            'source_strata_lt10_fraction':support[name]['source_less_10']/support[name]['total_actor'],
            'source_strata_lt30_fraction':support[name]['source_less_30']/support[name]['total_actor'],
            'sessions_used':sessions_used,
            'by_information_mask':{str(info):{'actor_logloss':mean(score[info][0]/score[info][2] for score in mask_scores[name].values() if score[info][2]),
                                              'actor_brier':mean(score[info][1]/score[info][2] for score in mask_scores[name].values() if score[info][2])}
                                   for info in (0,1)}}
    output['models']=scores
    paired=sorted(set(byheld['bridge'])&set(byheld['partial_invariant']))
    output['bridge_minus_partial']={key:bootstrap_diff([
      (byheld['bridge'][s][i]-byheld['partial_invariant'][s][i])/(factor*byheld['bridge'][s][3])
      for s in paired],seed=20261121+i) for key,i,factor in [('actor_logloss',0,6),('joint_U_D_logloss',2,1)]}
    # Group/no-switch loss and actors' information subgroups are separate targets.
    a4paired=[s for s in paired if byheld['bridge'][s][5] and byheld['partial_invariant'][s][5]]
    output['bridge_minus_partial']['old_A4_no_switch_Brier']=bootstrap_diff([
      byheld['bridge'][s][4]/byheld['bridge'][s][5] - byheld['partial_invariant'][s][4]/byheld['partial_invariant'][s][5]
      for s in a4paired],seed=20261125)
    for info in (0,1):
        output['bridge_minus_partial']['info'+str(info)+'_actor_logloss']=bootstrap_diff([
            mask_scores['bridge'][s][info][0]/mask_scores['bridge'][s][info][2] -
            mask_scores['partial_invariant'][s][info][0]/mask_scores['partial_invariant'][s][info][2]
            for s in paired],seed=20261126+info)
    return output


def main():
    p=argparse.ArgumentParser(description='Private source in, AGGREGATE ONLY JSON out')
    p.add_argument('approved_private_zip')
    p.add_argument('output_json')
    p.add_argument('--tau',type=float,default=8.0,choices=(0.,8.,16.,float('inf')),help='fixed, exploratory inherited memory discount')
    a=p.parse_args()
    ev,grp=load_private_events(a.approved_private_zip)
    result=bridge_cv(ev,grp,tau=a.tau)
    Path(a.output_json).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'complete','aggregate_only':True,'n_target_groups':result['evaluated']['group_transitions'],
                     'target_sessions':result['evaluated']['target_bearing_sessions']}))

if __name__=='__main__':main()
