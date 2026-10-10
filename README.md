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
