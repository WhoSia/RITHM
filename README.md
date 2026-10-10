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

**P8 GATES:** SOURCE INFORMATION CLOCK CORRECT / CROSS-TOPOLOGY MATHEMATICAL COUPLING PASS / ORIGINAL EXTERNAL GROUP HUMAN DATA BLOCKED / EXTERNAL HUMAN WELFARE SCORE NO SCORE / HABIT CAUSALITY HOLD. Do not tune 2017 P7 model or claim external success until new human group data pass admission.


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
