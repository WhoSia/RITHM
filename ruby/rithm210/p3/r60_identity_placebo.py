"""R60 same-six-person matched-source permutation of former-section propensities.

Keep each next-section outcome and every actor's publicly/privately observable
prior route, current info, treatment, and within-section choice prefix fixed.
Only reassign the *previous section* exposure within pre-specified strata.
No original actor identifiers are exported to public aggregates.
"""
from collections import defaultdict
from math import log
from random import Random
from statistics import mean
from r60_cross_segment import fit_training_base,pbase


def build_cost_matrices(events,*,strength=20):
    if not isinstance(strength,int) or strength<=0:raise ValueError('positive shrink required')
    bysession=defaultdict(list)
    for e in events:bysession[e['session']].append(e)
    out=[]
    for s in sorted(bysession):
        fitted=fit_training_base(events,s)
        groups=defaultdict(lambda:defaultdict(list))
        for e in bysession[s]:
            groups[(e['section'],e['group'])][e['actor']].append(e)
        for key,per_actor in groups.items():
            actors=sorted(per_actor)
            if len(actors)!=6:raise ValueError('wrong group size')
            prior=[per_actor[i][0]['own_count'] for i in actors]
            attrs=[(per_actor[i][0]['info'],
                    per_actor[i][0]['info']^per_actor[i][0]['info_changed'],
                    per_actor[i][0]['prior_terminal_route'],
                    per_actor[i][0]['target_initial_route']) for i in actors]
            matrix=[]
            for actor in actors:
                history=per_actor[actor]
                if sorted(e['period'] for e in history)!=list(range(2,41)):
                    raise ValueError('incomplete actor target period')
                row=[]
                for flips in prior:
                    cost=0.
                    for e in history:
                        p=(flips+strength*pbase(e,fitted))/(39+strength)
                        cost+= -log(p) if e['flip'] else -log(1-p)
                    row.append(cost)
                matrix.append(row)
            out.append({'session':s,'attrs':attrs,'matrix':matrix})
    if len(out)!=96:raise ValueError('expected 96 target group-sections')
    return out


def blocks(attrs,mode):
    by=defaultdict(list)
    for i,(newinfo,oldinfo,oldroute,newroute) in enumerate(attrs):
        if mode=='group':key=()
        elif mode=='same_information':key=(oldinfo,newinfo)
        elif mode=='same_information_and_boundary_route':key=(oldinfo,newinfo,oldroute,newroute)
        else:raise ValueError('invalid control scope')
        by[key].append(i)
    return list(by.values())


def permutation_check(matrices,*,reps=2000,seed=20261121):
    if not isinstance(reps,int) or reps<1:raise ValueError('invalid replicas')
    actual=sum(sum(x['matrix'][i][i] for i in range(6)) for x in matrices)/(len(matrices)*6*39)
    outputs={}
    for mode in ('group','same_information','same_information_and_boundary_route'):
        rng=Random(seed+len(mode))
        eligible=0;eligible_groups=0;expsum=0.
        for x in matrices:
            bs=blocks(x['attrs'],mode)
            if any(len(b)>1 for b in bs):eligible_groups+=1
            eligible+=sum(len(b) for b in bs if len(b)>1)
            for b in bs:
                for i in b:
                    expsum+=sum(x['matrix'][i][j] for j in b)/len(b)
        null=[]
        for _ in range(reps):
            c=0.
            for x in matrices:
                for group in blocks(x['attrs'],mode):
                    shuffled=group[:]
                    rng.shuffle(shuffled)
                    c+=sum(x['matrix'][i][j] for i,j in zip(group,shuffled))
            null.append(c/(len(matrices)*6*39))
        null.sort()
        outputs[mode]={
            'actor_decisions':len(matrices)*6*39,
            'permutable_actor_section_records':eligible,
            'groups_with_nontrivial_shuffle':eligible_groups,
            'observed_actor_logloss':actual,
            'permutation_null_exact_mean':expsum/(len(matrices)*6*39),
            'permutation_null_95_descriptive':[null[int(.025*reps)],null[min(reps-1,int(.975*reps))]],
            'one_sided_permutation_p_upper':(1+sum(v<=actual for v in null))/(reps+1),
            'interpretation':'Observed label specificity under THIS exchangeability null; no causal personality/memory inference.',
        }
    return outputs


if __name__=='__main__':
    import json,sys
    from r59_prior_exposure import parse_source_section_histories
    from r60_cross_segment import events_from_histories
    if len(sys.argv)!=2:raise SystemExit('usage: python r60_identity_placebo.py AUTHORIZED_PRIVATE_ZIP')
    people=parse_source_section_histories(sys.argv[1]);events,_=events_from_histories(people)
    print(json.dumps(permutation_check(build_cost_matrices(events)),sort_keys=True,indent=2))
