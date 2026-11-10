# RITHM-2.10 · P3-R32 — Prior Route Preference vs Experience Learning

**2026-11-11 · Research stage: exploratory original-source replay, not causal inference or new independent confirmation.**

## 1. Motivation and audited source

R31 found that the payoff and personal switching-rate history from No/Full treatment segments **already finished before** the participant entered the Partial treatment improved forecasts. The result could arise from experience-driven learning, but could also be explained by an individual's relatively persistent preference for route A. R32 directly competes these mechanisms using the same source, group structure and heldout session folds. The 'stable trait' label is operational shorthand for earlier observed route-share behavior; it is **not** a psychometric, genetically given or time-invariant trait.

Original-author private CSV `data_task_all_switch_230705.csv` exact SHA-256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. Original paper-main cohort excludes sessions 2 and 101. Partial treatment in 24 sessions, 48 six-actor groups, 1,872 heldout group-periods and 11,232 individual heldout choices (39 periods per group). Across these groups, Partial is first, second or third Part-I treatment in exactly 16 groups each.

## 2. Model and strict information filtration

With a participant's **own** A-route selections in all No/Full segments with `section < Partial section` only, construct

`z_i = 2 × mean(previous A route choice) − 1`, constrained to [-1,1].

If Partial is first, there is no earlier treatment: set z_i=0, retaining both prior-No/prior-Full order indicators so this structural absence is not confused with a true observed 50/50 personal propensity. An indicator interaction with the fixed informed marker allows separate association for informed vs uninformed actors. Do not calculate z_i from any Partial response period, later treatment segment, current outcome or hidden occupancy data. Past total observations must equal 40 × number of earlier completed Part-I arms; reject deviations.

All candidates retain R30's legal previous own route and **previous actually received payoff**; *previous group occupancy only for informed*; prior group-count secrecy is enforced by source-free tests. Within each of the six original session-based folds, 20 sessions train and four score; all coefficients fit only training sessions using fixed L2 λ=.02 and group scores are averaged equally by session. Latent group shock τ is independently picked from {0,.2,.4,.6} using **training-session six-mask joint logloss only** and all three candidates selected τ=.2 in all six folds.

The three model families differ only in **pre-Partial summaries**: `experience` uses order indicators + previous mean payoff and previous switching rate (R31 benchmark); `preference` uses order indicators + prior route A share and interaction with informed; `both` uses all of these. As historical choices and payoffs covary, these are predictive *rival feature families*, not orthogonal interventions.

## 3. Exact source replay results (lower is better)

| Model | Actor logloss | Six-choice mask joint logloss (independent) | Joint logloss (selected latent τ) | 7-count logloss | Group cost MAE |
|---|---:|---:|---:|---:|---:|
| R31 experience | 0.562248311 | 3.373489863 | 3.368149404 | 1.415970004 | 2.945228832 |
| R32 prior route preference | **0.550642233** | **3.303853398** | **3.301046845** | 1.409787813 | 2.911179426 |
| R32 both | **0.550103232** | **3.300619391** | **3.297877891** | **1.409011842** | **2.903310898** |

**Important:** preference minus R31 experience was −0.01160608 actor logloss and **−0.06963647** independent six-choice logloss. The latter 24-session exploratory paired bootstrap interval is **[−0.10727689,−0.03564135]**, not independent hypothesis confirmation; the same original dataset has been reused across R23–R31.

Adding earlier mean payoff and switching rate to the prior preference model improves the independent six-choice logloss by only **−0.00323401** (exploratory session bootstrap interval **[−0.00554951,−0.00112055]**); it also improves group cost MAE by −0.007869. The strongly predictive route preference itself may be a product of earlier learning, so this pattern **does not disprove learning** and **does not identify a permanent individual trait**. Nor does a lower **predicted cost MAE** mean a causal decrease in observed social cost.

## 4. Negative control — break historical actor matching while preserving group and info strata

Randomly permute only the previous route-preference score among the three actors with the same information status *inside the same current Partial group*, leaving each actor's current choices, current payoff, treatment order, training/heldout fold, and historical payoff/switch-rate features unchanged.

| Permutation / actor route-share matching | Preference independent six-mask joint logloss | Both independent joint logloss |
|---|---:|---:|
| True identity mapping | **3.303853** | **3.300619** |
| Random reassignment seed 20261111 | 3.380308 | 3.372983 |
| Random reassignment seed 20261112 | 3.374361 | 3.367754 |
| Random reassignment seed 20261113 | 3.381262 | 3.374168 |

The advantage of historical preference is substantially impaired when its **individual identity linkage** is broken. These are **three post hoc illustrative negative controls, not a permutation p-value**. This is entirely consistent with longstanding individual heterogeneity, learned stable habits, rational response to earlier costs, and other unmeasured persistent factors; none can be causally separated by these features alone.

## 5. Validation, reproducibility and boundaries

- Private original source SHA check, 24-session / 48-group population, fixed 6-fold original-session holdout, 40-period earlier-segment count, six stable identities, and no post-Partial history in feature calculations.
- Source-free unit tests 8/8 PASS: exact R31 experience-model nesting, future/current outcome invariance, uninformed hidden occupancy noninterference, stand-alone trait feature independence from previous payoff summary, first-segment missing-history handling, invalid source SHA rejection, trait-domain guards.
- GitHub R31 exact original code SHA source checked against local ZIP. R32 GitHub Python code and tests were committed and **Git blob SHA exactly matches local source files**, after a trailing-newline normalization.
- Original per-person CSV and derived person-level traits **not published**. Public aggregates and source-free code/test ZIP only.
- **HOLD**: full independent checkout with all GitHub dependencies, remote CI PASS; repeated-experiment / randomized causal effect of information or cognition; independent external data replication; pre-registered inferential error rate; whether fixed preferences reflect personality or learning.
- Difference of predictive logloss is not evidence of lowered *observed realized congestion*, and a 24-session resampling interval is exploratory after a long adaptive research sequence.

## 6. Next scientific challenge

R33 should compare a **preference-only personal heterogeneity model** against a model where the same actor's preferences update through *past payoff prediction errors and disclosed congestion* over current Partial periods. The key falsification is **incremental prediction beyond the strong prior route-share baseline**, holding admissible information and session/actor fold boundaries. A latent parameter named 'hassle' needs either an explicit measurable time/effort signal or independently identifying assumptions; no such cost is observed in these data. To claim welfare implications, distinguish source-fixed outcome cost from model-expected cost and any real resource/computation cost.
