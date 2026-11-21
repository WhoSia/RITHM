"""RITHM-2.10 P3-R61: cross-section individual-memory discount, entirely predecision.

CAUTION: Retrospective predictive evidence only; human identity or learned memory
is not causally identified. Raw authorized participant data remain private.
The unit of splitting and resampling is the original 24-person session cohort.
"""
from collections import defaultdict
from math import exp, inf, log
from random import Random
from statistics import mean
from r60_cross_segment import events_from_histories, group_flow_law, poisson_binomial
from r59_prior_exposure import parse_source_section_histories
from r54_original_batch_clock import APPROVED_ZIP_SHA256

TAUS=(0, 2, 4, 8, 16, 32, 64, inf)
SHRINK=20


def prior_weight(exposure,tau):
    """Discount *effective previous-section sample size*, not present evidence."""
    if type(exposure) is not int or exposure<0:
        raise ValueError('exposure must be prior observed target transitions only')
    if tau not in TAUS:
        raise ValueError('unregistered prospective tau')
    if tau==0:return 0.
    if tau==inf:return 1.
    return exp(-exposure/tau)


def summarize_session_bases(events):
    """Aggregate by original sessions; no actor rows leave in-memory training."""
    totals=defaultdict(lambda:defaultdict(lambda:[0,0]))
    for e in events:
        x=totals[e['session']]
        for key in ((e['treatment'],e['info'],e['previous_route']),
                    (e['treatment'],e['info'])):
            x[key][0]+=e['flip'];x[key][1]+=1
    return dict(totals)


def base_without(totals,excluded):
    counts=defaultdict(lambda:[0,0]);excl=set(excluded)
    if not excl or any(k not in totals for k in excl):raise ValueError('explicit known holdout required')
    for session,by_key in totals.items():
        if session in excl:continue
        for key,(y,n) in by_key.items():counts[key][0]+=y;counts[key][1]+=n
    if not counts:raise ValueError('empty training population')
    return counts


def get_pbase(e,counts):
    key=(e['treatment'],e['info'],e['previous_route'])
    if key not in counts or counts[key][1]<5:key=(e['treatment'],e['info'])
    y,n=counts[key]
    return (y+.5)/(n+1)


def adaptive_probability(e,base,tau,shrink=SHRINK):
    if shrink<=0:raise ValueError('positive smoothing required')
    w=prior_weight(e['current_exposure'],tau)
    y=e['current_count']+w*e['own_count']+shrink*base
    n=e['current_exposure']+w*39+shrink
    p=y/n
    if not 0<p<1:raise AssertionError('invalid smoothed probability')
    return p


def inner_select(events_by_session, totals, outer, *, candidates=TAUS, scores='actor'):
    """Inner LO(S)O over 23 other independent sessions, never outer outcomes.

    Tau chosen by equal-inner-session actor logloss. Selection does not access
    any data/outcome of outer session. The full inner fold base excludes both
    the inner and outer original sessions.
    """
    if scores!='actor':raise ValueError('only preregistered actor-loss selector')
    sessions=sorted(events_by_session)
    if len(sessions)<4 or outer not in sessions:raise ValueError('bad independent sessions')
    if tuple(candidates)!=tuple(TAUS):raise ValueError('selection grid must be frozen')
    totals_by_tau={tau:0. for tau in TAUS}
    for inner in sessions:
        if inner==outer:continue
        base=base_without(totals,{outer,inner})
        samples=events_by_session[inner]
        avgs={tau:0. for tau in TAUS}
        for e in samples:
            pbase=get_pbase(e,base)
            for tau in TAUS:
                p=adaptive_probability(e,pbase,tau)
                avgs[tau]+=(-log(p) if e['flip'] else -log1p_safe(-p))
        for tau in TAUS:totals_by_tau[tau]+=avgs[tau]/len(samples)
    # deterministic tie by grid order
    selected=min(TAUS,key=lambda tau:totals_by_tau[tau])
    return selected,{str(tau):totals_by_tau[tau]/(len(sessions)-1) for tau in TAUS}


def log1p_safe(x):
    from math import log1p
    return log1p(x)


def get_predictions(events,*,show_nested=False):
    """Actor-level heldout probability only in runtime, never emit these rows."""
    bysession=defaultdict(list)
    for e in events:bysession[e['session']].append(e)
    if len(bysession)!=24:raise ValueError('must use 24 original sessions')
    totals=summarize_session_bases(events)
    predictions=[];selected={};inner_scores={}
    for outer in sorted(bysession):
        tau,inner=inner_select(bysession,totals,outer)
        selected[outer]=tau
        if show_nested:inner_scores[outer]=inner
        trained=base_without(totals,{outer})
        for e in bysession[outer]:
            base=get_pbase(e,trained)
            predictions.append((e,{
                'base':base,
                'current_only':adaptive_probability(e,base,0),
                'static_prior':adaptive_probability(e,base,inf),
                'nested_adaptive':adaptive_probability(e,base,tau),
                'fixed_tau_8':adaptive_probability(e,base,8),
                'fixed_tau_16':adaptive_probability(e,base,16),
            }))
    return predictions,selected,inner_scores


