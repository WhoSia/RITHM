# RITHM-2.7 P26 — Observed Exposure vs Offered Signal, and Equal-Horizon Strong-P6 Welfare Prediction

**2026-10-13 · RITHM-2.7 sole active Flowing mainline.** A genuine scientific rerun of original 2017 human laboratory source and older P6 executable model, not an independent new human experiment or an identified causal policy effect.

## Source and independence

Original Wijayaratna, Dixit, Denant-Boemont & Waller (2017), PLOS ONE, [paper](https://doi.org/10.1371/journal.pone.0184191), [source S2](https://doi.org/10.1371/journal.pone.0184191.s002), owner Drive XLSX original checksum `f2047f7c2ae8999a9f0660f3b5c192aea171b715284bf2aa05b40c10b902d863`. Owner's original historical P6 source ZIP, SHA `9b825f1a5b52c757bbb0ac227165114683bebc6617fbe8853b76767139751ee5`, was recovered and its ACTUAL original model code refitted. Source-derived packed routes [in repo](../data/rithm23_wijayaratna2017_routes.csv) and original S2 cross-match at **every person / group / session / round**, all 480 source group-rounds, original incidents and route-count cost. Original six source individual-Cost discrepancies preserved.

The same **2–20** round mask applies to P25 and P6 fitting/scoring, unlike older historical 1–20 P6 published scores: 5,472 actual recorded human routes, 3,332 observed C-eligible entrants, 456 group-rounds, six session-held-out folds (912 human decisions and 76 group rounds/fold). Training-group residuals use only the other five sessions (380 group rounds). This source has already been reused repeatedly in RITHM; this is **exploratory retrospective model checking**, NOT an untouched validation or an original-data field intervention.

## Strict comparison

Human full-route logloss / original theoretical source cost, pre-current-shock group MAE under independent people / same expected group MAE with training-only residual:

| Competitor | Full-route logloss | Independent group MAE | Same train-only group-residual MAE |
|---|---:|---:|---:|
| **P6 older personal propensity+last choice** | 0.931209 | 12.705169 | 12.383690 |
| **P6 + first A choice + actual C eligibility history** | 0.930065 | 12.706579 | **12.367585** |
| P6 plus historical real recorded individual Cost | 0.930344 | 12.834600 | 12.499707 |
| P25 LEGAL_EXPOSURE | **0.929157** | 12.804076 | 12.481294 |
| P25 LEGAL_COST, theoretical cost proxy | 0.929842 | 12.652082 | **12.322160** |

The P6 group residual uses P6's **original training-only** `D=(X−E X)^2−sum Var(ABD)+(Y−E Y)^2−sum Var(route≠ACD)` group statistic, partitioned by arm+realized incident, shrunk n/(n+120), and averaged over the original 4/20 experimenter-known *pre-shock* hazard. The P25 fair control is subject to the **identical** calibration rule. It also replicates both original P25 unadjusted scores to floating-point tolerance.

- Strong P6 vs **uncalibrated** P25: P6 group MAE 12.3676 beats P25 LEGAL_EXPOSURE 12.8041 in 6/6 folds, but this is **not a fair model architecture comparison**.
- Strong P6 vs **equally calibrated** P25 LEGAL_COST: P25 12.3222 vs P6 12.3676 (mean P6 minus P25 0.045424), just **3/6** session wins. Illustrative paired six-session t interval [−0.146815,+0.237664]; contains zero, NOT confirmatory inference.
- P25 LEGAL_EXPOSURE personal logloss vs strongest P6: gain 0.000908, just 3/6 sessions; illustrative interval [−0.003237,+0.005054] also contains zero.
- Added person-level actual historical Cost worsened P6 group MAE. Stronger individual-route fitting is **not evidence** of a robustly superior collective outcome model.

**Scientific limits:** both model families use teacher-forced actual past routes, group cost estimated under individual conditional independence, and hypothetical unobserved stage-C choices for A–B nonentrants. The P6/P25 group residual can contain individual mean-calibration error and is NOT causally established driver coordination. Original seven/multiple candidate comparisons are outcome-exposed and source repeatedly reused.

## Actual exposure is a missing measurement, not a feature-engineering problem

2017 S2 has real route selections, actual incidents, group costs and route-click/confirmation time columns such as `TimeABChoiceOK`, `TimeACChoiceOK`, `TimeCBChoiceOK`, `TimeConfirmChoiceOK`. It does **not** independently log per-person advice content/version reception, advice rendered/opened, attention/understanding, or individual compliance. Being assigned information-at-C and actually reaching C = **eligible for offered information**, not verified reading or advice-caused response.

Observed P25 source conditional eligible C–B rates in info arm: `m_normal=869/1399` and `m_incident=7/370`. In the **purely constructed** mixture `m_z=(1−α)b+αr_z`, ALL-READ `α=1,r_z=m_z` and PARTIAL-READ `α=(1+m_normal−m_incident)/2≈0.801,b=m_incident/(1−α),r_normal=(m_normal−m_incident)/α,r_incident=0` give *identical observed human choice margins*. This is a mathematical observational-equivalence witness, NOT evidence that 80.1% read. A toy `α≥|m_normal−m_incident|≈0.602` requires **unverified constant attention fraction, state-invariant nonreaders and compatible C entrant composition**; it is NOT a measured lower bound on readership or reliable causal exclusion. Without such assumptions, no nonzero reading fraction is empirically identified.

Under stage-legal timing, real advice content can matter at C only after actual A–C entry. A random session/group information offer can potentially inform intention-to-treat **group** comparisons with independently measured groups and justified randomization/carryover assumptions, but not automatically individual uptake and mechanistic mediation. The original 2017 published mean theoretical cost contrast (info minus blind +8.53333) is descriptive and does not identify the full offer→read→response→group congestion→experienced welfare chain.

## P26 status and next falsifier

**SOURCE MATCH + ORIGINAL P6 CODE RE-EXECUTION PASS**; same-horizon P25 train-only calibration PASS; **strong P6/P25 winning claim NOT ESTABLISHED**; constructive latent reading nonidentification PASS; actual person-specific advice receipt/view/attention/compliance HOLD; causal preference/history and group welfare HOLD; independent new human field transport HOLD.

**Next actual human-network evidence:** an independent session/group interference-aware guidance assignment, authoritative advice version/render event linked to eligible person at node C, direct action, full independent group route-specific experienced cost and precommitted multi-round benefit/harm horizon, with frozen P6/P25 calibrated rivals. If unavailable report a sharp assumption-bound, NOT a new causal welfare claim. Distinct 2025 Seoul observational sensors are NOT the same 2017 people.

[Current RITHM-2.7 Notion](https://app.notion.com/p/3f8ef561cf9281829b60c1085605448d) · [P25 source comparator](rithm27_p25_human_info_choice_welfare_rivals_20261013.md) · [Flowing inheritance](rithm27_flowing_transition_20261013.md). Full P26 source-fidelity scripts, original archived P6 source, folds, fitted controls, ten passing local tests, and SHA-verified original workbook instructions are supplied in the user-local P26 replay ZIP (archive SHA-256 `c2718e4e5f72ae172d094bc617b5f41be2ac322d965159e2e13e5336099565ef`). No original 2017 XLSX or copyrighted PDF redistributed in ZIP. No GitHub Actions run.
