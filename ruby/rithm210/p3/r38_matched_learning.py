"""Compare online learning forecasts on the same held-out Partial sessions."""
import argparse
import json

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

from r31_order_history import prior_contexts
from r33_within_partial_payoff_learning import construct_source, fit, x_y
from r37_ewa_author_cv import attractions
from r37_ssm_source_cv import SOURCE_SHA, group_metrics, source_groups

METRICS = ("actor_logloss", "six_choice_logloss", "occupancy_logloss", "group_cost_mae")


def matched_features(path):
    source = construct_source(path)
    _, group_order = prior_contexts(path)
    groups = source_groups(path)
    if set(source) != {group[0] for group in groups}:
        raise ValueError("session mismatch")

    datasets = {}
    for sid, records in sorted(source.items()):
        by_group = {group[2]: group for group in groups if group[0] == sid}
        ordered = [by_group[group_id] for group_id in group_order[sid]]
        ewa = attractions(ordered)[sid]
        x, y = x_y(source, sid, "both")
        for (_, _, group, actors, periods), block in zip(
            ordered, [records[i:i + 39] for i in range(0, len(records), 39)], strict=True
        ):
            for t, rows, *_ in block:
                expected = [
                    (previous[0], previous[3], previous[2], previous[1], periods[t][actor][0])
                    for actor in actors
                    for previous in [periods[t - 1][actor]]
                ]
                if list(map(tuple, rows)) != expected:
                    raise ValueError(f"actor-period alignment failure in group {group}")

        if not np.array_equal(y, np.asarray([target for _, target in ewa]).ravel()):
            raise ValueError("EWA target alignment failure")
        delta = np.asarray([values for values, _ in ewa]).ravel()
        habit, gap = np.asarray([h for *_, online in records for h in online]).T
        datasets[sid] = ({
            "ewa": delta[:, None],
            "habit": habit[:, None],
            "payoff": gap[:, None],
            "ewa_habit": np.column_stack((delta, habit)),
            "ewa_payoff": np.column_stack((delta, gap)),
            "ewa_habit_payoff": np.column_stack((delta, habit, gap)),
            "r33": x,
        }, y)
    return datasets


def fit_compact(x, y, weights):
    def objective(coef):
        z = x @ coef
        return np.dot(weights, np.logaddexp(0, z) - y*z), x.T @ (weights*(expit(z)-y))

    # Constrain the EWA response and the single-feature baselines to be
    # nonnegative. Other added coefficients can have either sign.
    bounds = [(0, 16)] + [(None, None)]*(x.shape[1]-1)
    result = minimize(objective, np.zeros(x.shape[1]), jac=True, bounds=bounds,
                      method="L-BFGS-B", options={"ftol": 1e-13, "gtol": 1e-9})
    if not result.success:
        raise ArithmeticError(result.message)
    return result.x


def ridge_edf(x, coef, ridge):
    p = expit(x @ coef)
    hessian = (x.T * (p*(1-p))) @ x / len(x)
    penalty = ridge * np.diag([0] + [1]*(x.shape[1]-1))
    return float(np.trace(np.linalg.solve(hessian + penalty, hessian)))


def evaluate(datasets):
    sessions = sorted(datasets)
    if len(sessions) != 24:
        raise ValueError("expected 24 sessions")
    names = list(datasets[sessions[0]][0])
    held = {name: {} for name in names}
    selections = {name: [] for name in names}
    for fold in range(6):
        test = sessions[fold::6]
        train = [s for s in sessions if s not in test]
        y_train = np.concatenate([datasets[s][1] for s in train])
        weights = np.concatenate([
            np.full(len(datasets[s][1]), 1/(len(train)*len(datasets[s][1]))) for s in train
        ])
        for name in names:
            x_train = np.concatenate([datasets[s][0][name] for s in train])
            if name == "r33":
                coef = fit(x_train, y_train, ridge=.02)
                selections[name].append({"nominal":len(coef), "ridge_edf":ridge_edf(x_train, coef, .02)})
            else:
                coef = fit_compact(x_train, y_train, weights)
                selections[name].append(coef.tolist())
            for s in test:
                features, y = datasets[s]
                probabilities = expit(features[name] @ coef).reshape(-1, 6)
                held[name][s] = np.mean([
                    group_metrics(p, target) for p, target in zip(probabilities, y.reshape(-1, 6), strict=True)
                ], axis=0)

    rng = np.random.default_rng(20261113)
    indices = rng.integers(0, len(sessions), (10000, len(sessions)))
    contrasts = {}
    for model, reference in [
        ("habit", "ewa"), ("payoff", "ewa"), ("ewa_habit", "ewa"), ("ewa_payoff", "ewa"),
        ("ewa_habit_payoff", "ewa_habit"), ("ewa_habit_payoff", "ewa_payoff"),
        ("r33", "ewa_habit_payoff"), ("r33", "ewa"),
    ]:
        diff = np.asarray([held[model][s]-held[reference][s] for s in sessions])
        contrasts[f"{model}_minus_{reference}"] = {
            "delta": diff.mean(axis=0).tolist(),
            "descriptive_session_resampling_95": np.quantile(diff[indices].mean(axis=1), [.025,.975], axis=0).T.tolist(),
            "sessions_lower_actor_loss": int(np.sum(diff[:,0] < 0)),
        }
    return {
        "source_sha256": SOURCE_SHA,
        "sessions": len(sessions),
        "group_periods": sum(len(y)//6 for _, y in datasets.values()),
        "metrics": METRICS,
        "scores": {name: np.mean(list(rows.values()), axis=0).tolist() for name, rows in held.items()},
        "fold_parameters": selections,
        "paired_contrasts": contrasts,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_csv")
    print(json.dumps(evaluate(matched_features(parser.parse_args().private_csv)), indent=2, allow_nan=False))
