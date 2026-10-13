# RITHM-2.7 P28 — Person-Linked Twenty-Round Response Budgets and Independent Real-World Route-Evidence Gate

**2026-10-13 · SINGLE ACTIVE RITHM-2.7 / NOMOS Flowing · inherited P1–P27 findings preserved.**

## 1. Primitive question and central result

Can finite limits on **additional policy-induced switches by the SAME participant over repeated decisions**, rather than independently chosen one-step responses, materially tighten *source-conditional* group welfare bounds? Separately, which actually independent human or vehicle datasets distinguish **guidance assignment**, **rendering**, **reading**, **route choice**, and **experienced welfare**?

The answer is quantitative but deliberately constrained. Under a frozen replay of the actual 2017 human choices, one extra switch at most per person per 20-round treatment, and at most one change per group-round, the incident-only one-switch P27 improvement upper envelope contracts from **1072** cost units (mean +**2.233333** across 480 observed group-rounds) to **1053** (+**2.193750**). If also at most **two** hypothetical policy-related C-stage response changes occur per 20-round group-treatment panel, the exact upper bound becomes **642** (+**1.337500**). The lower bound remains **0**: someone may ignore every newly offered recommendation. These results do NOT identify benefits actually caused by a guidance policy.

## 2. Exact original-human data and causal limits

