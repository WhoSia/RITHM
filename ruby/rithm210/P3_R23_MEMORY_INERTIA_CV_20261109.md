# RITHM-2.10 P3-R23 — Memory Decay, Actor Inertia and Group Welfare Forecasts

**2026-11-09 KST · Exploratory real original-source research unit.** [Complete Korean dated research record, SHA-sealed Google Drive original](https://drive.google.com/file/d/1KEUeDpZ8V1jbJZdpL-PULDSqtOYvWYOl/view). Authenticated re-download and local original both **8,621 bytes, SHA256 `42afb5f0c18c73639e5d550800f423787ec7bd22e683baed6cbc033f56960c1a`**. Original participant rows not committed.

## Problem, data and model

Earlier R21's 24 EWA-like candidates and R22's q≤9 limited SSM did not outperform each actor's Beta(1,1)-smoothed own-route history frequency on six-person group occupancy logloss. R23 tests whether a *finite-decay memory estimate* and a *direction-specific transition propensity* add independent predictive value, while preserving strictly prior-only observations.

- Original SHA-256 approved source `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. Verified 24 independent sessions, 3 information treatments × 1,920 group-period observations = **5,760 six-actor groups**.
- Decayed actor choice counts `a_t=d a_(t−1)+y_t`, `b_t=d b_(t−1)+(1−y_t)`, `p_freq=(a+1)/(a+b+2)`, decay d∈{.5,.8,1}. The nondecayed d=1 reproduces the R20/R21 baseline.
- Direction-specific Markov switch propensity using actor's previous route and historical switches from that route: `p_switch=(switches+1)/(opportunities+strength)`, strength∈{2,5,12}. `p_A=1−p_switch` if previously A, otherwise `p_switch`. At the first round it is .5.
- Blended actor probability `p_A=(1−w)*p_freq+w*p_markov`, w∈{0,.25,.5,.75,1}. Deduplicate pure baselines to obtain **33 distinct candidate configurations**. No payoff, information condition or future outcomes enter actor predictions; these omissions are deliberate to isolate memory/inertia.
- All six actor forecasts computed BEFORE any period-t outcome updates the actor histories; Poisson-binomial convolution supplies all seven possible next occupancies. Actor conditional independence is a model assumption, not a causal discovery.
- Six folds, 20 training and four heldout whole sessions per fold; parameter choice minimizes **session-equal-weight** group occupancy logloss on training sessions only. Twenty-four-session paired whole-cluster resampling 4,000 times supplies purely exploratory intervals. Repeated inspection of these exact same 24 sessions precludes independent-confirmatory significance claims.

## Original-data result (24 equally weighted sessions within each treatment)

| Treatment | Frequency baseline logloss | Selected memory-inertia logloss | Candidate−baseline | Exploratory bootstrap95 |
|---|---:|---:|---:|---|
| No information | 1.464643 | **1.453473** | **−0.011170** | [−0.021358,−0.001131] |
| Partial information | 1.432968 | **1.426681** | **−0.006287** | [−0.011819,−0.001195] |
| Full information | 1.456460 | **1.446030** | **−0.010430** | [−0.019182,−0.001606] |

Among **all 18 fold-specific selections**, memory decay d=1 won; all chose Markov inertia at mixing weight .25 or .5. No-info: κ5,w.25 in 1 fold; κ5,w.5 in 4; κ12,w.25 in 1. Partial: κ5,w.25 in 6. Full: κ5,w.25 in 2; κ5,w.5 in 4. This is evidence of *incremental one-period group prediction*, not evidence that humans maintain an infinite or perfect cognitive memory.

Mean group Brier changes (candidate−baseline): **−0.003885**, **−0.001506**, **−0.006013** (No/Partial/Full). But expected **one-period total congestion-cost absolute error worsens** by +0.031104,+0.018175,+0.006161 respectively. Thus a better group occupancy distribution does not imply a better point prediction of non-linear welfare C(n)=24+3(n−4)², much less 40-round autonomous welfare.

## Epoch diagnostic without reselecting on the test epoch

Define early periods1–10, middle11–29, late30–40. Choose the model once on the **other 20 training sessions across all periods**, then score the heldout session by epoch. Candidate-minus-frequency logloss:

| Treatment | Early | Middle | Late |
|---|---:|---:|---:|
| No information | +0.006599 | −0.015759 | −0.019398 |
| Partial | −0.007564 | −0.008970 | −0.000492 |
| Full | −0.026762 | −0.001067 | −0.011754 |

The sign reversal in No-information treatment's early epoch and strongly time-varying Full improvement are descriptive; composition, endogenous adaptation and selection on source could generate them without causal inertia mechanisms.

## Code, verification and MCP

Source-free tested GitHub modules:
- [Ruby actor state](p3/r23_actor_memory.rb), [Ruby six-group/6fold source adapter](p3/r23_group_memory_cv.rb), [fold-selection contamination probe](p3/test_r23_group_folds.rb) and accompanying two other Ruby test suites.
- [Python independently implemented exact-law model](p3/r23_inertia_memory_cv.py), [Python time-stratified diagnostic](p3/r23_epoch_effects.py) and two test suites.
- Read-only CI updated for **3 Ruby test suites and 2 Python test suites**, with no original human CSV in CI.

Local independent Ruby3.3.8: **8 tests / 63 assertions / 0 failures**. Local Python3: **7 tests / 0 failures**. Original human-data execution in Python about 2.47s / ~140MB RSS, in Ruby about 4.80s / ~126MB RSS. **Treatment-specific heldout logloss, Brier, cost absolute-error deltas and all 18 selected fold configurations matched independently between Ruby and Python to 1e−10.** Local Ruby's source-free `R20GroupBridge.score` stub matched its published quadratic-score algorithm; exact final checked-out GitHub SHA test and remote Actions PASS still separately HOLD.

Connected MCP-Hub tools **actually invoked**: reviewed Ponytail/Superpowers TDD metadata discovery and offline public unified-diff inspection. These do not install/run the private Ponytail agent or verify code semantics. Core code was verified by direct synthetic/unit tests and independent full-source replay rather than treating MCP output as a pass.

## Research significance, R24 direction

This is the first recent R21–R23 candidate family whose predeclared within-session actor state offers modest extra group-logscore value beyond choice frequency. Yet it trades away slight one-period expected-cost accuracy and its value varies by epoch. Next R24 must decompose *direction-specific probability calibration* and *aggregate joint-transition residual* while preserving persistent actor composition; identify whether the improvement survives competition with richer information-conditioned learning or a correctly specified time-varying independent model. A source-reused CV score is not an independent research paper theorem or cognitive causal identification. No new human recruitment.
