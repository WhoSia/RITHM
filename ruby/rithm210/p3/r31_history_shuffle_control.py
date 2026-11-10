"""Post-hoc falsification: shuffle earlier-arm payoff and switching histories.

Permute only historical experience summaries within strata of CV fold,
Partial order and current informed status. No heldout-fold covariates enter
the training folds through reassignment. Keep source legality, actor exposure, group
formation, and current chosen outcomes fixed. This is exploratory and does
NOT constitute a randomization-inference p-value.
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch
import numpy as np
import r31_order_history as R31
from r29_partial_information_cv import load


def permuted_contexts(path,seed):
    contexts,groups=R31.prior_contexts(path)
    partial=load(path)
    strata=defaultdict(list)
    # Reidentify ID order using source CSV: R29 emits all six actors in ID order.
    import csv
    membership=defaultdict(set)
    with Path(path).open(newline='',encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            s=int(r['session']);trt=int(r['trt']);t=int(r['Period'])
            if trt==2 and t==1 and s not in (2,101):
                membership[s,int(r['Group'])].add(int(r['ID']))
    folds={sid:i%6 for i,sid in enumerate(sorted(groups))}
    for s,ordered_groups in groups.items():
        for groupidx,g in enumerate(ordered_groups):
            ids=sorted(membership[s,g])
            record=partial[s][39*groupidx]
            for i,aid in enumerate(ids):
                v=contexts[s,groupidx,aid]
                sec=2+int(v[0])+int(v[1])
                info=record[i][3]
                strata[folds[s],sec,info].append((s,groupidx,aid))
    rng=np.random.default_rng(seed)
    shuffled=dict(contexts)
    for keys in strata.values():
        perm=rng.permutation(len(keys))
        for index,key in enumerate(keys):
            donor=contexts[keys[perm[index]]]
            original=contexts[key]
            shuffled[key]=(original[0],original[1],donor[2],donor[3])
    return shuffled,groups


def run(path,seeds=(20261111,20261112,20261113)):
    results=[]
    for seed in seeds:
        contexts,order=permuted_contexts(path,seed)
        with patch.object(R31,'prior_contexts',lambda unused:(contexts,order)):
            results.append((seed,R31.run(path)))
    return [{'seed':seed,
             'prior_experience_delta_actor_vs_R30':z['paired_relative_to_r30_late']['prior_arm_experience_independent']['delta'][0],
             'prior_experience_delta_joint_vs_R30':z['paired_relative_to_r30_late']['prior_arm_experience_independent']['delta'][1]}
            for seed,z in results]

if __name__=='__main__':
    import json,sys
    if len(sys.argv)!=2:raise SystemExit('usage: python r31_history_shuffle_control.py PRIVATE_CSV')
    print(json.dumps(run(sys.argv[1]),indent=2))