MODELS=('base','current_only','static_prior','nested_adaptive','fixed_tau_8','fixed_tau_16')


def score_predictions(predictions,*,periods=None):
    """Per-session group- and actor-level scores; no cross-session pseudo-replication."""
    grouped=defaultdict(list)
    for e,ps in predictions:
        if periods is not None and e['period'] not in periods:continue
        grouped[e['session'],e['section'],e['group'],e['period']].append((e,ps))
    session_loss=defaultdict(lambda:{n:[0.,0.,0.,0] for n in MODELS})
    for (s,sec,g,t),actors in grouped.items():
        if len(actors)!=6:raise ValueError('six participant exposure required')
        for name in MODELS:
            probs=[p[name] for e,p in actors]
            act=[e for e,p in actors]
            u=sum(e['flip'] for e in act if not e['previous_route'])
            d=sum(e['flip'] for e in act if e['previous_route'])
            law=group_flow_law(act,probs)
            S=session_loss[s][name]
            S[0]+=sum(-log(p) if e['flip'] else -log1p_safe(-p) for e,p in zip(act,probs))
            S[1]+=sum((p-e['flip'])**2 for e,p in zip(act,probs))
            S[2]+=-log(law[u,d])
            S[3]+=1
    if len(session_loss)!=24:raise ValueError('24 sessions required')
    summary={}
    for name in MODELS:
        summary[name]={
            'equal_session_actor_logloss':mean(L[name][0]/(6*L[name][3]) for L in session_loss.values()),
            'equal_session_actor_brier':mean(L[name][1]/(6*L[name][3]) for L in session_loss.values()),
            'equal_session_group_joint_logloss':mean(L[name][2]/L[name][3] for L in session_loss.values())}
    return summary,session_loss


def bootstrap_comparison(loss,*,alternative='nested_adaptive',reference='current_only',metric='actor',reps=4000,seed=20261121):
    if alternative not in MODELS or reference not in MODELS:raise ValueError('unknown model')
    k,i=(6,0) if metric=='actor' else (1,2)
    d=[(loss[s][alternative][i]-loss[s][reference][i])/(k*loss[s][reference][3]) for s in sorted(loss)]
    rng=Random(seed);draws=sorted(mean(d[rng.randrange(len(d))] for _ in d) for _ in range(reps))
    return {'delta_nats':mean(d),'session_resampling_95_descriptive':[draws[int(.025*reps)],draws[min(reps-1,int(.975*reps))]],'n_sessions':len(d)}


def run(source,*,reps=4000):
    people=parse_source_section_histories(source)
    events,groups=events_from_histories(people)
    predictions,selected,inners=get_predictions(events,show_nested=True)
    model,loss=score_predictions(predictions)
    stages={'early_period_2_6':range(2,7),'middle_period_7_20':range(7,21),'late_period_21_40':range(21,41)}
    stage_out={}
    for name,periods in stages.items():
        a,b=score_predictions(predictions,periods=periods)
        stage_out[name]={'models':a,'nested_minus_online_actor':bootstrap_comparison(b,reps=reps,seed=20261122),'nested_minus_static_actor':bootstrap_comparison(b,reference='static_prior',reps=reps,seed=20261123)}
    return {'version':'R61.0','source_zip_sha256':APPROVED_ZIP_SHA256,
            'estimation':'R60 cohort, strict target-period prefix; outer 24-session heldout, inner 23-session actor-loss crossvalidation among frozen tau grid',
            'session_count':24,'linked_actor_pairs':576,'actor_decisions':len(events),'group_transitions':len(groups),'decay_grid':list(map(str,TAUS)),
            'selection_count':{str(x):list(selected.values()).count(x) for x in TAUS},
            'nested_train_only_average_actor_losses_min_max':{'min':min(min(x.values()) for x in inners.values()),'max':max(min(x.values()) for x in inners.values())},
            'overall':model,
            'overall_nested_vs_online_actor':bootstrap_comparison(loss,reps=reps),
            'overall_nested_vs_static_actor':bootstrap_comparison(loss,reference='static_prior',reps=reps,seed=20261124),
            'overall_nested_vs_online_group':bootstrap_comparison(loss,metric='group',reps=reps,seed=20261125),
            'stages':stage_out,
            'privacy':'NO person, session, group, or exogenous Value rows or per-session fitted tau published',
            'causal_scope':'descriptive prediction, NOT proof of decaying memory, personal latent traits or real welfare interventions'}
