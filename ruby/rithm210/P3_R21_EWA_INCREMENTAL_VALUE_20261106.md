# RITHM-2.10 P3-R21 — EWA-Style Cost Learning Added-Value Trial

Date: 2026-11-06 KST. **Original 24-session observational human-source exploratory scoring, NOT an original-author fitted EWA replication, a new causal trial or a paper-level result.**

## Question and method

Can experiential cost learning with truthful, available information about counterfactual route cost improve the six-person group-occupancy forecast beyond each actor's strictly prior within-section route-frequency baseline? We used the original author-approved source `data_task_all_switch_230705.csv`, SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`, 24 sessions × 3 information treatments = 5,760 six-actor group-period observations (1,920/treatment).

[R21 EWA group CV](p3/r21_ewa_group_cv.rb) uses two initial zero cost-attractions and EWA-like experiential updating. For each actor, the chosen route incurs the actual cost; the unchosen counterfactual route updates with weight δ **only when informed**; it is not disclosed to uninformed actors. For each six-actor group, all predictions are made before any actor's period-t outcome changes learning states. Group occupancy distribution is exactly the Poisson-binomial convolution of six independent predicted route probabilities. The EWA-style model grid is `phi∈{.5,.9}`, `rho∈{.5,1}`, `delta∈{0,.8}`, `beta∈{.3,.8,1.5}` (24 candidates). For every heldout fold of 4 independent sessions, parameters are chosen from other 20 sessions by mean session-aggregated negative log score, separately by treatment.

**EWA-only heldout equal-session-weight group occupancy logloss:** No-info **1.895852**, Partial **1.769731**, Full **1.711692**. This implementation is an EWA-*type* rival using experienced route congestion costs, NOT the full original EWA with its own unestimated choices or the exogenous person-specific `Value` part of `profit`. The sign and units of the underlying reward matter.

[R21 incremental mixture CV](p3/r21_ewa_incremental_cv.rb) evaluates `p_mix=w*p_EWA+(1-w)*p_own_frequency`, weights `w∈{0,.5,1}`, avoiding duplicated baseline; **49 candidates** total. Again, candidates selected on the 20 training sessions only, not heldout outcomes. Every one of the 6 folds in each of the 3 treatments selects **`w=0`, own-route history frequency only**.

| Treatment | Session-weighted group occupancy logloss | Brier | Absolute expected group-cost error | Selected |
| --- | ---: | ---: | ---: | --- |
| No info | 1.464643 | 0.735053 | 2.956477 | Baseline in all 6 folds |
| Partial | 1.432968 | 0.719123 | 2.938988 | Baseline in all 6 folds |
| Full | 1.456460 | 0.722887 | 3.094891 | Baseline in all 6 folds |

**Weighting boundary:** R20's pooled per-group scores gave own-frequency logloss ~1.45280/1.43441/1.44283 (No/Partial/Full). R21 averages **independent session means equally**: some session-treatment cells have 40 groups, others 80. The difference does NOT mean altered participant data, and no R20 score is directly presented as equally weighted R21.

## Error-driven correction, tests, preservation

An early mixture test shadowed the whole-group `n_a` occupancy variable with an actor's *historical* A-count. Original-source execution rejected impossible group occupancy; faulty result discarded. We renamed the actor count `prior_a`, reran the full source, and added a two-period six-person fixture verifying `w=0` reproduces prior-only own-frequency forecasts, along with invalid mixture weight and training-fold coverage tests.

- [EWA implementation](p3/r21_ewa_group_cv.rb) · [synthetic tests](p3/test_r21_ewa_group_cv.rb).
- [49-variant incremental CV](p3/r21_ewa_incremental_cv.rb) · [synthetic tests](p3/test_r21_ewa_incremental_cv.rb).
- Read-only `.github/workflows/rithm29-ruby-research.yml` includes the two new tests, no actor-level private rows on GitHub.
- Local Ruby3.3.8 **functionally equivalent** EWA and incremental CV on source CSV SHA passed, **8 tests / 24 assertions / 0 failures**, two full original-source scoring runs (24 and 49 variants). Final exact remote GitHub blob checked out and remote GitHub Actions PASS remain HOLD.

## Research decision

This is a **conditional negative benchmark**: the declared 24 cost-based EWA candidates with weights .5 or 1 fail to add cross-session predictive value to prior actor route frequency. It does NOT reject canonical EWA, SSM, or cognitive learning generally; there is model-choice reuse of the same 24 sessions, and a future validation dataset has not been used.

Next **R22**: recover closer-to-original EWA definition from the historical primary papers and author code, account for the person-specific value/utility and route costs, include transition inertia and full-q latent SSM; judge all models by same group occupancy, proper scores and finite-horizon welfare criteria. Do not plan new human recruitment.

**Original full Korean evidence report** preserved in [RITHM Drive dated file](https://drive.google.com/file/d/1VLKzf8I1wKQWrZ7-gMnHCesK8Ji0y3xb/view?usp=drivesdk) (7,496 bytes, authenticated downloaded SHA256 `6bcb7f6bcf2778162211701d3d38f9d41e54c5705838535e200258d4060db0ac` exactly matches source).
