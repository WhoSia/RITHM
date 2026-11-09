# RITHM-2.10 P3-R24 — Welfare Attribution from R23 Inertia Forecasts

**Date: 2026-11-09 KST.** Actual SHA-sealed original-source 24-session, 5,760 six-person group-period replay, 33 prior-only R23 training-fold candidates. **Exploratory and descriptive, not a dependency/causal discovery.**

## Actual result

Using the exact R23 six-fold session-heldout model selection (20 training sessions, 4 heldout), predict six binary route choices **before updating personal route histories**, then partition the one-period quadratic group welfare error against the independent Poisson-binomial forecast. Baseline is the same actor's Beta(1,1)-smoothed full-history route frequency. 24 sessions were already repeatedly used in R19–R23; same-data model development invalidates confirmatory significance claims.

For observed current A-route count n, actor forecasts p_i, residual e_i=y_i−p_i, μ=Σp_i:

`C(n)-E_ind[C(N)] = 6(μ−4)Σe_i + 3Σ(e_i²−p_i(1−p_i)) + 6Σ_(i<j)e_ie_j`.

Split the last term by whether the two actors occupied the **same route in the immediately preceding period** or opposite routes. First-period pairs have no legitimate previous route, hence remain separately *unclassified*. All 64 possible six-choice binary outcomes exhaustively verify the identity, as did every original-source group-period.

### R23 selected inertia − frequency baseline (24 equally weighted independent sessions)

| Treatment | Group logloss | Individual Brier | One-period cost MAE | Pair term: same old route | Pair term: different old route |
|---|---:|---:|---:|---:|---:|
| No information | −0.011170 | −0.008492 | +0.031104 | −0.082841 | +0.172477 |
| Partial | −0.006287 | −0.005846 | +0.018175 | −0.052258 | +0.128115 |
| Full | −0.010430 | −0.011811 | +0.006161 | −0.166388 | +0.338270 |

These pair changes are **algebraic changes induced by replacing the forecast p_i for the SAME observed outcomes**, not estimates of changing group covariance. At Full information: mean-position term −0.099158, diagonal term −0.110287, same-route pair −0.166388, cross-route pair +0.338270, sum −0.037562 for observed−predicted cost-error difference. Relative to frequency, the 24-session bootstrap95 for the Full cost MAE change is **[−0.024012,+0.035130]**: do not claim confident worsening of welfare forecast error.

### Epoch heterogeneity, Full information (group-weighted means)

| Period | Groups | logloss candidate−baseline | cost-MAE candidate−baseline |
|---|---:|---:|---:|
| 1–10 | 480 | −0.023996 | +0.023403 |
| 11–29 | 912 | −0.000432 | +0.023481 |
| 30–40 | 528 | −0.013288 | −0.047385 |

No causal information/epoch effect can be inferred from these endogenous histories.

## Exact negative control — independence DOES NOT imply zero residual pairs under model miscalibration

Six truly independent persons each choose A with probability .7, while the model predicts p_i=.5. Then E[e_i e_j]=.04 even though no pair dependence exists. Hence E[6Σ_(i<j)e_i e_j] = 6*C(6,2)*.04 = **3.6**. The actual 64-state probability-weighted enumeration verified 3.6 to numerical precision. A second synthetic control with correctly calibrated independent heterogeneous p gives mean pair term near zero; a common latent shock causes positive pair terms without necessarily representing conscious strategic interaction.

**Consequence:** Large same-route or opposite-route pair residuals cannot be interpreted as causal coordination before stringent individual probability calibration and latent common-shock negative controls.

## Source code and verification

- [R24 core attribution](p3/r24_welfare_attribution.py) and [exhaustive/negative-control tests](p3/test_r24_welfare_attribution.py).
- [R24 R23-source adapter and 24-session paired uncertainty](p3/r24_inertia_welfare_source.py) and [training-only/chronology tests](p3/test_r24_inertia_welfare_source.py).
- Read-only CI workflow invokes both synthetic test suites without original human participant data.
- **Local Python 3 source-equivalent independent implementation:** 5 tests/0 failures, actual SHA-sealed 5,760-source group replay in ~3.5 s. Original CSV remains private and is **not** committed. Published HEAD exact-byte replay and remote GitHub Actions PASS remain HOLD.
- [Full Korean 7,151-byte report on dated Google Drive](https://drive.google.com/file/d/1IjQv4t5vRisV867Qavz71z3fwnZjSVgt/view?usp=drivesdk); authenticated re-download SHA256 **`b92fec49cfccce5324bff71ce9acb6bdce11246d001cca11a9e23a8fa79b71a4`** matched original exactly. Aggregated source-free reproducer and results are also available as a user-visible ZIP attachment from this research turn.

**Next R25:** fit/calibrate actor-wise route-choice probabilities using other sessions only, compete with time-/route- and information-conditioned independent histories, and test whether residual pair structure survives calibration. Treat possible shared latent shocks and individual miscalibration as primary competing explanations; 40-period autonomous welfare and independent paper contribution remain separate HOLDs. No recruitment of new human participants.
