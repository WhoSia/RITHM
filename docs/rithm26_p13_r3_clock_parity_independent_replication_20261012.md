# RITHM-2.6 P13-R3 — Source-Legal Clock-Parity Mechanisms, Independent C++ Cross-Check, and Welfare Boundary

**2026-10-12 · RITHM-2.6 OPEN.** This is a separately executed Python forensic cross-check and date-level extension of [P13-R2b](rithm26_p13_r2b_weekly_rolling_crosscheck.md) and the independently posted [P14 C++ parity discovery](rithm26_p14_network_coherent_aliasing_20261012.md). **Do not call P14's already-existing finding a new P13 theorem.** All datasets are 2025 original Seoul urban expressway sensor sources, NOT individual people or group treatment experiments. Original [Seoul source license and schema](https://data.seoul.go.kr/dataList/OA-22351/F/1/datasetView.do); [38 real RITHM Drive CSV shards](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30).

## Executed full-shard source court

P13-R3 Python rehashed SHA-256 and row counts of 38 surviving UTF-8 CSV shards, parsed **18,420,707 true original observations**, **178 stable links**, four entirely missing source dates June9/July10/11/15. Deleted pre-transcoding CP949 originals CANNOT have their old hash reverified. All 41 original R2b accepted rolling 21-day-training / 7-day-test calendar weeks reconstructed, 8 blackout-intersecting 28-day candidates failed closed. For strict same observation cohort at 5/10/15/30/60/120-minute input lags, N **14,493,248** (not P13-R2b's 14,605,993 nor P14's 14,520,028, which have different target restrictions). Source predictive models are **observed-one-step teacher-forced**, not seven-day autonomous rollout.

| Input observation age (min) | Flow MAE vehicles/5min | Speed MAE km/h | q/speed proxy MAE |
|---:|---:|---:|---:|
| 5 | 21.084 | 2.677 | 0.579 |
| 10 | 21.709 | 3.591 | 0.711 |
| 15 | 25.455 | 4.316 | 0.879 |
| 30 | 30.700 | 6.019 | 1.208 |
| 60 | 40.746 | 7.987 | 1.618 |
| 120 | 60.129 | 11.000 | 2.263 |

Train-only per-link ridge-smoothed lag5/10 with beta clipped [-.5,.5]: **flow 18.904**, speed 2.663, q/v 0.554; untrained equal mean lag5+lag10 flow 18.986. This descriptive reanalysis is after repeated data inspection; no fresh prospective gain and no identity between differently masked populations.

## Period-two nonmonotone memory regimes: independent replication

Seven diagnostic 7-day source windows with fixed SAME target rows at each 5,10,15,...,40-minute delay. For Apr16–22, **354,194 matched sensor cells**, flow error for 5/10/15/20/25/30/35/40-minute lags = **57.173 / 26.607 / 57.668 / 33.555 / 59.117 / 38.835 / 61.114 / 42.559** vehicles/bin. The odd-lag-minus-even-lag group contrast = **+24.987**. The same contrast ordinary February **−2.391**, August **−2.339**, post-Apr23 **−2.534**. On Apr16 source link 5/10 lag preference is inverted for **177/178** links; volume contrasts reverse while **speed 5/10 error remains 2.786/3.648 km/h**. An explicit native source row of link LDO2000010 Apr16 08:00/05/10/15/20/25 has volumes **315,557,312,562,343,584** and speeds **75.94,73.13,68.78,71.26,76.33,72.86**.

**Source-day localization** (diagnostic threshold retrospectively chosen, not prospective): days where daily source flow MAE(5)/MAE(10)>1.20 form March22–27, April3–7, April9, April15–19. Apr19 ratio **3.540**; Apr18 **3.167**, with across-day carry of legitimate previous bins. The separate P14 within-day C++ result on Apr18 **3.175** is consistent under a different evaluation mask. Local median absolute within-day parity gap in the 4/16 week **5.535 vehicles/bin** versus 1.306 ordinary February; even/odd parity *daily RMS* exceeds 20 on **140/178** source links versus zero on ordinary February, April23, August or November. Signed means cancel when alternating bin phase flips during the week.

Five-minute differenced source volume-versus-speed observational correlation Apr16 week **+0.0013** versus Feb **−0.0868**, August **−0.1031**; source OCC differential correlation Apr16 **+0.170**. Both negative controls remain descriptive because source speed and occupancy aggregation are not independently certified. In March19 week the real test cohort prefers 10-minute flow on **158/178** links while only **3/178** link-specific 21-day-trained smoothing coefficients have learned the lower clip -0.5; by March26 week **155/178** coefficients clip, consistent with **predictor training-history adaptation lag**, not proven physical state onset causality. Train-versus-test pooled flow means change -11.52% in March19 week and -8.00% Apr16 week, +6.83% after Apr23. Aggregate shift alone does not explain period-two alternating loss.

## Competing source-world construction and welfare limit

Let observed volume `Y_(l,t)` and unverified physical true volume `Q_(l,t)` satisfy `Y=Q+M`. Physically periodic world `Q=Y; M=0` and measurement-alias world `Q=b_(l,t); M=Y-b` generate the *same* source Y, SPD, OCC unless an independent verified measurement model ties these quantities. This elementary observational equivalence is constructive, **not original universal theorem** and NOT proof of sensor defect or a physical 10-minute traffic-wave cause. The source `q/v` operational cost proxy has units vehicle-hours/km (per five-minute source bin) but is not actual individual travel time or counterfactual human welfare; link geometry, speed-averaging authority, repeated vehicle passages and exogenous VMS variation unavailable. Hence group welfare and intervention causal effect **NOT IDENTIFIED**.

## Reproduction and verification boundary

The **complete locally executed** original-data reingestion scripts, 360-day daily output, 41 weekly model outputs, source-derived link-week CSV, negative controls, exact mathematical tests, and SHA-256 manifest are in the accompanying conversation download `RITHM-2.6_P13-R3_LagParity_Independent_Source_Falsification_20261012.zip` (SHA256 `1ec4ce5c463077f61a1d13c3ca94fa7975ccd6153e1cf49acb5f759412e6ccd0`), with **11/11 local PASS**. GitHub's compact [aggregate consistency checker](../tools/traffic_sources/p13_r3_regime_crosscheck.py) independently validates the exported summaries; this smaller runner alone **does not** rehash the 38 raw shards. The source-level C++ P14 code also remains published alongside this court and should not be overwritten. No CI execution claimed: commit [skip ci]. No original 2025 source rows redistributed on GitHub.

**Verdict: source count period-two episodes and ordinary-memory failure TRUE / P14 independent concordance TRUE / adaptation to source changing state descriptive / specific detector mechanism HOLD / causal human traffic information effect HOLD / actual group welfare HOLD / RITHM 2.6 OPEN.**