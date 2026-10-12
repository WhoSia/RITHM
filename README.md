# RITHM — Route-choice Inertia and Traffic Hysteresis Modeling

**Current scientific stage: RITHM-2.6 OPEN (2026-10-10).**  
**When Guidance Changes Habits: Identifiable Route-Choice Learning, Congestion Externalities & Horizon-Dependent Welfare**

RITHM asks how repeated individual route choice, learned cost, switching resistance, information timing and congestion feedback interact to shape collective welfare. The original traffic-habit question—not archive infrastructure or machine observability—is the scientific target. **OPEN ≠ identified human habit causality, identified guidance effects, or novel universal theorem.**

## Current evidence: real 2017 staged human route-choice data

The current experimental analysis uses the original [Wijayaratna et al. (2017)](https://doi.org/10.1371/journal.pone.0184191) six-session [S2 participant workbook](https://docs.google.com/spreadsheets/d/1Kv-fWLa6kP_tv9PpgNDUYIV3oiC-zmRc/edit) (**not redistributed here**): 144 participants, 12 independent groups of 12, 20 rounds per information condition, **5,760 recorded route decisions and 480 group-rounds**. Three sessions were no-information-first and three information-first.

**The causal clock matters:** travelers choose A–B or A–C before seeing the current C–B incident; travelers on A–C learn the current incident **only at node C in the online-information condition**, before choosing C–B versus C–D. Everyone is informed of the previous round's outcomes afterward. Do not insert future incident information into a pre-departure model.

The original private travel costs are c(ABD)=10+n1+n2, c(ACBD)=13+n2+19z, c(ACD)=22−n1 with n1+n2+n3=12 and actual incident z∈{0,1}. The group-cost identity is

`C=264−24n1−9n2+2n1²+2n1n2+n2²+19zn2`.

**P1 source warning:** in **6/480** group-rounds the source's sum of individual recorded Cost entries differs from count-derived group cost. The paper's reported aggregate costs **210.629 (no info) / 219.163 (info)** agree with count-derived means **210.6291667 / 219.1625**, *not* directly summed participant-cost means **210.8625 / 219.1250**. Preserve both outcomes; never silently alter the original source.

## RITHM-2.6 initial behavioral prediction court (P1–P2)

Six **leave-one-session-out** folds; regularized logistic models evaluated separately for (A) upstream A–C choice and (C) downstream C–B choice *conditional on entering A–C*:

| Nested information set | Upstream log loss ↓ | Node-C log loss ↓ |
|:--|--:|--:|
| S0: past public state + experiment clock | 0.666493 | 0.550630 |
| S1: S0 + individual's previous routes and streak | **0.653405** | 0.524417 |
| S2: S1 + experienced individual/relative costs | 0.653507 | **0.524148** |

The independent-individual group-cost diagnostic (under **cross-person conditional independence and unvalidated hypothetical-node-C extrapolation**) has held-out MAE S0 **9.77335**, S1 **9.70436**, S2 **9.84203**. Personal history predicts individual decisions better, but adding experience history **worsens** the group-welfare projection. Group MAE uses the **realized shock for ex-post cost assessment**; it is not a genuinely pre-shock welfare forecast.

This is exploratory prediction from actual people, **not** an estimate that memory causes route choices or that changing public guidance causes group welfare. Group correlation, no-info incident ignorance, dynamic adaptation and treatment order remain central rivals. Preserve the original RITHM S02.6 behavioral-PHASE forecasting defeat and the 2.5-D negative memory-necessity result.

Read the [full 2.6 Notion source-bound research court](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021) and the [P1–P2 concise GitHub court](docs/rithm26_source_bound_behavior_20261010.md). The complete read-only source parser, exploratory prediction script, results JSON and eight local contract tests were produced as a **chat-local research ZIP**, not as a repository CI dependency. Full source XLSX remains only in the cited Drive.

**Version policy:** main-only permanent branch; no Actions for exploratory work; source authority and genuine held-out group welfare take precedence over version proliferation. **RITHM-2.6 OPEN · HABIT-CAUSALITY HOLD · GROUP-DEPENDENCE HOLD · INTERVENTION-WELFARE HOLD.**

## New: P5 — stable personal propensity versus recent action and observed group covariance

The [P5 source-bound human panel audit](docs/rithm26_p5_state_dependence_and_covariance_20261010.md) makes a new, narrower comparison of **restricted** individual preference models and observed route-change persistence. In six session-heldout folds with source-valid information timing, an online empirical-Bayes personal-propensity predictor (prior strength 6) scored 0.626045 upstream and 0.519175 conditional at node C; adding a *training-selected* last-action term scored **0.626267 (worse)** upstream and **0.513161 (better)** at C. This is NOT an identified dynamic random-effects causal estimator, and Stage C's “last” means last previously eligible C decision, which may be more than one day ago. The classical dynamic-panel *initial conditions problem* remains OPEN.

The original twelve-driver system cost admits an **exact** conditional mean/count-variance/pairwise-covariance decomposition. On the real 480-group-round S2 source panels (holding shock strata separate), original-paper group mean cost INFO−BLIND = **+8.533333** comprises **+8.219531** due to mean-count cost, **−0.619531** from individual dispersion, and **+0.933333** from cross-person covariances. Both absolute covariance contributions are **negative** (−1.334375 blind, −0.401042 information); these observations do NOT prove information causally weakened coordination. Across six sessions the exploratory paired covariance contrast has an approximate interval spanning zero.

A fixed-margin stress test preserved each driver's **total A–C choices** and each group-date's **A–C occupancy**, and randomized only the intertemporal binary assignment through 2×2 switches. The actual same-route transition count modestly exceeded Monte Carlo null means in the information arm; TWO seeds gave informative but sampling/mixing-sensitive Monte Carlo upper tails ≈0.020 and 0.042. These are NOT exact randomization p-values and do NOT identify habit causality.

**Hard interpretation ceiling:** the data support descriptive personal propensity and temporal-order information, plus an exact algebraic welfare decomposition. They do not yet identify innate traits, causal route inertia, learned response, cross-person policy spillovers, or a superior guidance policy. Original S2 raw participant rows remain in Drive only. No new GitHub Actions have been run for P5.

## New: source-bound personal-persistence rivalry and pre-incident welfare (P3–P4)

The [P3–P4 original-human-choice research court](docs/rithm26_p3_p4_history_and_clock_20261010.md) goes beyond “previous route predicts next route” by separating an individual's **older revealed route frequency (up to t−2)** from their immediately previous route (t−1). Six held-out sessions with the original staged A–C → C–B/C–D information clock yield:

| Model | Upstream binary log loss ↓ | Node-C binary log loss ↓ | **Pre-incident** group-cost MAE ↓ |
|:--|--:|--:|--:|
| Structural/time/state S0 | .666493 | .550630 | 12.80750 |
| Older choice-frequency history only | .634149 | .520310 | 12.74898 |
| Older history **plus immediate previous route** | **.629044** | **.506456** | **12.68130** |
| Full revealed-frequency + recent route + cost experience | .629866 | .506880 | 12.88616 |

The finite incident clock explicitly respects **4 incidents per 20 rounds**: forecast before the shock by weighting the two conditional node-C paths by `(4 − previous incidents)/(21 − current period)`. Current incidents never enter the upstream choice. The 12.68130 improvement over 12.80750 is SMALL. Stage-C behavior for hypothetical A–B travelers and **cross-person conditional independence** remain UNIDENTIFIED modeling assumptions. **Neither state-dependent habit causality nor intervention welfare is identified.** The individual's historical route share is endogenous; it must not be mislabeled immutable “type.” No actual S2 participant records or raw spreadsheet are in GitHub. The tests (27/27 local PASS) and full executable source-audit package are maintained as a separate chat artifact, not a CI dependency.

---

## New: P6 — source-clock-legal joint welfare and initial/selection rival (2026-10-11)

Source: [original S2 2017 human route-choice workbook](https://docs.google.com/spreadsheets/d/1Kv-fWLa6kP_tv9PpgNDUYIV3oiC-zmRc/edit), 6 sessions, 144 humans, 5,760 routes, 3,511 actually eligible node-C responses, 480 group-rounds. Source XLSX excluded from repository. First A–B/A–C choice PRECEDES current accident signal; only online C entrants learn current accident at node C; a valid 4-in-20 finite shock quota is used for pre-incident forecasts.

| Six-session-heldout model | Upstream LL ↓ | Eligible node-C LL ↓ | Pre-incident group-cost MAE independent ↓ | Group residual-corrected MAE ↓ |
|---|---:|---:|---:|---:|
| S0 structure/time | .666493 | .550630 | 12.807504 | 12.406005 |
| Older choice history + last route | .629044 | .506456 | **12.681299** | 12.375989 |
| Above + initial observed choice + real C eligibility history | **.628568** | .505493 | 12.694375 | **12.373013** |
| Above + experienced cost history | .629135 | **.505210** | **12.818099 (FAIL)** | 12.502330 |

**This is exploratory, not a full initial-conditions-corrected random-effects estimator.** The first-choice covariate is merely a predictive initial-state proxy. C-stage likelihood uses only actual entrants; full group forecast combines model-predicted conditional choices with an unverified observational transport assumption. Residual correction estimates a TRAIN-ONLY pair-residual adjustment and can absorb individual probability miscalibration; it is NOT a purified covariance estimate or causal social-coordination effect. Compared with a simpler train-only intercept calibration, the older+last model had MAE 12.624710 versus residual correction 12.375989; all six sessions improved, but these six sessions were also used throughout model development. No untouched confirmatory dataset remains. **Full P6 focused regression court: 17/17 PASS**; executable parser/code/JSON/test log are in a separate user chat archive, not auto-triggered by this documentation commit.

**Novelty hard-stop:** [Yu & Gao (2019)](https://doi.org/10.1016/j.trc.2019.07.014) already treats learning contingent routing policies, memory and one-step versus full-trajectory forecasting. Generic dynamic fixed effects, true state dependence, social interaction and partial identification have established econometric/optimal-transport predecessors. The paper-worthy target is *new independently validated staged human-choice → aggregate congestion-welfare transfer*, not a claim to have invented habit-aware routing.

See [P6 executed court and 2.0–2.6 retrospective](docs/rithm26_p6_initial_selection_jointwelfare_20261011.md), [RITHM-2.6 Notion canonical](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021) and [parallel Literature Harvest](https://app.notion.com/p/3f5ef561cf9281489be4c0d410e357dd). The full historical RITHM-2.0 README remains below. **RITHM-2.6 OPEN / CAUSAL HABIT HOLD / NEW GROUP WELFARE HOLD / NOVELTY HOLD.**

---

## New: P7 — legally staged initial-effect joint likelihood and external-welfare HARD HOLD (2026-10-11)

**The P7 model LOST to the simpler P6 source-bound rival.** Six-session-heldout rounds 2–20, not the original 20-round P6 score. A shared Gaussian individual effect conditioned on initial upstream A–C choice and jointly integrated across observed upstream and eligible node-C choices is a working **Wooldridge-inspired** correlated-effect likelihood (9-node Gaussian quadrature); **NOT** an identified psychological habit effect, formally certified strict-exogeneity model, or counterfactual C-choice imputation.

| Matched model | Upstream LL ↓ | Eligible C-stage LL ↓ | Final 3-route LL ↓ | Pre-incident group-cost MAE ↓ | Train-only shock-error-corrected MAE ↓ |
|:--|--:|--:|--:|--:|--:|
| P6 structural clock | .666175 | .546658 | .999065 | 12.860869 | 12.466254 |
| P6 older-person history + last + initial/C eligibility | **.626311** | **.498962** | **.929999** | **12.695040** | **12.330329** |
| P7 shared Gaussian person effect | .629784 | .509076 | .939630 | 12.921752 | 12.509932 |

P7 final route log loss was worse on **6/6** sessions. The P7 joint group-cost adjusted MAE was worse on **5/6** sessions, mean difference +.17960 source cost units; tiny number of sessions and extensive prior model selection preclude a confirmatory inference. Optimizers all converged, independent gradient check and 30/30 combined regression tests passed. A more complicated latent effect has NO automatic predictive or causal value.

**Exact node-C nonentrant selection cut:** from original flow (6,0,6), one hypothetical former A–B entrant rerouted A–C while remaining 11 people fixed has group cost 194 if she chooses C–D and 196 if C–B without incident, versus 194 or 215 with incident. No original A–B choice reveals her potential C–B/C–D response; at incident chance 1/5, attained policy-effect interval for this one-person hypothetical is [+2,+7.8] source group-cost units. Classical local nonidentification witness, NOT treatment effect estimation or novel universal theorem.

**Independent group-welfare external confirmation remains BLOCKED.** The user acquired 10 key historical original papers; all were source-identified, renamed and moved from Drive 00_INTAKE to canonical 10_PAPERS with unchanged IDs. Original *papers* are NOT original person-by-round external source *data*. The same 2017 S2 six sessions have already guided iterative model development. Ashraf 2023 original 18-person data were already studied and have a different topology. Noussair–Qiao (2025, author revised 2026-07-24) publisher references supplemental data, but its raw independent participant group data were not fetched or tested here. **No new external transport score should be claimed.**

See [P7 mathematical, numerical and source custody court](docs/rithm26_p7_joint_initial_conditions_external_transfer_20261011.md), [2.6 canonical Notion](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021) and [independent P7 Harvest record](https://app.notion.com/p/3f5ef561cf928127a7dbf7e7b6dde6d1). Full executable + JSON + tested evidence are available in the user-chat P7 ZIP without the raw original human XLSX or copyrighted papers. **RITHM-2.6 OPEN · P7 COMPLEXITY-PREDICTION FAIL · FRESH EXTERNAL GROUP-WELFARE HOLD · CAUSAL HABIT HOLD.**

---

## New: P8 — Independent external group-welfare *source gate*, not yet a score (2026-10-11)

**RITHM-2.6 remains OPEN. Fresh external HUMAN group-welfare validation is STILL BLOCKED because original new participant×group×round records have not been ingested.** Frozen evidence/engineering gate [P8 external transfer contract](docs/rithm26_p8_external_source_admissibility_and_frozen_welfare_20261011.md) was created BEFORE seeing any individual original outcomes from the new candidate, but the 2025 paper's **published aggregate results are already known**; not globally outcome-blind.

- [Noussair–Qiao 2025](https://doi.org/10.1287/mnsc.2023.00056): independent **six-player**, 2-route network, four 40-round treatments, 24 sessions/48 six-player groups; full original export expected 46,080 choices and 7,680 group-rounds, but these are DESIGN COUNTS, NOT obtained records. Information concerns PREVIOUS-period route occupancy after simultaneous route choice, **not** 2017 incident at node C within the journey. P7's node-C coefficients cannot be exported as if a matching second-stage label existed.
- Published source private travel cost a=k and b=2(6-k) gives source group C(k)=k²+2(6−k)²=24+3(k−4)². If each of six people has P(a)=2/3, identical marginals support exact mean system costs **24** (balanced k=4 coupling), **28** (independent) and **48** (all choose the same road). This is source-specific CLASSICAL expectation/covariance/transport algebra, not human observations or an innovative general theorem.
- [Bode et al. 2015 public Dryad dataset](https://doi.org/10.5061/dryad.7m645): original README fetched and inspected, 464 people, 29-column processed history of simulated exit queues; download of actual data ZIP blocked HTTP 403 in this environment. Other 89 agents are simulated, so this is a separate dynamic human **choice-only** candidate, NOT a live-human joint-traffic congestion welfare dataset.
- Historical Ashraf 2023 was already explored in RITHM 2.0–2.3: **cannot** be passed off as untouched replication.
- **Frozen P8 original-data interface**: 6 person IDs/group, 40 periods/arm, 4 arms, stable membership, 24 sessions/48 groups if complete; predictions use only earlier observed own routes, independent online Beta(4,2) person marginals, source optimum C=24, and an ANALYST-only last-occupancy cost comparator. Exact 64-profile LP gives sharp *EXPECTED* welfare sensitivity to unknown dependence, NOT observed round prediction intervals. Synthetic-fixture and source-math tests **18/18 PASS**; original participant data NEVER supplied as test fixtures. External real-group MAE, 40-round cumulative error and session-level uncertainty: **NOT SCORED**.
- Full locally tested P8 source, source registry and SHA-256 manifest in conversation archive `RITHM-2.6_P8_Frozen_Independent_GroupWelfare_Transfer_Gate_20261011.zip`, SHA256 `da4be3453f0bf9a200545baaffaf7bad91bbe430f79aefd4008b73e19492350a`; no original source participant ZIP/PDF redistributed. [Current Notion scientific court](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021) · [P8 parallel Harvest](https://app.notion.com/p/3f5ef561cf9281fea38cfbc043cabe48).

**Important replication-file permission gate (verified):** The [INFORMS replication-file portal](https://services.informs.org/dataset/mnsc/download.php?doi=mnsc.2023.00056) DOES exist and explicitly restricts files to reproducing the original paper's results with the same data and models; **new RITHM behavioral models and external welfare transfer are a different use requiring express author/data-owner permission**. No terms accepted and no restricted original data downloaded. The source evaluator now demands a positive user-verified legal-reuse confirmation before scoring a new full original. Latest chat ZIP verified SHA-256 `79b1c58a6b6b1d928a6b6b549cf300f8c0d918078e6b834c3ed36639c1d25f93` (supersedes initial exploratory package checksum). No human experimental external group score exists.

**P8 GATES:** SOURCE INFORMATION CLOCK CORRECT / CROSS-TOPOLOGY MATHEMATICAL COUPLING PASS / ORIGINAL EXTERNAL GROUP HUMAN DATA BLOCKED / EXTERNAL HUMAN WELFARE SCORE NO SCORE / HABIT CAUSALITY HOLD. Do not tune 2017 P7 model or claim external success until new human group data pass admission.


---

## P8-E2 — Real archived Lyon source recovered; historical evidence corrected (2026-10-11)

**Source recovery matters more than an unnecessary new agency inquiry.** The original author [Figshare 2019 Lyon choice experiment](https://doi.org/10.6084/m9.figshare.9791285) had already been preserved in [RITHM's canonical Drive source ZIP](https://drive.google.com/file/d/1E7kuUOqEZa5lw6z5OenkMj9sm4byR804/view) since 2026-08-31. Its version-2 original CSV and data dictionary are now actually read and matched by published **MD5 checksums**. The *specific preserved subset* has **10,002 alternative rows = 3,334 3-route decisions**, **483 participant IDs**, **30 ODs**; t1/no information 1,069, t3/visible travel-time information 2,265. Original raw data not copied into GitHub. A 2017 PLOS node-C policy, Korean aggregated VMS/VDS flows, and 2019 Lyon alternative route choices are DIFFERENT source geometries.

**A historical-error correction:** Lyon was ALREADY analyzed in old RITHM origin M05.2, M05.133R, S02.7 and S02.8. Thus this is exploratory *reanalysis*, NOT untouched external confirmation. M05.133R retained a non-significant history-versus-stable-frailty challenge; S02.7 allowed Lyon as human choice evidence but NOT collective-welfare validation.

| Fixed 5-fold out-of-sample logloss ↓ | Person-disjoint | OD-disjoint |
|---|---:|---:|
| Route label + experiment arm prior | 1.05768 | 1.06108 |
| Add route geometry and **only actually visible** travel times | 1.02378 | 1.02917 |
| Add last and older **same participant × same OD** routes | **0.98886** | **0.99325** |

**Scientific distinction:** A previous `R1` chosen for another OD is NOT the same actual road; cross-OD route-label 'inertia' would be an erroneous interpretation. Train/test splits separate people or 30 ODs, and observed previous actions in the heldout stream are teacher-forced sequential history (not hidden future data). For t1, TT_INFO appears in the source CSV but is explicitly **MASKED** in the estimator since no participant received it. Improvements 5/5 folds in both designs are descriptive; **stable individual route preferences versus causal habit remain unidentified**, there is no original simultaneous real human group-cost outcome and no new independent welfare score. [Full P8-E2 source-data court](docs/rithm26_p8_e2_recovered_lyon_source_20261011.md) · [RITHM-2.6 scientific Notion court](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021). Reproduction source/tests/aggregate score JSON are delivered separately as chat archive, not as new GitHub Actions dependencies. **RITHM-2.6 OPEN / HUMAN CHOICE REANALYSIS PASS / NEW HUMAN GROUP WELFARE HOLD / CAUSAL HABIT HOLD.**


---

## P9 — Within-OD stationary preference versus recency, plus Korean public road-flow admission (2026-10-11)

**A real negative/rival model competition:** 2019 author Lyon source has 3,334 choices / 483 people / 30 ODs. This source is ALREADY EXPOSED to RITHM since Aug 2026 (M05.2, M05.133R, S02.7/8); numbers below are exploratory reanalysis and DO NOT constitute untouched independent human or group-welfare validation. Source [CC BY Figshare](https://doi.org/10.6084/m9.figshare.9791285) · [existing original raw ZIP in Drive](https://drive.google.com/file/d/1E7kuUOqEZa5lw6z5OenkMj9sm4byR804/view).

| Same three-route softmax, fixed source-clock-legal features | Person-heldout 5-fold logloss ↓ | OD-heldout 5-fold logloss ↓ |
|---|---:|---:|
| M2 route geometry + t3-only actually disclosed time | 1.023783 | 1.029168 |
| **S stationary taste proxy**: same person×OD prior choice share | **.987709** | **.992261** |
| L last same-person×OD choice only | 1.000011 | 1.004431 |
| O older history EXCLUDING the last choice | 1.002330 | 1.007627 |
| **OL older history + last separated** | **.987424** | **.991844** |
| SL entire prefix share PLUS extra last | .988059 | .992620 |

The *incremental* separate-recency gain S→OL is **+0.000285 person / +0.000417 OD** LL, 3 of 5 fold gains each; illustrative 2500-bootstrap intervals resampling 483 people **[−.001146,+.001722]**, resampling 30 ODs **[−.001287,+.002277]**, both include zero. SL direct extra last indicator even worsens S. S is a **HISTORY-BASED prefix taste proxy**, NOT a causal immutable individual trait; *psychological habit and true state dependence remain unidentified*. Within named person×OD actual adjacent stays 837 of 1567, exact choice-count-constrained exchange expectation 825.153, 2500 shuffle two-sided diagnostic p≈.274 (cannot control changing travel-time and info). NO causal finding.

**Public Korean source contact-free, but bounded:** Verified actual [한국도로공사 2025 3,100-row section×vehicle×month CSV](https://www.data.go.kr/data/15062523/fileData.do) metadata says **no-login file download**, but raw full CSV was inaccessible from this runtime. Public-page preview's **FIRST FOUR ROWS ONLY** comprise 서울~신갈JC 2025 small/medium/large/subtotal ×12 months; all 12 class sums match, day-weighted published annual mean **199,479.756 →199,480 vehicles/day**. Nov 206,330 vs Jan 184,436 is a **flow-volume** contrast, NOT measured congestion speed, system travel-time cost, guide-effect or group-welfare score. For full Korean time series the only manual need is one original full 2025 CSV; for fine-grain congestion, original continuous [five-minute VDS speed/count/occupancy](https://www.bigdata-transportation.kr/frn/prdt/detail?prdtId=PRDTNUM_000000000024), optionally with [detector-zone mapping](https://www.data.go.kr/data/15087182/fileData.do). Agency emails remain lowest-priority and **none were sent**. NQ English author permission request user-reported sent independently.

**Tests**: 18/18 local source/clock/rounding/cluster-contract tests PASS. [Full P9 science and acquisition court](docs/rithm26_p9_stable_taste_recent_choice_korean_flow_20261011.md), [Notion canonical P1–P9](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021), [P9 parallel Harvest](https://app.notion.com/p/3f6ef561cf9281d8a536ef973546a15c). Source code, aggregated result JSON, public **preview-only** CSV, integrity manifest and tests in separate chat ZIP `RITHM-2.6_P9_Trait_Recency_and_Korea_Public_Flow_20261011.zip`, SHA256 `987ab7b639804590d19697d33fcda251445870f5fcce6616ac4356e53b3e13b5`. No original human participant table in ZIP. **RITHM-2.6 OPEN; incremental recent effect HOLD; true external group welfare HOLD.**

---

## P10 — Real 2025 Korean Expressway full section-month source (2026-10-12)

**SOURCE DATA MOVED, INGESTED AND ANALYZED; NOT WELFARE.** The user-supplied [Korea Expressway 2025 original CSV](https://drive.google.com/file/d/1FZ6UtY50W6r6Fy6wgmDePHrfqK9foGpx/view) is now in the existing Google Drive [RITHM](https://drive.google.com/drive/folders/1jn7NxAXAKSvBW64IREX3dB4EC81OuWhu) folder (original file ID retained, source parent removed, verified). Government [original annual official data](https://www.data.go.kr/data/15062523/fileData.do), SHA256 `8b76bb06a2d874bddce5d0fd2885154f72fdcffc0a14f8e9163847d0ff030292`, **3100** source rows = **775** consecutive 4-vehicle-type blocks.

- For every block, all 12 monthly source `small + medium + large = subtotal` exactly, 0 blank numeric cells. **715** blocks have positive counts all 12 months; **40** partial with a zero month; **20** all-zero months. The latter 60 are quarantined from complete-year trends. Annual AADT reconstitution error in 715 complete blocks is at most **1.447 vehicles/day**; incomplete/horizon-changing blocks do NOT match 365-day calendar zero-imputation and source zero semantics are unverified.
- Spatial keys unobserved: **766 different label strings** for 775 blocks. `~` occurs 9 times; `서세종~남세종` repeats twice with all four original source rows identical (block ids 326/332). The trace block ID is file order, not a physical unique road-link ID, and source rows were NOT deduplicated or fabricated.
- Within the 715 complete blocks, **467/715 peak in October**, **415/715 trough in February**. Median section traffic as fraction of its source AADT: October **110.872%**, February **90.167%**. Across same 715 entry IDs, October-to-February ratio of summed section-level average daily counts **+19.561%** (this is a comparison index, NOT number of unique national vehicles). Excluding suspect duplicated block 332 has only tiny effect **+19.562%**, but not geolocational duplicate certification.
- Among **706/715** source full-year sections with positive 2024 source AADT, 2025 source annual change positive for **294** and negative for **412**, section median **−0.686%**, arithmetic mean **+3.816%**, ratio of same-section yearly AADT sums **−0.435%**; these are descriptive without source link-history or speed. Repeated vehicles across adjacent sections preclude describing sum as Korean individual drivers or VKT.
- Complete [P10 full-source scientific court](docs/rithm26_p10_korea_2025_section_month_fullsource_20261012.md), [RITHM 2.6 Notion canonical](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021). Local chat zip `RITHM-2.6_P10_Korea_2025_Full_SectionMonth_Court_20261012.zip` SHA256 `bc56f1bf65d289097427ef115adb8b7d694b0a940454077df3623d45f186d405` includes tested source parser, Excel evidence review workbook with real formulas, source-section aggregate CSV preserving all 775, machine output, 18/18 real-source checks and full report; raw government CSV remains Drive-only.

**P10 PASS:** full 2025 source reconstruction and bounded seasonality. **P10 HOLD:** VDS speeds, individual route-choice, VMS message exposure, incident exogeneity, actual traffic welfare and any causal information effect. Annual 2019–2024 versions exist on government's source page but raw bytes have NOT been acquired or measured in this court. RITHM-2.6 OPEN.

---

## P11 — High-frequency congestion source joinability and true-welfare nonidentification (2026-10-12)

**P11 VERIFIED EXECUTION: 20/20 source-contract/math/synthetic temporal tests; 2025 Korea Expressway original CSV unchanged and SHA checked. NO NEW 5-MIN ORIGINAL LINK DATA OBTAINED AND NO EXTERNAL COST SCORE.** RITHM-2.6 OPEN.

- Official [Seoul 5-minute urban expressway link dataset](https://data.seoul.go.kr/dataList/OA-22351/F/1/datasetView.do) lists 2025 semiannual 690.88MB/692.93MB and importantly a **6.18MB small older CSV**, named 서울특별시_도시고속도로 5분단위 링크 속도.csv, posted 2024-05-22. Published dataset covers link ID/date/time/volume/speed/occupancy; exact small-file columns and period remain unverified until source bytes are acquired. [Seoul service-link distances and IDs](https://t-data.seoul.go.kr/dataprovide/trafficdataviewfile.do?data_id=1) may supply length. [Korea Expressway VDS 1-hour sample](https://www.data.go.kr/data/15103522/fileData.do) has only 9 publicly listed rows; full platform requires login. No government email or API key requested.
- Official 2024 [KEC monthly version metadata](https://www.data.go.kr/data/15062523/fileData.do) reports **2,808 source rows**, whereas the actually read 2025 original has **3,100**. If four vehicle-class rows per section hold in both, these correspond to 702 and 775 file-order blocks; **NOT 73 verified newly opened roads**. Section-label and block-order geographic identity changes prohibit uncontrolled multi-year matching.
- Mathematical construction: hypothetical 1km link, two cars, same count 2 and arithmetic mean speed 60km/h: individual speeds (60,60) give 2.00 vehicle-minutes, (40,80) give 2.25. Thus mean speed + count alone do not identify actual sum of individual constant-speed travel times. Classical Jensen bound applies only under same-individual arithmetic speed and constant-link-speed assumptions, **not verified for real VDS aggregation**.
- Executable [P11 source and mathematical court](docs/rithm26_p11_highfreq_congestion_joinability_20261012.md) gates explicit link+direction identity, 5-minute chronology, unique observations, speed >0, volume counts >=0, occupancy 0..100, source-specific link length or per-km output; prospectively trains first 21 days, scores next 7 days against fixed clock baseline and observed previous 5-minute measurement. Output is expressly an **operational proxy** in vehicle-hours/km and NOT human group welfare. Source absent => NO_EXTERNAL_SOURCE_SCORE, not a synthetic score masquerading as evidence.
- Chat-local validated P11 code+machine audit+source registry ZIP SHA256 **e329323fa52a1b07b9844d954483eb7eafa39f5ab5b412dd707f67d600b1f255**, no raw original source copied. [Notion scientific canonical](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021). One source file needed before any new actual speed-flow score: the official 6.18MB Seoul CSV from the linked published dataset. No causal guidance/behavior/welfare claims.

**P11 VERDICT:** real original monthly source read PASS / source-heterogeneity and mathematical counterexample PASS / 20/20 tests PASS / high-frequency original speed-flow not ingested / exact travel-time welfare not identified / RITHM-2.6 OPEN.

---

## P12 — Project-source custody, large-CSV sharding and real 2022 Seoul sensor pilot (2026-10-12)

**Already completed with connected Drive:** the actual `00_INTAKE — Literature Radar` folder is now **EMPTY** after 28 direct entries (3 source CSVs, one EvoNOMOS archive folder containing 55 direct descendants and nested history, and project-specific source papers/handoffs) were MOVED WITHOUT DELETIONS, preserving file IDs. The whole original EvoNOMOS archive resides under `EvoNOMOS/06_Legacy_Runner_and_Artifacts`; original source hierarchy was not flattened. Other materials were assigned to established NOMOS/MQR/KSGT/RITHM/EvoNOMOS folder types after primary-title examination. RITHM source corpus [P11_2025_Seoul_Expressway_5min_Source](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30) holds the existing original 2025 H1 **707,465,536 B**, 2025 H2 **709,564,285 B**, and historical small 2022 CSV **6,326,958 B**.

**Actual Google Drive MCP limitation verified:** trying streamed H1 download fails HTTP **413**: source 707465536 bytes exceeds connector **268435456-byte** limit. This is NOT a missing CSV and does NOT require an agency email. A tested [row-safe user-side streaming shard program](tools/traffic_sources/split_csv_stream.py) outputs original-order, UTF-8 BOM CSV parts capped at **45 MB** including repeated header and checksum/row-count manifest. Source encoding auto-detects UTF8 or CP949. When uploaded into `00_INTAKE`, verify all shard hashes/rows, then move them into the existing RITHM dataset folder. Original 700MB authoritative CSVs remain untouched.

**Real historical original ingested and checked:** small CSV is **2022-08-01 ONE DAY**, not a 2024 or 2025 longitudinal cohort: CP949, SHA256 `6755647fd5b73b340693898bf9ff4bd8f0320bc540087f2c5135dee3af6b768e`, **56,732** actual records across **197** distinct source links, 288 nominal five-minute bins; four missing link × bin combinations. **5,760** original count cells blank on 20 entire links; **8,640** occupancy cells blank on 30 entire links; ZERO missing speed. Missing IS NOT zero. Matched within source links, 07h vs 01h hourly speed median difference **−17.625 km/h**, 178/197 link differences negative (one day descriptive). Posted source length units have not been certified: **no fabricated vehicle-hour social cost**. One day forbids P11's prospective 21-day training + 7-day test. Source original shard program actually passed original 56,732-record 7-part 1 MB smoke run and independent sha/header verifier; quote/newline case tested.

**Science and reproducibility:** Real one-day read/missingness proof is observational; no truly external 2025 high-frequency group-welfare score and no causal guidance response. The source audit and code/tests are preserved in conversation-local ZIP, SHA256 `6dd36b12a36535a67d4587a693e476af805435f8ae7d76fd878b0795ea1d02ef`; see [P12 scientific handoff](docs/rithm26_p12_source_custody_and_seoul_2022.md). No automatic CI or bot-authored commits. **RITHM-2.6 OPEN.**

---

## New: P13 — full original 2025 Seoul sensor shard fixity & actual 21d+7d forward benchmark (2026-10-12)

**RITHM-2.6 OPEN.** All original 2025 Seoul city five-minute source **38/38 user-preserved UTF-8 BOM shards**, 18,420,707 real observations, had actual shard SHA-256/record-count and native nine-column chronological checks. **Not** 365 source days: 4 completely unrecorded dates **June 9 / July 10–11 / July 15**. The CP949 originals were deleted to save Drive storage after UTF-8 transcoding; their original binary SHA cannot be recomputed from the shards. [Verified source custody](https://drive.google.com/drive/folders/1cmkEb841P5MIf4kKhl1DTBg2V3DNcH30).

Actual link-level **future sensor** source tests use 21 train-days then 7 test-days, 178 stable source IDs, comparison on same actual five-minute t bins. January Jan22–28: clock-only speed MAE **7.446 km/h** vs actually observed t−5 source state **2.439** (358,663 paired bins). October Chuseok Oct3–9: **12.580 vs 2.377** (358,463). Exploratory posthoc normal Oct24–30 **7.554 vs 2.937** (358,621). Volume/flow and q/v error improve similarly; q/v is **vehicle-hour/km sensor PROXY**, **not** individual/group true travel-time welfare. Source 5min persistence error increases at 15/30/60/120 min horizons; simple t−5 is a demanding prospective challenger. Neither human route-choice causality nor VMS information effect estimated.

[Executable P13 source CLI](tools/traffic_sources/p13_2025_forward.py) · [Detailed scientific source court](docs/rithm26_p13_seoul_2025_verified_highfreq.md) · [Machine summary JSON](docs/data/rithm26_p13_2025_aggregate.json). Original 38 data chunks and their unmodified Drive IDs remain external to GitHub; full independent locally tested code, 15/15 source/mathematical tests and per-link results in accompanying chat ZIP. No bot contributor/Actions via docs commit (`[skip ci]`).


---

## RITHM P13-R2 — 2025 whole-year traffic sensor clock regime (2026-10-12)

Original 38/38 SHA-256 validated UTF8-BOM CSV shards, 18,420,707 source observations, 178 stable link IDs; four complete network-observation absent days. 13 fixed nonoverlapping 21-day training/7-day test periods: 9 pass strict 90% daily coverage, 4 reject. On 3,223,365 paired future source points, train-only clock baseline vs prior5 sensor state speed MAE 6.314 vs 2.681 km/h, flow 36.560 vs25.757 vehicles/5min, proxy q/v 1.300 vs0.657. April16-22 DISCONFIRMS flow prior5 generalization (57.44 vs clock44.25); prior10 flow 26.58 vs prior5 57.18 on a matched clock cohort while speed still favors prior5. Train-only lag chooser catches April but misses March; source-exposed online trailing24h rival pooled 20.967 flow MAE vs prior5 25.743 but wins only 3/9 weeks. No intervention, physical sensor-fault proof, person-level route choice or group welfare inference.

Runnable GitHub annual source: tools/traffic_sources/p13_annual.py ; tests/test_p13_annual_source.py ; docs/rithm26_p13_r2_sensor_clock_regime.md ; docs/data/rithm26_p13_r2_annual_summary.json. The fully rerun local source, 12/12 local test case suite, manifests, all outcome folds and scientific report in conversation ZIP SHA256 58823b8b1f634728fe0971596a2fb449cec996a3e68c0ac39c18eed00c0694f4. Historic P13 source and README preserved. No bot contributions and skip ci used. RITHM-2.6 OPEN.


---

## P13-R2b — Full 2025 41-week rolling sensor prediction (2026-10-12)

**Different and complementary to P13-R2, not an independent experiment.** Original 38/38 SHA256-verified 2025 UTF8-BOM Seoul source shards; 18,420,707 records, 178 native link IDs, zero duplicate link-time keys; four fully missing days (Jun 9; Jul 10, 11, 15) are blocked, never zero-filled. A 21d train/7d forward-test rolling calendar from Jan22 to Dec30 yields 49 candidate weeks, 8 blocked, **41** evaluated; tests are nonoverlapping while training periods overlap, with **14,605,993** identical source sensor/bin targets for each model.

Weekly observation-weighted speed MAE km/h, calendar/prior5/trained two-lag smoothing: **6.7364 / 2.6802 / 2.6666**. Flow MAE vehicles/5min: **38.4070 / 21.2465 / 19.0641**. Proxy q/v (vehicle-hours/km per 5min) MAE: **1.3961 / 0.5819 / 0.5488**. Smoothing beats last5 in 37/41 speed weeks, 41/41 flow and proxy weeks. Its fitted lag-difference coefficient is usually NEGATIVE for volume: a smoothing effect, NOT positive trend extrapolation. Crucial April14–20 falsifier: prior5 volume MAE 60.508 WORSE than fixed weekday/clock 46.493, but train-fit two-lag smoothing 39.418. Earlier P13-R2 used a different 13 block/9 valid-week strict 28d portfolio and therefore differs in denominators; neither is externally untouched. Seven-day test week is a sequence of one-step forecasts receiving the latest observed five-minute state, NOT a 7-day policy forecast or human welfare evaluation.

[Scientific audit](docs/rithm26_p13_r2b_weekly_rolling_crosscheck.md) · [Aggregate summary JSON](docs/data/rithm26_p13_r2b_weekly_rolling.json) · [GitHub source summary program](tools/traffic_sources/p13_weekly_rolling_report.py). Original completed C++17 source walker and actual 20/20 local source contracts, per-link aggregates/manifests/run logs are in verified chat ZIP SHA256 d0f7bcecfbe891ab0daa468402d6cefb1386517823daf195314db19bd9f9828e. Gigabyte original human-free sensor source stays in Drive. Actual individual group travel time, habitual human decisions, VMS causal policy effect remain UNIDENTIFIED. RITHM-2.6 OPEN.

---

## P14 — Network-synchronous five-minute volume oscillation and memory-rival defeat (2026-10-12)

**New source-based finding:** Reparsed all 38 existing user-owned Seoul 2025 CSV fragments in independently authored C++17: **18,420,707 real sensor observations**, **178 stable route×link IDs**, 0 duplicate five-minute records, 0 invalid source keys. This source was previously used in P13: **P14 is exploratory and cannot be called an untouched human-intervention replication**. Four whole-network empty source dates remain June 9, July 10–11 and July 15, NEVER zero-filled.

**Found mechanism-relevant anomaly:** April **16–19, 2025** link vehicle counts reveal near-network-synchronous 5-minute alternation. On April 18, 5-minute-lag count MAE **92.676**, 10-minute-lag **29.186**; **173 of 174 adequately observed links** have lower lag10 source error, and **178/178 links across 16 route groups** have higher odd-slot than even-slot mean volume. April 19 parity reverses on **171/178** links. Speed does **not** show comparable period-two dominance; occupancy mostly does not either. These are negative-control observations motivating a **source-aggregation/measurement-clock hypothesis**, NOT identification of a faulty device or a real collective traffic wave. [Actual source witness C++17](tools/traffic_sources/p14_parity_witness.cpp), [scientific falsification court](docs/rithm26_p14_network_coherent_aliasing_20261012.md).

**Six pre-existing temporal baselines on identical 14,520,028 actual sensor targets** (21d train/7d rolling test, 41 weeks, all third-lag-present): volume MAE last5 **21.2106**, fixed mean(last5,last10) **19.0999**, training-only fitted ridge/bounded coefficient **19.0174**. Roughly **9.95%** source forecast improvement comes from plain two-bin averaging; the fitted coefficient adds only **0.43%** relative to mean2 (descriptive weekly resampling interval for MAE gain includes zero). Speed is different: fixed two-bin average **2.880** km/h MAE, WORSE than last5 **2.678**.

**Adversarial policy trial:** Link-local online past36-bin choice between last10 and fitted source smoothing improves the exceptional April test but WORSENS pooled annual volume source MAE (19.052→19.222). More restrictive prior-2h *citywide-synchronous* source detector with ratio cutoff 1.2 yields 19.052→**18.515** volume units (−2.815%) on identical 14,537,369 source sensor targets, but wins only **10/41 weeks** and almost all improvement is March–April concentration; after excluding the five abnormal test weeks the pooled source reduction is merely **0.134%**. Nine cutoff/window variants were inspected after discovering April; **none are sealed independent confirmation**.

**Scientific status:** original-source C++17 ingestion and daily parity witness plus actual 2025 dataset tests (**21 source/mathematical tests + 3 C++ synthetic-fixture tests pass locally**), downloadable complete code/results archive under chat (P14, SHA256 published there); GitHub commits source witness, aggregate data and scientific court WITHOUT uploading 1.6GB sensor originals. Human path choices, VMS information assignment, actual individual trip times and welfare effects remain **NOT IDENTIFIED**. **RITHM-2.6 OPEN.**

---

## P13-R3 — Independent exact source clock-parity regime replication (2026-10-12)

[Full P13-R3 source-level scientific court](docs/rithm26_p13_r3_clock_parity_independent_replication_20261012.md) · [compact machine values](docs/data/rithm26_p13_r3_source_regime_compact.json) · [aggregate checker](tools/traffic_sources/p13_r3_regime_crosscheck.py). This **does not supersede** [P13-R2b 41-week source court](docs/rithm26_p13_r2b_weekly_rolling_crosscheck.md) or concurrent [P14 independent C++ whole-network alias court](docs/rithm26_p14_network_coherent_aliasing_20261012.md): the original P14 anomaly was already discovered and published while this second-language check was underway.

All **38** surviving user-provided 2025 5-min Seoul CSV shard SHA256+rows independently rechecked, **18,420,707** actual source readings and 178 links. 41 eligible weekly 21d/7d tests and 8 entire-date-blackout rejections. On a new *more restrictive common* 14,493,248-cell 5-to-120-minute-lag cohort, flow MAE 5/10/15/30/60/120 lag: 21.084/21.709/25.455/30.700/40.746/60.129 vehicles/bin; speed 2.677/3.591/4.316/6.019/7.987/11.000 km/h. Different target masks preclude treating P13-R2b and P14 pooled MAEs as direct paired results.

Apr16–22 exact 354,194 common 5-to-40 minute target cells expose alternating volume lag loss: 5/10/15/20/25/30/35/40 minute volume MAE 57.17/26.61/57.67/33.55/59.12/38.83/61.11/42.56; 177/178 links prefer lag10 over lag5; speed remains 5-min preferable (2.786 versus 3.648 km/h). Retrospectively localized daily bursts March22–27, April3–7, April9, April15–19, with no a priori threshold guarantee. Across links April16–22, 140/178 show daily RMS even/odd volume phase gap above 20 vehicles/bin, versus zero ordinary February/August. Contemporaneous differenced volume-speed correlation near zero (+.0013) in the April episode. Source-production physical cause still **not identified**, nor individual travel-time welfare or causal human guidance. Original deleted CP949 large-source hashes remain a manifest witness only, not recomputable. Full original-source code and **11/11 locally passing** source/assumption tests in chat ZIP SHA256 `1ec4ce5c463077f61a1d13c3ca94fa7975ccd6153e1cf49acb5f759412e6ccd0`; no raw source CSV redistributed; GitHub compact checker alone is not a fresh source-read.

---

## Historical RITHM-2.0 README (preserved in place)

**RITHM — Route-choice Inertia and Traffic Hysteresis Modeling**

**RITHM-2.0 — Behavioral–Structural Reconciliation: History-Causality Discrimination, Micro-to-Macro Welfare Mediation & Independent-Witness Admission Court**

This is the active, human-choice research repository. The explanandum is why people retain or revise familiar routes and how those decisions interact to cause collective traffic outcomes. Measurement, custody and CI serve that question; they are not the question itself.

## First human-network empirical result

Ashraf et al. (2023) Study 1, the original author-provided 18-player live-group repeated-route-choice experiment, contains 10 sessions × 100 rounds × 18 participants (18,000 choices). The game payoff identity is `W(s)=-36+66s-5s²`, where `s` is side-road occupancy. The unique pure-strategy Nash occupancy is 6, with group welfare 180. Integer social optimum is 7, with welfare 181.

A direct descriptive replay of the original 1,000 group-rounds found average side occupancy 5.986, population variance 3.957804 and mean group payoff 160.126. Consequently `181 - E[W(s)] = 20.874 = 1.08498 + 19.78902`: 94.80% of the observed optimum shortfall is the exact occupancy-variance term. This is an algebraic, descriptive allocation/dispersion decomposition, **not** evidence that individual habit caused that loss or that new information would improve welfare.

Across 990 successive within-session group transitions, 5.58 of 18 participants changed their road on average; 118 transitions had some switching without any net change in side-road occupancy. Source and method are described in the [active Notion lab record](https://app.notion.com/p/3f4ef561cf9281da9fa5ef9084913994).

Study 2's earlier +12.07 percentage-point randomized information-onset switching result involves **prerecorded opponent distributions**, not simultaneous live-group congestion, and cannot be relabeled a causal group-welfare improvement.

## Information onset, selection and group welfare (continued 2.0)

Reconstructed all 10 live human sessions by treatment and checked the
round-51 information onset. Study 1 has two control groups, two groups
with all 18 informed, three with the four most frequent *baseline*
switchers informed, and three with the four least frequent baseline
switchers informed.

Late-minus-early group-payoff changes (experimental currency units per
group-round; **descriptive session means only**) were: Control +12.23,
All +2.39, Frequent-4 -0.19 and Infrequent-4 +0.81. These do **not**
establish that information lowers group welfare: session counts are
2/2/3/3, the untreated groups also learn over time, and the informed
individuals in both four-person treatments were selected on prior behavior.

See [Information timing and welfare](docs/INFORMATION_TIMING.md)
for exact definitions, author-paper comparison and limitations.

```sh
python rithm20_information.py path/to/study1.csv --strict-source
```

## Run

Download the original Ashraf et al. Study 1 CSV (`study1.csv`) through the legitimate source. Raw human participant data and any credentials are intentionally absent here.

```sh
python rithm20.py path/to/study1.csv --strict-source
python -m unittest discover -s tests -v
Rscript R/check_study1.R path/to/study1.csv
```

Python 3.11+ only needs its standard library; the optional base-R script independently verifies the group aggregation/payoff identity. CI runs only the synthetic 2-round fixture and **does not** itself re-run the human dataset. The research has not admitted an information→live-group welfare causal estimand or causal habit/memory mechanism.

## Retired science and minimal Git branch lifecycle

The S02 SUMO/MoST programs and historical scientific receipts are **not**
active RITHM-2.0 code. The original pre-2.0 Git history is not rewritten.
Tracked source backups in
[Drive RITHM Code Backups](https://drive.google.com/drive/folders/16T5wRdLx_nSMgiMSZ7K1e6EugJqum9mJ)
were independently compared by Git blob identity and content:
**21/21 old-main blobs** and **26/26 experimental-runner blobs**.
A [30-commit historical lineage ledger](https://docs.google.com/document/d/10scZkn3ANdHBzFjWI8vWnEvlFYz2iZRQphdEu9cTBtY/edit)
records both old branch heads, Git parent/tree hashes, authors and commit
messages.

Historical frozen head IDs:

- Old scientific main: `0f857e34fa1203acd62f84139a0e614c597865b4`
  (ancestor of the present `main`).
- Experimental SUMO runner: `c5f219d63b01dbb197afe2f6a968cc1f745c3bca`
  (source and commit metadata preserved in Drive).

**Git branch policy:** `main` is the only persistent live branch.
Temporary branches exist solely to carry one open PR and must be pruned
after merge or closure. Never retain duplicate experimental/archive refs
as permanent repository clutter. Notion and Drive preserve the full
historical research context; GitHub `main` contains minimal executable
current science. Do not regenerate branch sprawl in order to archive it.

**Archive limitation:** content-preserving Google Docs and commit-metadata
ledgers are **not** a complete Git bundle. If exact restoration of a
historical Git commit graph is required, obtain and verify a `git bundle`
*before* retiring its last branch ref. Do not mistake a recorded SHA for
a still-resolvable remote commit object.

The frozen S02.16 verdict remains
**CLOSED — CONDITIONAL_POSITIVE_EVIDENCE / NATIVE_ADMISSION_HOLD**.

## Polyglot doctrine

Python owns the group-level analysis and data validation. Base R independently audits the payoff identity using a separate parser and evaluator. GitHub Actions YAML controls read-only tests; CSV and JSON carry research data/results; Markdown/Notion carry the scientific claims. Legacy Stata, SUMO, shell and XML execution belong to the archive. No Rust/Lean/Julia language adoption without an actual new computational or proof requirement. See [polyglot ledger](docs/POLYGLOT.md).

No automated next research version or expensive server replay is implied by this codebase.
