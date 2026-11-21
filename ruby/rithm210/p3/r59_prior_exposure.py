"""R59 original section carryover & latent-person score, aggregate-only.

The original ZIP is owner-authorized and never exported. Person identifiers are
used privately ONLY for linking section histories, not written to the result.
The permutation within sessions is descriptive, NOT a causal identification.
"""
from collections import defaultdict
from hashlib import sha256
from io import StringIO
from pathlib import Path
from random import Random
from statistics import mean
from zipfile import ZipFile
import csv

from r54_original_batch_clock import (audit_zip, APPROVED_ZIP_SHA256,
                                      SOURCE_NAME, EXCLUDED_SESSIONS)


def parse_source_section_histories(source):
    # Exact SHA gate is run *before* unpacking the source or its participant IDs.
    audit_zip(source,require_original=True)
    people=defaultdict(dict)
    with ZipFile(source) as archive:
        rows=csv.DictReader(StringIO(archive.read(SOURCE_NAME).decode('utf-8-sig')))
        for row in rows:
            session,section,trt,t=(int(row[k]) for k in
                                  ('session','section','trt','Period'))
            if session in EXCLUDED_SESSIONS or trt not in (1,2,3) or t<1:
                continue
            if section not in (2,3,4):raise ValueError('out-of-cohort section')
            key=(session,section,int(row['ID']))
            if t in people[key]:raise ValueError('duplicate person-period')
            people[key][t]=(int(row['RouteA']),int(row['Informed']),trt,int(row['Group']))
    for history in people.values():
        if sorted(history)!=list(range(1,41)):
            raise ValueError('incomplete person history')
        if len({v[1] for v in history.values()})!=1:
            raise ValueError('info mask varies inside source segment')
        if len({v[3] for v in history.values()})!=1:
            raise ValueError('person changes group within source section')
    return people


def _cov(x,y):
    if not x or len(x)!=len(y):raise ValueError('invalid moment arrays')
    xm=mean(x);ym=mean(y)
    num=sum((a-xm)*(b-ym) for a,b in zip(x,y))
    den=(sum((a-xm)**2 for a in x)*sum((b-ym)**2 for b in y))**.5
    if den==0:raise ValueError('zero variance in section rates')
    return num/den


def section_pairs(people):
    sessions=sorted({s for s,sec,pid in people})
    if len(sessions)!=24:raise ValueError('expected 24 sessions')
    pairs=[]
    for s in sessions:
        for first,second in ((2,3),(3,4)):
            before={actor:hist for (ss,sec,actor),hist in people.items()
                    if ss==s and sec==first}
            after={actor:hist for (ss,sec,actor),hist in people.items()
                   if ss==s and sec==second}
            if set(before)!=set(after) or len(before) not in (6,12,18):
                raise ValueError('source participant roster not preserved at section boundary')
            for actor in sorted(before):
                x=before[actor];y=after[actor]
                if x[40][3]!=y[1][3]:
                    raise ValueError('group reassignment across source sections')
                pairs.append({
                    'session':s,'group':x[40][3],'boundary':(first,second),
                    'prior_rate':sum(x[t][0]!=x[t-1][0] for t in range(2,41))/39,
                    'later_rate':sum(y[t][0]!=y[t-1][0] for t in range(2,41))/39,
                    'prior_terminal':x[40][0], 'later_initial':y[1][0],
                    'prior_last_flip':int(x[40][0]!=x[39][0]),
                    'later_first_flip':int(y[2][0]!=y[1][0]),
                    'info_changed':int(x[40][1]!=y[1][1]),
                    'treatment_changed':int(x[40][2]!=y[1][2])})
    if len(pairs)!=576:raise AssertionError('source 576 cross-section actor links')
    return pairs


def summarize_section_pairs(pairs,*,permutations=2000,seed=20261121):
    if not isinstance(permutations,int) or permutations<1:
        raise ValueError('positive permutation count')
    if not pairs:raise ValueError('no pairs')
    cross_rate=mean(int(z['prior_terminal']!=z['later_initial']) for z in pairs)
    prior_last=mean(z['prior_last_flip'] for z in pairs)
    later_first=mean(z['later_first_flip'] for z in pairs)
    correlation=_cov([z['prior_rate'] for z in pairs],
                     [z['later_rate'] for z in pairs])
    # Preserve each session's two section transitions and their rate marginals,
    # and randomize the *identity match* within a session-boundary pair.
    boundary=defaultdict(list)
    stable_group=defaultdict(list)
    for p in pairs:
        boundary[(p['session'],p['boundary'])].append(p)
        stable_group[(p['session'],p['boundary'],p['group'])].append(p)
    if len(boundary)!=48 or len(stable_group)!=96:
        raise AssertionError('unexpected treatment/section/group count')
    rng=Random(seed)
    def permuted(groups):
        null=[]
        for _ in range(permutations):
            x=[];y=[]
            for group in groups.values():
                old=[z['prior_rate'] for z in group]
                new=[z['later_rate'] for z in group]
                rng.shuffle(new)
                x.extend(old);y.extend(new)
            null.append(_cov(x,y))
        return sorted(null)
    null=permuted(boundary)
    strict_null=permuted(stable_group)
    # Whole-session paired bootstrap: 24 clusters, never 576 independent actors.
    bysession=defaultdict(list)
    for p in pairs:bysession[p['session']].append(p)
    session_keys=sorted(bysession)
    boot=[]
    for _ in range(permutations):
        sample=[r for _ in session_keys for r in bysession[session_keys[rng.randrange(len(session_keys))]]]
        boot.append(_cov([z['prior_rate'] for z in sample],
                         [z['later_rate'] for z in sample]))
    boot.sort()
    return {
        'sessions':len({z['session'] for z in pairs}),
        'adjacent_section_pairs':len(boundary),
        'linked_actor_section_transitions':len(pairs),
        'source_selection':'trt 1..3, sections 2..4, Period 1..40, session not 2 or 101',
        'cross_section_route_change_fraction':cross_rate,
        'within_previous_section_last_period_flip_fraction':prior_last,
        'within_next_section_first_period_flip_fraction':later_first,
        'observed_adjacent_section_actor_rate_pearson':correlation,
        'identity_permutation_null_95_descriptive':[
            null[int(.025*permutations)],null[int(.975*permutations)]],
        'identity_permutation_null_mean':mean(null),
        'identity_permutation_stable_group_95_descriptive':[
            strict_null[int(.025*permutations)],strict_null[int(.975*permutations)]],
        'identity_permutation_stable_group_null_mean':mean(strict_null),
        'stable_group_identity_permutation_one_sided_p_upper':
            (1+sum(r>=correlation for r in strict_null))/(permutations+1),
        'whole_session_resampling_95_descriptive':[
            boot[int(.025*permutations)],boot[int(.975*permutations)]],
        'informed_mask_changed_fraction':mean(z['info_changed'] for z in pairs),
        'treatment_changed_fraction':mean(z['treatment_changed'] for z in pairs),
        'scope':'Whole cohort source-derived descriptive person links; no private person/session identifiers in output. No causal persistence claim.',
        'source_sha256':APPROVED_ZIP_SHA256,
    }


def audit_section_carryover(source,*,permutations=2000,seed=20261121):
    return summarize_section_pairs(section_pairs(parse_source_section_histories(source)),
                                   permutations=permutations,seed=seed)


if __name__=='__main__':
    import json,sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r59_prior_exposure.py APPROVED_SOURCE.zip')
    print(json.dumps(audit_section_carryover(sys.argv[1]),indent=2,sort_keys=True))
