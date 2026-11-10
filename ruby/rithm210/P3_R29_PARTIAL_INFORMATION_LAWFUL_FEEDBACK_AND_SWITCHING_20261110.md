# RITHM-2.10 P3-R29 — Partial-Information Payoff Learning, Stable 3/3 Disclosure and Route Switching

**2026-11-10 · EXPLORATORY ORIGINAL-SOURCE PREDICTION + DESCRIPTIVE BEHAVIOR. NOT CAUSAL PSYCHOLOGICAL FRICTION.**

## Source authority and information filtration

[Original author manuscript §4.1](https://drive.google.com/file/d/1rTL9qTpYV6zwee6pC3nZy64H07oSWzlK/view) documents each Partial group of six as 3 informed and 3 uninformed, identities fixed during the 40-period segment, all users observe own payoff; only informed users observe group counts for the just-completed period. Experimental `Cost` and random `Value` in the analyst CSV are **not** treated as observed input to any uninformed agent, and `NumA` is only used for informed agents' previous-period feature. Original-author CSV SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb` verified.

Paper-restricted 24-session Partial trt2 source, excluding pilot session2 and session101: **48 six-person groups × 39 forecast periods = 1,872 groups, 11,232 person-period forecasts** (5,616 informed and 5,616 uninformed). Strictly 3/3 fixed informed status checked for every group-period. Sixfold 20-train/4-heldout session-outer CV, fixed ridge λ=.02. In every fold, select coefficients **on training sessions alone**. Individual Bernoulli model group forecasts are convolved under a benchmark conditional-independence assumption.

## Actual original-source predictive outcomes

| Model | All actor logloss | Informed logloss | Uninformed logloss | 7-count logloss | Congestion cost MAE |
|---|---:|---:|---:|---:|---:|
| Prior own route + informed status | .572075357 | .550562175 | .593588538 | 1.446233401 | 3.150084497 |
| Plus own prior realized payoff | .566032984 | .542146354 | .589919614 | 1.425195742 | 3.021611174 |
| Plus **permitted public prior occupancy for informed only** | **.563752746** | **.537540671** | .589964822 | **1.417192590** | **2.967388130** |

Incremental public-feature gain vs route+payoff: informed actor logloss difference **−.004605683**, uninformed actor logloss difference **+.000045208** (near zero), overall actor logloss **−.002280238**, group count logloss **−.008003152**, congestion cost MAE **−.054223044**. Resampled existing 24 sessions yield exploratory 95% bootstrap intervals for informed actor logloss [−.005926933,−.003432217], group-count logloss [−.009322426,−.006621280], and cost MAE [−.059317673,−.049277386]. These are **not independent confirmatory significance intervals**; the candidate family was designed after repeated exploration of the same human source. Changing the informed-only feature can slightly alter coefficients and predictions for uninformed subjects via joint model fitting, even though the unseen count is never included in their feature vector.

## Observed switches as a distinct outcome

Session-equal-weight raw choice changes `RouteA(t) != RouteA(t-1)`, no model needed:

| Periods | Informed switch rate | Uninformed switch rate |
|---|---:|---:|
| 2–10 | .297582305 | .288580247 |
| 11–30 | .259722222 | .299421296 |
| 31–40 | **.212731481** | **.309027778** |

Difference between subgroup late-minus-early rates **−.105298354** (−10.53 percentage points), exploratory session-bootstrap95 [−.160164609,−.053006687]. **Do not call this causal difference-in-differences**: treatment-order effects, interference between members of a congested group, and individual heterogeneity are not removed. This descriptive divergence and legally permitted predictive value jointly motivate, but cannot identify, the behavior friction → adjustment → social welfare mechanism.

## Artifacts and verification

- [Python original-source validator, lawful filtration and CV](p3/r29_partial_information_cv.py)
- [Descriptive observed-switch window evaluator](p3/r29_switching_did.py)
- [Source-free model tests](p3/test_r29_partial_information_cv.py) and [descriptive validation tests](p3/test_r29_switching_did.py)
- [Aggregate numeric source replay](P3_R29_PARTIAL_INFORMATION_PAYOFF_AND_SWITCHING_20261110.json) (**no individual rows**).
- [Drive complete research report](https://drive.google.com/file/d/1GrvAVD9r0ReG6Qu7aBjxrt_f4hezpfJ-/view), [source-free 7-member ZIP](https://drive.google.com/file/d/1HzX4qobR_cLOTSNBt7OgrfmYYS43LX7X/view); original ZIP SHA256 `94959a3bf1754275d34a405de7fb350cf34279bbec705fa5c2506cf542ae18c9` verified locally with internal 7-file SHA manifest.
- **Local 8/8 source-free tests PASS**, original source SHA and 24-session 3/3 fixed-identity census PASS; local numerical CV and descriptive bootstrap executed. GitHub remote Actions PASS and **clean checkout exact blob parity are HOLD** until independently re-executed.

## Novelty and next research gates

No novelty is claimed for providing an informed/uninformed logistic predictor, learning from payoff, group switching divergence, or asynchronous revision as concepts. Source literatures Horowitz (1984), Marden & Shamma (2012), Sandholm (2010) and original Noussair–Qiao analyses impose strong prior-art constraints. Potential incremental contribution would require: rigorously matched legal information filtration, within-session informed randomization interpreted with congestion-network interference, dynamic welfare and social cost identity, and a demonstrated competing behavioral friction mechanism.

**NEXT:** include informed/uninformed × early/middle/late effects in the *session-heldout* predictive model; adjust or stratify by actual Part1 treatment order; test R26 marginal-preserving group-shock correction to the Partial group forecast; use original-author Endogenous treatment's information-price questions only with verified actual exposure and choice. Do not turn observational switching into causal information effects or propose new human recruitment.
