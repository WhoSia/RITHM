"""Audit the support and permutation reference for the R37 switching placebos."""
import argparse
import json

import numpy as np

from r37_negative_control_gates import SHA, make_cells, original_rows


def permutation_audit(cells, reps=9999, seed=20261113):
    """Joint two-sided tests sharing one set of permutations per stratum."""
    rng = np.random.default_rng(seed)
    observed = np.zeros(3)
    null = np.zeros((reps, 3))
    variance = np.zeros(3)
    informative = np.zeros(3, dtype=int)
    denominator = 0.0
    for _, values in cells:
        x = values[:, 0] - values[:, 0].mean()
        y = np.column_stack((values[:, 1:], values[:, 2]-values[:, 1]))
        y -= y.mean(axis=0)
        ssx = x @ x
        # The conditional variance of x_perm' y is SSx SSy / (n - 1).
        contribution = ssx * np.sum(y*y, axis=0)/(len(x)-1)
        variance += contribution
        informative += contribution > 0
        denominator += ssx
        observed += x @ y
        order = np.argsort(rng.random((reps, len(x))), axis=1)
        null += x[order] @ y
    if denominator <= 0:
        raise ValueError("no within-cell variation in Value")
    return {
        name: {
            "beta": float(observed[j]/denominator),
            "exact_conditional_null_sd": float(np.sqrt(variance[j])/denominator),
            "informative_cells": int(informative[j]),
            "permutation_p": (
                float((1+np.count_nonzero(np.abs(null[:, j]) >= abs(observed[j])-1e-10))/(1+reps))
                if variance[j] > 0 else None
            ),
        } for j, name in enumerate(("before", "after", "after_minus_before"))
    }


def run(path):
    rows = original_rows(path)
    conditions = {}
    for mode in ("previous", "current", "info_only", "both"):
        cells = make_cells(rows, mode)
        conditions[mode] = {
            "actor_periods": sum(len(x) for _, x in cells),
            "cells": len(cells),
            "tests": permutation_audit(cells),
        }
    return {"source_sha256": SHA, "permutations": 9999, "conditions": conditions}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_csv")
    print(json.dumps(run(parser.parse_args().private_csv), indent=2, allow_nan=False))
