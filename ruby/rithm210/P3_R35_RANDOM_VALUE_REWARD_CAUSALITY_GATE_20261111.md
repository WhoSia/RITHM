# RITHM-2.10 / P3-R35 — Randomized travel Value: reward-response versus a predecision placebo

**2026-11-11 | original-author-source replay | decision: P1 CAUSAL HOLD; prediction evidence retains its own scope.**

## Research question and authority

R33/R34 found additional *forecast* information from participants' past **actually received payoff** after controlling prior and online route-choice habits, but a within-route same-group-period payoff shuffle preserved much of that gain. R35 tried a more stringent test: the authors' independently drawn travel `Value` is a source of random variation in realized payoff `profit=Value-Cost`. However, **Value is not disclosed before route choice**, so it may be used as an experimenter-side randomization diagnostic and **never as a lawful participant forecasting input**.

In the authors' July 24 2026 manuscript §3, values are uniformly drawn in `[6,16]` independently for each actor and period, with route choice before value revelation. The same manuscript already studies **EWA-lite, SSM5 and SSM1–9**, so the hypothesis that agents learn from small histories of payoffs is explicit prior art. RITHM novelty claims must be narrower than generic payoff learning and revision timing.

## Exact original-source protocol

CSV `data_task_all_switch_230705.csv`, original private SHA-256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`; authors' main 24 sessions, Partial `trt=2`, 48 six-person groups, all `t=1..39` transitions. Do **not** accidentally include disputed pilot 2 or session 101 in the paper-main population.

Within-cell comparison strata are `session × section × group × period × actually chosen route × informed flag`. The chosen route fixes the shared congestion cost within each stratum, while the author's independently assigned `Value_t` moves the participant's received payoff. Require ≥2 actors per stratum. Total 11,232 actor-period records; 3,744 eligible conditional cells containing 8,619 actor-period records; 2,613 singleton cells excluded. Exact identity `profit=Value-Cost`, bounds `6≤Value≤16` and source SHA checked before calculating.

The slope is `Σ_cellΣ_i (V_i−mean V_cell)(Switch_i−mean Switch_cell) / Σ_cellΣ_i(V_i−mean V_cell)^2`. Within-stratum value permutation holds actual route, period, publicly observed occupancy and information flag constant. Conditional exchangeability is **assumed from the authors' design description**; original RNG assignment logs have not been independently audited.

## Main results: a decisive negative control prevents causal promotion

| Contrast of experimental Value at t | Slope per 1 Value point | Conditional randomization |
|---|---:|---:|
| Against **next** switch `1{Y_t+1 ≠ Y_t}` | **−0.0075536** | 2,999 draws, p≈**0.001** |
| Against **already decided** switch `1{Y_t ≠ Y_t−1}` | **−0.0064730** | 2,999 draws, p≈**0.002** |
| Matched `[next switch]−[already decided switch]` | **−0.0009435** | 4,999 draws, p≈**0.743** |

The matched contrast uses only 8,394 actor periods / 3,648 cells with both outcomes, and its session-resampled **exploratory** 95% interval is **[−0.006797,+0.005851]**. The negative-control result is an unexpectedly large association with a choice made **before** the contemporaneous random value could have been observed. This is **NOT proof of misconduct or broken experimental randomization**: finite-sample chance, conditioning, source processing, actor histories and the unknown RNG schedule require audit. But the positive-looking next-switch slope must **NOT** be published as causal payoff learning without resolving this warning. Subtracting the negative control is only a diagnostic, **not a causal difference-in-differences estimator**.

Information-stratified next-switch slope: uninformed −0.006061 (4,323 records) vs informed −0.009124 (4,296); no causal moderation claim. Across first/last 12 sessions, next-switch slopes −0.00543/−0.00962 and predecision placebo slopes −0.00375/−0.00913. Descriptive sample-wide `Value` mean 10.979, SD 2.878 and actor lag-1 correlation about −0.006; marginal resemblance to uniform iid does not validate conditional independence.

**Supported:** predictive R33/R34 payoff-history signals, a raw-data randomized-shock association, and a **failed predecision falsification gate**. **Not supported:** causal reinforcement learning, positive causal switching-cost effect, cognitive-hassle coefficient, policy optimality, randomized-IV interpretation or implementation instructions.

## Methodological and novelty gates for the laboratory

1. Inspect source original RNG generation/assignment timing and counterbalancing metadata; avoid concluding the Value draw was nonrandom based only on these diagnostics. Re-run alternative stratification and predecision placebos, then independently replicate.
2. Compare RITHM R33/R34 against the authors' own EWA-lite and Small Sample models with exactly matched online legal information and session folds; mere history-payoff prediction is not novel.
3. Keep full-population vs eligible-within-cell estimands distinct; discard any naive p-values from postselected models after repeated R23–R35 exploration.
4. Preserve **causal HOLD** separate from valid predictive improvements; avoid inferring actual social welfare changes from differences in predicted cost.

## Reproducibility

[Original-author canonical manuscript](https://drive.google.com/file/d/1rTL9qTpYV6zwee6pC3nZy64H07oSWzlK/view). [R35 aggregate results](P3_R35_RANDOM_VALUE_NEGATIVE_CONTROL_20261111.json). [R35 executable](p3/r35_value_randomization.py). [Source-free tests](p3/test_r35_value_randomization.py). SHA-verified local source rerun completed and six local unit checks passed. Public GitHub source implements the same estimand and falsification but the local detailed script and published compact source are **not represented as byte-identical**; clean GitHub checkout and remote CI remain HOLD. No individual actor rows released.

## 2026-11-11 late-source provenance audit: randomization-generation code is not in author R archive

Independently inspected the source ZIP `rererequestforpermissiontouseexperimentalroutechoi.zip`, including all six bundled `.R` analysis scripts. The files implement post-experiment data preparation, Part-I outcomes, Part-II information purchase, questionnaires and plotting/bootstrapping. The R scripts include `set.seed()` and resampling in *analysis code*, but **no located R code that generates/assigns the actor-period `Value` randomization itself**. Thus the author manuscript's independent Value assignment is documented as experiment design, and the available ZIP supplies realized Value data, but the **underlying experimental treatment RNG algorithm, seed/scheduling and assignment logs remain unavailable** in inspected sources. Do NOT misidentify analytical bootstrap seeds as randomized treatment assignment code or claim the randomization was disproved.

Observed source-wide Value mean about **10.9790**, standard deviation about **2.8785**, bound [6,16] and within-person lag-1 Value correlation about **−0.0062**: these marginal diagnostics are compatible with the manuscript's uniform iid description but do **not** repair the significant within-cell predecision placebo. The code/artifact is a conditional analysis requiring further source audit.
