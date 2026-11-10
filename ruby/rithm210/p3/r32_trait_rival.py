"""RITHM R32 — pre-Partial stable route preference versus prior payoff/switching experience.

The source is private, SHA-checked by r31.prior_contexts and r29.load.
Historical exposures use only fully completed earlier sections; no later data.
No individual rows or personal covariates are exported. The same 24 session folds
and R31 late+order+experience baseline are retained. No causal inference.
"""
from __future__ import annotations
import csv, json, sys
from collections import defaultdict
import numpy as np
from scipy.special import expit
from r31_order_history import (prior_contexts,design as r31_design,
     session_metrics,TAUS,fit,load_partial,SOURCE_SHA)

FAMILIES=('experience','preference','both')

def previous_route_traits(path, group_order):
    # ALL recorded earlier segments are eligible; current Partial and future segments are prohibited.
    partial_sections={}
    rows=defaultdict(list)
    with open(path,newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            sid=int(r['session']);trt=int(r['trt']);section=int(r['section'])
            if sid in (2,101) or trt not in (1,2,3):continue
            key=(sid,int(r['Group']),int(r['ID']))
            if trt==2:
                if key in partial_sections and partial_sections[key]!=section:raise ValueError('multiple Partial sections')
                partial_sections[key]=section
            else:
                rows[key].append((section,int(r['Period']),int(r['RouteA'])))
    out={}
    for sid,groups in group_order.items():
        for gi,g in enumerate(groups):
            ids=sorted(k[2] for k in partial_sections if k[0]==sid and k[1]==g)
            if len(ids)!=6:raise ValueError('bad group actor identities')
            for aid in ids:
                section=partial_sections[sid,g,aid]
                previous=[(sec,t,y) for sec,t,y in rows[sid,g,aid] if sec<section]
                if len(previous)!=40*(section-2):raise ValueError('prior count mismatch')
                # Range [-1,1] for earlier route A share; missing is set to zero and
                # the order indicators distinguish structural absence from 50/50.
                share=(2*float(np.mean([y for _,_,y in previous]))-1) if previous else 0.
                out[sid,gi,aid]=(share,float(len(previous)/40))
    if len(out)!=288:raise ValueError('bad trait cardinality')
    return out

def design(row,t,family,context,trait):
    if family not in FAMILIES:raise ValueError('unknown family')
    core=r31_design(row,t,'prior_arm_experience',context)
    # order indicators retained for all competitors; experience columns only
    # used in 'experience'/'both', trait columns only in 'preference'/'both'.
    if family=='preference':core=core[:-4]
    if family in ('preference','both'):
        share,number=trait
        if not -1<=share<=1 or number not in (0.,1.,2.):raise ValueError('invalid pre-Partial trait')
        informed=row[3]
        core.extend([share,informed*share])
    return core

def run(path, permute_seed=None):
    groups=load_partial(path)
    contexts,group_order=prior_contexts(path)
    traits=previous_route_traits(path,group_order)
    sessions=sorted(groups)
    if len(sessions)!=24:raise ValueError('source population')
    folds={s:i%6 for i,s in enumerate(sessions)}
    ids={}
    with open(path,newline='',encoding='utf-8-sig') as f:
        by=defaultdict(set)
        for r in csv.DictReader(f):
            sid=int(r['session'])
            if sid in (2,101) or int(r['trt'])!=2 or int(r['Period'])!=1:continue
            by[sid,int(r['Group'])].add(int(r['ID']))
    for sid in sessions:
        ids[sid]=[sorted(by[sid,g]) for g in group_order[sid]]
        if len(ids[sid])*39!=len(groups[sid]):raise ValueError('group alignment')
    # Post-hoc negative control: remove individual linkage of historical preference
    # within each fixed Partial group and informed status. This never changes any
    # participant's current choice, date, fold, info assignment or group membership.
    if permute_seed is not None:
        rng=np.random.default_rng(permute_seed)
        for sid in sessions:
            for gi,actors in enumerate(ids[sid]):
                first=groups[sid][gi*39]
                for informed in (0,1):
                    subset=[aid for aid,row in zip(actors,first) if row[3]==informed]
                    if len(subset)!=3:raise ValueError('information stratum mismatch')
                    values=[traits[sid,gi,aid] for aid in subset]
                    shuffle=rng.permutation(len(values))
                    for aid,k in zip(subset,shuffle):traits[sid,gi,aid]=values[int(k)]
    def predictions(sid,coef,family):
        out=[]
        for gi,actors in enumerate(ids[sid]):
            Xcontexts=[contexts[sid,gi,aid] for aid in actors]
            Xtraits=[traits[sid,gi,aid] for aid in actors]
            for j in range(39):
                t=j+2
                rows=groups[sid][gi*39+j]
                X=np.asarray([design(r,t,family,Xcontexts[i],Xtraits[i]) for i,r in enumerate(rows)])
                p=expit(X@coef)
                out.append((p,[r[0] for r in rows],[r[4] for r in rows]))
        return out
    results={};held={};tau_choices={}
    for family in FAMILIES:
        fold_values={};choices=[]
        for fold in range(6):
            train=[s for s in sessions if folds[s]!=fold]
            test=[s for s in sessions if folds[s]==fold]
            X=[];Y=[]
            for sid in train:
                for gi,actors in enumerate(ids[sid]):
                    ctx=[contexts[sid,gi,a] for a in actors]
                    trait=[traits[sid,gi,a] for a in actors]
                    for j in range(39):
                        t=j+2
                        for i,r in enumerate(groups[sid][gi*39+j]):
                            X.append(design(r,t,family,ctx[i],trait[i]))
                            Y.append(r[4])
            coef=fit(X,Y,ridge=.02)
            train_prediction={s:predictions(s,coef,family) for s in train}
            train_loss={tau:float(np.mean([session_metrics(train_prediction[s],tau)[1] for s in train])) for tau in TAUS}
            chosen=min(TAUS,key=lambda x:(train_loss[x],x))
            choices.append(chosen)
            for sid in test:
                pp=predictions(sid,coef,family)
                fold_values[sid]={'independent':session_metrics(pp,0.),'joint':session_metrics(pp,chosen)}
        held[family]=fold_values
        results[family]={kind:np.mean([fold_values[s][kind] for s in sessions],axis=0).tolist() for kind in ('independent','joint')}
        tau_choices[family]=choices
    contrasts={}
    for family in ('preference','both'):
        for family0 in ('experience','preference'):
            if family==family0:continue
            for kind in ('independent','joint'):
                delta=np.asarray([held[family][s][kind]-held[family0][s][kind] for s in sessions])
                rng=np.random.default_rng(20261111)
                sampled=delta[rng.integers(0,24,(2000,24))].mean(axis=1)
                contrasts[f'{family}_minus_{family0}_{kind}']={
                    'delta':delta.mean(axis=0).tolist(),
                    'exploratory_95percent_interval':np.quantile(sampled,[.025,.975],axis=0).T.tolist()}
    return {'study':'R32 source-first prior route preference rival',
            'source_sha256':SOURCE_SHA,'sessions':24,'groups':48,'group_periods':1872,
            'prior_context':'No/Full fully finished before Partial only; route A share from pre-Partial sections; absent for Partial-first actors',
            'families':FAMILIES,'metrics':('actor_logloss','joint_logloss','count_logloss','cost_mae','expected_cost','variance','bernoulli_variance','covariance_contribution','actor_brier'),
            'results':results,'selected_tau':tau_choices,'contrasts':contrasts,
            'negative_control_seed':permute_seed,
            'limitation':'Same participants and experimental data; latent trait proxy uses earlier observed route preference, not a randomized stable trait; no cognitive hassle identification, no external confirmation.'}

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python r32_trait_rival.py PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
