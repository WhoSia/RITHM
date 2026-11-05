# RITHM-2.10 P3-R16B — Seven-Occupancy Original-Source Calibration and Session-Block Uncertainty

Date: 2026-11-05 KST. **Exploratory within-source original-data replay; causal and external-paper claim HOLD.**

## Scientific question and correction

P3-R14/R15 concentrated on 411 Full-information groups at current efficient A occupancy n=4, early (N154) / late (N257). The prior independent actor Markov failed strikingly there, and train-only epoch adjustment improved its calibration. **Does this result generalize across all seven n=0,...,6 and all information treatments?** A finding conditional on chosen optimal occupancy is not an unconditional statement about human learning or group interaction.

Using the [author-approved source ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view), extracted `data_task_all_switch_230705.csv` original SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`, 24 filtered sessions, 5,616 six-agent group transitions; treatments 1,2,3, each initial occupancy 0..6. Sorted-session modulo6 sixfold heldout; 20 other sessions train actor probability for each fold, with exact pre-existing P3-R14 state key (treatment, Informed, personal RouteA, personal Cost), alpha20 smoothing, separate early/middle/late training-only epoch counts. Both models make independent individual predictions. Scores: observed joint U,D logloss, next-occupancy logloss, exact quadratic next-period welfare, gross switching, no-switch and countervailing U=D>0 rates. Model score's analytical variance formula was checked against independent binomial convolution for every scored group.

## Results: entire dataset, not preselected n4

| Metric | Original actor Markov | Train-only epoch20 | Absolute change epoch-minus-baseline |
| --- | ---: | ---: | ---: |
| Joint U,D logloss (lower better) | 1.98098033 | 1.97693911 | -0.00404122 |
| Next A occupancy logloss | 1.39992439 | 1.39791527 | -0.00200912 |
| Predicted next excess cost | 3.31780047 | 3.31398210 | -0.00381838 |
| Actual next excess cost | 2.99519231 | 2.99519231 | 0 |
| Predicted gross switches | 1.58426956 | 1.58676327 | +0.00249371 |
| Observed gross switches | 1.58636040 | 1.58636040 | 0 |
| Predicted no-switch | 0.17136719 | 0.17427440 | +0.00290721 |
| Observed no-switch | 0.18856838 | 0.18856838 | 0 |

The epoch adjustment has only **marginal** aggregate improvements on this heterogeneous all-occupancy sample. It has NOT cured the full-sample next-cost bias, which remains actual-minus-predicted -0.31879 (versus -0.32261 baseline). The apparent successful calibration of the selected n4 group should not be extrapolated to all current occupancies.

By treatment and epoch (NOT conditioned on n=4), joint U,D logloss:
| Treatment, epoch | N | Markov | Epoch20 |
| --- | ---: | ---: | ---: |
| 1 early | 480 | 1.998 | 2.008 |
| 1 late | 480 | 2.004 | 2.014 |
| 2 early | 480 | 2.092 | 2.093 |
| 2 late | 480 | 1.952 | 1.957 |
| 3 early | 480 | 2.148 | 2.103 |
| 3 late | 480 | 1.666 | 1.633 |

This heterogeneity suggests the epoch effect is **not a treatment-invariant individual adaptation law**. Caveat: descriptive contrast, no causal intervention on elapsed time.

## Uncertainty: paired complete-session bootstrap

After fitting and scoring the original sixfold heldout data, block by each of 24 sessions. Reweight 24 complete sessions with replacement, 20,000 draws, seed20261105, preserving a paired epoch20-minus-Markov contrast; empty selected strata in draws are skipped. Do **not** refit model parameters inside resamples.

- Overall joint U,D logloss mean delta **-0.004041**, exploratory percentile95 **[-0.009515,+0.002062]**, includes zero.
- Overall next-occupancy logloss delta **-0.002009**, interval **[-0.005069,+0.001056]**, includes zero.
- Treatment3 early, *all n* joint logloss delta **-0.044793**, interval **[-0.081783,-0.009864]**.
- Treatment3 late, *all n* joint logloss delta **-0.032856**, interval **[-0.084863,+0.022232]**.

Do not equate treatment3/all-n N480 with the earlier treatment3/n4 N154 or N257; they are different targets. None is prospective independent validation after repeated within-source model exploration. These percentile intervals ignore refit uncertainty, hyperparameter search and repeated comparisons, and provide no causal effect of an epoch variable.

As a cross-check, the source-equivalent all-state code when restricted to the **original 411 selected groups** reproduced P3-R14's exact forecasts: early mean next excess Markov2.255158506 / epoch3.025488081, joint logloss Markov2.151070723 / epoch2.015504976; late mean next excess Markov2.253190220 / epoch1.582270624, joint loss Markov1.430521475 / epoch1.356559862.

## Independent source audit and necessary controls

[Qi et al. 2024 Part II](https://drive.google.com/file/d/1sC_O0U_T90IdUeHXA400sgQJn1mAl4ar/view) already proposes a route-dependent attraction/inertia independent-agent stochastic process and scores flow switching, one-step flow transitions and the equilibrium distribution. [Cantarella & Watling 2016](https://drive.google.com/file/d/1oFYvFMXekKqDcdgu6Om8vNEz1zfcaLBx/view) already investigates habit and memory in mean-process stability and warns that variance is not explained by mean alone. [Smith et al. 2014 publisher PDF in 00](https://drive.google.com/file/d/11o1ZPHaCSA2GY9ZDnOU_JgizfI1DKQcA/view) already analyzes multiple stochastic ergodic structures and long-term behavior. The exact synthetic finite-horizon witness in [R16A](P3_R16A_00_INTAKE_PRIOR_ART_AND_EXACT_WELFARE_20261105.md) is an implementation control, not new theory.

Do not call a model "strongest possible independent learning" until independently implementing and contrasting route-dependent attraction RDAB-SP, SSM1–9, EWA/experience-weighted learner and possibly flexible nonparametric models while obeying original information release. Independently calibrated mean improvement does not alone identify strategies, shared latent shocks or psychological learning.

## Source-code custody and execution limits

- [R16B all-occupancy 6fold Ruby](p3/all_state_epoch_cv.rb) relies on existing P2/R14 Ruby actor APIs; checks original SHA, 24 sessions, group coverage and next-occupancy invariants, and prints aggregates only.
- [R16B source-free tests](p3/test_all_state_epoch_cv.rb): all seven occupancies, convolution, cancellation, mismatch rejection.
- [R16B complete-session bootstrap](p3/all_state_session_bootstrap.rb) and [synthetic resampling tests](p3/test_all_state_session_bootstrap.rb).
- Local source-equivalent original-data Ruby implemented and executed for all 5,616 group observations; separately ran 20,000 session-block draws and checked 411-group P3-R14 parity. GitHub public Python/CSV participant-level content absent. **Exact final GitHub byte-identical checkout execution, remote Actions PASS, refit bootstrap and independent dataset are HOLD.**

## Research-manager gate

**R16B scientific verdict: aggregate time-stratum prediction advantage is weak and treatment-specific**. This is a valuable falsification of an overgeneralized reading of R14/R15, but an exploratory negative result by itself does not guarantee a publishable methodological paper.

Next R16C: implement and pre-register route-dependent attraction/inertia at the level of *available* individual signals, then compare with original SSM and EWA on all-occupancy one-step and genuinely forward-heldout finite-horizon trajectories. Avoid using current observed human costs to update hypothetical future simulations. R17 must target controlled information and adjustment clocks and characterize identification conditions beyond known day-to-day stochastic dynamics. **Micro information/learning -> temporal collective process -> welfare remains the objective.**
