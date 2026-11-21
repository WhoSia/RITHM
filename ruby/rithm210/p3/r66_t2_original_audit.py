"""RITHM-2.10 R66-T2: R65 author-approved original-data aggregate-only transition covariance.

SOURCE PRIVACY: R65 SHA-approved private data stay in RAM. Only pooled, >=20-group
aggregation and 24 original-session paired uncertainty leave this process.

Three independence references, all trained on OTHER original sessions:
  M0 Legal own route, info mask, time epoch, treatment; all source occupancies.
  M1 Same plus individual own-route tenure; shrinkage 20; all occupancies.
  M2 Analyst-only old-A4 conditional information-status/route/epoch model; NOT
     a permissible cognitive variable for originally uninformed agents.

Independence is a modeling assumption, not the observed absence of correlation.
Residual joint error may be due to missing personal state, type heterogeneity,
source selection, observed-common feedback and/or truly common updates; NOT
an identification of the latter. Endogenous always last, self-selection and
nonrandom information fees; no information-policy causal claim.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from math import log, log1p
from pathlib import Path
from random import Random
import argparse
import json
from r65_endogenous_stability import load_private, APPROVED_SHA, TREATMENT

EPOCH = ('early','late')


def period_epoch(t):
    if 1 <= t <= 10: return 'early'
    if 30 <= t <= 39: return 'late'
    return None


def age_bin(age):
    if age < 1: raise ValueError('invalid route streak')
    return 1 if age==1 else 2 if age==2 else 3 if age<=4 else 4


def legal_events(groups):
    """No future state used in features. Keep participant keys entirely in memory."""
    events=[]
    bygroup=defaultdict(list)
    for (sid, group, trt), history in groups.items():
        roster=sorted(history[1]); tenure={actor:1 for actor in roster}
        for t in range(1,40):
            ep=period_epoch(t)
            if ep:
                old=sum(history[t][actor][0] for actor in roster)
                new=sum(history[t+1][actor][0] for actor in roster)
                for actor in roster:
                    previous_route, info=history[t][actor]
                    next_route=history[t+1][actor][0]
                    ev={'session':sid,'group':group,'treatment':trt,'epoch':ep,
                        'period':t,'previous_A':old,'next_A':new,
                        'previous_route':previous_route,'info':info,
                        'tenure_bin':age_bin(tenure[actor]),
                        'flip':int(previous_route!=next_route),
                        'up':int(previous_route==0 and next_route==1),
                        'down':int(previous_route==1 and next_route==0)}
                    events.append(ev)
                    bygroup[(sid,group,trt,t)].append(ev)
            for actor in roster:
                if history[t][actor][0]==history[t+1][actor][0]:tenure[actor]+=1
                else:tenure[actor]=1
    if len(events)!=48*4*20*6 or len(bygroup)!=48*4*20:
        raise ValueError('unexpected original data cohort/epoch design')
    for ge in bygroup.values():
        if len(ge)!=6 or len({e['session'] for e in ge})!=1 or len({e['treatment'] for e in ge})!=1:
            raise ValueError('group integrity')
        u=sum(e['up'] for e in ge);d=sum(e['down'] for e in ge)
        if ge[0]['previous_A']+u-d!=ge[0]['next_A']:
            raise ValueError('occupancy conservation')
    return events,dict(bygroup)


def coarse_key(e):
    return (e['treatment'],e['epoch'],e['info'],e['previous_route'])


def fit_by_session(events,held):
    base=defaultdict(lambda:[0,0]); fine=defaultdict(lambda:[0,0]);
    oracle=defaultdict(lambda:[0,0]);
    for e in events:
        if e['session']==held:continue
        k=coarse_key(e)
        base[k][0]+=e['flip'];base[k][1]+=1
        kt=k+(e['tenure_bin'],)
        fine[kt][0]+=e['flip'];fine[kt][1]+=1
        if e['previous_A']==4:
            oracle[k][0]+=e['flip'];oracle[k][1]+=1
    return base,fine,oracle


def prediction(e,m,kind):
    base,fine,oracle=m
    key=coarse_key(e)
    if key not in base:raise ValueError('missing mask support outside held-out session')
    y,n=base[key]
    p0=(y+0.5)/(n+1)
    if kind=='legal_coarse':p=p0
    elif kind=='legal_tenure':
        y2,n2=fine.get(key+(e['tenure_bin'],),(0,0))
        p=(y2+20*p0)/(n2+20)
    elif kind=='analyst_A4':
        if e['previous_A']!=4:raise ValueError('oracle only A4')
        y2,n2=oracle.get(key,(0,0))
        p=(y2+20*p0)/(n2+20)
    else:raise ValueError('unknown model')
    if not 0<p<1:raise AssertionError('probability out of bounds')
    return p


def signed_second_from_independence(e,ps):
    """n' = n + U-D; Bernoulli independence given legal histories."""
    if len(e)!=6 or len(ps)!=6:raise ValueError('invalid group length')
    delta=sum(p if row['previous_route']==0 else -p for row,p in zip(e,ps))
    variance=sum(p*(1-p) for p in ps)
    return delta,delta*delta+variance


