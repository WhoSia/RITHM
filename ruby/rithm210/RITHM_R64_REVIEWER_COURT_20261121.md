# RITHM-2.10 P3-R64 — Simulated Adversarial Reviewer Court and Editorial Decision

**2026-11-21 · Internal three-perspective stress test written by AI, NOT a real independent peer review.** The purpose is to predict credible reviewer objections and redirect research effort. Verifiable related work is recorded in [R64 prior-art collision registry](RITHM_R64_PRIOR_ART_COLLISION_20261121.md).

## Reviewer A — Transportation behavioral learning / novelty

**Recommendation: Reject in current framing; reconsider after major redesign.**

R61–R63 improve various feedback and memory switching models on Noussair–Qiao's experimental dataset. But the original authors already fitted Small Sample behavior to these choices, Mak et al. (2015) studied inertia with information, Yu & Gao (2019) separately evaluated one-step and full-trajectory forecasts, and Yang et al. (2026) compared information-specific reinforcement rules against EWA, Q-learning, mixed logit and a Selten variant. Consequently the novelty cannot be simply **'memory, payoff learning, different information masks, or first one-step/full-horizon comparison'**. Classical Fréchet event bounds and a no-free-transfer counterexample are also not new general theorems.

**Required rebuttal**: State an exact central contribution that remains after subtracting each predecessor. Reproduce the original paper's Small Sample benchmark with exact source-legal inputs; compare established fitted learners under an equal data budget. If no new theorem or independently tested mechanism remains, position this as a rigorous **replication/benchmark note**, not as a major new model or causal explanation.

## Reviewer B — Causal inference / experimental identification

**Recommendation: Major revision or reject any mechanistic claim.**

The evidence is repeatedly reexamined original data. There are 24 original independent sessions and only 17 with Partial target; the 1,248 group transitions and 7,488 actor decisions are **NOT** 1,248 or 7,488 independent treatment replications. Feedback conditions and individual information masks change together in the source; matching own info masks does not randomize treatment context or identify invariance. Personal inertia, unobserved shared shocks and rational adaptive learning can fit overlapping distributions. An analyst-only previous-group-occupancy intercept is not a valid uninformed participant's causal feature.

**Required rebuttal**: Label all current estimates retrospective/exploratory. Specify group-level randomization, carryover, interference, belief elicitation, and observable information filtration in any new design. Require an independent cohort or a genuinely locked subsequent prospective study before a causal mechanism claim.

## Reviewer C — Prediction, distribution shift and valid metrics

**Recommendation: Major revision even if objectives are prediction-only.**

An out-of-sample heldout original *session* is good, but choosing dozens of architectures after repeatedly checking those same sessions induces researcher overfitting. The 2019 Yu–Gao study already distinguished one-step and multi-step rollout. Free-running historical-Value(t)-tape congestion is a valid *conditional environmental replay*, not proof of an unconditional future-unknown policy forecast. Group-total MSE, treatment contrast, A4 all-stay, switch count and individual logloss cannot be optimized interchangeably.

R63B also used approximately **2× the training actor panels for each No/Full bridge mask** compared with Partial-only. R64A fixed that sample-count discrepancy; despite 3/3 nominally lower group MSEs, all three **17-session cluster-bootstrap intervals include zero**, and 8/8 panel-matched one-step U,D losses remain worse than Partial-only. An unqualified claim of robust transfer is unjustified.

**Required rebuttal**: Strong prespecified baselines, fixed model selection, equal training data budgets, independent holdout population and explicit interval coverage by session. Separate actual deployment constraints from historical exogenous-tape sensitivities.

## Reviewer D — Engineering and research reproducibility

**Recommendation: Positive, but not a substitute for novelty.**

Author-original SHA enforcement, private data custody, exact six-person simultaneous action semantics, source-free CI, synthetic counterexamples and independent Drive readback establish unusual discipline for an exploratory project. The right academic use is **reproducible falsification of unsupported claims** and a clear benchmark. However passing dozens of source-free tests does not validate an empirical model, and 20 commits do not correspond to 20 independent results.

## Editorial ruling (hypothetical, not actual reviewers)

| Dimension (heuristic 0–5, not statistically estimated) | Current RITHM-2.10 | Why |
|---|---:|---|
| Infrastructure and reproducibility | **4/5** | Source sealing, replay, CI, actor/legal restrictions |
| Novelty of new learning model | **1/5** | Serious overlap with author Small Sample and 2015/2019/2026 learning literature |
| Current empirical generalization | **2/5** | Original 24 sessions repeatedly exposed; 17 Partial-bearing; no independent replication |
| Identification of cognition/coordination | **0–1/5** | Treatment, feedback, information and strategic learning not independently manipulated |
| Research question importance | **4/5** | Misaligned individual, group-stability and social cost predictions matter |
| Publishability as **major causal/model discovery** now | **LOW** | No clear novel mechanism and independence |
| Publishability as **auditable benchmark/replication note** after baseline parity | **POSSIBLE, conditional** | Must show robust new diagnostic against existing models |
| Publishability after new independent experiment plus identification | **HIGHER POTENTIAL, unverified** | An information/interference experiment can resolve live competing mechanisms |

**Directive:** Do not inflate another R63X model generation without answering a discriminating causal/predictive question. R64 has three research gates: (I) original-paper/modern strong-baseline parity, (II) sample-size- and information-support-matched transfer, (III) new, genuinely independent evidence or rigorous new theoretical identification result. Criterion failure routes to a transparent replication note or termination of the mechanism claim.

## Claim corrections effective immediately

- Do not call the R63B transfer 'robust' or 'externally validated'.
- No + Full predictive bridge **may** outperform Partial-only on the reused cohort's conditional 40-step MSE. Once actor panels are size-matched, the three paired 17-session intervals cross zero. It is a useful **robustness anomaly / hypothesis generator**, not proof of an invariant behavior law.
- R63C's 530 old-A4 cases suggest marginal miscalibration matters, but its old-A4-conditioned intercept is **researcher-only** and does not establish actual cognition or social coordination. Its broad Fréchet bounds are mathematical feasibility regions assuming fitted marginal probabilities are correct.
- A forthcoming source-free CI success means tested software contracts; original human dataset replay and scientific generalization are separate receipts.

No outside reviewer was contacted or has endorsed this ruling.