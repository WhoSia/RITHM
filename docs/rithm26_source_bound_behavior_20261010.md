# RITHM-2.6 — Original human S2 source audit and staged behavior court

**2026-10-10 · OPEN · six-session human leave-one-session-out exploratory prediction; no memory causal claim.**

[Author source](https://doi.org/10.1371/journal.pone.0184191) · [Original S2 Google Drive workbook](https://docs.google.com/spreadsheets/d/1Kv-fWLa6kP_tv9PpgNDUYIV3oiC-zmRc/edit) · [Research Notion record](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021)

**Source custody:** 2017 zTree XLSX SHA256 f2047f7c2ae8999a9f0660f3b5c192aea171b715284bf2aa05b40c10b902d863, 6 sessions × 2 groups × 2 treatments × 20 rounds × 12 people = 5,760 individual choices (480 group-rounds). Group route counts match final individual choices for every group-round; zero staged-vs-final route inconsistencies. Treat experiment sessions as independent CV units, not 5,760 human-independent observations.

**Design:** A–B or A–C chosen BEFORE observing current incident. Only online-information A–C entrants can observe incident at node C prior to C–B versus C–D choice. Treatment coding from staged-choice source columns, NOT Profit_Info label: session 5's staged choice is marked Profit_NoInfo in its source header. Sessions 1–3 no-info-first; sessions 4–6 info-first.

**Original costs:** c1=10+n1+n2; c2=13+n2+19z; c3=22−n1, n1+n2+n3=12. Summation identity: C=264−24n1−9n2+2n1²+2n1n2+n2²+19zn2.

**P1 anomaly:** EXACTLY 6 group-rounds among 480 have named recorded Cost sums not equal to theoretical cost based on original route-flow columns. Summed raw Cost means: noinfo 210.8625 / info 219.1250. Recomputed source-flow aggregate means 210.6291667 / 219.1625, matching published Table 5 rounded 210.629 / 219.163. Retain both definitions and the exact six-row discrepancy receipt; never silently repair individual source rows. The 6 anomalous group-rounds are:
- (session, block, group, period) (3,3,2,16): raw 210, formula 214
- (4,3,1,5): raw 214, formula 200
- (4,3,2,17): raw 208, formula 196
- (5,2,2,17): raw 195, formula 200
- (5,3,2,1): raw 220, formula 208
- (5,3,2,19): raw 210, formula 192

**P2 models:** six session-heldout logistic CV models with fixed C=1, no outcome-driven hyperparameter selection. S0 features: regime, order, round, lagged public network occupancy and incident; S1 adds previous named route/route streak; S2 adds experienced own and relative cost histories. Upstream binary choice is AC vs AB (5760); downstream CB vs CD only among actual AC entrants (3511); current incident enters ONLY for node-C online-information choice.

| Feature family | Upstream held-out log loss | Downstream held-out log loss | Group conditional realized-shock cost MAE |
|---|---:|---:|---:|
| S0 | .666493 | .550630 | 9.77335 |
| S1 | .653405 | .524417 | 9.70436 |
| S2 | .653507 | .524148 | 9.84203 |

**Interpretation:** route history improves person-level prediction but more cost-history features do not improve upstream or group-cost prediction. Group cost prediction presumes independent people and extrapolates downstream behavior to people not entering C; it is NOT prospective information-policy welfare identification. Fixed-group no-info conditional shock subgroup observations are retrospective only (actual current incident was not displayed). The 12-member group welfare function is quadratic, so omitting interpersonally correlated route decisions suppresses covariance terms. Do not promote universal information value, memory causality, or a new PSR theorem from this court.

**Research next:** distinguish stable taste from genuine learned inertia, prospective information clock, cross-person covariance and a session-level independent-group welfare outcome. Benchmark against older CLOCK/STATE, 2.2 negative micro→macro findings, and RITHM S02.6 predictive defeat. Keep 2.5-D’s falsified memory-necessity claim in the genealogy. Read-only S2 source and no GitHub Actions in exploratory work.
