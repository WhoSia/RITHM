"""RITHM R31: source-honest Part-I order and pre-Partial experience rivals.

Uses only source SHA-checked experimenter CSV for provenance, not for releasing
participant rows. Lagged public occupancy is allowed only for informed actors.
Previous-treatment history is constructed strictly from sections completed
BEFORE the Partial segment, never from future treatment assignments/outcomes.
Exploratory source re-use; no causal order or psychology interpretation.
"""
from __future__ import annotations
import csv, json, hashlib, sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.special import expit
from r29_partial_information_cv import load as load_partial, fit, SOURCE_SHA
from r30_partial_dynamic_joint import design as r30_design, joint_scores, TAUS

FAMILIES=('r30_late','prior_arm_order','prior_arm_experience')
METRICS=('actor_logloss','six_mask_joint_logloss','count_logloss','cost_mae',
         'mean_predicted_cost','count_variance','independent_variance',
         'covariance_contribution','actor_brier')


def prior_contexts(path):
    path=Path(path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError('original source SHA mismatch')
    parts=defaultdict(dict)
    partial_group_order=defaultdict(list)
    with path.open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            sid=int(r['session']); trt=int(r['trt']); t=int(r['Period'])
            if sid in (2,101) or trt not in (1,2,3) or not 1<=t<=40:
                continue
            g=int(r['Group']); section=int(r['section']); aid=int(r['ID'])
            key=(sid,g,trt,section,aid)
            if key not in parts:parts[key]={}
            if t in parts[key]:raise ValueError('duplicate actor-period')
            parts[key][t]=(int(r['RouteA']),float(r['profit']),int(r['Informed']))
            if trt==2 and t==1 and g not in partial_group_order[sid]:
                partial_group_order[sid].append(g)
    out={}
    for sid,group_order in partial_group_order.items():
        for group_index,g in enumerate(group_order):
            current={key:vals for key,vals in parts.items() if key[0]==sid and key[1]==g and key[2]==2}
            if len(current)!=6:raise ValueError('wrong Partial actor size')
            orders={key[3] for key in current}
            if len(orders)!=1:raise ValueError('mixed section within Partial group')
            section=orders.pop()
            if section not in (2,3,4):raise ValueError('invalid Partial section')
            actors=sorted(key[4] for key in current)
            if len(actors)!=6:raise ValueError('invalid actor set')
            for aid in actors:
                current_records=next(values for key,values in current.items() if key[4]==aid)
                if set(current_records)!=set(range(1,41)):
                    raise ValueError('incomplete current section')
                previous=[]
                seen=set()
                for (ss,gg,trt,sec,actor),records in parts.items():
                    if (ss,gg,actor)!=(sid,g,aid) or trt not in (1,3):continue
                    if not 2<=sec<=4:raise ValueError('invalid previous section')
                    if sec>=section:continue  # NO FUTURE SECTION DATA
                    if trt in seen:raise ValueError('duplicate previous treatment')
                    seen.add(trt)
                    if set(records)!=set(range(1,41)):raise ValueError('incomplete prior section')
                    previous.append((sec,trt,records))
                previous.sort(key=lambda entry:entry[0])
                if len(previous)!=section-2:raise ValueError('prior treatment count mismatch')
                observed_prior_no=float(any(trt==1 for _,trt,_ in previous))
                observed_prior_full=float(any(trt==3 for _,trt,_ in previous))
                previous_payoffs=[records[t][1] for _,_,records in previous for t in range(1,41)]
                previous_switch=[float(records[t][0]!=records[t-1][0])
                                 for _,_,records in previous for t in range(2,41)]
                summary=(observed_prior_no,observed_prior_full,
                         float(np.mean(previous_payoffs))/10 if previous_payoffs else 0.,
                         float(np.mean(previous_switch)) if previous_switch else 0.)
                out[sid,group_index,aid]=summary
            # ensure exact actor set is preserved across all observed sections
            for (ss,gg,trt,sec,actor),records in parts.items():
                if (ss,gg)==(sid,g) and trt in (1,2,3) and actor not in actors:
                    raise ValueError('actor group membership changed')
    if len(partial_group_order)!=24 or len(out)!=288:
        raise ValueError('unexpected Part-I cohort size')
    return out,partial_group_order


def design(row,period,family,context):
    if family not in FAMILIES:raise ValueError('unknown model')
    core=r30_design(row,period,'payoff_public_late')
    if family=='r30_late':return core
    prior_no,prior_full,prior_payoff,prior_switch=context
    info=row[3]
    if not all(np.isfinite(x) for x in context):raise ValueError('non-finite prior history')
    if prior_no not in (0,1) or prior_full not in (0,1):raise ValueError('bad order flag')
    core.extend((prior_no,prior_full,info*prior_no,info*prior_full))
    if family=='prior_arm_experience':
        core.extend((prior_payoff,prior_switch,info*prior_payoff,info*prior_switch))
    return core


def extract_group_context(partial_group,session,group_index,contexts,ids):
    if len(ids)!=6 or len(partial_group)!=6:raise ValueError('six actor matching required')
    return [contexts[session,group_index,aid] for aid in ids]


def predict_session(groups,contexts,session,group_ids,coef,family):
    predictions=[]
    for group_index in range(len(group_ids)):
        context=extract_group_context(groups[group_index*39],session,group_index,contexts,group_ids[group_index])
        for j in range(39):
            t=j+2
            g=groups[group_index*39+j]
            X=np.asarray([design(r,t,family,context[i]) for i,r in enumerate(g)])
            p=expit(X@coef)
            predictions.append((p,[r[0] for r in g],[r[4] for r in g]))
    if len(predictions)!=len(groups):raise ValueError('group order mismatch')
    return predictions


def session_metrics(predictions,tau):
    """Vectorized exact 6-person mixture scores; no Monte Carlo."""
    from scipy.special import xlogy
    q=np.asarray([row[0] for row in predictions],float)
    prior=np.asarray([row[1] for row in predictions],float)
    y=np.asarray([row[2] for row in predictions],int)
    delta=tau*(2*prior-1)*np.minimum(q,1-q)
    plus=q+delta;minus=q-delta
    def count_law(prob):
        law=np.ones((len(prob),1))
        for j in range(6):
            law=np.pad(law*(1-prob[:,j:j+1]),((0,0),(0,1)))+np.pad(law*prob[:,j:j+1],((0,0),(1,0)))
        return law
    dist=(count_law(plus)+count_law(minus))/2
    joint=(np.prod(np.where(y==1,plus,1-plus),axis=1)+np.prod(np.where(y==1,minus,1-minus),axis=1))/2
    counts=y.sum(axis=1)
    cost=np.asarray([24+3*(n-4)**2 for n in range(7)])
    mean=q.sum(axis=1)
    variance=dist@np.arange(7)**2-mean**2
    within=(q*(1-q)).sum(axis=1)
    err=-xlogy(y,q)-xlogy(1-y,1-q)
    predict_cost=dist@cost
    return np.mean(np.column_stack((err.mean(axis=1),-np.log(np.maximum(joint,1e-300)),
       -np.log(np.maximum(dist[np.arange(len(y)),counts],1e-300)),
       np.abs(predict_cost-cost[counts]),predict_cost,variance,within,variance-within,
       ((q-y)**2).mean(axis=1))),axis=0)


def run(path):
    partial=load_partial(path)
    contexts,group_order=prior_contexts(path)
    session_ids=sorted(partial)
    folds={s:i%6 for i,s in enumerate(session_ids)}
    # Determine observed actor IDs in each Partial group from original source, never from future outcomes.
    group_actor_ids={}
    with Path(path).open(newline='',encoding='utf-8-sig') as stream:
        first=defaultdict(set)
        for r in csv.DictReader(stream):
            s=int(r['session']);trt=int(r['trt']);period=int(r['Period'])
            if s in (2,101) or trt!=2 or period!=1:continue
            first[s,int(r['Group'])].add(int(r['ID']))
        for sid in session_ids:
            group_actor_ids[sid]=[sorted(first[sid,g]) for g in group_order[sid]]
            if len(group_actor_ids[sid])*39!=len(partial[sid]):
                raise ValueError('R29 group ordering inconsistent')
            # Validate actor position via previous-period route and public occupancy in source.
    output={};heldout={};selected_tau={}
    for family in FAMILIES:
        per_session={};selections=[]
        for fold in range(6):
            train=[s for s in session_ids if folds[s]!=fold]
            hold=[s for s in session_ids if folds[s]==fold]
            X=[];y=[]
            for sid in train:
                for group_index,actor_ids in enumerate(group_actor_ids[sid]):
                    ctx=[contexts[sid,group_index,aid] for aid in actor_ids]
                    for j in range(39):
                        g=partial[sid][group_index*39+j];t=j+2
                        for i,row in enumerate(g):
                            X.append(design(row,t,family,ctx[i]));y.append(row[4])
            coef=fit(X,y,ridge=.02)
            train_predictions={sid:predict_session(partial[sid],contexts,sid,group_actor_ids[sid],coef,family) for sid in train}
            train_joint={tau:float(np.mean([session_metrics(train_predictions[s],tau)[1] for s in train])) for tau in TAUS}
            tau=min(TAUS,key=lambda z:(train_joint[z],z))
            selections.append({'fold':fold,'tau':tau,'train_joint_scores':train_joint})
            for sid in hold:
                p=predict_session(partial[sid],contexts,sid,group_actor_ids[sid],coef,family)
                per_session[sid]={"independent":session_metrics(p,0.),"joint":session_metrics(p,tau)}
        if set(per_session)!=set(session_ids):raise ValueError('heldout sessions incomplete')
        heldout[family]=per_session
        output[family]={which:np.mean([per_session[s][which] for s in session_ids],axis=0).tolist() for which in ('independent','joint')}
        selected_tau[family]=selections
    contrasts={}
    for candidate in ('prior_arm_order','prior_arm_experience'):
        for which in ('independent','joint'):
            d=np.asarray([heldout[candidate][sid][which]-heldout['r30_late'][sid][which] for sid in session_ids])
            rng=np.random.default_rng(20261110)
            sample=d[rng.integers(0,24,size=(2000,24))].mean(axis=1)
            contrasts[candidate+'_'+which]={'delta':d.mean(axis=0).tolist(),
                'exploratory_session_bootstrap95':np.quantile(sample,[.025,.975],axis=0).T.tolist()}
    return {'source_sha256':SOURCE_SHA,'source_cohort':'24 main-paper sessions, Partial, 48 groups; 16 groups at each part1 section order',
      'source_unit':'1872 six-person periods t=2..40 (11232 actor choices)',
      'model_families':FAMILIES,'metrics':METRICS,'results':output,'selected_tau_training_only':selected_tau,
      'paired_relative_to_r30_late':contrasts,
      'authority':'NO future segments in prior contexts. Order indicators and older observed payoff/switches from already-completed Part-I sessions only. Partial public count restricted to informed actors. Exploratory observational model, not causal effect.'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python r31_order_history.py SEALED_PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
