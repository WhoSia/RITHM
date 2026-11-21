"""RITHM 2.10 P3-R65: authorized group-level Endogenous-regime stability.

Private original source never leaves the in-memory loader. Public output contains
only pooled treatment/epoch/event counts, 24-session paired descriptive bootstrap,
and Endogenous information-coverage groups. Reused within-subject dataset: NOT an
independent validation sample or a causal comparison.
"""
import argparse
import csv
from collections import Counter, defaultdict
from hashlib import sha256
from io import TextIOWrapper
import json
from pathlib import Path
from random import Random
from statistics import mean
from zipfile import ZipFile

APPROVED_SHA = 'e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953'
CSV = 'data_task_all_switch_230705.csv'
EXCLUDED_SESSIONS = {2, 101}
TREATMENT = {1: 'No', 2: 'Partial', 3: 'Full', 4: 'Endogenous'}
EPOCH = {'early': range(1, 11), 'late': range(30, 40)}
EVENTS = ('previous_A4', 'all_stay_A4', 'balanced_cancel_A4', 'exit_A4', 'gross_switches', 'transition_count')


def load_private(source):
    """Verify original SHA BEFORE unpacking; actor identifiers are transient keys."""
    source = Path(source)
    if sha256(source.read_bytes()).hexdigest() != APPROVED_SHA:
        raise ValueError('non-approved original ZIP; source SHA gate')
    records = defaultdict(dict)
    with ZipFile(source) as archive:
        with TextIOWrapper(archive.open(CSV), encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                session, treatment, period = (int(r[x]) for x in ('session', 'trt', 'Period'))
                if session in EXCLUDED_SESSIONS:
                    continue
                if treatment not in TREATMENT or not 1 <= period <= 40:
                    raise ValueError('unrecognized original condition or period')
                actor = int(r['ID'])
                key = session, int(r['Group']), treatment, period
                if actor in records[key]:
                    raise ValueError('duplicate source actor observation')
                records[key][actor] = (int(r['RouteA']), int(r['Informed']))
    if len(records) != 48 * 4 * 40 or any(len(g) != 6 for g in records.values()):
        raise ValueError('24-session original cohort / six-person grouping changed')
    groups = defaultdict(dict)
    for (session, group, treatment, period), members in records.items():
        groups[session, group, treatment][period] = members
    assert len(groups) == 48 * 4
    if any(set(h) != set(range(1, 41)) for h in groups.values()):
        raise ValueError('missing original period')
    sessions = {key[0] for key in groups}
    if len(sessions) != 24:
        raise ValueError('unexpected number of original session clusters')
    for (s, g, trt), history in groups.items():
        roster = set(history[1]); info = {i: history[1][i][1] for i in roster}
        for t in range(2, 41):
            if set(history[t]) != roster or {i: history[t][i][1] for i in roster} != info:
                raise ValueError('roster or information mask changed within condition')
        if trt == 1 and any(info.values()): raise ValueError('No information mask invalid')
        if trt == 2 and sum(info.values()) != 3: raise ValueError('Partial 3+3 invalid')
        if trt == 3 and sum(info.values()) != 6: raise ValueError('Full mask invalid')
    return dict(groups)


def transition_event(before, after):
    if len(before) != 6 or set(before) != set(after):
        raise ValueError('six matched simultaneous choices required')
    a = sum(v[0] for v in before.values())
    up = sum(before[k][0] == 0 and after[k][0] == 1 for k in before)
    down = sum(before[k][0] == 1 and after[k][0] == 0 for k in before)
    if not 0 <= a + up - down <= 6:
        raise AssertionError('occupancy conservation violated')
    return {'a_before':a,'a_after':a+up-down,'up':up,'down':down,
            'all_stay':int(up+down==0),'balanced_cancel':int(up==down and up>0)}


def epoch_counts(groups):
    counts = defaultdict(Counter)
    counts_session = defaultdict(Counter)
    coverage = Counter()
    endogenous_full_groups = set()
    for (sid, group, trt), hist in groups.items():
        info = sum(x[1] for x in hist[1].values())
        if trt == 4:
            coverage[info] += 1
            if info == 6:
                endogenous_full_groups.add((sid, group))
        for epoch, periods in EPOCH.items():
            for t in periods:
                result = transition_event(hist[t], hist[t+1])
                c = Counter({'transition_count':1, 'gross_switches': result['up']+result['down']})
                if result['a_before'] == 4:
                    c['previous_A4'] = 1
                    c['all_stay_A4'] = result['all_stay']
                    c['balanced_cancel_A4'] = result['balanced_cancel']
                    c['exit_A4'] = int(result['up'] != result['down'])
                counts[trt,epoch].update(c)
                counts_session[sid,trt,epoch].update(c)
    if sum(coverage.values()) != 48:
        raise ValueError('endogenous condition not complete')
    return counts, counts_session, coverage, endogenous_full_groups


def rate(c):
    if not c['previous_A4']: raise ValueError('undefined A4 denominator')
    return c['all_stay_A4'] / c['previous_A4']


def compare_epoch(counts):
    return {TREATMENT[trt]: {
        epoch: {'transitions': c['transition_count'], 'previous_A4':c['previous_A4'],
                'all_stay_A4':c['all_stay_A4'], 'balanced_cancel_A4':c['balanced_cancel_A4'],
                'exit_A4':c['exit_A4'], 'P_all_stay_given_A4':rate(c),
                'P_cancel_given_A4':c['balanced_cancel_A4']/c['previous_A4'],
                'P_exit_given_A4':c['exit_A4']/c['previous_A4'],
                'mean_gross_switches':c['gross_switches']/c['transition_count']}
        for epoch in EPOCH for c in [counts[trt,epoch]]}
        for trt in TREATMENT}


def bootstrap_paired(stats, *, draws=4000, seed=20261121):
    """Pair all 4 treatments inside 24 original source sessions; no pseudo-independence."""
    sessions = sorted({key[0] for key in stats})
    if len(sessions) != 24 or draws < 1: raise ValueError('expected original session bootstrap')
    rng = Random(seed)
    def contrast(selected):
        results = {}
        for trt in (1,2,3,4):
            scores = {}
            for epoch in EPOCH:
                subtotal = Counter()
                for sid in selected:
                    subtotal.update(stats[sid,trt,epoch])
                scores[epoch] = rate(subtotal)
            results[trt] = scores['late'] - scores['early']
        return results
    point = contrast(sessions)
    order = {'No': 1,'Partial':2,'Full':3,'Endogenous':4}
    samples = defaultdict(list)
    for _ in range(draws):
        selected = [sessions[rng.randrange(len(sessions))] for _ in sessions]
        val = contrast(selected)
        for trt, name in ((1,'No'),(2,'Partial'),(3,'Full'),(4,'Endogenous')):
            samples[name].append(val[trt])
        samples['Endogenous_minus_Full'].append(val[4]-val[3])
    def interval(v):
        v.sort()
        return [v[int(draws*.025)], v[min(draws-1,int(draws*.975))]]
    return {'method':'whole-original-session paired cluster bootstrap, descriptive only',
            'independent_sessions':24,'resamples':draws,
            'late_minus_early_by_treatment': {name:{'delta':point[k],
                            'descriptive_95':interval(samples[name])} for name,k in order.items()},
            'Endogenous_minus_Full_change': {'delta':point[4]-point[3],
                                            'descriptive_95':interval(samples['Endogenous_minus_Full'])}}


def run(source, *, draws=4000, seed=20261121):
    groups = load_private(source)
    totals, sessions, coverage, endogenous_full = epoch_counts(groups)
    output={'status':'EXPLORATORY_SOURCE_PRIVATE_NOT_CAUSAL',
            'original_zip_sha256':APPROVED_SHA,
            'cohort':{'original_sessions':24, 'repeated_six_person_groups':48,
                      'conditions': ['No','Partial','Full','Endogenous'],
                      'raw_data_rows_used':48*4*40*6, 'part2_order':'always last',
                      'endogenous_information_selection':'endogenous/fee-dependent; NOT randomized'},
            'epoch_moments':compare_epoch(totals),
            'endogenous_groups_by_informed_count':{str(k):coverage[k] for k in range(7)},
            'endogenous_all_six_informed_group_count':len(endogenous_full),
            'paired_session_descriptive':bootstrap_paired(sessions,draws=draws,seed=seed),
            'limits':['Same original subjects/groups across treatments; Endogenous always last',
                      'Part2 information choice determined by incentivized strategy method and price',
                      'Conditional previous A4 selection is post-treatment, not a causal estimand',
                      'Twenty-four original session clusters, not 48 independent randomized groups',
                      'Does not test author SSM model without a separately generated source-free simulation']}
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('approved_original_zip')
    p.add_argument('out_aggregate_json')
    p.add_argument('--draws',type=int,default=4000)
    args=p.parse_args()
    result=run(args.approved_original_zip,draws=args.draws)
    Path(args.out_aggregate_json).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'status':'aggregate_only','groups':result['cohort']['repeated_six_person_groups'],
                      'endogenous_group_count':sum(result['endogenous_groups_by_informed_count'].values())}))

if __name__=='__main__':main()