def event_stats(ge,ps):
    if len(ge)!=6 or len(ps)!=6 or ge[0]['previous_A']!=4:
        raise ValueError('requires exact old A4 group')
    u=sum(e['up'] for e in ge); d=sum(e['down'] for e in ge)
    gross=u+d;net=u-d
    predicted_net,predicted_net_sq=signed_second_from_independence(ge,ps)
    p_allstay=1.
    for p in ps:p_allstay*=1-p
    return {'gross_obs':gross,'gross_pred':sum(ps),
            'net_obs':net,'net_pred':predicted_net,
            'net_sq_obs':net*net,'net_sq_pred':predicted_net_sq,
            'welfare_obs':3*net*net,'welfare_pred':3*predicted_net_sq,
            'all_stay_obs':int(gross==0),'all_stay_pred':p_allstay,
            'nochange_occupancy_obs':int(net==0),
            'cancel_obs':int(u==d and u>0),
            'up_obs':u,'down_obs':d,'up_sq_obs':u*u,'down_sq_obs':d*d,'up_down_obs':u*d,
            'zero_switch_brier':(p_allstay-int(gross==0))**2,
            'actor_logloss':sum(-log(p) if e['flip'] else -log1p(-p) for e,p in zip(ge,ps))/6}



def pooled_summary(c):
    n=c['n']
    if n<20:raise ValueError('do not emit small cohort')
    d={'n_old_A4_transitions':n}
    for key in ('gross','net','net_sq','welfare','all_stay'):
        for suffix in ('obs','pred'):
            d[f'{key}_{suffix}_mean']=c[f'{key}_{suffix}']/n
    for key in ('nochange_occupancy_obs','cancel_obs','up_obs','down_obs','up_sq_obs','down_sq_obs','up_down_obs','zero_switch_brier','actor_logloss'):
        d[key+'_mean']=c[key]/n
    d['observed_up_variance']=d['up_sq_obs_mean']-d['up_obs_mean']**2
    d['observed_down_variance']=d['down_sq_obs_mean']-d['down_obs_mean']**2
    d['observed_up_down_covariance']=d['up_down_obs_mean']-d['up_obs_mean']*d['down_obs_mean']
    d['observed_net_variance']=d['net_sq_obs_mean']-d['net_obs_mean']**2
    if abs(d['observed_net_variance']-(d['observed_up_variance']+d['observed_down_variance']-2*d['observed_up_down_covariance']))>1e-9:
        raise AssertionError('directional variance decomposition')
    d['independent_predicted_net_variance']=d['net_sq_pred_mean']-d['net_pred_mean']**2
    d['signed_covariance_plus_miscalibration_welfare_residual']=d['welfare_obs_mean']-d['welfare_pred_mean']
    d['signed_covariance_plus_miscalibration_second_moment_residual']=d['net_sq_obs_mean']-d['net_sq_pred_mean']
    return d


