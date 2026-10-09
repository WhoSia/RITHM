# RITHM-2.0

**RITHM — Route-choice Inertia and Traffic Hysteresis Modeling**

**RITHM-2.0 — Behavioral–Structural Reconciliation: History-Causality Discrimination, Micro-to-Macro Welfare Mediation & Independent-Witness Admission Court**

This is the active, human-choice research repository. The explanandum is why people retain or revise familiar routes and how those decisions interact to cause collective traffic outcomes. Measurement, custody and CI serve that question; they are not the question itself.

## First human-network empirical result

Ashraf et al. (2023) Study 1, the original author-provided 18-player live-group repeated-route-choice experiment, contains 10 sessions × 100 rounds × 18 participants (18,000 choices). The game payoff identity is `W(s)=-36+66s-5s²`, where `s` is side-road occupancy. The unique pure-strategy Nash occupancy is 6, with group welfare 180. Integer social optimum is 7, with welfare 181.

A direct descriptive replay of the original 1,000 group-rounds found average side occupancy 5.986, population variance 3.957804 and mean group payoff 160.126. Consequently `181 - E[W(s)] = 20.874 = 1.08498 + 19.78902`: 94.80% of the observed optimum shortfall is the exact occupancy-variance term. This is an algebraic, descriptive allocation/dispersion decomposition, **not** evidence that individual habit caused that loss or that new information would improve welfare.

Across 990 successive within-session group transitions, 5.58 of 18 participants changed their road on average; 118 transitions had some switching without any net change in side-road occupancy. Source and method are described in the [active Notion lab record](https://app.notion.com/p/3f4ef561cf9281da9fa5ef9084913994).

Study 2's earlier +12.07 percentage-point randomized information-onset switching result involves **prerecorded opponent distributions**, not simultaneous live-group congestion, and cannot be relabeled a causal group-welfare improvement.

## Run

Download the original Ashraf et al. Study 1 CSV (`study1.csv`) through the legitimate source. Raw human participant data and any credentials are intentionally absent here.

```sh
python rithm20.py path/to/study1.csv --strict-source
python -m unittest discover -s tests -v
Rscript R/check_study1.R path/to/study1.csv
```

Python 3.11+ only needs its standard library; the optional base-R script independently verifies the group aggregation/payoff identity. CI runs only the synthetic 2-round fixture and **does not** itself re-run the human dataset. The research has not admitted an information→live-group welfare causal estimand or causal habit/memory mechanism.

## Retired code and exact archival identity

The old S02 SUMO/MoST runner and scoring scripts, all old Actions workflows, and historical receipts were retired from the active main tree. Two immutable legacy references preserve old HEADs, and their per-file source-text snapshots and Git blob SHA values were read back in [Drive RITHM code backups](https://drive.google.com/drive/folders/16T5wRdLx_nSMgiMSZ7K1e6EugJqum9mJ).

- [Old main](https://github.com/WhoSia/RITHM/tree/archive/pre-rithm-2.0-main-20261009)
- [Old experimental runner](https://github.com/WhoSia/RITHM/tree/archive/pre-rithm-2.0-experimental-20261009)

The historical S02.16 outcome remains **CLOSED / CONDITIONAL_POSITIVE_EVIDENCE / NATIVE_ADMISSION_HOLD**; the missing original p000 supervisor receipt has not been fabricated.

## Polyglot doctrine

Python owns the group-level analysis and data validation. Base R independently audits the payoff identity using a separate parser and evaluator. GitHub Actions YAML controls read-only tests; CSV and JSON carry research data/results; Markdown/Notion carry the scientific claims. Legacy Stata, SUMO, shell and XML execution belong to the archive. No Rust/Lean/Julia language adoption without an actual new computational or proof requirement. See [polyglot ledger](docs/POLYGLOT.md).

No automated next research version or expensive server replay is implied by this codebase.
