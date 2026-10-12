# RITHM-2.6 P18 — Source-Clock-Legal, Ten-Minute Phase-Invariant Forecast Falsification

**2026-10-12 · source-exposed real 2025 Seoul urban expressway sensor data · RITHM-2.6 OPEN.** Extends the [P17 phase-invariant source aggregation and welfare limits](rithm26_p17_phase_robust_mesoscopic_externalities_20261012.md) and source forensic [P13-R3](rithm26_p13_r3_clock_parity_independent_replication_20261012.md). This does not newly discover the March–April alias/phase mechanism, nor a universal theorem, and does NOT identify actual human welfare.

## Original data status: verified without deleted full originals

User owns the complete [2025 38-shard Drive collection](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30) ([city official publication](https://data.seoul.go.kr/dataList/OA-22351/F/1/datasetView.do)). Exact extant original-owner shard manifests specify H1 19 CSVs 9,176,088 rows and H2 19 CSVs 9,244,619 rows; **18,420,707** genuine 5-minute observations. Every present shard's SHA256, byte count, header and record count actually matched its original manifest (**38/38 PASS**). Both now-deleted CP949 full originals' historical SHA256 are preserved only in those manifests and NOT currently independently recomputed. Re-reading all source dates confirms **361/365**, totally absent dates 2025-06-09 and July 10, 11, 15 (not zero traffic), 178 consistent directed route/link keys and no duplicate key within months. 152 volume readings and 52 occupancy readings blank: never substitute zero.

This source has been reviewed repeatedly in prior P13–P17; subsequent retrospective windows are **exploratory** despite legitimate time-ordered test-label separation.

## Paired source-clock experiment: same source target and same mask

On each calendar month separately, use source days **1–21** to learn `LINK_ID × weekday × ten-minute clock` source count medians (fallback train-only link/clock/link), evaluate days **22–28**, requiring 50% source data coverage for each link in both partitions. Maintain only complete *adjacent even/odd five-minute pairs* for each link/time; define `T(l,k)=q(l,2k)+q(l,2k+1)`. Conditional on **exact reported 10-minute count conservation**, any hypothetical `q0→q0+δ, q1→q1−δ` leaves T EXACTLY unchanged; `2×previous odd-five-minute q` changes by `−2δ`, so it is not phase-invariant. This is classical pair-sum algebra, not certified physical true flow when reporting itself may be biased.

Four genuine contemporaneously legal SOURCE predictions of the same **future 10-minute SOURCE count**: previous complete 10-minute pair total T(t−1); twice last five-minute count 2q(t−1,odd); average of previous two complete 10-minute totals; source calendar median. All lagged source values must be present in the exact previous bin, no gap carryforward, test samples observed only after prediction. This is **one-step teacher forcing updated every ten minutes**, NOT an autonomous seven-day simulator.

| Source 10-min count forecast | Full 12-month matched MAE, vehicles/10min ↓ |
|---|---:|
| Train-only day-of-week/time median | 67.649492 |
| 2 × actual previous 5min source count | 39.269881 |
| Average of previous two 10min source totals | 36.753975 |
| **Actual previous 10min source total** | **34.900208** |

Original completed source ten-minute pairs **9,196,409**; strict same-sample training/test/past court **2,136,298** source target cells. Previous full-ten-minute pair wins in **12/12** historical months against doubled last-five-minute, weighted relative MAE reduction **11.13%**. Retrospective March source week (22–28) has source MAE 54.062 vs 82.606 (**34.55%**); this source regime was previously identified and is not untouched discovery. All 12 monthly outcomes are explicitly serialized in [machine compact results](data/rithm26_p18_tenmin_full_2025.json).

## P13 annual five-minute evaluation cross-check (separate, non-comparable units/mask)

Another original-source P13 annual 21+7 repeated comparison, matched five-minute target **4,287,316** cells across 178 links for each month, pre-fixed `0.75 last5+0.25 source calendar median` blend. Annual source speed MAE train calendar **6.530573**, last true five-minute **2.685996**, blend **3.017525** km/h. Flow count MAE **36.966124**, **21.993460**, **21.882413** vehicles/5min respectively; q/SPD operational proxy MAE **1.357814**, **0.604463**, **0.693474**. Last5 beats calendar for count, speed, proxy in **12/12** months; blend is worse for speed **12/12**, slightly better for count in **9/12**. Do not compare five-minute MAEs numerically with ten-minute targets. This P13 retrospective analysis is one of several different masks from already-exposed prior P13/P14/R3 analyses, not a replacement for those original authors' stronger weekwise findings.

## Measurement and welfare boundary

City VOL/SPD/OCC are not independently certified physical flow/density/speed signals. Exact 10-minute pair sums are phase-robust ONLY within the stipulated zero-sum within-pair operator nullspace; they are not correct if the reporting system biases ten-minute totals. `VOL/SPD` is a source-conditional vehicle-hour/km **proxy** per 5-minute counted interval, not a direct sum of individual drivers' actual travel times or policy social welfare. There is no actual intervention, individual driver trajectory, independent calibrated five-minute detector, VMS exposure, capacity/route topology evidence or causal route-choice habit in this dataset. Adjacent source links reuse same vehicles; 2M observations are NOT 2M independent experiment subjects.

## Reproducibility; no huge raw duplicate

- Complete actually executed P13 full-year Python + P18 10-minute Python + exact owner manifests + observed 38/38 SHA checks + source full-year calendar audit + all monthly machine outputs + P13 9 tests/P18 7 tests + full scientific 8.7KB court are in the conversation ZIP `RITHM-2.6_P13_Annual_P18_PhaseInvariant_RealSource_Court_20261012.zip` SHA256 `342c4f76b0976e02eadffb80d48c79cabf99086416812729333056126e5cffc1`; **16/16 local PASS**. No 1.6GB source shards in the zip.
- The repo's [portable source-ten-minute runner](../tools/traffic_sources/p18_tenmin_source_forecast.py) and [new mathematical/source tests](../tests/test_p18_tenmin_source_forecast.py) were posted after original executable source run. First verify 38 original shards using [P15 SHA gate](../tools/traffic_sources/p15_source_manifest_gate.py), then pass local shard directory and H1/H2 manifest paths on command line. No CI execution claimed for these [skip ci] commits. Machine summary is [here](data/rithm26_p18_tenmin_full_2025.json). Do not commit the original 1.6GB CSVs.
- A claim that new independent real 5-minute calibration, a prospective 2026 sample, or real human guidance welfare was validated is strictly forbidden by current evidence.

**P18 VERDICT:** existing P17 algebra ACCEPTED; true 2025 38-shard read/sha PASS; real 10min count-pair empirical one-step forecast PASS; competing doubled-5min benchmark DEFEATED 12/12; source phase cause HOLD; correct physical latent flow HOLD; road-level actual driver welfare and guidance causal effect HOLD; RITHM-2.6 OPEN.

**Next potential P18-R2:** acquire a *genuinely independent co-located five-minute measurement with calibrated timing* or a truly prospective source window. Only then distinguish physical traffic phase from publisher aggregation and consider robust traffic actuation certificates.
