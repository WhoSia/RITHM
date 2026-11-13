"""Replay R38 policies against their own feedback and measure group welfare."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.special import expit

from r37_ssm_source_cv import COST, SOURCE_SHA, source_groups

FULL = "ewa_habit_payoff"
FACTORS = {"f00": (0, 0), "f10": (1, 0), "f01": (0, 1), FULL: (1, 1)}
FITTED = ("ewa", "ewa_habit", "ewa_payoff", FULL)
MODELS = FITTED + ("ssm5", "ssm1_9", "f00", "f10", "f01")
SEED = 20261113
OTHER = np.arange(6)


def feedback_step(attraction, experience, belief, choice, payoff, informed, count, t):
    cost_a = OTHER + 1
    cost_b = 2 * (6 - OTHER)
    actual = np.where(choice[..., None], cost_a, cost_b)
    alternative = np.where(choice[..., None], cost_b, cost_a)
    value = payoff[..., None] + actual
    feasible = (value >= 6 - 1e-9) & (value <= 16 + 1e-9)
    feasible = np.where(informed[..., None], (np.asarray(count)[..., None, None] - choice[..., None]) == OTHER, feasible)
    mass = feasible.sum(axis=-1, keepdims=True)
    if np.any(mass == 0):
        raise ValueError("infeasible feedback")
    posterior = feasible / mass
    foregone = payoff + np.sum(posterior * (actual - alternative), axis=-1)
    belief = ((t - 1) * belief + posterior) / t
    phi = np.clip(1 - .5 * np.sum((belief - posterior)**2, axis=-1), 0, 1)
    weight = phi * experience
    experience = weight + 1
    attended = np.where(foregone >= payoff, foregone, 0)
    reinforce = np.stack((np.where(choice, attended, payoff),
                          np.where(choice, payoff, attended)), axis=-1)
    return (weight[..., None] * attraction + reinforce) / experience[..., None], experience, belief


def signals(a_count, a_pay, b_pay, rounds):
    return (2*(a_count+2)/(rounds+4)-1,
            (a_pay/(a_count+4) - b_pay/(rounds-a_count+4))/10)


def sampled_choice(differences, payoff_a, payoff_b, a_count, t, q, draws, informed, coin):
    """Previous histories stored in dense final-axis buffers, with replacement."""
    u, v = draws
    keep = np.arange(u.shape[-1]) < q[..., None]
    d = np.take_along_axis(differences, (u*t).astype(int), axis=-1)
    b_count = t-a_count
    a = np.take_along_axis(payoff_a, (u*a_count[..., None]).astype(int), axis=-1)
    b = np.take_along_axis(payoff_b, (v*b_count[..., None]).astype(int), axis=-1)
    score = np.where(informed, np.sum(d*keep, axis=-1), np.sum((a-b)*keep, axis=-1))
    score = np.where(~informed & ((a_count == 0) | (b_count == 0)), 0, score)
    return (score > 1e-7) | ((np.abs(score) <= 1e-7) & coin)


def simulate(name, coef, info, initial_choice, initial_payoff, uniforms, values, q, sample_seed, warm):
    reps, groups, _, _ = uniforms.shape
    shape = (reps, groups, 6)
    attraction = np.ones((*shape, 2))
    experience = np.ones(shape)
    belief = np.zeros((*shape, 6))
    a_count = np.zeros(shape, dtype=int)
    a_pay = np.zeros(shape)
    b_pay = np.zeros(shape)
    counts = np.empty((reps, groups, 40), dtype=np.int8)
    switch = np.empty((reps, groups, 39, 6), dtype=bool)
    if name.startswith("ssm"):
        a_history = np.zeros((*shape, 40))
        b_history = np.zeros((*shape, 40))
        differences = np.zeros((*shape, 40))
        rng = np.random.default_rng(sample_seed)
        q = np.full(shape, 5) if name == "ssm5" else q
        slots = np.indices(shape)
        state_mean = state_var = None
    else:
        state_mean = np.empty_like(counts, dtype=float)
        state_var = np.empty_like(counts, dtype=float)
    for t in range(40):
        coin = uniforms[:, :, t] < .5
        if t == 0:
            choice = np.broadcast_to(initial_choice, shape) if warm else coin
        elif name.startswith("ssm"):
            draws = rng.random((2, *shape, 9))
            choice = sampled_choice(differences, a_history, b_history, a_count, t, q, draws, info, coin)
        else:
            habit, gap = signals(a_count, a_pay, b_pay, t)
            delta = attraction[..., 1] - attraction[..., 0]
            z = coef[:, 0, None] * delta + coef[:, 1, None] * habit + coef[:, 2, None] * gap
            p = expit(z)
            state_mean[..., t] = p.sum(axis=-1)
            state_var[..., t] = (p*(1-p)).sum(axis=-1)
            choice = uniforms[:, :, t] < p
        count = choice.sum(axis=-1)
        counts[..., t] = count
        if t > 0:
            switch[:, :, t-1] = choice != previous
        cost = np.where(choice, count[..., None], 2*(6-count[..., None]))
        payoff = initial_payoff if t == 0 and warm else values[:, :, t]-cost
        if name.startswith("ssm"):
            ia = (*slots, a_count)
            ib = (*slots, t-a_count)
            a_history[ia] = np.where(choice, payoff, a_history[ia])
            b_history[ib] = np.where(choice, b_history[ib], payoff)
            k = count[..., None]-choice
            differences[..., t] = 2*(6-k)-(k+1)
        else:
            attraction, experience, belief = feedback_step(
                attraction, experience, belief, choice, payoff, info, count, t+1
            )
        a_count += choice
        a_pay += np.where(choice, payoff, 0)
        b_pay += np.where(choice, 0, payoff)
        previous = choice
    return counts, switch, state_mean, state_var


def summarize(counts, switches, info, state_mean=None, state_var=None):
    n = counts[..., 1:].astype(float)
    excess = COST[n.astype(int)]-24
    mean_by_time = n.mean(axis=(0, 1))
    bias = 3*np.mean((mean_by_time-4)**2)
    dispersion = 3*np.mean(n.var(axis=(0, 1)))
    assert np.isclose(excess.mean(), bias+dispersion)
    prev, nxt = counts[..., :-1], counts[..., 1:]
    at_optimum = prev == 4
    outside = ~at_optimum
    net = nxt.astype(int)-prev
    gross = switches.sum(axis=-1)
    stats = {
        "excess_per_round": excess.mean(),
        "cumulative_excess_2_40": excess.sum(axis=-1).mean(),
        "early_excess_2_10": excess[..., :9].mean(),
        "late_excess_31_40": excess[..., 29:].mean(),
        "mean_A": n.mean(),
        "exit_efficient_rate": (nxt[at_optimum] != 4).mean() if at_optimum.any() else None,
        "return_efficient_rate": (nxt[outside] == 4).mean() if outside.any() else None,
        "opposing_switch_pairs_per_round": ((gross-np.abs(net))/2).mean(),
        "excess_1_10": (COST[counts[..., :10]]-24).mean(),
        "bias_cost_by_period": bias,
        "dispersion_cost_by_period": dispersion,
        "switch_rate": switches.mean(),
        "switch_rate_by_information": {
            str(i): switches.transpose(0, 2, 1, 3)[..., info == i].mean()
            if np.any(info == i) else None
            for i in (0, 1)
        },
        "efficient_rate": (n == 4).mean(),
        "severe_rate": (np.abs(n-4) >= 2).mean(),
        "occupancy_frequencies": [(n == i).mean() for i in range(7)],
        "period_excess_1_40": (COST[counts]-24).mean(axis=(0, 1)).tolist(),
        "first_round_excess": (COST[counts[..., 0]]-24).mean(),
    }
    if state_mean is not None:
        mu = state_mean[..., 1:]
        stats["conditional_independent_variance_cost"] = 3*state_var[..., 1:].mean()
        stats["history_dispersion_cost"] = 3*mu.var(axis=(0, 1)).mean()
        stats["conditional_bias_cost"] = 3*np.mean((mu.mean(axis=(0, 1))-4)**2)
        stats["rao_blackwell_excess"] = sum(stats[k] for k in
            ("conditional_independent_variance_cost", "history_dispersion_cost", "conditional_bias_cost"))
    return stats, excess.mean(axis=-1), switches.mean(axis=(-1, -2))


def contrasts(results, session_ids):
    pairs = [(FULL, "ewa"), ("ewa_habit", "ewa"), ("ewa_payoff", "ewa"),
             ("f10", "f00"), ("f01", "f00"), (FULL, "f01"), (FULL, "f10"),
             (FULL, "ssm5"), (FULL, "ssm1_9")]
    specs = {f"{m}_minus_{ref}": {m: 1, ref: -1} for m, ref in pairs}
    specs["interaction"] = {FULL: 1, "f10": -1, "f01": -1, "f00": 1}
    out = {}
    for label, weights in specs.items():
        if not weights.keys() <= results.keys():
            continue
        diff = sum(w*results[k][1] for k, w in weights.items())
        sw = sum(w*results[k][2] for k, w in weights.items())
        mean = diff.mean(axis=1)
        direction = [diff[:, session_ids == s].mean() for s in np.unique(session_ids)]
        out[label] = {
            "cost_delta_per_round": mean.mean(),
            "paired_mc_se": mean.std(ddof=1)/np.sqrt(len(mean)),
            "sessions_lower_cost": int(np.sum(np.asarray(direction) < 0)),
            "switch_rate_delta": sw.mean(),
        }
    return out


def observed_other_treatments(path):
    grouped = {1: {}, 3: {}}
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            session, treatment, period = (int(row[k]) for k in ("session", "trt", "Period"))
            if session in (2, 101) or treatment not in grouped or not 1 <= period <= 40:
                continue
            key = (session, int(row["section"]), int(row["Group"]))
            block = grouped[treatment].setdefault(key, {})
            aid, y, n, info = (int(row[k]) for k in ("ID", "RouteA", "NumA", "Informed"))
            if (period, aid) in block or y not in (0, 1) or info != (treatment == 3):
                raise ValueError("invalid source treatment rows")
            block[period, aid] = (y, n)
    result = {}
    for treatment, groups in grouped.items():
        if len(groups) != 48 or len({key[0] for key in groups}) != 24:
            raise ValueError("other-treatment source census")
        trajectories = []
        for block in groups.values():
            actors = sorted({aid for _, aid in block})
            if len(block) != 240 or len(actors) != 6:
                raise ValueError("other-treatment group shape")
            y, n = np.asarray([[block[t, aid] for aid in actors] for t in range(1, 41)]).transpose(2, 0, 1)
            if not np.all(y.sum(axis=-1, keepdims=True) == n):
                raise ValueError("source occupancy mismatch")
            trajectories.append(y)
        actions = np.asarray(trajectories)[None]
        result["none" if treatment == 1 else "full"] = summarize(
            actions.sum(axis=-1), actions[:, :, 1:] != actions[:, :, :-1],
            np.full((48, 6), treatment == 3)
        )[0]
    return result


def run(path, fitted_results, reps):
    if reps < 2:
        raise ValueError("need at least two independent simulation draws")
    if fitted_results["source_sha256"] != SOURCE_SHA:
        raise ValueError("R38 source mismatch")
    groups = source_groups(path)
    sids = np.array([g[0] for g in groups])
    folds = np.searchsorted(np.unique(sids), sids) % 6
    observed = np.asarray([[[(p[t][a]) for a in actors] for t in range(1, 41)]
                           for _, _, _, actors, p in groups])
    info = observed[:, 0, :, 1].astype(bool)
    observed_choice = observed[..., 0].astype(bool)
    observed_stats, _, _ = summarize(observed_choice.sum(axis=-1)[None],
                                    (observed_choice[:, 1:] != observed_choice[:, :-1])[None], info)
    coeff = {}
    fitted = fitted_results["fold_parameters"]
    for name in FITTED:
        raw = np.asarray(fitted[name])[folds]
        coeff[name] = np.zeros((len(groups), 3))
        columns = [0] + ([1] if "habit" in name else []) + ([2] if "payoff" in name else [])
        coeff[name][:, columns] = raw
    for name, (habit, payoff) in list(FACTORS.items())[:-1]:
        coeff[name] = coeff[FULL]*np.array([1, habit, payoff])
    rng = np.random.default_rng(SEED)
    dims = (reps, len(groups), 40, 6)
    uniforms = rng.random(dims)
    u_value = rng.random(dims)
    values = 6 + np.floor(u_value*101)/10
    tight = 9 + np.floor(u_value*41)/10
    q = rng.integers(1, 10, (reps, len(groups), 6))
    out = {}
    conditions = [
        ("partial_warm", info, values, True, MODELS),
        ("partial_cold", info, values, False, MODELS),
        ("none_warm", np.zeros_like(info), values, True, FITTED + tuple(FACTORS)[:-1]),
        ("full_warm", np.ones_like(info), values, True, FITTED + tuple(FACTORS)[:-1]),
        ("partial_low_value_noise", info, tight, True, tuple(FACTORS)),
    ]
    for label, informed, value, warm, models in conditions:
        results = {}
        for name in models:
            counts, changes, mu, var = simulate(name, coeff.get(name), informed,
                observed_choice[:, 0], observed[:, 0, :, 2], uniforms, value, q, SEED+1, warm)
            results[name] = summarize(counts, changes, informed, mu, var)
        out[label] = {"models": {k: v[0] for k,v in results.items()},
                      "contrasts": contrasts(results, sids)}
    return {"source_sha256": SOURCE_SHA, "sessions": len(np.unique(sids)),
            "groups": len(groups), "replications_per_group": reps, "seed": SEED,
            "observed": observed_stats,
            "observed_other_treatments": observed_other_treatments(path), "experiments": out}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_csv")
    parser.add_argument("r38_results")
    parser.add_argument("--replications", type=int, default=256)
    args = parser.parse_args()
    print(json.dumps(run(args.private_csv, json.loads(Path(args.r38_results).read_text()),
                         args.replications), indent=2, allow_nan=False))
