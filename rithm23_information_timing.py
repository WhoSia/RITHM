"""RITHM-2.3 minimal reproducible timing-aware human route-choice court.

Usage: python rithm23_information_timing.py public_source_derived_compact.csv
Source DOI: 10.1371/journal.pone.0184191.s002 (Wijayaratna et al. 2017).
Exploratory six-session-held-out prediction, NOT a causal welfare estimate.
"""
import csv
import sys
from collections import defaultdict
import numpy as np


def read_stages(path):
    stages = {}
    with open(path, newline='', encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            x = int(row['choices_base3_hex'], 16)
            seq = []
            for _ in range(240):
                x, digit = divmod(x, 3)
                seq.append(digit + 1)
            assert x == 0
            bits = int(row['incident_20_bits_hex'], 16)
            incidents = np.array([(bits >> (19 - t)) & 1 for t in range(20)])
            assert incidents.sum() == 4
            key = (row['session'], int(row['group']), int(row['stage']))
            stages[key] = (np.array(seq[::-1]).reshape(20, 12), incidents, int(row['info']))
    assert len(stages) == 24
    return stages


def fit_other_sessions(rows, excluded, timed):
    F = defaultdict(lambda: np.zeros(2))
    D = defaultdict(lambda: np.zeros(2))
    F0 = defaultdict(lambda: np.zeros(2))
    D0 = defaultdict(lambda: np.zeros(2))
    DB = defaultdict(lambda: np.zeros(2))
    for sid, info, prev, incident, choice in rows:
        if sid == excluded:
            continue
        first = int(choice != 1)
        F0[info][first] += 1
        F[info, prev][first] += 1
        if first:
            second = int(choice == 2)
            D0[info][second] += 1
            DB[info, prev][second] += 1
            D[info, prev, incident if (timed and info) else -1][second] += 1
    def forecast(info, prev, incident):
        a = F0[info]
        p0 = (a[1] + 1) / (a.sum() + 2)
        b = F[info, prev]
        p_ac = (b[1] + 9 * p0) / (b.sum() + 9)
        c = D0[info]
        r0 = (c[1] + 1) / (c.sum() + 2)
        db = DB[info, prev]
        r_prev = (db[1] + 9 * r0) / (db.sum() + 9)
        if timed and info:
            d = D[info, prev, incident]
            r = (d[1] + 9 * r_prev) / (d.sum() + 9)
        else:
            r = r_prev
        return np.array([1 - p_ac, p_ac * r, p_ac * (1 - r)])
    return forecast


def count_mass(q, n1, n2):
    dp = np.zeros((13, 13))
    dp[0, 0] = 1
    for person in q:
        out = dp * person[2]
        out[1:, :] += dp[:-1, :] * person[0]
        out[:, 1:] += dp[:, :-1] * person[1]
        dp = out
    assert abs(dp.sum() - 1) < 1e-10
    return max(float(dp[n1, n2]), 1e-15)


def evaluate(stages, timed):
    rows = []
    for key, (choices, accidents, info) in stages.items():
        for t in range(1, 20):
            for subject in range(12):
                rows.append((key[0], info, int(choices[t-1, subject]),
                             int(accidents[t]), int(choices[t, subject])))
    metrics = {0: {'person': [], 'group': [], 'cross': []},
               1: {'person': [], 'group': [], 'cross': []}}
    for sid in sorted({key[0] for key in stages}):
        forecast = fit_other_sessions(rows, sid, timed)
        aggregate = {}
        for key, (choices, accidents, info) in stages.items():
            if key[0] != sid:
                continue
            residual = []
            for t in range(1, 20):
                q = np.array([forecast(info, int(choices[t-1, i]), int(accidents[t]))
                              for i in range(12)])
                target = choices[t] - 1
                metrics[info]['person'].extend(-np.log(q[np.arange(12), target]))
                counts = np.bincount(choices[t], minlength=4)[1:]
                metrics[info]['group'].append(-np.log(count_mass(q, int(counts[0]), int(counts[1]))))
                residual.append((np.eye(3)[target] - q).sum(axis=0))
            aggregate[key] = np.array(residual)
        for stage in (2, 3):
            one = aggregate[(sid, 1, stage)]
            two = aggregate[(sid, 2, stage)]
            one -= one.mean(axis=0)
            two -= two.mean(axis=0)
            info = stages[(sid, 1, stage)][2]
            metrics[info]['cross'].append(float(np.mean(np.sum(one * two, axis=1))))
    return {str(info): {'individual_logloss': float(np.mean(v['person'])),
                        'group_count_logscore': float(np.mean(v['group'])),
                        'matched_cross_residual_dot': float(np.mean(v['cross'])),
                        'six_session_cross': v['cross']}
            for info, v in metrics.items()}


if __name__ == '__main__':
    source = read_stages(sys.argv[1])
    for variant in (False, True):
        print(('incident_after_fork' if variant else 'incident_excluded'),
              evaluate(source, timed=variant))
