"""RITHM R23: prior-only finite-memory vs inertia competition.

All decisions are predicted before a group's period-t outcomes update history.
The original author-approved CSV is read locally, never embedded in public files.
Analysis is exploratory because the same 24 sessions have been repeatedly studied.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from random import Random

SOURCE_SHA = "d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb"
COST = tuple(n * n + 2 * (6 - n) ** 2 for n in range(7))
DECAYS = (0.5, 0.8, 1.0)
STRENGTHS = (2.0, 5.0, 12.0)
MIXES = (0.0, 0.25, 0.5, 0.75, 1.0)


@dataclass
class Actor:
    periods: int = 0
    last_route: int | None = None
    count_a: int = 0
    decayed: dict[float, tuple[float, float]] = field(
        default_factory=lambda: {d: (0.0, 0.0) for d in DECAYS}
    )
    transitions: dict[int, list[int]] = field(
        default_factory=lambda: {0: [0, 0], 1: [0, 0]}
    )

    def frequency(self, decay: float) -> float:
        a, b = self.decayed[decay]
        return (a + 1.0) / (a + b + 2.0)

    def markov(self, strength: float) -> float:
        if self.last_route is None:
            return 0.5
        switched, opportunities = self.transitions[self.last_route]
        p_switch = (switched + 1.0) / (opportunities + strength)
        return 1.0 - p_switch if self.last_route else p_switch

    def update(self, choice: int) -> None:
        if choice not in (0, 1):
            raise ValueError("nonbinary route")
        if self.last_route is not None:
            counts = self.transitions[self.last_route]
            counts[0] += int(self.last_route != choice)
            counts[1] += 1
        for decay, (a, b) in self.decayed.items():
            self.decayed[decay] = (decay * a + choice, decay * b + (1 - choice))
        self.count_a += choice
        self.last_route = choice
        self.periods += 1


def candidates() -> tuple[tuple[float, float, float], ...]:
    # Exactly one non-duplicated frequency-only model per memory time scale;
    # exactly one Markov-only model per transition prior strength.
    choices = {(d, 5.0, 0.0) for d in DECAYS}
    choices.update((1.0, s, 1.0) for s in STRENGTHS)
    choices.update((d, s, mix) for d in DECAYS for s in STRENGTHS
                   for mix in MIXES if mix not in (0.0, 1.0))
    return tuple(sorted(choices))


def label(candidate: tuple[float, float, float]) -> str:
    decay, strength, mix = candidate
    if mix == 0.0:
        return f"frequency_decay_{decay:g}"
    if mix == 1.0:
        return f"markov_strength_{strength:g}"
    return f"memory_{decay:g}_markov_{strength:g}_mix_{mix:g}"


def occupancy_distribution(ps: list[float]) -> tuple[float, ...]:
    if len(ps) != 6 or any(not math.isfinite(p) or not 0 <= p <= 1 for p in ps):
        raise ValueError("six valid forecast probabilities needed")
    dist = [1.0]
    for p in ps:
        next_dist = [0.0] * (len(dist) + 1)
        for n, mass in enumerate(dist):
            next_dist[n] += mass * (1 - p)
            next_dist[n + 1] += mass * p
        dist = next_dist
    if not math.isclose(sum(dist), 1.0, abs_tol=1e-11):
        raise ArithmeticError("group probability mass lost")
    return tuple(dist)


def scores(ps: list[float], actual_n: int) -> tuple[float, float, float, float]:
    if actual_n not in range(7):
        raise ValueError("occupancy 0..6")
    dist = occupancy_distribution(ps)
    logloss = -math.log(max(dist[actual_n], sys.float_info.min))
    brier = sum((p - (n == actual_n)) ** 2 for n, p in enumerate(dist))
    predicted_cost = sum(p * COST[n] for n, p in enumerate(dist))
    error = predicted_cost - COST[actual_n]
    return logloss, brier, abs(error), error


def load_groups(source_path: str) -> dict[tuple[int, int, int, int], list[dict[str, str]]]:
    p = Path(source_path)
    if hashlib.sha256(p.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("original-source SHA256 mismatch")
    groups: dict[tuple[int, int, int, int], list[dict[str, str]]] = defaultdict(list)
    with p.open(newline="") as stream:
        for row in csv.DictReader(stream):
            session, trt, period = (int(row[k]) for k in ("session", "trt", "Period"))
            if session in (2, 101) or trt not in (1, 2, 3) or not 1 <= period <= 40:
                continue
            key = (session, int(row["section"]), period, int(row["Group"]))
            groups[key].append(row)
    if len(groups) != 5760 or any(len(group) != 6 for group in groups.values()):
        raise ValueError("not 5760 complete groups")
    if len({k[0] for k in groups}) != 24:
        raise ValueError("expected 24 sessions")
    return groups


def evaluate(groups: dict, requested_candidates: tuple | None = None) -> dict:
    requested_candidates = candidates() if requested_candidates is None else requested_candidates
    if len(set(requested_candidates)) != len(requested_candidates) or not requested_candidates:
        raise ValueError("duplicate/empty candidates")
    states: dict[tuple[int, int, int], Actor] = {}
    # score sums, count; no per-person data stored or emitted.
    totals: dict[tuple[int, int, str], list[float]] = defaultdict(lambda: [0., 0., 0., 0., 0.])
    periods_seen = 0
    for (session, section, period, group), people in sorted(groups.items()):
        people = sorted(people, key=lambda r: int(r["ID"]))
        ids = [int(r["ID"]) for r in people]
        if len(set(ids)) != 6:
            raise ValueError("duplicate actors")
        treatment = int(people[0]["trt"])
        if any(int(r["trt"]) != treatment for r in people):
            raise ValueError("mixed treatment within group")
        outcome = [int(r["RouteA"]) for r in people]
        if any(choice not in (0, 1) for choice in outcome):
            raise ValueError("not binary")
        n = sum(outcome)
        if any(int(r["NumA"]) != n for r in people):
            raise ValueError("observed group occupancy mismatch")
        actor_states = [states.setdefault((session, section, ident), Actor()) for ident in ids]
        if any(actor.periods != period - 1 for actor in actor_states):
            raise ValueError("actor history continuity or look-ahead violation")
        frequency = [{d: actor.frequency(d) for d in DECAYS} for actor in actor_states]
        markov = [{s: actor.markov(s) for s in STRENGTHS} for actor in actor_states]
        # Forecast every candidate BEFORE updating any current-period actor.
        for config in requested_candidates:
            decay, strength, mix = config
            label_name = label(config)
            ps = [(1 - mix) * f[decay] + mix * m[strength]
                  for f, m in zip(frequency, markov)]
            values = scores(ps, n)
            record = totals[(session, treatment, label_name)]
            for i, value in enumerate(values):
                record[i] += value
            record[4] += 1
        for actor, choice in zip(actor_states, outcome):
            actor.update(choice)
        periods_seen += 1
    results = []
    for (session, treatment, model), accum in sorted(totals.items()):
        count = int(accum[4])
        if not count:
            raise ArithmeticError("empty group support")
        results.append(dict(session=session, treatment=treatment, model=model,
                            groups=count, logloss=accum[0]/count,
                            brier=accum[1]/count, cost_abs_error=accum[2]/count,
                            cost_bias=accum[3]/count))
    return dict(groups=periods_seen, sessions=len({r['session'] for r in results}),
                candidates=len(requested_candidates), session_results=results)


def cross_validate(payload: dict, *, folds: int = 6, draws: int = 4000,
                   seed: int = 20261109) -> dict:
    rows = payload["session_results"]
    sessions = sorted({r["session"] for r in rows})
    if len(sessions) != 24 or folds != 6 or draws < 1:
        raise ValueError("24 sessions, six folds, and positive resamples required")
    fold_of = {session: i % folds for i, session in enumerate(sessions)}
    lookup = {(r["session"], r["treatment"], r["model"]): r for r in rows}
    if len(lookup) != len(rows):
        raise ValueError("duplicate session/model cell")
    variants = sorted({r["model"] for r in rows})
    baseline = "frequency_decay_1"
    if baseline not in variants:
        raise ValueError("unavailable primary baseline")
    heldout = []
    selection = defaultdict(int)
    for fold in range(folds):
        training = [s for s in sessions if fold_of[s] != fold]
        testing = [s for s in sessions if fold_of[s] == fold]
        for treatment in (1,2,3):
            # Equal weight PER INDEPENDENT SESSION, not per 6-person group.
            winning = min(variants, key=lambda name: (
                sum(lookup[(s,treatment,name)]["logloss"] for s in training)/len(training), name))
            selection[(treatment,winning)] += 1
            for s in testing:
                r = lookup[(s,treatment,winning)]
                b = lookup[(s,treatment,baseline)]
                if r["groups"] != b["groups"]:
                    raise ValueError("unequal support of compared models")
                heldout.append(dict(session=s,treatment=treatment,model=winning,
                                    groups=r["groups"],
                                    delta_logloss=r["logloss"]-b["logloss"],
                                    delta_brier=r["brier"]-b["brier"],
                                    delta_cost_abs_error=r["cost_abs_error"]-b["cost_abs_error"],
                                    model_logloss=r["logloss"],
                                    baseline_logloss=b["logloss"]))
    def aggregate(treatment):
        rr = [r for r in heldout if r["treatment"] == treatment]
        if len(rr)!=24:
            raise ValueError("heldout session coverage error")
        rng = Random(seed+treatment)
        differences = [r["delta_logloss"] for r in rr]
        sampled = sorted(sum(rng.choice(differences) for _ in range(24))/24
                         for _ in range(draws))
        return dict(treatment=treatment, sessions=24,
                    chosen={k[1]:v for k,v in selection.items() if k[0]==treatment},
                    mean_logloss=sum(r["model_logloss"] for r in rr)/24,
                    baseline_logloss=sum(r["baseline_logloss"] for r in rr)/24,
                    delta_logloss=sum(differences)/24,
                    delta_logloss_bootstrap95=[sampled[int(.025*draws)],sampled[int(.975*draws)]],
                    delta_brier=sum(r["delta_brier"] for r in rr)/24,
                    delta_cost_abs_error=sum(r["delta_cost_abs_error"] for r in rr)/24)
    return dict(sessions=24, groups=payload["groups"], candidates=len(variants),
                results=[aggregate(t) for t in (1,2,3)],
                note="Exploratory repeatedly-inspected historical source; fold-specific selection uses 20 training sessions only. No human causal claim.")


def run(source_path: str, *, draws: int = 4000) -> dict:
    return cross_validate(evaluate(load_groups(source_path)), draws=draws)


if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1]), indent=2))
