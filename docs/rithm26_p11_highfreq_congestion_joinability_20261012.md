# RITHM-2.6 P11 — High-Frequency Congestion-State Reconstruction, Directional Detector Identity and Welfare-Joinability Falsification

**2026-10-12 · Source-bound mathematical/methods court · No real new high-frequency speed/flow sample has been ingested. No new external forecast score.**

Original unchanged source [2025 Korea Expressway full 3,100-row CSV](https://drive.google.com/file/d/1FZ6UtY50W6r6Fy6wgmDePHrfqK9foGpx/view), SHA-256 8b76bb06a2d874bddce5d0fd2885154f72fdcffc0a14f8e9163847d0ff030292. Direct original read confirms monthly vehicle counts by section label, no immutable link direction/5min speed/occupancy/travel time. All 775 source file blocks from P10 and the 60 partial/all-zero quarantines retained.

Official [2024 historical metadata on same dataset](https://www.data.go.kr/data/15062523/fileData.do) indicates 2808 rows, 2025 actually read 3100; assuming same 4 class rows, 702 vs 775 file blocks NOT newly verified roads. No 2024 original monthly file downloaded. Don't identify source file row position as immutable physical road code.

## Published 5-minute sources, no raw source admitted yet

[Seoul city 5-minute urban-expressway link speed dataset](https://data.seoul.go.kr/dataList/OA-22351/F/1/datasetView.do) documents volumes, speeds, occupancy, link IDs and 5-minute times. Official file table: 2025 H1 690.88MB, H2 692.93MB, **older smaller original 6.18MB CSV posted 2024-05-22**. Its file name 서울특별시_도시고속도로 5분단위 링크 속도.csv. Exact CSV headings/period currently UNKNOWN. [Seoul official service link lengths/IDs](https://t-data.seoul.go.kr/dataprovide/trafficdataviewfile.do?data_id=1) is optional join candidate, not source-ingested. [KEC VDS hourly 9-row sample](https://www.data.go.kr/data/15103522/fileData.do) plus [KEC VDS-zone geometry](https://www.data.go.kr/data/15087182/fileData.do) likewise candidates, no bytes ingested.

## Exact Jensen counterexample — NOT a new universal traffic theorem

For individual constant-speed 1 km traversals under arithmetic speed reports, 2 cars at (60,60) vs (40,80) km/h both have count2, mean60 km/h, but total constant-link traversal times of 2.00 vs 2.25 vehicle-minutes. Jensen: sum(L/v_i) >= NL/mean_arithmetic(v_i) if the same vehicles and fixed L are meant. Road VDS sensor reporting mean (spot/time/space) and actual in-trip speed trajectories unknown; no justified direct real-source lower-bound claim. Count q × link length L / reported v is an *operational proxy*, not measured individual human welfare. Without measured source L, model result in vehicle-hours/km. Free-flow 85th percentile estimated on training only is a descriptive reference not a physical known equilibrium.

## No-leak high-frequency forecast gate implemented and tested

Standard-library Python source parser with mandatory explicit native column-name mapping, link+direction identity, date+5min bin, count integer >=0, valid finite speed >0 <=250 km/h, occupancy 0..100, no duplicate detector/time. Missing speed rows recorded but not zero-filled. Per stable link: first21 days for train, next7 days for test; require >=50% temporal coverage in each; two fixed rivals train-only same weekday×5-min medians (fallback time/global) and last actually observed adjacent 5min count/speed. Unit-safe MAE speed km/h, traffic vehicles/bin, operational q/v proxy vehicle-hours/km/bin. Train-only observed speed P85 sets proxy delay reference. Failed source gate outputs NO_EXTERNAL_SOURCE_SCORE rather than inventing data. NO sign/exposure and NO causal effects in this estimator.

Actually ran 20/20 tests: three original 2025 source SHA/grain contracts and 17 synthetic/mathematical data-gate and 28-day clock/forecast tests; code/source/JSON/README/report in chat ZIP RITHM-2.6_P11_HighFrequency_Congestion_Joinability_Court_20261012.zip, SHA256 e329323fa52a1b07b9844d954483eb7eafa39f5ab5b412dd707f67d600b1f255. Original 2025 file remains Drive only and original high-frequency records absent from ZIP.

**Only useful next manual action:** one published 6.18MB historical Seoul 5-min CSV downloaded from source dataset and uploaded to Drive RITHM or chat, then inspect actual native headers and date coverage. If less than 28 days, no out-of-time score. Do NOT request credentials or send authority email. Full 690MB 2025 files only later if justified. [Notion scientific canonical](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021).

**RITHM-2.6 OPEN / P11 source and logical contract PASS / 5-min original human group welfare DATA HOLD / true realized travel-time welfare NO_SCORE / causal human route choice/info HOLD.**