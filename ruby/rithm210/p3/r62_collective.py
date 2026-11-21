"""RITHM R62: marginal-preserving latent common pause, strict analyst/actor filtration.

A pause is an UNOBSERVED group-period state in a retrospective probabilistic model,
not evidence that people coordinated or observed hidden occupancy. Source private.
"""
from collections import defaultdict
from math import log, log1p
from statistics import mean
from random import Random

from r60_cross_segment import poisson_binomial
from r61_adaptive_prior import get_predictions, summarize_session_bases, base_without, get_pbase, adaptive_probability
from r61_closed_loop import collect_groups, rollout_one

FROZEN = ('independent','pause_uniform','pause_at_four','pause_late_four', 'common_positive')
GRID = (0., .05, .10, .15, .20, .25, .30, .35, .40, .50, .60)


def group_events(predictions):
    d=defaultdict(list)
    for e, p in predictions:
        d[e['session'], e['section'],e['group'],e['period']].append((e,p))
    for key, group in d.items():
        if len(group)!=6:raise ValueError('group must be six distinct actors')
        n=sum(e['previous_route'] for e,p in group)
        if not 0<=n<=6:raise ValueError('bad old state')
        yield key,n,group


def pause_distribution(ps,q):
    """Full labelled 64-mask probabilities, respecting actor switch marginals.

    With probability q all actors stay, otherwise each independently flips with
    conditional probability p_i/(1-q). Each actor's P(flip)=p_i EXACTLY.
    """
    if len(ps)!=6 or any(not 0<p<1 for p in ps):raise ValueError('six open individual marginals required')
    if not 0<=q<1-max(ps):raise ValueError('pause must preserve feasible marginals with positive active support')
    act=[p/(1-q) for p in ps]
    law={}
    for mask in range(64):
        mass=1.
        for i,p in enumerate(act):mass*=p if mask&(1<<i) else 1-p
        law[mask]=(1-q)*mass+(q if mask==0 else 0.)
    if abs(sum(law.values())-1)>1e-12:raise AssertionError('non-normalized full law')
    return law


def positive_shock_distribution(ps,lam):
    """Symmetric shared shock; exact preservation of every actor mean."""
    if len(ps)!=6 or any(not 0<p<1 for p in ps):raise ValueError('invalid ps')
    if not 0<=lam<1:raise ValueError('invalid shock')
    deltas=[lam*min(p,1-p) for p in ps]
    law={}
    for mask in range(64):
        mass=0.
        for sign in (-1,1):
            product=1.
            for i,p in enumerate(ps):
                x=p+sign*deltas[i]
                product*=x if mask&(1<<i) else 1-x
            mass+=.5*product
        law[mask]=mass
    return law


def joint_law(old_routes,ps,law):
    """Map 64 switch masks into gross directional (B->A U,A->B D)."""
    if len(old_routes)!=6 or len(ps)!=6:raise ValueError('expected labelled six')
    result=defaultdict(float)
    for mask,mass in law.items():
        u=d=0
        for i,r in enumerate(old_routes):
            if mask&(1<<i):
                if r:d+=1
                else:u+=1
        result[u,d]+=mass
    if abs(sum(result.values())-1)>1e-12:raise AssertionError('normalization')
    return dict(result)


def pause_parameter(q,model,previous_a,period,ps):
    if model=='independent':return 0.
    if model=='pause_uniform':return min(q,(1-max(ps))*.999999)
    if model=='pause_at_four':return min(q,(1-max(ps))*.999999) if previous_a==4 else 0.
    if model=='pause_late_four':return min(q,(1-max(ps))*.999999) if previous_a==4 and period>=21 else 0.
    raise ValueError('unknown pause model')


def directional_prob(e,ps,model,q):
    old=[x['previous_route'] for x,p in e]
    if model=='common_positive':law=positive_shock_distribution(ps,q)
    else:law=pause_distribution(ps,pause_parameter(q,model,sum(old),e[0][0]['period'],ps))
    return joint_law(old,ps,law)


def fast_group_proba(old,ps,u,d,model,q,period):
    """Exact marginalized (U,D) event likelihood, without 64 labelled masks."""
    if len(old)!=6 or len(ps)!=6:raise ValueError('six actors needed')
    if model=='common_positive':
        probs=[]
        for sign in (-1,1):
            pp=[p+sign*q*min(p,1-p) for p in ps]
            ups=poisson_binomial([p for r,p in zip(old,pp) if not r])
            downs=poisson_binomial([p for r,p in zip(old,pp) if r])
            probs.append((ups[u]*downs[d],ups[0]*downs[0]))
        return ((probs[0][0]+probs[1][0])/2,(probs[0][1]+probs[1][1])/2)
    qq=pause_parameter(q,model,sum(old),period,ps)
    pp=[p/(1-qq) for p in ps]
    ups=poisson_binomial([p for r,p in zip(old,pp) if not r])
    downs=poisson_binomial([p for r,p in zip(old,pp) if r])
    return ((1-qq)*ups[u]*downs[d]+(qq if u==d==0 else 0.),
            (1-qq)*ups[0]*downs[0]+qq)


