# RITHM-2.6 P5 — Restricted Stable-Preference Rival, State Dependence and Joint Traffic Welfare

**Date:** 2026-10-10. **Verdict:** P5 source-based exploratory human prediction + exactly verified original group-cost algebra; RITHM-2.6 OPEN / causal habit HOLD / policy effect HOLD / novelty HOLD.

**Source:** [Wijayaratna et al. 2017](https://doi.org/10.1371/journal.pone.0184191); [six-session original participant S2 workbook](https://docs.google.com/spreadsheets/d/1Kv-fWLa6kP_tv9PpgNDUYIV3oiC-zmRc/edit); SHA-256 for original XLSX: f2047f7c2ae8999a9f0660f3b5c192aea171b715284bf2aa05b40c10b902d863. [P1–P5 canonical Notion scientific receipt](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021). No raw personal records are reproduced in GitHub. Six real experimental sessions, 12 actual groups of 12, each participant both info treatments of 20 rounds, 5,760 final choices and 480 group-rounds. Exactly 4 incidents in each group-treatment sequence; always stratify past/current incident information by original A/C node time.

## Part A — constrained predictive test against stable revealed individual propensity

**NOT a Heckman/Wooldridge dynamic panel causal estimator.** Six complete-session heldout test folds. Within each treatment and participant, define online empirical-Bayes smoothed Bernoulli propensity with prior equivalent sample size 6; training sessions alone provide the population prior. For the node-C choice, current shock may enter a reference-odds shift only in the information arm once A–C has been chosen. The last-action model adjusts log-odds by delta times (last eligible binary choice minus current individual posterior mean). Delta chosen only on FIVE training sessions from grid −2 to +2 in increments .05, evaluated on the sixth session with prior choices observed one-step-ahead; original 20 rounds as recorded.

| Restricted rival | A-stage heldout binary log loss (n=5,760) | C-stage conditional heldout binary log loss (n=3,511) |
|:--|--:|--:|
| Pooled source-context prior (no named history) | .666742 | .560769 |
| **Personal stable-propensity posterior, no last action** | **.626045** | .519175 |
| **Stable propensity + last eligible binary action** | .626267 (worse) | **.513161 (better)** |

The last-action term improved 4/6 folds in each stage but worsened the pooled upstream mean; training-selected deltas A=.10,.20,.15,.25,.10,.10 versus C=.55,.70,.60,.70,.70,.65. Stage C entrant-only histories have a changing eligibility window; “last” is last ACTUALLY OBSERVED C-stage decision, not necessarily t−1. The person propensity is itself an endogenous history summary and must NOT be renamed a fixed innate type. Test unobserved heterogeneity and endogenous initial conditions explicitly before any causal state dependence claim. [Wooldridge 2005](https://doi.org/10.1002/jae.770) directly addresses the standard dynamic nonlinear panel initial-conditions issue.

## Part B — original exact quadratic traffic welfare identity

Let X=#A–B–D and Y=#A–B–D or A–C–B–D, so at current incident Z=z, the source group cost is

    C(X,Y,z) = 264 + X² + Y² − (15+19z)X + (−9+19z)Y.

At constant z and for any joint distribution of all 12 named driver choices, exact equality:

    E(C|z) = C(EX,EY,z) + SUM_i [Var(U_i) + Var(V_i)]
             + 2 SUM_{i<j} [Cov(U_i,U_j) + Cov(V_i,V_j)],

where U_i=1{person i uses ABD}, V_i=1{person i does not use ACD}. This is a classical identity, not a new general theorem.

**Concrete attained nonidentification:** each of twelve individuals has P(ABD)=P(ACD)=1/2 and P(ACBD)=0; then E C=192+2 Var(X). Synchronous exactly-6/6 anticoupling yields **192**; individual independence yields **198**; all-ABD or all-ACD perfect coupling yields **264**. Same person-level marginals, sharply different group welfare, attained finite couplings.

## Part C — S2 observed covariance composition

Across 12 groups ×2 regimes×2 z strata = 48 source cells, each normal-traffic stratum has 16 rounds and incident stratum has 4, preserving actual group identities. For each cell reconstruct exact joint occupation on each round, personal empirical Bernoulli propensities across the fixed-z rounds, individual Bernoulli variance, and group joint variance. Compute pairwise covariance contribution as group variance minus sum individual variances. Exactly checked E C = C(EX,EY,z)+variance for all 48 cells, ZERO residual.

| Average paper-defined group cost component | BLIND | INFO | INFO−BLIND |
|:--|--:|--:|--:|
| C at conditional mean route counts | 207.500521 | 215.720052 | +8.219531 |
| Sum of single-person Bernoulli variances | +4.463021 | +3.843490 | −0.619531 |
| **Pairwise cross-person covariance correction** | **−1.334375** | **−0.401042** | **+0.933333** |
| **Observed average group cost** | **210.629167** | **219.162500** | **+8.533333** |

This 0.933333 contrast is 10.9375% of the published aggregate cost difference IN A PURELY DESCRIPTIVE DECOMPOSITION. Both individual arm-level covariance corrections are negative. Across six independent sessions, paired covariance differences are .584375, 1.63125, 1.45625, 2.015625, −.675 and .5875. Mean .933333; an illustrative t(5)-based interval approximately [−.091,1.957] includes zero. Two groups in a single session are not independent sessions. Original six prior S2 raw Cost inconsistencies are preserved separately; this analysis uses the PAPER'S route-count-generated group C.

## Part D — exact-margin-preserving temporal-order rival (Monte Carlo diagnostics ONLY)

Use each source group-treatment 12×20 binary upstream A–C matrix (24 panels). Each swap of a 2×2 rectangle of entries [1,0;0,1] to [0,1;1,0] preserves EACH PERSON'S total number of A–C choices and EACH ROUND'S actual A–C occupancy. Test S=sum_{person,t>1} 1{upstream binary choice at t equals t−1}.

| Regime | Observed S | Null mean seed 18342 | Null mean seed 9431 |
|:--|--:|--:|--:|
| BLIND | 1,626 | 1,597.81 | 1,598.86 |
| INFO | 1,696 | 1,657.42 | 1,658.70 |

First run each of 24 panels: burn 30,000 attempted swaps, 350 draws separated 650 attempted swaps; BLIND upper-tail .120, INFO .020. Second run: burn 90,000 attempts, 400 draws every 1,250 attempts; BLIND upper-tail .102, INFO .042. Samples are MCMC dependent, exact uniform fixed-margin mixing and formal inferential validity NOT certified. No real-world intervention, not a causal estimate of habit. Need independent exact or certified sampler for valid tests; also test eligibility-limited node-C transition order and person-level endogenous initial conditions. Conditional person×period margins control observed personal frequencies and common occupancy trajectory but do not block latent time-varying individual drivers.

## P5 limitations and P6 target

1. Stable beta propensity vs dynamic last-action are deliberately TWO RESTRICTED RIVALS; predictive superiority alone cannot prove a causal state transition coefficient. Need initial-conditions-corrected dynamic logit/probit/fixed-effects or alternative risk, with actual experimental conditional information clock.
2. Within-group covariance is descriptively measured, but positive INFO−BLIND cross-person correction is not an information-causality claim; 4 incident observations per group leaves very wide uncertainty.
3. Existing P3/P4 forecasts assume group-independent driver responses, and C response among hypothetical A–B entrants is unobserved. P6 should add an explicitly joint-choice/group random effect and compare **held-out session-level welfare**, ideally with reference shocks known only at legal information time.
4. Preserve all negative controls, 2.2 micro prediction versus group-welfare failure, prior S02.6 phase predictor defeat, and 2.5 synthetic memory-necessity counterexample.

**GitHub artifact is documentation of current verified arithmetic and scripts run in the in-conversation computing environment.** No untested Python script has been added to the repository. Original XLSX source remains in Drive; this commit intentionally requests no CI via [skip ci].
