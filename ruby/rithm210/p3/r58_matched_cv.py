"""R58 one-step matched folds: author Appendix A/B algorithms versus R57.

Original private rows are read transiently and never leave this process.
Published outputs aggregate 24 sessions, not persons, groups or session IDs.
"""
from collections import defaultdict, Counter
from math import log
from random import Random
from statistics import mean

from r58_author_rivals import (actor_rows_sealed, ewa_path_differences,
        ssm_probabilities,ssm_posterior_predictive,logistic_probs_from_diffs,score_laws,
        macro_cost_moments,flow_law_from_actor_flip,flip_probs_from_a)
from r57_history_cv import (load_history_events, fitted_laws,train_histories,
        actor_probabilities,flow_from_probabilities,tenure_bin,profit_bin)
from r56_joint_flow_cv import loss
from r54_original_batch_clock import APPROVED_ZIP_SHA256


def fitted_ewa_lambda(learn_differences,observed_route,*,max_lambda=3.0):
    """Convex heldout-exclusive grid-free 1D MLE on 0..3 in each treatment.
    Lambda is refit in *23 training sessions only*, never on the heldout 24th.
    Bound is a documented researcher choice, not the original author's MLE.
    """
    import numpy as np
    x=np.asarray(learn_differences,dtype=float)
    y=np.asarray(observed_route,dtype=float)
    if x.ndim!=1 or x.size==0 or x.size!=y.size or not np.isfinite(x).all():
        raise ValueError('bad EWA likelihood inputs')
    sign=2*y-1
    p=sign*x
    def objective(lam):
        return float(np.mean(np.logaddexp(0,-lam*p)))
    a,b=0.0,float(max_lambda)
    z=(5**0.5-1)/2
    c=b-z*(b-a);d=a+z*(b-a)
    fc=objective(c);fd=objective(d)
    for _ in range(62):
        if fc<fd:
            b,d,fd=d,c,fc
            c=b-z*(b-a);fc=objective(c)
        else:
            a,c,fc=c,d,fd
            d=a+z*(b-a);fd=objective(d)
    mid=(a+b)/2
    return min((0.0,mid,max_lambda),key=objective)


def legal_training(events):
    """Use only own lagged route, tenure, received profit and information mask.

    This is a participant-information-conservative behavioral comparator, unlike
    the researcher-oracle R57 baseline which also conditions on group occupancy.
    All counts are learned from OTHER sessions.
    """
    base=defaultdict(Counter);refined=defaultdict(Counter)
    for e in events:
        for actor,switched in zip(e['actors'],e['flips']):
            route,streak,profit,info=actor
            bkey=(e['trt'],route,info)
            rkey=bkey+(tenure_bin(streak),profit_bin(profit))
            base[bkey]['n']+=1;base[bkey]['y']+=switched
            refined[rkey]['n']+=1;refined[rkey]['y']+=switched
    return base,refined


def legal_predict(e,trained,*,refined=False,pseudoexposure=20):
    base,full=trained;probs=[]
    for route,streak,profit,info in e['actors']:
        key=(e['trt'],route,info)
        count=base[key]
        prior=(count['y']+0.5)/(count['n']+1)
        if refined:
            detailed=key+(tenure_bin(streak),profit_bin(profit))
            nested=full.get(detailed,Counter())
            p=(nested['y']+pseudoexposure*prior)/(nested['n']+pseudoexposure)
        else:p=prior
        probs.append(p)
    return tuple(probs)


def _source_precomputed(original,*,lapse):
    groups=actor_rows_sealed(original)
    extras=[]
    for record in groups:
        periods=record['periods']
        diffs=ewa_path_differences(periods)
        ssm_raw=ssm_probabilities(periods)
        ssm=ssm_posterior_predictive(ssm_raw,periods,epsilon=lapse)
        extras.append({**record,'ewa':diffs,'ssm':ssm,'ssm_raw':ssm_raw})
    return extras


def welfare_mse_at_k(coefficients,kappa):
    """MSE forecast of realized excess congestion + kappa*person changes.

    This is a predictive mean-square score, NOT realized causal welfare.
    The price kappa is external and cannot be identified from movements alone.
    """
    if not kappa>=0:
        raise ValueError('resource switch price must be nonnegative')
    return (coefficients['excess_congestion_mse'] +
            2*kappa*coefficients['gross_excess_cross_error'] +
            kappa*kappa*coefficients['gross_mse'])


