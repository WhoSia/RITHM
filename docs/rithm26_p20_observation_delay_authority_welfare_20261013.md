# RITHM-2.6 P20 — Observation-Delay Robustness, Independent Sensor Authority & Welfare-Valid Control Boundaries

**2026-10-13 · RITHM-2.6 OPEN · ORIGINAL 2025 source scanned, but previous P13–P19 exposure means EXPLORATORY, not fresh experimental confirmation.**

## Source and exact new operation

Revalidated all **38/38 surviving original owner-authored UTF-8 CSV shard SHA256s and byte sizes**, parsed **18,420,707 original 5min Seoul urban-expressway source observations**, 178 real directed route/link identities, source missing VOL 152 and four entire absent 2025 dates (June 9, July 10/11/15); source absent is not zero. Original full CP949 CSVs were previously deleted; preserve the historical CP949 digests **without falsely rehashing those original bytes**. Author public [dataset](https://data.seoul.go.kr/dataList/OA-22351/F/1/datasetView.do) describes VOL, SPD, OCC and lists irregular FILE updates. It **does not certify measured per-bin publication latency**. Original shards remain [Drive](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30).

The previously existing [P19 court](rithm26_p19_train_only_phase_mixer_20261013.md) tested 2,136,298 real ten-minute source targets and found link-fitted α nearly tied a post-result simple 75:25 mixing rule. P20 instead fixes **one stricter common cohort of 2,121,699** complete target and up-to-8-prior ten-minute totals for EVERY new delay scenario. Therefore differences between P19 original MAEs and P20 zero-delay MAE are a MASK effect, not improved historical performance.

A published source ten-minute count T_k exists only if both original five-minute VOL bins exist, T_k=q_even+q_odd. For target [t,t+10), suppose historical T for a pair ending at e first becomes **available at e+Δ**. Then the most recent legitimate lag is **j=1+ceil(Δ/10)**. Δ is an ASSUMED post-interval reporting delay, not the actually measured release time. Train days1–21 of every 2025 month and evaluate future days22–28. The dynamic one-step forecast uses already past real observations updated during the evaluation week (teacher forcing), not an autonomous 7-day rollout.

## Actual same-target SOURCE forecasting, MAE vehicles / ten minutes

| Assume Δ minutes | Last available T lag | Last T MAE | Fixed .75 mix MAE | Source calendar MAE | Months mix better / 12 |
|---|---|---:|---:|---:|---:|
| 0 |1|34.566|**34.249**|66.649|12|
| 5–10 |2|45.216|**44.955**|66.649|10|
| 15–20 |3|54.178|**53.927**|66.649|6|
| 30 |4|61.925|**61.715**|66.649|4|
| 40 |5|69.202|68.998|**66.649**|4|
| 50 |6|75.885|75.721|**66.649**|4|
| 60 |7|82.514|82.417|**66.649**|3|

The source average crossover is between hypothesized Δ=30 and Δ=40; **NOT a certified operational SLA**. Already at Δ=30 only 4/12 months favor mixing over calendar. Exploratory 5,000 twelve-month block re-samples show mix/calendar relative gain at lag4 spans **−18.19% to +26.38%**, including zero. At lag1 it spans **+35.74% to +58.68%**. No claim of independent statistical significance from 2025 exposed same-sensor source.

## Classical information filtration and stronger falsification boundary

For delay Δ, let F_t^Δ be all source data whose observation intervals ended and were published by t. If Δ2≥Δ1, F_t^Δ2 ⊆ F_t^Δ1; **Bayes-optimal** loss under all F-measurable predictors cannot improve when information is removed. This inclusion does NOT imply monotonic realized MAE for a SPECIFIC lag/mixing predictor. If Δ is unknown, using a recently measured value permissible only at smaller Δ is an information leak. A worst-case-Δ predictor may be evaluated instead, but P20's grid-mean crossover is not a uniform-across-month certificate.

Source SPD and VOL were published together, so they do not furnish **independent calibrated physical flow measurements**. The earlier P15/P16 exact within-ten-minute alias model still admits distinct latent 5min processes consistent with the same SOURCE T. A serious independent instrument must verify aligned physical section, direction, lanes/vehicles, original timestamping and release clock, bounded calibration errors, and unrelated acquisition/processing lineage. A filled evidence checklist alone does not prove sensor independence.

**Sharp but strictly conditional speed heterogeneity witness:** for N cars traversing identical length L with fixed true individual speeds v_i∈[a,b] and independently certified exact arithmetic individual mean m, Jensen gives minimum ΣL/v_i = NL/m. Under these assumptions the sharp attainable maximum puts all but at most one speed at a or b to satisfy Σv_i=Nm. N=2, L=1km, a=40,b=80,m=60 yields **[2.00,2.25] vehicle-minutes**. Original Seoul SPD has NOT been certified as that individual arithmetic mean; no source individual-trip or welfare value is licensed by this conditional formula. Even an independently measured true driver-time total would not identify **causal guidance benefit** absent actual intervention/exogenous exposure and network interference analysis.

## Software/receipts

[Executed latency code](../tools/traffic_sources/p20_latency_court.py) rehashes original extant source shards and builds presence-aware 2025 day×link×5minute tensor before scoring. [Classical authority/bounds](../tools/traffic_sources/p20_conditional_authority.py) and [offline mathematical tests](../tests/test_p20_latency_authority.py) impose strict source information clock and deny inference without independent reference; local original-derived 18/18 mathematical and contract tests pass, GitHub Actions NOT RUN for [skip ci] authorship control. [Compact actual score JSON](data/rithm26_p20_latency_source_2025.json); full original per-link diagnostic and executable logs are in chat-local ZIP, not GitHub, and no 1.6GB raw sensor shard was copied into repo.

**P20 verdict:** Re-measured genuine 2025 SOURCE delay-sensitivity PASS / provider true per-record publication clock UNOBSERVED / physical count calibration NOT INDEPENDENT / individual human travel-time welfare NOT IDENTIFIED / guidance causal effect NOT ESTIMATED / RITHM-2.6 OPEN.
