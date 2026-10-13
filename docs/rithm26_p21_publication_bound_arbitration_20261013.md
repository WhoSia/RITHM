# RITHM-2.6 P21 — Delay-Bound Link-Specific Forecast Arbitration and Nonuniform Welfare Authority

**2026-10-13 · RITHM-2.6 OPEN · scientific source-based replay, not prospective independent or live-provider-availability proof.**

## Source and historical discrepancy

The original surviving 38 2025 Seoul city CSV shards were rehashed and validated against owner manifests (9,176,088 first-half + 9,244,619 second-half **18,420,707 original five-minute source records**, 178 directed source links, 361 represented dates, 152 missing VOL). The deleted original CP949 whole-file bytes were NOT rehashed. Source author collection remains on [user's RITHM Drive](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30). P20 pasted user output reports 2,123,227 future bins; the current GitHub P20 canonical [original source code](../tools/traffic_sources/p20_latency_court.py) instead uses a STRICTER SAME-LAG MASK yielding **2,121,699**; P21 independently recreated exactly the P20 canonical N and fixed-mix values. The two masks/scores must not be mixed.

## Legal source clock & rolling calibration

All predictions use two complete native five-minute VOL readings per ten-minute source total. Only when *both* individual component readings are published can their sum be legally used. Current original file contains DATE_CD/HH5M_CD, no actual provider per-bin publication timestamps. For assumed publication delay Δ after ten-minute interval end, the earliest legal previous pair is j=1+ceil(Δ/10) bins back. Δ=0,5–10,15–20,30,40,50,60 minutes -> lag1,2,3,4,5,6,7. These are SOURCE SIMULATIONS, not measured actual release delays.

Per month and link, calendar baseline is fit on days1–14 (two observed preceding weekly cycles); days15–21 are the **only** arbitration/calibration outcomes. Compare calendar vs simple *fixed* source mixer 0.875 latest admitted pair + 0.125 preceding pair. Days1–21 recalibrate the calendar without touching the evaluation days22–28. Then freeze one per-link delay-specific choice; use previously observed test-day values only after that timestamp in a **one-step, teacher-forced** evaluation. The network-wide pooled-choice rival uses only validation data. The test-period oracle is illegal deployment and is reported only as a pointwise comparison of TWO model policies, not a tight global bound.

## Actual 2025 source results — 2,121,699 identical future bins, vehicles / ten-minute MAE

| Hypothetical delay | Required lag | Calendar | Fixed mixing | Validation network gate | **Validation link gate** | Test-oracle ILLEGAL |
|--|--:|--:|--:|--:|--:|--:|
| 0 | 1 | 66.649 | 34.249 | 34.249 | 34.249 | 34.247 |
| 5–10 | 2 | 66.649 | **44.955** | 44.955 | 45.957 | 43.192 |
| 15–20 | 3 | 66.649 | 53.927 | 55.378 | **52.653** | 47.542 |
| 30 | 4 | 66.649 | 61.715 | 58.842 | **55.887** | 50.411 |
| 40 | 5 | 66.649 | 68.998 | 60.298 | **58.128** | 52.683 |
| 50 | 6 | 66.649 | 75.721 | 62.232 | **60.165** | 54.307 |
| 60 | 7 | 66.649 | 82.417 | 64.157 | **61.849** | 55.705 |

Fixed mixing vs per-link gate improvements: 30min **5.828** (9.44%), 40min **10.870** (15.75%), 60min **20.568** (24.96%) vehicles/10min; at lag2 link gate instead LOSES 1.002. Link-gate failures survive even long delay: at lag4 March it LOSES to fixed mix by 24.68; at lag7 May link gate MAE 80.36 vs calendar 63.49, November 53.98 vs calendar 32.11. There is **NO month-uniform guarantee**.

Exploratory 20,000 resamples of twelve SOURCE months weighted by fixed month-bin totals give mix-minus-link gate 95% percentile ranges at lag4 **[-1.970,+12.864]**, lag5 **[+2.073,+19.245]**, lag7 **[+9.489,+31.526]** vehicles/10min. These do not establish prospective statistical significance because 2025 and the policy family have been repeatedly examined.

## Operational guarantee only under external clock authority

If an ACTUAL source published release upper bound D is independently certified, a policy using source pairs at lag j(D) or older is legal even when realized delay varies within [0,D]. The D=60 source conservative replay predicts MAE 61.849, but **neither a published official per-record release log nor a certified D=60 guarantee is currently held.** Merely setting `verified=True` in a toy authority validator is not evidence of actual certification. Polling first-observed timestamp is not the provider first-publication time, and two component five-minute readings must both be available. Without measured publication clock, no live information-access claim.

No independent physical sensor, true individual source trip time, human congestion welfare, or randomized advice-effect result. Same source P13–P20 means NOT new independent validation. Nested sigma-field/Bayes-information monotonicity is classical and does not grant every fixed predictor monotonic realized accuracy.

## Reproduction and next falsification

- [Portable GitHub P21 replay](../tools/traffic_sources/p21_trainval_switch.py) calls the existing source-SHA-verifying [P20 loader](../tools/traffic_sources/p20_latency_court.py). [Authority boundary](../tools/traffic_sources/p21_latency_authority.py) + [source-clock tests](../tests/test_p21_latency_authority.py), not run by GitHub Actions under `[skip ci]`.
- Full locally executed, independently SHA-checked 38-shard P21 replay with **25/25 offline contract tests**, 14,952 source link-month-lag diagnostic cells, source owner manifests, 2025 aggregate 12-month result and bootstrap JSON plus full Korean scientific report in user-chat ZIP `RITHM-2.6_P21_Latency_Bound_Conditional_Policy_and_Human_Welfare_HOLD_20261013.zip` verified SHA256 `7bab6187ae460e856c4b540259cc186712ea2d2d855627bc73e242c955de816a`. Original 1.6GB user shards are NOT in GitHub or this ZIP.
- The original-source work is reproducible from the 38 user-owned Drive shard files plus owner manifest copies; source clock/censoring must be tested before any real-time or policy conclusion. **Next actual task**: obtain independent measurement-end, provider-release and client-receipt timestamps or an externally certified release upper bound. No public-authority mail needed for these retrospective computations.

**VERDICT: 2025 SOURCE CHOICE-GATE EXPLORATORY PASS / ACTUAL RELEASE CLOCK UNKNOWN / SOME MONTHS GATE FAIL / LIVE DEPLOYMENT HOLD / REAL HUMAN WELFARE HOLD / RITHM-2.6 OPEN.**