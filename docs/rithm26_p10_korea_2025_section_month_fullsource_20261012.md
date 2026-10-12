# RITHM-2.6 P10 — Korean Expressway 2025 Full Source Section-Month Audit, Observability and Seasonal Variation

**2026-10-12. ORIGINAL government human-traffic sensor source, not human route-choice experiment. Research open.**

[Official Korea Expressway file](https://www.data.go.kr/data/15062523/fileData.do) · [exact Drive CSV](https://drive.google.com/file/d/1FZ6UtY50W6r6Fy6wgmDePHrfqK9foGpx/view) · [canonical Notion](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021)

Original file SHA256 `8b76bb06a2d874bddce5d0fd2885154f72fdcffc0a14f8e9163847d0ff030292`, byte length 312412, full 3100 rows, UTF-8 BOM; original file moved **Google Drive `00_INTAKE` -> MyDrive/RITHM** while preserving original file ID, name and content. Same-parent readback success.

## Source grain, exact valid counts and zero exposure

Each consecutive four rows identifies one **source file-order group** with distinct type rows small, medium, heavy, subtotal, totaling 775 groups. Source has 766 distinct section label strings but NO immutable geography/direction ID. Exactly all monthly and annual source type sums equal subtotal; no blank numeric cells. 715 groups strictly positive all 12 months, 40 partially zero, 20 all-year-zero. No evidence zeros mean no travel, closed road or data missingness rather than some reporting-policy state. On full-year 715, author published AADT minus day-weighted 12 integer rounded monthly means max abs <1.447 vehicles/day. On 40 partial, discrepancy can be huge (신탄진~상서, source annual130465 vs naive 33376): **calendar averaging with assumed zero traffic is not licensed**. No relabeling invalid months as counts.

Original `[~]` label repeated 9 groups; `서세종~남세종` twice; exact 4-row source tuple duplicates are `[279,293]`, `[281,283,285]` and nonzero `[326,332]`. No automatic physical dedup. Sensitivity explicitly excluding block332 gives October–February comparison 19.561975% instead of full source 19.560543%. Trace IDs are source block position only.

## Full-year 715 section traffic results (DESCRIPTIVE, NOT unique cars)

| Month | Median source section (monthly mean daily traffic / 2025 annual daily mean traffic) | # sections where 2025 month is peak | # sections where month is trough |
|---|---:|---:|---:|
| Jan | 93.73% | 1 | 178 |
| Feb | **90.17%** | 2 | **415** |
| Mar | 94.94% | 0 | 82 |
| Apr | 99.84% | 7 | 0 |
| May | 103.59% | 10 | 0 |
| Jun | 99.87% | 0 | 0 |
| Jul | 98.78% | 0 | 0 |
| Aug | 103.14% | 59 | 0 |
| Sep | 101.98% | 35 | 0 |
| Oct | **110.87%** | **467** | 0 |
| Nov | 105.57% | 125 | 0 |
| Dec | 96.36% | 9 | 40 |

Across published full-positive link entries, the sum of link-specific daily averages has Oct 37,454,968 and Feb 31,327,198 (+19.56%); NOT a total count of unique car trips; same vehicles cross adjacent link segments. Sum-of-link annual AADT relative class counts: small 85.24%, medium 2.15%, heavy 12.60%. The external 2024 AADT comparator in 706 full-year nonzero-2024 groups: 2025 higher in 294, lower in 412; section median −0.686%, unweighted mean +3.816%, linked aggregate section-count index −0.435%. Route/corridor identity across years unverified; no causal inference.

## Original source reproducibility and instrument limitations

Chat zip `RITHM-2.6_P10_Korea_2025_Full_SectionMonth_Court_20261012.zip` SHA256 `bc56f1bf65d289097427ef115adb8b7d694b0a940454077df3623d45f186d405` holds immutable source-hash validator, 775 source-block derived CSV, JSON, formal 18/18 source-grounded tests, full MD research report and `.xlsx` overview/monthly panel/source trace/reconciliation formulas/60 exceptions (artifact_tool). **Raw source CSV not redistributed into GitHub or ZIP**, but stable user Drive source points to bytes.

Dataset source only has vehicle passages by link and month, no speeds, travel times, individual paths, signed driving directions, VMS signs or exogenous incident policy. NEVER equate volume or road flow with congestion **cost/welfare** or with individual choice. Next gate: audited VDS timestamp×detector×direction speed+volume+occupancy for aligned 4+week period, geometry crosswalk, message-exposure timing if VMS, and independent link-level inference. Public portal lists 2024–2019 prior versions, but this execution accessed ONLY 2025 raw bytes. No public-authority email or API key needed for this source. **RITHM-2.6 OPEN.**