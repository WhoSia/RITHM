# RITHM-2.6 P15 — Cross-Sensor Observation-Operator Identification & Temporal Phase-Regime Falsification

**2026-10-12 · Original 2025 Seoul data actively executed, but physical cause not identified. RITHM-2.6 OPEN.**

The source-specific research court, exact original-shard scripts, interval results, daily alarm results, both original user manifests, 2022 temporal negative control, classical kernel construction, and 15 tests are in reproducible conversation archive `RITHM-2.6_P15_Phase_Operator_Regime_Falsification_20261012.zip` SHA256 `cef6835756349338087a13eee10c0b4a6e4056a28ac315eb7e69f445d0c010bf`. The archive has **26 files and no 1.6GB raw source CSVs or 464MB derived memory snapshots**. [Author source 2025 Seoul data](https://data.seoul.go.kr/dataList/OA-22351/F/1/datasetView.do) · [actual original 38 Drive shards](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30).

### Genealogy and original measurements

Existing [P13-R3](rithm26_p13_r3_clock_parity_independent_replication_20261012.md) and independently authored C++ [P14](rithm26_p14_network_coherent_aliasing_20261012.md) already discovered the strong 10-minute parity anomaly, common traffic-network coherence, and Apr18/19 sign reversal. The P15 addition is a **16 ROUTE_ID-direction group** coupling quantification, same-group SPD/OCC negative controls, exactly matched within-pair sum analysis, retrospective daily alarm replay with antagonistic examples, and typed independent-instrument admissibility boundary. Never call this a newly proved universal theorem, source-causal alarm, or true measured driver welfare.

P15 rehashed all **38/38 extant UTF8 source shards** and matched sizes/row counts to both original manifests: H1 9,176,088+H2 9,244,619 = **18,420,707 real source observations**, 178 stable LINK_ID keys, 16 ROUTE_IDs for 8 named roads with two directions, zero duplicate link-date-5min observations. H1 and H2 route metadata correspond exactly. Deleted original CP949 bytes cannot be rehashed. Four completely absent source dates 2025-06-09, 07-10, 07-11, 07-15 remain SOURCE BLACKOUT not zero flow.

### Cross-corridor route-clock phase (all real source)

Define `D[l,k] = VOL[l,2k+1] - VOL[l,2k]` over each aligned ten-minute pair. Compute the 144-clock-slot signal mean across linked routes separately within each of 16 ROUTE_ID groups; compare the resulting 120 group-pair temporal Pearson correlations, and repeat with source speed. Source results:

| Source date | median group-pair q-phase corr | median group-pair speed-phase corr |
|---|---:|---:|
| Feb12 | 0.140 | 0.149 |
| Mar23 | 0.976 | 0.096 |
| Apr16 | 0.963 | 0.106 |
| Apr18 | **0.968** | 0.120 |
| Apr19 | **0.973** | 0.111 |
| Apr21 | 0.186 | 0.116 |

Apr18 **177/177** eligible per-link daily q phase positive, next Apr19 **171/177** negative; on Apr18 all **16/16** group directions show negative phase in 08–10h and positive phase at 11h, a rapid synchronized sign reversal that cannot be explained by one fixed source-link offset. This does NOT certify centrally programmed detector switching: correlated physical sources or common downstream reconstruction can make same output. Apr16–22 mean q lag5 MAE **57.583** vs lag10 **26.776** vehicles/bin while the adjacent ten-minute paired mean drift is 20.003 vehicles per 5-minute equivalent; these are distinct target operators, not an apples-to-apples welfare gain. The corresponding source speed lag5 is 2.795 km/h and q-speed first-difference source corr +0.0014.

### Classical exact observation-kernel nonidentification

For nonnegative 5min `y`, let `B(y)[k]=y[2k]+y[2k+1]`. Its kernel includes `(a,-a)` independently for each pair. Witness observed source `(315,557)` admits physical true `(315,557)` and m=0, **or** physically flat `(436,436)` with zero-sum measurement component `(-121,+121)`; BOTH produce the same five-minute source outputs and ten-minute total 872. This is a proof that even **independent correct ten-minute totals do not identify the origin of five-minute parity**, assuming additive zero-sum measurement perturbations permitted. The source itself does not validate the additive hypothesis. Proof-carrying pure code [kernel witness](../tools/traffic_sources/p15_phase_operator.py); [SHA shard integrity gate](../tools/traffic_sources/p15_source_manifest_gate.py).

An independent 5-minute source must measure the **same physical section, direction, timestamps and vehicles/event coverage** with separate acquisition/processing lineage and demonstrated calibration errors. New TOPIS independent-link event logs, authenticated raw lane detector, or independent co-located probe/optical count would qualify if verified. [TOPIS source descriptions](https://topis.seoul.go.kr/refRoom/openRefRoom_1.do) mention loop/video/DSRC feed to a single output system, which does NOT establish sensor independence of its SPD/OCC columns. [T-Data smart junction 5min](https://t-data.seoul.go.kr/dataprovide/trafficdataviewfile.do?data_id=20001) is a different geography and not co-registered here; [Yu et al. 2009](https://doi.org/10.3141/2099-06) and [Lee & Coifman 2012](https://doi.org/10.1016/j.trc.2012.02.005) are prior mechanisms, not an explanation of this Seoul anomaly.

### Regime alarm replay and negative controls

Use *only* Jan1–Feb28 59 dates to set 99th-percentile thresholds for three **ALREADY P13-motivated** characteristics: 16-direction q-parity temporal corr **0.374**, share links with smaller lag10 error **0.1573**, and median normalized adjacent source q-gap **0.09107**. All must exceed threshold. For **302 eligible source days** after February, flags **32**: March7, April13, May1, August3, September8, including previously undescribed 9/5–11 seven days. Source May21 has high synchronized absolute oscillation but lag10 better on only **1.13%** links, a negative counterexample to conflating general volatility with the period-two regime.

The schema is POST-HOC constructed with original 2025 P13/P14 exposure; 59-day calibration does not create a source-blind experiment. Final daily outcome available only when day ends; this is not an intraday detection latency test or a sensor-defect label. In 2022-08-01 same-publisher historical original 56,732 rows, lag5 source volume MAE **19.505** beats lag10 **22.470**, but this is NOT independent current-site 2025 physical validation. A naive 2000 route circular-shift placebo gives small reference p even in Feb ordinary source, so it **FAILS specificity** and is rejected for sensor-malfunction inference.

**Local source tests:** 14/14 scientific/contract tests plus separately run 1/1 38-original-shard SHA regression = **15/15** local PASS. GitHub documentation/[pure witness source](../tools/traffic_sources/p15_phase_operator.py)/[source gate](../tools/traffic_sources/p15_source_manifest_gate.py)/[4 synthetic unit tests](../tests/test_p15_phase_operator.py) committed `[skip ci]`, so **CI was NOT run**; the complete executed original parser and entire source-run numerical court remain in the separate ZIP.

**Verdict:** SOURCE HASH/ROW PASS · 16-DIRECTION SYNCHRONY OBSERVED · PHASE REVERSAL TRUE · FOUR SOURCE BLACKOUT DATES NOT ZERO · 2022 TEMPORAL CONTROL CONFIRMS NONUNIVERSALITY · 2025 POSTHOC WATCH 32 CANDIDATES BUT NO PROSPECTIVE CALIBRATION · COMMON SENSOR/PROCESSING CAUSE **NOT IDENTIFIED** · HUMAN REAL TRAVEL-TIME WELFARE **NOT IDENTIFIED** · ROUTE-GUIDANCE CAUSALITY **HOLD** · **RITHM-2.6 OPEN**.