def paired_bootstrap(sess,models,*,draws=3000,seed=20261121):
    sessions=sorted({key[0] for key in sess})
    if len(sessions)!=24:raise ValueError('session-cluster bootstrap must cover 24 distinct originals')
    rng=Random(seed)
    result={}
    for treatment in TREATMENT:
        for epoch in EPOCH:
            key=f'{TREATMENT[treatment]}_{epoch}'
            point={kind:Counter() for kind in models}
            for s in sessions:
                for kind in models:point[kind].update(sess.get((s,treatment,epoch,kind),{}))
            if any(point[kind]['n']<20 for kind in models):continue
            points={kind:pooled_summary(point[kind])['signed_covariance_plus_miscalibration_welfare_residual'] for kind in models}
            arr={kind:[] for kind in models}
            valid=0
            for _ in range(draws):
                sample=[sessions[rng.randrange(len(sessions))] for _ in sessions]
                cc={kind:Counter() for kind in models}
                for sid in sample:
                    for kind in models:cc[kind].update(sess.get((sid,treatment,epoch,kind),{}))
                if any(cc[kind]['n']<20 for kind in models):continue
                valid+=1
                for kind in models:arr[kind].append(3*(cc[kind]['net_sq_obs']-cc[kind]['net_sq_pred'])/cc[kind]['n'])
            result[key]={'cluster_unit':'original session, not group transition',
                'original_sessions':24,'resamples_requested':draws,'valid':valid,
                'model_residuals':{kind:{'point':points[kind],
                 'descriptive_bootstrap_95':[sorted(arr[kind])[int(.025*valid)],sorted(arr[kind])[min(valid-1,int(.975*valid))]]}
                 for kind in models}}
    return result


def run(source,*,draws=3000):
    groups=load_private(source)
    events,bygroup=legal_events(groups)
    models=('legal_coarse','legal_tenure','analyst_A4')
    accum=defaultdict(Counter)
    ses=defaultdict(Counter)
    sessions=sorted({sid for sid,_,_ in groups})
    for held in sessions:
        trained=fit_by_session(events,held)
        for key,ge in bygroup.items():
            if key[0]!=held or ge[0]['previous_A']!=4:continue
            trt=ge[0]['treatment'];epoch=ge[0]['epoch']
            for model in models:
                ps=[prediction(e,trained,model) for e in ge]
                metrics=event_stats(ge,ps)
                record=Counter(metrics);record['n']=1
                accum[trt,epoch,model].update(record)
                ses[held,trt,epoch,model].update(record)
    pooled={TREATMENT[trt]:{epoch:{model:pooled_summary(accum[trt,epoch,model]) for model in models}
                            for epoch in EPOCH} for trt in TREATMENT}
    aggregate={'scope':'EXPLORATORY ORIGINAL HUMAN DATA; all 4 treatments; 24 original sessions reused; post-treatment A4 risk set; not causal',
     'approved_sha256':APPROVED_SHA,'original_sessions':24,'unique_repeated_six_person_groups':48,
     'treatment_sequences':'Endogenous always last, nonrandom voluntary information selection',
     'transition_horizon':'period t in 1..10 vs 30..39 -> t+1; old nA=4 only',
     'models':{
         'legal_coarse':'LOSO session; train other 23 source sessions all nA, treatment/epoch/own info/own prior route',
         'legal_tenure':'same + own route-tenure bin 1/2/3-4/5+, shrink 20 to coarse; no analyst occupancy',
         'analyst_A4':'LOSO old-A4 source outcomes with shrink20 to legal_coarse; old occupancy not actor-legal for uninformed'},
     'estimand':'observed - Bernoulli-independent predicted 3 E[(U-D)^2] in old-A4; combines signed covariance plus marginal-model mismatch',
     'pooled':pooled,'descriptive_24_session_bootstrap':paired_bootstrap(ses,models,draws=draws),
     'failure_mode':'difference is NOT equal to identified common-clock covariance unless fitted individual marginals calibrated at the full relevant group-state/history level; cannot infer cognitive coordination',
     'no_original_rows_exported':True}
    return aggregate


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('approved_original_zip');parser.add_argument('public_aggregate_json')
    parser.add_argument('--draws',type=int,default=3000)
    args=parser.parse_args()
    result=run(args.approved_original_zip,draws=args.draws)
    Path(args.public_aggregate_json).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'aggregate_only':True,'sha256':result['approved_sha256'],'n_old4_by_treatment_epoch':{
        trt:{epoch:result['pooled'][trt][epoch]['legal_coarse']['n_old_A4_transitions'] for epoch in EPOCH}
        for trt in result['pooled']}}))

if __name__=='__main__':main()
