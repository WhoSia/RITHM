"""RITHM-2.10 R66-T3: actor-legal last payoff and investigator-only configuration age.

Approved original-author human data stay private in RAM. Export eight LARGE
condition-by-epoch cells + original-SESSION-paired descriptive uncertainty only.
Exploratory reuse of 24 original sessions; no identification of common clocks,
observed cooperation, information-policy effect, or physiological switching cost.

Actor-legal predictors at the decision for t+1: own observed route, treatment
context, own info flag, own previous route tenure, and own received payoff t.
Information on t+1 or others' unrevealed routes/payoffs is NEVER in legal models.
Analyst-only models can see previous total A, entire six-person route-vector age.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from hashlib import sha256
from io import TextIOWrapper
import json
from math import log, log1p
from pathlib import Path
from random import Random
from zipfile import ZipFile

from r65_endogenous_stability import load_private, APPROVED_SHA, CSV, TREATMENT
from r66_t2_original_audit import period_epoch, age_bin

MODELS=('legal_coarse','legal_tenure','legal_payoff_tenure',
        'analyst_A4','analyst_A4_age','analyst_A4_age_payoff')
EPOCH=('early','late')
SHRINK_TENURE=20
SHRINK_PAYOFF=25
SHRINK_A4=20
SHRINK_AGE=25
SHRINK_AGE_PAYOFF=30


def payoff_bin(x):
    # preexisting R63B payoff discretization; NOT selected on R66-T3 targets
    if not isinstance(x,(int,float)) or x!=x or abs(x)==float('inf'):
        raise ValueError('invalid last experienced payoff')
    return 0 if x<4 else (1 if x<8 else 2)


def read_private_payoff(source, groups):
    """Revalidates authorized bytes; returns private row map, never serialized."""
    if sha256(Path(source).read_bytes()).hexdigest()!=APPROVED_SHA:
        raise ValueError('approved source sha256 mismatch')
    rows={}
    with ZipFile(source) as z, TextIOWrapper(z.open(CSV),encoding='utf-8-sig') as fp:
        for r in csv.DictReader(fp):
            sid,trt,t,actor=int(r['session']),int(r['trt']),int(r['Period']),int(r['ID'])
            if (sid,int(r['Group']),trt) not in groups:continue
            key=sid,int(r['Group']),trt,t,actor
            if key in rows:raise ValueError('duplicate payoff row')
            rows[key]=float(r['profit'])
    if len(rows)!=48*4*40*6:raise ValueError('wrong original payoff-join population')
    for (sid,group,trt),history in groups.items():
        for t in range(1,41):
            if any((sid,group,trt,t,i) not in rows for i in history[t]):
                raise ValueError('payoff join missing actor')
    return rows


def create_events(groups,payoffs):
    events=[];joint=defaultdict(list)
    for (sid,g,trt),history in groups.items():
        roster=sorted(history[1])
        own_age={i:1 for i in roster}
        previous_joint=None; joint_age=0
        info_count=sum(x[1] for x in history[1].values())
        for t in range(1,40):
            before=tuple(history[t][i][0] for i in roster)
            after=tuple(history[t+1][i][0] for i in roster)
            joint_age=joint_age+1 if before==previous_joint else 1
            n_old=sum(before)
            epoch=period_epoch(t)
            if epoch:
                for j,i in enumerate(roster):
                    prev,info=history[t][i]
                    e={'session':sid,'group':g,'treatment':trt,'epoch':epoch,
                       'previous_A':n_old,'previous_route':prev,'info':info,
                       'tenure_bin':age_bin(own_age[i]),
                       'payoff_bin':payoff_bin(payoffs[sid,g,trt,t,i]),
                       'joint_age_bin':age_bin(joint_age),
                       'info_count_analyst':info_count,
                       'flip':int(before[j]!=after[j]),
                       'up':int(before[j]==0 and after[j]==1),
                       'down':int(before[j]==1 and after[j]==0)}
                    events.append(e);joint[(sid,g,trt,t)].append(e)
            for j,i in enumerate(roster):
                own_age[i]=own_age[i]+1 if before[j]==after[j] else 1
            previous_joint=before
    if len(events)!=48*4*20*6 or len(joint)!=48*4*20:
        raise ValueError('unexpected 24-session 4-condition sample size')
    for group in joint.values():
        if len(group)!=6:raise ValueError('not six matched actors')
        n=group[0]['previous_A'];u=sum(x['up'] for x in group);d=sum(x['down'] for x in group)
        if not 0<=n+u-d<=6:raise AssertionError('out-of-range transition')
    return events,dict(joint)


def coarse_key(e):return e['treatment'],e['epoch'],e['info'],e['previous_route']


def build_tables(events,held):
    names=('coarse','tenure','tenure_payoff','A4','A4_age','A4_age_payoff')
    tables={name:defaultdict(lambda:[0,0]) for name in names}
    for e in events:
        if e['session']==held:continue
        k=coarse_key(e);age=e['tenure_bin'];pay=e['payoff_bin']
        keys={'coarse':k,'tenure':k+(age,),'tenure_payoff':k+(age,pay)}
        if e['previous_A']==4:
            keys.update({'A4':k,'A4_age':k+(e['joint_age_bin'],),
                        'A4_age_payoff':k+(e['joint_age_bin'],age,pay)})
        for name,key in keys.items():
            item=tables[name][key];item[0]+=e['flip'];item[1]+=1
    return tables


def shrink_table(tables,name,key,p_parent,smoothing):
    y,n=tables[name].get(key,(0,0))
    return (y+smoothing*p_parent)/(n+smoothing)


def predict(e,tables):
    k=coarse_key(e)
    if k not in tables['coarse']:raise ValueError('out-of-fold source support absent')
    y,n=tables['coarse'][k]
    p0=(y+0.5)/(n+1)
    p1=shrink_table(tables,'tenure',k+(e['tenure_bin'],),p0,SHRINK_TENURE)
    p2=shrink_table(tables,'tenure_payoff',k+(e['tenure_bin'],e['payoff_bin']),p1,SHRINK_PAYOFF)
    if e['previous_A']!=4: return {'legal_coarse':p0,'legal_tenure':p1,'legal_payoff_tenure':p2}
    pA4=shrink_table(tables,'A4',k,p0,SHRINK_A4)
    p_age=shrink_table(tables,'A4_age',k+(e['joint_age_bin'],),pA4,SHRINK_AGE)
    p_age_pay=shrink_table(tables,'A4_age_payoff',
        k+(e['joint_age_bin'],e['tenure_bin'],e['payoff_bin']),p_age,SHRINK_AGE_PAYOFF)
    models={'legal_coarse':p0,'legal_tenure':p1,'legal_payoff_tenure':p2,
            'analyst_A4':pA4,'analyst_A4_age':p_age,'analyst_A4_age_payoff':p_age_pay}
    if any(not 0<p<1 for p in models.values()):raise AssertionError('invalid probability')
    return models


def group_scores(group,ps):
    if len(group)!=6 or len(ps)!=6 or group[0]['previous_A']!=4:
        raise ValueError('group scoring requires six old-A4 decisions')
    u=sum(e['up'] for e in group);d=sum(e['down'] for e in group)
    net=u-d;welfare=3*net*net
    e_net=sum(p*(1 if e['previous_route']==0 else -1) for e,p in zip(group,ps))
    e_net_sq=e_net*e_net+sum(p*(1-p) for p in ps)
    predicted_welfare=3*e_net_sq
    allstay=int(u+d==0)
    p_stay=1
    for p in ps:p_stay*=1-p
    loss=sum(-log(p) if e['flip'] else -log1p(-p) for e,p in zip(group,ps))/6
    return {'n':1,'observed_welfare':welfare,'pred_welfare':predicted_welfare,
            'residual_welfare':welfare-predicted_welfare,
            'welfare_sqerr':(welfare-predicted_welfare)**2,
            'observed_gross':u+d,'pred_gross':sum(ps),
            'observed_allstay':allstay,'pred_allstay':p_stay,
            'brier_allstay':(allstay-p_stay)**2,
            'actor_logloss':loss,'observed_up':u,'observed_down':d}


def public_mean(counts):
    if counts['n']<20:raise ValueError('public output cell must have >=20 group transitions')
    return {'n_old_A4_transitions':counts['n'],**{k+'_mean':counts[k]/counts['n'] for k in
        ('observed_welfare','pred_welfare','residual_welfare','welfare_sqerr',
         'observed_gross','pred_gross','observed_allstay','pred_allstay',
         'brier_allstay','actor_logloss','observed_up','observed_down')}}


def session_bootstrap(sess,draws=4000,seed=20261121):
    sessions=sorted(set(k[0] for k in sess))
    if len(sessions)!=24 or draws<1:raise ValueError('24 sessions required')
    rng=Random(seed)
    delta_metrics=['residual_welfare','welfare_sqerr','brier_allstay','actor_logloss']
    comparisons={'legal_payoff_tenure': 'legal_tenure',
                'analyst_A4_age':'analyst_A4',
                'analyst_A4_age_payoff':'analyst_A4_age',
                'analyst_A4_age_payoff_vs_legal_payoff':'legal_payoff_tenure'}
    out={}
    for trt in TREATMENT:
        for ep in EPOCH:
            tag=f'{TREATMENT[trt]}_{ep}'
            samples={f'{model}:{met}':[] for model in comparisons for met in delta_metrics}
            # same original groups in every comparator; paired whole-session draws
            def combined(selected,model):
                c=Counter()
                for sid in selected:c.update(sess.get((sid,trt,ep,model),{}))
                return c
            p={m:combined(sessions,m) for m in MODELS}
            if min(x['n'] for x in p.values())<20:continue
            pts={}
            for key,base in comparisons.items():
                model=key.replace('_vs_legal_payoff','')
                pts[key]={met:p[model][met]/p[model]['n']-p[base][met]/p[base]['n'] for met in delta_metrics}
            accepted=0
            for _ in range(draws):
                selected=[sessions[rng.randrange(len(sessions))] for _ in sessions]
                sub={m:combined(selected,m) for m in MODELS}
                if min(c['n'] for c in sub.values())<20:continue
                accepted+=1
                for key,base in comparisons.items():
                    model=key.replace('_vs_legal_payoff','')
                    for met in delta_metrics:
                        samples[f'{key}:{met}'].append(sub[model][met]/sub[model]['n']-sub[base][met]/sub[base]['n'])
            if accepted<draws*.9:raise ValueError('too many invalid original-session resamples')
            out[tag]={'original_sessions':24,'paired_original_session_resamples':draws,
                      'accepted':accepted,'differences':{key:{met:{'delta':pts[key][met],
                 'descriptive_95':_percentile_interval(samples[f'{key}:{met}'])}
                 for met in delta_metrics} for key in comparisons}}
    return out


def _percentile_interval(arr):
    xs=sorted(arr);n=len(xs)
    if n<1:raise ValueError('no bootstrap draws')
    return [xs[int(.025*n)],xs[min(n-1,int(.975*n))]]


def run(source,*,draws=4000):
    groups=load_private(source)
    payoffs=read_private_payoff(source,groups)
    events,joint=create_events(groups,payoffs)
    sessions=sorted(set(sid for sid,_,_ in groups))
    pooled=defaultdict(Counter);ses=defaultdict(Counter)
    for held in sessions:
        fit=build_tables(events,held)
        for (sid,g,trt,t),ge in joint.items():
            if sid!=held or ge[0]['previous_A']!=4:continue
            probs=[predict(e,fit) for e in ge]
            for name in MODELS:
                scores=group_scores(ge,[p[name] for p in probs])
                ep=ge[0]['epoch']
                pooled[trt,ep,name].update(scores)
                ses[held,trt,ep,name].update(scores)
    final={TREATMENT[t]:{ep:{m:public_mean(pooled[t,ep,m]) for m in MODELS}
                          for ep in EPOCH} for t in TREATMENT}
    return {'scope':'RITHM R66-T3 EXPLORATORY; actual historical original-author 24 sessions reused; noncausal',
        'original_author_zip_sha256':APPROVED_SHA,
        'source_roster':{'original_sessions':24,'distinct_six_person_groups':48,
                         'conditions':list(TREATMENT.values()),'periods':40},
        'models':{
        'legal_coarse':'treatment, epoch, own info, own previous route; all occupancy states train-only; LOSO original session',
        'legal_tenure':'same + own route tenure (1/2/3-4/5+), shrink count 20',
        'legal_payoff_tenure':'same + OWN received payoff at previous decision t (<4,4-8,>=8); shrink count 25 to own-tenure; legal at t+1',
        'analyst_A4':'OLD A4 group occupancy, shrink count20 to legal coarse; cannot infer uninformed player cognition',
        'analyst_A4_age':'OLD A4 + six-person configuration age (1/2/3-4/5+), shrink count25 to analyst_A4; analyst-only',
        'analyst_A4_age_payoff':'OLD A4 + six-person configuration age + OWN tenure/payoff, shrink count30 to analyst_A4_age; analyst-only'},
        'analysis_population':'48 groups x 4 conditions x 20 old-state early/late scored transitions, subset old nA=4; train every model without held-out original session',
        'pooled':final,'paired_24_session_descriptive_bootstrap':session_bootstrap(ses,draws=draws),
        'limitations':['original cohort repeatedly examined across RITHM R7-R66; exploratory after selection',
            'old A4 and configuration age unavailable to originally uninformed players; analyst models NOT actor cognition',
            'Endogenous was always last and selected information by price/incentive; not randomized',
            'a model that predicts mean group welfare need not fit joint probability nor long-horizon generated welfare',
            'residual can be marginal miscalibration; its sign does not identify clock covariance',
            'public output contains no participant IDs, individual routes, group histories or individual payoffs'],
        'source_free_contract':True}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('approved_original_zip');p.add_argument('aggregate_json')
    p.add_argument('--draws',type=int,default=4000)
    args=p.parse_args()
    result=run(args.approved_original_zip,draws=args.draws)
    Path(args.aggregate_json).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'aggregate_only','original_sessions':24,
                      'n_old_A4':{trt:{ep:result['pooled'][trt][ep]['legal_coarse']['n_old_A4_transitions']
                      for ep in EPOCH} for trt in result['pooled']}}))
if __name__=='__main__':main()
