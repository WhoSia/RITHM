# RITHM-2.6 P19 — Train-Only Phase-Invariant 10-Minute Mixer, with the Fixed-Baseline Adversarial Check

**2026-10-13 · real 2025 Seoul source · already exposed in P13–P18 · RITHM-2.6 OPEN.**

## Scientific ancestry and no-repeat rule

The existing [P18 original 10-minute source forecast](rithm26_p18_tenminute_phase_invariant_forecast_20261012.md) had ALREADY verified all 38 uploader shards and reported 18,420,707 actual five-minute readings, 178 link IDs, 361/365 observed days and four full-source missing days. P13's annual five-minute last-observation and P18 10-minute last-total forecasts already existed in `main` when this new P19 court began. Do NOT present this as new independent source discovery or a novel 10-minute conservation theorem. The present additional test is whether an additional LINK-specific trained weight improves the fixed-parameter source-phase-invariant P18 benchmark.

## Identical observed target and time

For each 2025 month, source days 1–21 train; days 22–28 are the future source test. Form original paired ten-minute sensor count T=q_even+q_odd only when BOTH constituent five-minute rows genuinely exist, have nonnegative observed VOL and share a native LINK_ID; source missing is NA not zero. Models use only source observations strictly prior to the current target. The new per-link training-only mixing weight α∈{0,.25,.5,.75,1} minimizes TRAINING MAE of α T(t−1) +(1−α)[T(t−1)+T(t−2)]/2. For full transparency compare unfitted fixed α=.75, fixed α=.5, original P18 last10, last20mean, twice-last-odd-five-minute and training-only calendar. Same 2,136,298 complete ten-minute source test targets /178 real link IDs /12 monthly windows for EVERY rival.

| Prediction target: source TEN-MINUTE vehicle count | Matched MAE vehicles/10min |
|---|---:|
| Train-only weekday/time calendar | 67.649492 |
| 2 × previous observed odd-five-minute bin | 39.269881 |
| Previous two 10-minute source totals mean | 36.753976 |
| **P18 previous observed 10-minute total** | **34.900209** |
| Fixed α=.5 mixer | 34.785166 |
| **Fixed α=.75 mixer** | **34.560137** |
| Link-wise train-only five-point grid alpha | **34.517763** |

The added training freedom gains **0.382445 vehicles/10min (1.096%)** over P18 last10, but just **0.042373 vehicles/10min (0.123%)** over fixed .75. Adaptive beats last10 in all 12 retrospective monthly windows but beats fixed .75 only in **10/12**: March and April reverse. Historical training chose alpha 0.75 for **1,087/2,136** source link-months, alpha 0.5 for 572, alpha 1 for 467, 0.25 for 9 and 0 for 1; no uniqueness or causal state-change identified. Among 2,136 link-months adaptive beats last10 1,453, loses 215, ties 468.

Exploratory month-block bootstrap (5,000 resamples of 12 repeated months) gives a relative improvement range **0.680%–1.564% versus P18 last10**, and **−0.143%–0.315% versus simple fixed .75**, the latter including zero. Same links recur throughout the year. This is **not confirmatory statistical significance, nor a newly untouched source test**; 2025 source and its period-two anomaly were previously inspected.

## Phase invariance and human-welfare impossibility

For a stipulated unchanged source T=q0+q1, arbitrary within-pair transfer (q0+δ,q1−δ) leaves T invariant, so forecasting entirely from preceding complete T history is algebraically invariant to that SOURCE nuisance. The double-last5 rival is not invariant. This conditional property does not certify actual latent physical count if the published 10-minute total is biased. City VOL/SPD/OCC may share an unresolved observation operator; no original calibrated independent sensor, actual driver trajectories, measured individual travel times, route-choice interventions or VMS treatment. The 2025 10-minute forecast is a SENSOR forecast, not an effect of motorist information, not physical welfare and not a justification for traffic control.

## Reproduce and governance

[Portable P19 source](../tools/traffic_sources/p19_train_only_phase_mixer.py) reads the genuine local P13 presence-aware `native.f4` tensor and census constructed from the two authenticated manifests; local original-ingestion script + 14 original-source P13 checks and P19 14 adversarial tests are in current conversation deliverables. Read both [manifests and 38 shards in Google Drive](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30); **do not commit 1.6GB original source or reconstruct a false CP949 hash**. [Small actual source results](data/rithm26_p19_mixer_real_2025.json). The P19 SOURCE engine is local-tested on all 2025 original data; new committed portable wrapper and offline tests must not be labeled Actions-verified because commit uses `[skip ci]`.

**P19 conclusion:** Train-only adaptive mixing beats original ten-minute persistence modestly, but the simple fixed .75 mixer nearly fully explains improvement; the *extra* per-link fitting freedom has no stable 12-month bootstrap gain over fixed .75. Cross-experiment physical sensor calibration and actual human welfare remain HOLD; RITHM-2.6 OPEN.