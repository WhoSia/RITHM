# RITHM-2.10 · P3-R34 — Conditional Reward-Shuffle Falsification and R30→R31 Dependency Repair

**2026-11-11 · R34 source-verified exploratory replay. Human reward-learning causality: HOLD.**

## Research problem

R33's source-legal online payoff-route gap improved independent six-person joint logloss from 3.111032043 to 3.077580862 after conditioning on prior-treatment route tendency and online current-Partial route-choice history. **Could this apparent payoff benefit largely reflect common route congestion/environment rather than a participant's own individual reinforcement?** R34 tests that statement with a *retrospective artificial placebo*, not an experiment delivered to people.

## P1 software reproducibility finding and repair

GitHub's posted R31 `r31_order_history.py` imports `joint_scores` from GitHub R30 `r30_partial_dynamic_joint.py`, but the posted R30 previously provided `score` and no `joint_scores`. This makes a clean repository import chain R31→R32→R33 fail before scientific tests. A backward-compatible R30 alias was committed as [`66b9cdfbbdb010b48749fea554e410eb41c23ac0`](https://github.com/WhoSia/RITHM/commit/66b9cdfbbdb010b48749fea554e410eb41c23ac0), preserving the nine-output score API. Add a source-free import bridge regression to CI. **The packaged legacy R30 source differs bytewise from posted R30; R31–R33 sources in the local ZIP match GitHub Git blob IDs.** Passing the source-free local tests does not replace clean-checkout remote CI evidence.

## Data and exact filtration