def globally_better_mse(first,second,*,strict=True):
    """Check if polynomial forecast MSE(first) < MSE(second) for all κ>=0.

    For a quadratic d0+d1*k+d2*k², exact nonnegative-axis minimum
    occurs at κ=0 or κ=max(0,-d1/(2*d2)).  Numeric caveats for
    nearly equal coefficients require precision/a separate tolerance audit.
    """
    keys=('excess_congestion_mse','gross_excess_cross_error','gross_mse')
    differences=[second[k]-first[k] for k in keys]
    d0,d1,d2=differences[0],2*differences[1],differences[2]
    if d2<0 or (d2==0 and d1<0):return False
    minimum=d0
    if d2>0 and d1<0:
        minimum=d0-d1*d1/(4*d2)
    return bool(minimum>0 if strict else minimum>=0)


def aggregate(original,*,lapse=0.02,bootstrap=1000,seed=20261121,
              ewa_lambda_max=3.0):
    if not 0<lapse<1:raise ValueError('positive fixed lapse for log scoring')
    if not isinstance(bootstrap,int) or bootstrap<1:raise ValueError('invalid bootstrap')
    tracks=_source_precomputed(original,lapse=lapse)
    bysession=defaultdict(list)
    for x in tracks: bysession[x['session']].append(x)
    events=load_history_events(original)
    bysession_r57=defaultdict(list)
    for x in events:bysession_r57[x['session']].append(x)
    sessions=sorted(bysession)
    if sessions!=sorted(bysession_r57) or len(sessions)!=24:
        raise AssertionError('lost source session alignment')
    # precompute each participant's EWA attraction differences on precisely
    # the 39 evaluation periods; only R57 baseline and lambda are trained.
    ewa_fit={}; q_fit={}
    for held in sessions:
        training=[x for s in sessions if s!=held for x in bysession[s]]
        lams={}
        for trt in (1,2,3):
            f=[];y=[]
            for x in training:
                if x['treatment']!=trt:continue
                for t in range(1,40):
                    f.extend(x['ewa'][t]);y.extend(x['periods'][t][i][0] for i in range(6))
            lams[trt]=fitted_ewa_lambda(f,y,max_lambda=ewa_lambda_max)
        ewa_fit[held]=lams
        qs={}
        for trt in (1,2,3):
            sample=[x for x in training if x['treatment']==trt]
            criterion=[0.0]*9
            n=0
            for x in sample:
                for t in range(1,40):
                    for i,actor in enumerate(x['periods'][t]):
                        for j,p in enumerate(x['ssm_raw'][t][i]):
                            pred=lapse/2+(1-lapse)*p
                            criterion[j]-=log(pred if actor[0] else (1-pred))
                        n+=1
            qs[trt]=min(range(1,10),key=lambda q:(criterion[q-1]/n,q))
        q_fit[held]=qs
    models=('state_independent','tenure_profit','legal_route_only','legal_private_history',
            'ewa_lite','ssm5','ssm1_9','ssmq_cv')
    per_session=[]
    for held in sessions:
        others=[e for s in sessions if s!=held for e in bysession_r57[s]]
        base=fitted_laws(others)
        extra=train_histories(others)
        legal=legal_training(others)
        ses=defaultdict(list)
        ses_actors=defaultdict(list)
        macro=defaultdict(list)
        zero_n={'ssm5':0,'ssmq_cv':0}
        stage=defaultdict(lambda:defaultdict(list))
        trt_groups=defaultdict(lambda:defaultdict(list))
        for e in bysession_r57[held]:
            for name in ('state_independent','tenure_profit','legal_route_only','legal_private_history'):
                if name.startswith('legal_'):
                    p=legal_predict(e,legal,refined=(name=='legal_private_history'))
                else:
                    p=actor_probabilities(e,name,base,extra,shrink=20)
                f=flow_from_probabilities(e,p)
                value=loss(f,e['ud'])[0]
                ses[name].append(value)
                trt_groups[e['trt']][name].append(value)
                ses_actors[name].append(sum(-log(q) if y else -log(1-q)
                    for q,y in zip(p,e['flips']))/6)
                moments=macro_cost_moments(e['a'],f)
                up,down=e['ud']
                true_gross=up+down;true_excess=3*(e['a']+up-down-4)**2
                macro[name].append((moments['gross_changes']-true_gross,
                                    moments['end_period_excess_congestion']-true_excess))
                stage['early' if e['period']<=20 else 'late'][name].append(value)
        for rec in bysession[held]:
            trt=rec['treatment']
            lam=ewa_fit[held][trt]
            periods=rec['periods']
            for t in range(1,40):
                fr=periods[t-1]; nxt=periods[t]
                ewa=logistic_probs_from_diffs(rec['ewa'][t],lam)
                selected_q=q_fit[held][trt]
                q_pred=tuple(lapse/2+(1-lapse)*rec['ssm_raw'][t][i][selected_q-1]
                             for i in range(6))
                for i,actor in enumerate(nxt):
                    for model,raw in (('ssm5',rec['ssm_raw'][t][i][4]),
                                      ('ssmq_cv',rec['ssm_raw'][t][i][selected_q-1])):
                        if (raw==0 and actor[0]) or (raw==1 and not actor[0]):
                            zero_n[model]+=1
                for model,p in (('ewa_lite',ewa),('ssm5',rec['ssm'][t]['ssm5']),
                                ('ssm1_9',rec['ssm'][t]['ssm1_9']),('ssmq_cv',q_pred)):
                    score,actor,brier=score_laws(fr,nxt,p)
                    if not (score<1e100 and actor<1e100):
                        raise ArithmeticError('nonfinite heldout forecast score')
                    ses[model].append(score)
                    ses_actors[model].append(actor)
                    trt_groups[trt][model].append(score)
                    up=sum(a[0]==0 and b[0]==1 for a,b in zip(fr,nxt))
                    down=sum(a[0]==1 and b[0]==0 for a,b in zip(fr,nxt))
                    moments=macro_cost_moments(sum(a[0] for a in fr),
                        flow_law_from_actor_flip(fr,flip_probs_from_a(p,fr)))
                    macro[model].append((moments['gross_changes']-(up+down),
                                         moments['end_period_excess_congestion']-3*(sum(a[0] for a in nxt)-4)**2))
                    stage['early' if t<20 else 'late'][model].append(score)
        if len(ses['state_independent'])!=len(ses['ewa_lite']):
            raise AssertionError('baseline/author sample not matched')
        per_session.append({
            'models':{m:mean(ses[m]) for m in models},
            'actors':{m:mean(ses_actors[m]) for m in models},
            'treatment':{str(t):{m:mean(trt_groups[t][m]) for m in models}
                         for t in (1,2,3)},
            'lambda':ewa_fit[held], 'chosen_ssm_q':q_fit[held],
            'macro':{model:{'gross_mse':mean(x[0]**2 for x in macro[model]),
                 'gross_bias':mean(x[0] for x in macro[model]),
                 'gross_excess_cross_error':mean(x[0]*x[1] for x in macro[model]),
                 'excess_congestion_mse':mean(x[1]**2 for x in macro[model]),
                 'excess_congestion_bias':mean(x[1] for x in macro[model])}
                 for model in models},
            'raw_ssm_zero_actor_observations':zero_n,
            'by_phase':{phase:{model:mean(stage[phase][model]) for model in models}
                        for phase in ('early','late')},
            'n':len(ses['state_independent'])})
    summaries={m:{'mean_heldout_group_logloss':mean(x['models'][m] for x in per_session),
                  'mean_heldout_actor_logloss':mean(x['actors'][m] for x in per_session)}
               for m in models}
    resampling={};rng=Random(seed)
    for baseline in ('state_independent','legal_route_only','legal_private_history'):
        resampling[baseline]={}
        for alt in models:
            if alt==baseline: continue
            contrasts=[x['models'][alt]-x['models'][baseline] for x in per_session]
            draws=sorted(mean(contrasts[rng.randrange(24)] for _ in range(24))
                         for _ in range(bootstrap))
            resampling[baseline][alt]={
                'mean_logloss_difference':mean(contrasts),
                'session_bootstrap_95_descriptive':[draws[int(0.025*bootstrap)],
                    draws[min(bootstrap-1,int(0.975*bootstrap))]],
                'sessions_better':sum(c<0 for c in contrasts)}
    welfare_robustness={}
    for alt in ('ewa_lite','ssm5','ssm1_9','ssmq_cv'):
        legal='legal_private_history'
        welfare_robustness[alt]={
            'legal_private_history_lower_mse_all_kappa_nonnegative':globally_better_mse(
                 {'gross_mse':mean(x['macro'][legal]['gross_mse'] for x in per_session),
                  'excess_congestion_mse':mean(x['macro'][legal]['excess_congestion_mse'] for x in per_session),
                  'gross_excess_cross_error':mean(x['macro'][legal]['gross_excess_cross_error'] for x in per_session)},
                 {'gross_mse':mean(x['macro'][alt]['gross_mse'] for x in per_session),
                  'excess_congestion_mse':mean(x['macro'][alt]['excess_congestion_mse'] for x in per_session),
                  'gross_excess_cross_error':mean(x['macro'][alt]['gross_excess_cross_error'] for x in per_session)})}
        for kappa in (0,1,5):
            per_fold=[welfare_mse_at_k(x['macro'][alt],kappa)-welfare_mse_at_k(x['macro'][legal],kappa)
                      for x in per_session]
            rand=Random(seed+137+kappa)
            draws=sorted(mean(per_fold[rand.randrange(24)] for _ in range(24))
                         for _ in range(bootstrap))
            welfare_robustness[alt][f'kappa_{kappa}_mse_gap']={
                 'mean':mean(per_fold),
                 'session_bootstrap_95_descriptive':[draws[int(.025*bootstrap)],
                     draws[min(bootstrap-1,int(.975*bootstrap))]]}
    return {'source_sha256':APPROVED_ZIP_SHA256,
            'sessions':len(sessions),'period_transitions':len(events),
            'individual_one_step_predictions':len(events)*6,
            'ssm_assumed_lapse':lapse,'fit_ewa_lambda_range':[0,ewa_lambda_max],
            'models':summaries,'vs_state_independent':resampling,
            'welfare_mse_robustness':welfare_robustness,
            'macro_moment_predictions':{model:{field:mean(x['macro'][model][field] for x in per_session)
                 for field in ('gross_mse','gross_bias','gross_excess_cross_error','excess_congestion_mse','excess_congestion_bias')}
                 for model in models},
            'raw_original_ssm_zero_actor_observations':{model:sum(x['raw_ssm_zero_actor_observations'][model] for x in per_session)
                for model in ('ssm5','ssmq_cv')},
            'by_treatment':{str(trt):{m:mean(x['treatment'][str(trt)][m] for x in per_session)
                for m in models} for trt in (1,2,3)},
            'welfare_score_polynomial':{model:{'intercept_excess_mse':mean(x['macro'][model]['excess_congestion_mse'] for x in per_session),
                 'linear_kappa':2*mean(x['macro'][model]['gross_excess_cross_error'] for x in per_session),
                 'quadratic_kappa':mean(x['macro'][model]['gross_mse'] for x in per_session)}
                 for model in models},
            'by_phase':{phase:{m:mean(x['by_phase'][phase][m] for x in per_session)
                for m in models} for phase in ('early','late')},
            'ssmq_training_selected':{str(trt):{str(q):sum(x['chosen_ssm_q'][trt]==q for x in per_session)
                                              for q in range(1,10) if any(x['chosen_ssm_q'][trt]==q for x in per_session)}
                                       for trt in (1,2,3)},
            'lambda_by_treatment':{str(trt):{'mean':mean(x['lambda'][trt] for x in per_session),
                'min':min(x['lambda'][trt] for x in per_session),
                'max':max(x['lambda'][trt] for x in per_session)} for trt in (1,2,3)},
            'scope':'Prospective source-history one-step fit; noncausal, SSM lapse is added, EWA lambda bound chosen, no mechanism identification.'}


if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('approved_source')
    p.add_argument('--lapse',type=float,default=0.02)
    p.add_argument('--bootstrap',type=int,default=1000)
    a=p.parse_args()
    print(json.dumps(aggregate(a.approved_source,lapse=a.lapse,bootstrap=a.bootstrap),indent=2,sort_keys=True))
