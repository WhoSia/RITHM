# RITHM-2.6 P13 — Actual Seoul 2025 Five-Minute Source and Forward Forecast Court

**2026-10-12**. RITHM-2.6 OPEN. Actual full source corpus **38/38 UTF-8 BOM CSV shards** with 18,420,707 original logical sensor observations, 361 of 365 dates, strictly 4 source-missing dates **2025-06-09, 2025-07-10, 2025-07-11, 2025-07-15**. No interpretation of missing full-day traffic as 0. Native schema `DATE_CD,ROUTE_ID,ROUTE_NAME,LINK_ID,ROAD_NAME,HH5M_CD,VOL,SPD,OCC`. [Source archived in existing RITHM Drive folder](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30), two half-year shard subdirectories with `manifest.json` and 19 shards each. DO NOT redistribute 1.63GB of public sensor raw records in GitHub.

**Fixity:** confirmed all 38 REAL shard SHA256 + bytes + 9-field logical row count + chronology. H1 9,176,088 records / H2 9,244,619. User deleted the original large CP949 files to save Drive space. Since the row-safe source splitter transcoded to UTF-8 BOM, the original CP949 file-hashes in the manifests **cannot be recomputed from transformed shards**; do not assert original-byte identity. End-to-end preserved shard bytes satisfy recorded SHA256 and 18,420,707 logical record total.

**Prespecified source sensor baseline**: exact per-link `(ROUTE_ID,LINK_ID)` 21 calendar days of training, immediately following 7 days of test. Require >=50% valid 5-minute observations in both. Clock model uses train-only weekday×HH5M median (fallback time/overall median). Persistence model uses ONLY the previous actually observed same-link five-minute q,v. On precisely matched forecast timestamps:

| Training | Test | Links | N | Clock speed MAE | Prior5 speed MAE | Clock flow MAE | Prior5 flow MAE | Clock proxy q/v MAE | Prior5 proxy MAE |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Jan 1–21 | Jan 22–28 | 178 | 358,663 | 7.446 | **2.439** | 39.693 | **17.985** | 1.601 | **.476** |
| Sep 12–Oct 2 | Oct 3–9 | 178 | 358,463 | 12.580 | **2.377** | 53.245 | **16.925** | 2.543 | **.436** |
| Oct 3–23 | Oct 24–30 | 178 | 358,621 | 7.554 | **2.937** | 49.525 | **16.241** | 1.502 | **.501** |

October 3–9 includes Korea's Chuseok + adjacent public holidays; the train-only weekday baseline is disadvantaged by a holiday regime shift. January 22–28 also includes Lunar New Year. October 24–30 is **post-hoc exploratory normal-week** cross-check, not a new independent holdout. Neither link-level paired observations nor links are independent geographic units, and comparisons are descriptive, not experimental causal claims.

**Mechanism stress-test:** 5/15/30/60/120 minute actual past-state retention errors (speed MAE, km/h): holiday 2.377 /3.764 /5.172 /6.423 /8.497; normal-week 2.937 /4.721 /6.668 /8.979 /12.277. These are source time-persistence forecasts, not a physically identified dynamic relaxation constant. Any richer trained model must beat very strong t−5 baseline OUT OF TIME on same observed sensors.

**WELFARE HOLD:** speed and volume are REAL observed SENSOR measurements. `q/v` is an OPERATIONAL **vehicle-hours/km per observed 5-minute interval proxy**; link length and spot-speed aggregation are not source-certified, so it is **NOT observed individual trip-time sum or multi-route group welfare**. Data contain no named driver repeat-route actions, exogenous VMS treatment, individual travel times, or causal treatment assignments. NO claim of policy improvement.

**EXECUTABLES**: [P13 source-first forecast CLI](../tools/traffic_sources/p13_2025_forward.py), [pre-existing P12 splitter](../tools/traffic_sources/split_csv_stream.py), [P13 aggregate machine results](data/rithm26_p13_2025_aggregate.json), [complete detailed real-data court in chat ZIP](https://github.com/WhoSia/RITHM) (ZIP delivered in conversation, not in repo). `p13_2025_forward.py` intentionally fails closed on absent/corrupted shard hashes, 5-minute clock contradictions and insufficient calendar coverage. The 15-source/synthetic-tests PASS pertains to the locally executed scientific code in the supplied ZIP; don't claim unrun GitHub Actions.

**REPRODUCTION**: `python tools/traffic_sources/p13_2025_forward.py --manifest /path/manifest_H2.json --parts-dir /path/to/both-half-shards --part-start 8 --part-end 12 --train-start 2025-09-12 --out /path/holiday.json`. For January use H1 manifest, parts 1–3, train-start 2025-01-01. The source ZIP in this chat has BOTH verified manifests and scripts, but raw 38 fragments remain Drive-only. **RITHM-2.6 OPEN.**
