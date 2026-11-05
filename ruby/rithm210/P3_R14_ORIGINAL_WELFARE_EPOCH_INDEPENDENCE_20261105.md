# RITHM-2.10 P3-R14 — Original-Data Welfare Replay and a Stronger Independent Actor Challenger

2026-11-05 KST. **Original CSV SHA-verified; source-equivalent local Ruby executed; causal and publication novelty claims HOLD.**

## Source, target and replication
Original author-approved [Drive ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view) contains `data_task_all_switch_230705.csv`; independently computed SHA256: `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. Existing experiment filter gives 24 sessions, 5,616 six-player group transitions. Preexisting Full-information, current optimal A occupancy 4 target: early t1–10 N154, late t30–39 N257 (411 groups). Existing sixfold whole-session CV, hold out 4 sessions/train 20 per fold.

The P3-R13 [groupwise exact welfare-error decomposition](p3/group_residual_welfare.rb) was replayed with genuine original-source rows. Per-group exact identity was checked for three preexisting actor-independent candidate models at both epochs. Mean signed components (observed minus predicted next excess cost):

| Model epoch | Linear calibration | Individual second-moment | Same-route residual pairs | Opposite-route residual pairs | Total error |
| --- | ---: | ---: | ---: | ---: | ---: |
| Markov early | +.088801 | +.788209 | +.448763 | -.561450 | +.764322 |
| Markov late | -.027143 | -.609355 | +.185103 | -.471055 | -.922451 |
| Online20 early | -.058058 | +.459039 | +.385041 | -.249769 | +.536253 |
| Online20 late | -.172258 | -1.062145 | +.421683 | -.627378 | -1.440099 |
| Online80 early | +.064679 | +.669647 | +.421920 | -.461240 | +.695006 |
| Online80 late | +.008311 | -.923845 | +.256432 | -.506286 | -1.165388 |

These sum to each observed forecast residual. The diagonal terms are a prominent calibration failure for baseline actor forecasts, preventing a leap from aggregate discrepancy to strategic dependence.

## Fixed, training-only epoch adjustment of individually independent probabilities
Use existing P2-style early (1–10), middle (11–29) and late (30–39) epoch categories and alpha20 shrinkage, without test-session outcomes. At actor state x=(treatment, informed, own previous route, own observed cost), train from other sessions: `p_epoch=(successes_train(x,epoch)+20*p_base(x))/(count_train(x,epoch)+20)`. Couple six individual switches by conditional independence, NOT a fitted group interaction. The [Ruby source](p3/epoch_independent_welfare.rb) uses existing P2 actor Markov training and [P3-R13 identity](p3/group_residual_welfare.rb). This is **not** a source-independent confirmation or identified cognitive mechanism: epoch is an observational proxy, current n4 is selected and same original data has been explored repeatedly.

| Target | Actual next excess | Existing Markov forecast | Epoch-independent forecast | Actual gross | Existing Markov gross | Epoch-independent gross |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Full n4 early (N154) | 3.01948 | 2.25516 | 3.02549 | 1.35714 | .91128 | 1.32688 |
| Full n4 late (N257) | 1.33074 | 2.25319 | 1.58227 | .58366 | .91022 | .59486 |

For the epoch-independent model, early welfare error -.00601 decomposes as linear -.0067, diagonal +.0430, same-route +.2741, opposite-route -.3164. Late error -.25153 decomposes as linear -.0252, diagonal -.0189, same-route +.0958, opposite-route -.3032.

Individual switch Brier on selected groups improves (early .16793→.15927, late .09014→.08653), with improved mean switch calibration (early bias +.07431→+.00504, late -.05443→-.00187). None of these within-source differences establish independent predictive or causal superiority.

## Uncertainty and interpretation
20,000 complete-session bootstrap reweights source sessions; fitted sixfold models are held fixed (not refitted). Exploratory percentile 95% intervals of observed minus epoch-independent next excess: early -0.006 [-.535,+.720]; late -.252 [-.646,+.266]. The remaining **opposite-route pair** term late -.303 has interval [-.565,-.060], but this is one selected, unadjusted component from repeatedly studied data: marginal misspecification, shared states and selection into n4 are still alternatives. A residual covariance is not direct peer influence.

The conditional-forecast difference (epoch-independent minus Markov) early -.770, late +.671, with very narrow conditional resampling intervals, is mainly a change in the fixed predicted means given shared observed groups. Do not interpret those intervals as a prospective advantage or independent external validation.

## Evidence and custody
- [Full raw-byte-preserved analysis report on Google Drive](https://drive.google.com/file/d/1Z4AJpuWyAuyHh93Ob2XY-p19FH93EpjN/view?usp=drivesdk) (SHA256 `b739840b8d3b1002c6b6e0ba78a0d1392580542a96550e24f012024dc26294d4`, remote readback verified).
- Source-only synthetic [Ruby test](p3/test_epoch_independent_welfare.rb): 3 tests / 10 assertions locally passed; P3-R13 exact module 5 tests / 141 assertions, adapter 2 tests / 5 assertions.
- Human participant-level rows, source CSV and source-author PDF are NOT committed to GitHub. GitHub CI is source-free/read-only; final merged HEAD Actions PASS and exact checked-out-SHA replay remain unverified.
- Original experiment heldout folds protect each target session from training labels; but the modeling ideas/epoch definition were studied on the same historical dataset. Observational conditional differences are not randomized treatment effects.

## P3-R15 research decision
The immediate task is to test whether a strong, *within-training-data calibrated*, actor-independent history model can reproduce the remaining opposing-direction cancellation and cost distribution beyond the current stratum-epoch model, using leave-session-out forecasts with within-fold tuning and session-block uncertainty. A shared latent group shock and directed strategic response remain observationally equivalent in important cases; independent new source or randomized signal/update-clock interventions are required for causal discrimination. The scientific target remains micro-to-macro finite-horizon congestion welfare mechanisms rather than chasing a small logloss improvement.