Original experimenter-owned file SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`, official manuscript-main **24 sessions**, Partial only, **48 stable six-actor groups**, **1,872 group-periods t=2,…,40** (11,232 next-choice actor predictions). Original 6-fold session split (20 training/4 held-out sessions). Fitted L2-regularized logistic models with fixed ridge 0.02; group joint latent-shock strength τ selected exclusively on each training fold from {0,.2,.4,.6}, then scored on held-out sessions. No participant rows were published.

R33's online choice habit and individual selected-route payoff gap are computed from *only already completed* Partial rounds; all actors can observe their OWN payoff. Public group occupancy is used only for informed actors. The baseline also includes known previous route, previous **actual received own payoff**, trial period, pre-Partial route preference proxy, informed status and order controls.

### Exact placebo recipe

For each six-person Partial group and each completed period k, partition actors by the actual route chosen in k. Within each partition, cyclically rotate the six people's **actually received payoffs** by a nonzero random offset if partition size is ≥2. Do not change: current or prior route choices, group/period, informed status, previous public count, outcome labels, exact group-by-route payoff totals, or any *last-period* own payoff feature from the original baseline. Recompute **only the cumulative personal payoff gap** with the sham history and then refit the exact same train-only model. The sham history at t uses only rotated payoffs for k<t, never k≥t. Sixteen predefined seeds 34001–34016; each of the 16 refits and original comparison uses identical historical session folds.

This is a deliberately impossible participant-information policy—people did NOT receive rotated payoffs! Its purpose is to distinguish the *statistical role* of individual reward attribution from group-route-period-common information and endogeneity. Because the chosen route is held fixed, conditional own payoff = independently drawn Value minus same route congestion cost, so same-route swapping mainly reallocates idiosyncratic travel-value draws while keeping route congestion. **Neither the placebo effect nor the residual is a formal causal decomposition.**

## Source replay results

| Candidate, same out-of-session folds | Actor logloss ↓ | Six-mask joint logloss ↓ | Seven-count logloss ↓ | Predicted congestion cost MAE ↓ |
|---|---:|---:|---:|---:|
| Choice habit alone (R33) | 0.518505 | 3.111032 | 1.398645 | 2.777836 |
| Choice + conditional within-route payoff-shuffle, 16-seed **median** | 0.515229 | 3.091374 | 1.393882 | 2.750513 |
| Choice + **actual own received** payoff | **0.512930** | **3.077581** | **1.392895** | **2.744521** |

True personal payoff history improves joint six-mask logloss by **-0.033451** vs choice baseline. Sixteen conditional reward-shuffle controls still improve joint loss by **-0.019658** (median; min/max improvement -0.021602 / -0.015190). The actual original link improves over the median shuffled model by **-0.013794**. The actual model beats each of the 16 sham refits in this exploration, but 16 shuffles after repeated source re-use do **not** justify a new preregistered p-value.

Exploratory 24-session bootstrap interval of true-vs-choice joint loss difference: [-0.042437,-0.024753]. **This interval is descriptive and post-selection; no new independent evidence.**

### Information subgroups (individual logloss)

| Same Partial treatment | Choice habit | Actual payoff + choice | Improvement |
|---|---:|---:|---:|
| 3 informed/group | 0.489198 | 0.484280 | -0.004918 |
| 3 uninformed/group | 0.547813 | 0.541580 | -0.006233 |

The payoff feature is beneficial in out-of-session prediction for both information strata. In the uninformed stratum, the model NEVER reads hidden previous occupancy as a predictor. Informational differences remain descriptive and confounded with individual strategy and group response, not a causal moderator estimate.

Of the 10,765 eligible (in a previous-period route cell containing ≥2 people) actor-period positions per sham run, approximately **99.07%** received a numerically different payoff. The random travel-value assignment is preserved as a multiset within each period×route cell, not per individual.

The selected τ for the true payoff model and all 16 sham refits was **0.2 in all six training folds**. Individual and joint score changes therefore do not arise from a comparison using different τ grids.

## Identification verdict and strict limits

1. **PASS:** Route-conditioned cumulative payoff history has predictive content beyond fixed pre-Partial preference, own route choice habit and last actual payoff; its own-person assignment matters relative to this artificial reward-shuffle benchmark.
2. **PASS:** Nonzero reward-placebo improvement shows a substantial part of the score improvement is not specific to own idiosyncratic receipt. A candidate explanation is endogenous route/period congestion environment or shared route history, without claiming an exact decomposition.
3. **HOLD:** The *causal* effect of received payoff on later choice, physiological or cognitive 'hassle' cost, cost of actually switching, distinct stable preference versus learning, and causal welfare improvements. Chosen-route payoffs are selected outcomes, and the baseline may absorb other group-time factors incompletely.
4. **PRIORITY NEXT / R35:** Use the author manuscript's independently randomized travel **Value** (uniform 6–16, not disclosed before route choice) as an experimenter-only randomized shock for an explicit **post-decision reward feedback diagnostic**. Use only previous Value for experimental identification regressions, NEVER assert players observed Value or make it a lawful information-forecast input. Need cluster-level interference assumptions and conditional randomization checks before causal claims. Also report sensitivity to payoff smoothing and prior-study model multiplicity.

## Executed reproducibility and paths

- Local SHA-verified original-author source replay: **16/16 conditional-placebo models plus actual R33 baseline**, fixed 24 sessions and 6 folds.
- Local source-free regression: **41 tests invoked, 38 passed, 3 explicitly skipped**, including 8 new R34 tests, hidden-information and future-time firewall, exact conditional payoff conservation, bootstrap, determinism and R30 `joint_scores` import. Source-free ZIP includes R29–R33 dependencies and all relevant tests; no original actor CSV or other private rows.
- Permanent code: [`ruby/rithm210/p3/r34_payoff_selection_placebo.py`](https://github.com/WhoSia/RITHM/blob/main/ruby/rithm210/p3/r34_payoff_selection_placebo.py); test in same folder; aggregate JSON and this report under `ruby/rithm210`.
- **CI status:** GitHub remote Actions PASS not inferred from CI step registration. GitHub exact clean checkout remains HOLD until independently verified. Historical 24 source sessions have been adaptively explored in R23–R34; all significance claims remain exploratory.