def loss_one(observations,model,q,*,actor_model='current_only'):
    """One-step group joint logloss, no t outcome enters any forecast."""
    out=[]
    for key,a,grp in observations:
        ps=[p[actor_model] for e,p in grp]
        target=(sum(e['flip'] for e,p in grp if not e['previous_route']),
                sum(e['flip'] for e,p in grp if e['previous_route']))
        target_prob,p0=fast_group_proba([e['previous_route'] for e,p in grp],ps,*target,model,q,key[3])
        out.append((key[0],key[3],a,-log(target_prob),
                    p0,int(target==(0,0)),
                    sum(ps),sum(e['flip'] for e,p in grp)))
    return out


def train_select(observations,*,model,actor_model='current_only'):
    """Train q on nonheldout original sessions only, evaluating joint flow logloss.

    NOTE: trained actor p in the provided objects may have been built with
    different heldouts. For strict fold fitting, pass actor probabilities
    freshly trained after removing each outer session. See source_full_cv.
    """
    scores={q:sum(x[3] for x in loss_one(observations,model,q,actor_model=actor_model))/len(observations) for q in GRID}
    return min(GRID,key=lambda q:scores[q]),scores


def full_cv(events,*,actor_model='current_only',grid=GRID):
    """No held session in base or latent group-coupling fit.

    For every outer fold, rebuild the actor population priors from other 23
    sessions, while target actors retain only their own legal history.
    For nested_adaptive tau, use R61 pre-computed train-only hyperparameter.
    """
    if actor_model not in ('current_only','nested_adaptive'):
        raise ValueError('unsupported actor model')
    by_s=defaultdict(list)
    for e in events:by_s[e['session']].append(e)
    if len(by_s)!=24:raise ValueError('24 independent sessions required')
    bases=summarize_session_bases(events)
    selected=None
    if actor_model=='nested_adaptive':
        _,selected,_=get_predictions(events)
    results={m:defaultdict(list) for m in FROZEN}
    q_selected={m:[] for m in FROZEN if m!='independent'}
    for held in sorted(by_s):
        b=base_without(bases,{held})
        def obs(slist):
            grouped=defaultdict(list)
            for e in slist:
                pbase=get_pbase(e,b)
                from math import inf
                tau=0 if actor_model=='current_only' else selected[held]
                p=adaptive_probability(e,pbase,tau)
                grouped[e['session'],e['section'],e['group'],e['period']].append((e,{actor_model:p}))
            if any(len(rows)!=6 for rows in grouped.values()):raise ValueError('incomplete group')
            return [(key,sum(e['previous_route'] for e,p in rows),rows) for key,rows in sorted(grouped.items())]
        train=obs([e for s,rows in by_s.items() if s!=held for e in rows])
        test=obs(by_s[held])
        for m in FROZEN:
            if m=='independent':q=0.
            else:
                q,scores=train_select(train,model=m,actor_model=actor_model)
                q_selected[m].append(q)
            results[m][held]=loss_one(test,m,q,actor_model=actor_model)
    return results,q_selected


def aggregate(results,selection,*,bootstrap=2000,seed=20261121):
    scores={}
    for m,per_s in results.items():
        scores[m]={
            'equal_session_group_logloss':mean(mean(x[3] for x in rows) for rows in per_s.values()),
            'equal_session_no_switch_brier':mean(mean((x[4]-x[5])**2 for x in rows) for rows in per_s.values()),
            'observed_no_switch_frequency':mean(mean(x[5] for x in rows) for rows in per_s.values()),
            'predicted_no_switch_mean':mean(mean(x[4] for x in rows) for rows in per_s.values()),
            'predicted_mean_gross_switches':mean(mean(x[6] for x in rows) for rows in per_s.values()),
            'actual_mean_gross_switches':mean(mean(x[7] for x in rows) for rows in per_s.values()),
            'at_four_no_switch_observed':sum(x[5] for rows in per_s.values() for x in rows if x[2]==4)/sum(x[2]==4 for rows in per_s.values() for x in rows),
            'at_four_no_switch_predicted':sum(x[4] for rows in per_s.values() for x in rows if x[2]==4)/sum(x[2]==4 for rows in per_s.values() for x in rows),
            'at_four_no_switch_brier':mean(mean((x[4]-x[5])**2 for x in rows if x[2]==4) for rows in per_s.values()),
        }
    rng=Random(seed)
    sids=sorted(results['independent'])
    for m in results:
        if m=='independent':continue
        diffs=[mean(x[3] for x in results[m][s])-mean(x[3] for x in results['independent'][s]) for s in sids]
        drawn=sorted(mean(diffs[rng.randrange(len(diffs))] for _ in sids) for _ in range(bootstrap))
        scores[m]['delta_logloss_from_independent']=mean(diffs)
        scores[m]['descriptive_cluster_95']=[drawn[int(.025*bootstrap)],drawn[min(bootstrap-1,int(.975*bootstrap))]]
        scores[m]['train_only_q_counts']={str(q):selection[m].count(q) for q in GRID if selection[m].count(q)}
    return {'scores':scores,'cohort':{'sessions':len(sids),'group_transitions':sum(len(x) for x in results['independent'].values()),'individual_decisions':6*sum(len(x) for x in results['independent'].values())},'description':'Analyst joint prior-occupancy condition, not participant private information; source-free synthetic tests separated from original ZIP.'}