Original study: Wijayaratna, Dixit, Denant-Boemont & Waller (2017), *An experimental study of the Online Information Paradox: Does en-route information improve road network performance?*, PLOS ONE 12(9):e0184191, [original article](https://doi.org/10.1371/journal.pone.0184191), [original author supplement S2](https://doi.org/10.1371/journal.pone.0184191.s002). Previously original-verified, compact 24 group-treatment panels stored in [RITHM data](https://github.com/WhoSia/RITHM/blob/main/data/rithm23_wijayaratna2017_routes.csv) (SHA256 `5926158a1a83172b1a4e119eb369140299a43fbceb2b1ba0321710c0f6723484`). Full original XLSX remains in owner Drive, is **not** redistributed here. Six actual laboratory sessions; 12 groups across two within-subject conditions; 20 rounds/treatment; 12 stable subject slots/group-treatment; **288 subject-treatment records = NOT 288 distinct people**; 480 group-rounds and 5,760 originally recorded route choices. Six original recorded-person Cost anomalies and five aggregated source vs theoretical cost differences are NOT repaired or omitted; policy geometry uses original paper's theoretical group cost only.

`C(n1,n2,z)=264−24n1−9n2+2n1²+2n1n2+n2²+19zn2`, with `n1+n2+n3=12`, and actual original incident `z` (four incidents/20 rounds/panel). `n2` counts C–B, and only an originally observed A–C entrant is eligible to switch between C–B and C–D in the **hypothetical new advice**. For historical blind-condition panels a newly installed policy would have to supply this information; **none was actually received during the blind condition**.

The original experimental group/treatment assignment and all future original route sequences are treated as **fixed baseline exogenous trajectories**; no person/group state, upstream A decision, or network feedback is recomputed after the hypothetical policy-induced C change. The model therefore cannot claim to simulate causal long-term congestion equilibrium, adaptation, or hysteresis. Twenty laboratory rounds are not twenty days of field traffic.

## 3. New nonrectangular longitudinal response support

For each original group-treatment panel `p`, original period `t=1..20`, persistent participant slot `i=1..12`, define a binary *additional response decision* `x_{p,t,i}`. Under the main model:

- `x=1` only if subject actually entered C in the original source and their historical C branch permits the policy-specified new direction; changing the branch does NOT impute a C decision for an A–B nonentrant.
- **Per-period group cap:** `sum_i x_{p,t,i} <= 1`.
- **Per-subject lifetime cap within ONE treatment:** `sum_{t=1}^{20} x_{p,t,i} <= 1`.
- **Per-panel total optional compliance budget:** `sum_{t,i} x_{p,t,i} <= B`, `B∈{0,1,2,4,8,12}`. The counter resets across treatment stages and is **NOT** claimed to bound a person's full study lifetime.
- The neutral `x=0` choice is permitted everywhere. Baseline cost minus recomputed hypothetical network cost defines `gain`; improve=positive, harm=negative.

Three policy *response support assumptions*: (i) `incident_avoid`: incident only, `C–B -> C–D`, otherwise no reaction; (ii) `state_direction`: avoid C–B at incidents, **encourage C–B when normal**; (iii) `unrestricted`: either C branch any period. The latter two can harm group welfare. None is established as actual human response to a new rendered app signal.

**Exact dynamic program:** each of 24 panels has a 12-bit mask `m` of already used individual change slots. Process 20 rounds, allow no action or one legal person, update `m -> m OR 2^i`, and add the exact integer group-cost change. Run MIN and MAX over reachable masks, then restrict to popcount(mask)`<=B`; all edges are finite, enumerated, and the states/paths exist as constructed response histories. `4096` possible masks × 20 rounds/panel. Thus bounds are **sharp under the explicitly stipulated frozen-baseline response budget**. Classical finite constrained-resource dynamic programming, no universal new theorem or real observed policy effect. Unconstrained across distinct rounds P27 extrema are recovered as a check.

## 4. Exact original-source numerical outcomes

**Costs are improvement = source-baseline total C − hypothetical total C; mean numbers divide aggregate (24 panel) total bounds by 480 actual group-rounds; zero choice always allowed. All numbers are conditional algebra, not uncertainty intervals or statistical significance.**

| Response support | B=2 bounds (mean/round) | B=12 bounds (mean/round) | P27 rectangular (mean/round) |
|---|---:|---:|---:|
| Incident-only C–B avoidance | [0, **+1.337500**] | [0, **+2.193750**] | [0, +2.233333] |
| Incident avoid + normal-day C–B encouragement | [**−1.150000**, +1.337500] | [**−4.587500**, +2.197917] | [−6.116667, +2.237500] |
| Unrestricted direction | [**−2.441667**, +1.908333] | [**−8.187500**, +5.752083] | [−10.645833, +6.845833] |

**Incident-only exact B progression**, original total then per-480 mean:

| B/panel | Lower total | Upper total | Upper mean/round |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 |
| 1 | 0 | 358 | 0.745833 |
| 2 | 0 | 642 | 1.337500 |
| 4 | 0 | 1053 | 2.193750 |
| 8 | 0 | 1053 | 2.193750 |
| 12 | 0 | 1053 | 2.193750 |
| No person-slot lifetime cap (P27) | 0 | 1072 | 2.233333 |

**Interpretation:** A fixed policy-only change budget can shrink exact long-run attainable gains; this is NOT evidence that human advice uptake is actually so sparse. In the original people’s historical observed C branches, **231/288** subject-treatment slots switched between C–B and C–D at least twice across successive *eligible C visits*, and **251/288** switched at least once (1069 naturally observed C-branch transitions). These are **natural historical choices**, not additional *new-guidance-induced* deviations: the historical frequency warns against silently imposing `<=1` on ordinary human routing. The incremental policy-compliance frequency remains unmeasured. The original source therefore **does not empirically justify B or the person-specific counterfactual cap**.

## 5. Independent outside-source encounter — real vehicles vs interface traces

### 5.1 Graphmasters 2022 Hanover — actually fetched original field GPS GeoJSON (independent observational external contact)

Original external [Graphmasters/traffic-lab BSD-3-Clause repository](https://github.com/Graphmasters/traffic-lab), [2022 experimental source report](https://github.com/Graphmasters/traffic-lab/blob/main/route-choice-2022/report.md), [Google Maps GeoJSON](https://github.com/Graphmasters/traffic-lab/blob/main/route-choice-2022/trajectory-geojson_route-choice_GoogleMaps.json), [NUNAV GeoJSON](https://github.com/Graphmasters/traffic-lab/blob/main/route-choice-2022/trajectory-geojson_route-choice_NunavSwarm.json). Original public UTF-8 GeoJSON files were **read in full from their source repository via GitHub connector**; provider Git blob SHA1 values `026a768f376c2cdfa43ca47f073bd0cb0c3bc636` and `5d35eda3a41a9fa6d31dc724f4bef2628a7be104`. No GPS coordinates, identifiers, or full original trajectories included in RITHM report/archive. The repository's BSD-3-Clause credit retained.

Independent source audit: full source files contain **24** and **21** GeoJSON feature objects. Requiring independently present, parseable start/end timestamps with `end > start` yields **22** and **17** valid trajectory records respectively. The six non-timed stub features are excluded transparently, not tuned by outcome. All 39 timed traces had extensive geographic points (minimum 560 and 516 nodes in each respective group); these 39 equal the report’s separately asserted vehicle counts. Source research summary reports vehicle mean recorded origin-destination travel times **34.4 min (22 Google Maps)** and **30.6 min (17 NUNAV)**. These means were **read from the research report**, NOT independently recomputed from a common start/finish line in GeoJSON; naïve feature timestamp differences need not match cropped travel-time measures. The reported -3.8min cross-app contrast is descriptive, not randomized treatment or independent city-wide group welfare.

**Positive external contact:** observed real individual vehicle GPS trajectories under assigned routing system, timestamps and group context (not a 2017 human-to-2022 vehicle identity link). **What is missing:** independently logged actual guidance display/read/obedience, same people’s 20-round behavior, explicit randomization (interleaved departure ≠ randomized policy), group total experienced cost including all road users, and counterfactual route allocation under the unselected app. This field evidence **cannot calibrate P28 hypothetical additional individual switching budget B or identify P28 policy gain**. The source grouping does not justify cross-world causal transport.

### 5.2 Snopková et al. 2025 virtual evacuation — different observational measure

[Primary Scientific Data article](https://doi.org/10.1038/s41597-025-04440-y), [Springer Nature Figshare dataset](https://springernature.figshare.com/articles/dataset/Predictors_of_evacuation_behavior_dataset_on_respondents_route_choice_and_web_interaction/27705402), CC BY listed on dataset. Reports **208 human respondents**, mouse viewpoint rotation and corridor choice clicks across randomly assigned scenes. Article explicitly defines `interaction.csv` (mouse rotation), `responses.csv` (AOI click and timestamp), and `confidence.csv`. This is an independently published *person-UI-interaction and response recording ecology*, not a rendered traffic-routing advice/version and not an interacting congested human group. Data listing and schema inspected; full 9.55 MB individual files **not acquired here**, so no new participant-level count, fit or efficacy effect claimed.

### 5.3 Noussair–Qiao 2025 — still no participant-level ingestion

[Management Science published original](https://doi.org/10.1287/mnsc.2023.00056), and the original author revised July 24 2026 working paper already held/read in Drive. Independent group congestion experiment has historically delivered *previous information* around different decision timing and showed short-run harm/long-run benefit in published results. Publisher lists supplementary data, but participant-by-round original bytes and independent per-person viewed/rendered message logs remain **unverified**. Cannot pretend they are a 2017 C-stage intervention or convert their paper-level averages to original raw individual outcomes.

### External source verdict

**Independent 2022 real field GPS primary source: SOURCE-READ / AGGREGATE QC PASS.** Real driver advice *assignment context* and actual routes documented, per-person guidance render/comprehension log **ABSENT/UNVERIFIED**. Independent 2025 UI interaction source: document/data location and original column schema confirmed, participant bytes **NOT READ**; it measures *cursor response*, not traffic guidance. No source presently connects **verified actual advice render + legal C-stage decision + repeated same-person behavior + independently measured full group welfare** in one causally valid design.

## 6. Reproduction and language roles

**Go:** all three distinct policy supports × six B budgets on 480 original source states; 4 scientific source/invariance/unit tests executed PASS (`GO111MODULE=off go test ./go/p28 -v`). **C++17:** independently parses 240 trits per panel using Boost multiprecision and solves per-person mask DP; compiled `-O2 -Wall -Wextra -Werror` and matched Go **18/18 source-derived integer contrasts**, including rectangular baselines. **Ruby:** original source human history decoder, 288 slot repeated-path audit; independently compares full C++/Go results 18/18, produces ONLY 432 aggregate group-treatment-budget records, no person identity. **Rust:** independent std-only integer 4096-state DP implementation, **written but NOT run** (`rustc` unavailable). **R:** base-R session-aware descriptive aggregation checker, **written but NOT run** (`Rscript` unavailable). No changes to global system libraries or friend-owned servers. All GitHub contributors must remain WhoSia, no automated GitHub Actions writeback/claim; no CI run claimed.

**Distribution:** owner’s original source 24 panel compact CSV is already [available as an existing GitHub source under original terms](https://github.com/WhoSia/RITHM/blob/main/data/rithm23_wijayaratna2017_routes.csv), not duplicated in P28 ZIP. External vehicle GPS source is hosted by Graphmasters, not redistributed. User local ZIP contains Go/Ruby/C++/Rust/R source, verified **aggregate-only** per-policy-panel results, complete scientific rationale, source URLs, and original-source SHA contracts. These are scientific **replay scripts**, not an application that fetches live advice telemetry.

## 7. Identified question for further flowing work

P28 replaces time-rectangular per-round envelopes with a **person-identity-linked nonrectangular response budget** and authenticates a **new independent GPS route observational ecology**; it does NOT identify an actual new treatment, user cognition, large-system realized policy welfare, or dynamic counterfactual feedback. All previous RITHM work remains live genealogical evidence; RITHM-2.7 alone remains OPEN.

Next measurable evidence must pair **group/session-randomized guidance offer assignment, stage-legal app version and render event, person eligible choice/action, repeated route and independently measured full group travel cost**, with interference/carryover explicitly handled. A cluster-level randomized **offer ITT** may be estimable even without each person’s verified cognitive reading, but attention mediation requires additional evidence or justified IV exclusion assumptions. If real records are unavailable, future work must model **history feedback** explicitly and state assumptions rather than call one-step frozen replay “long-run welfare causal prediction.”

**PASS:** exact conditional source geometry, 24×20 panel identity mask budget DP, 18/18 Go/C++ integer cross-comparisons, Go four test cases, Ruby original-history and contract audit, 2022 independent original vehicle GPS full-file read and timestamp QC. **HOLD:** scientific external attention/behavior compliance, independently causal group welfare, 2017→2022 causal transport, Rust/R execution, empirically identified policy-induced individual switching quotas, free-floating universal novelty.
