# RITHM-2.6 P8-E2 — Recovery of Previously Exposed Lyon Source and Within-OD History-Choice Audit

**2026-10-11 · NO new independent group welfare score · NO causal habit claim.**

## Provenance and historical exposure
Original [2019 Lyon Figshare source](https://doi.org/10.6084/m9.figshare.9791285) publicly licensed CC BY 4.0, version 2 author data; original archived [Drive ZIP](https://drive.google.com/file/d/1E7kuUOqEZa5lw6z5OenkMj9sm4byR804/view), created in RITHM Drive on 2026-08-31, was recovered in raw byte form this iteration. Original ZIP SHA-256 `d753a7e09d64b0ad8b8791f47812c7a61f69c5d206fa84359dc8734460e53c46`. CSV MD5 `fa8b8c97f49e2f2c5c17f9220a0be1e0` and dictionary MD5 `daac1e1f7175e9781060afcc76df7a5d`, both matched author Figshare checksums. The source was ALREADY handled in RITHM-ORIGIN chat archive 14.md, notably M05.2, M05.133R, S02.7 and S02.8. M05.133R's anti-frailty 19-to-10 test p≈.136 retained negative inference; S02.7 rejected Lyon as independent simultaneous-group welfare source. No fresh untouched holdout claim.

## Author-subset native contract
- 10,002 long-form rows / 3,334 unique decisions / 483 named original player IDs / 30 separate OD pairs. R1,R2,R3 exactly once each choice, CHOSEN 1 exactly once. t1 no displayed-time-info 1,069 choices, t3 visible-time 2,265. Of 483 people, 397 have >1 decisions; 1,567 decisions follow a previous same-person, same-OD choice.
- Native `TT_INFO` exists as a data-analysis field in BOTH t1 and t3, but is masked for t1 human predictors; using it in t1 as an observable signal would violate source clock. Native `TYPE=validation` does not mean a fresh study-level confirmatory cohort.
- Softmax ridge-regularized choice predictions across original 3 route alternatives. M0 label/treatment prior; M1 geometry; M2 t3-visible TT; M3 prior route label across ODs (cannot be called road habit); M4 last route and older chosen-route frequency restricted to same person and exactly same OD. Previous choices in heldout test persons/ODs fed sequentially ONLY after those past rounds (teacher-forced one-step). No counterfactual guide rollout.
- Five deterministic HASH participant-heldout folds and separate five OD-heldout folds, no model family hyperparameter tuning by test label.

| Alternative choice model | Person-disjoint all logloss | Person t1 | Person t3 | OD-disjoint all logloss |
|---|---:|---:|---:|---:|
| M0 treatment-path prior | 1.05768 | 1.05982 | 1.05666 | 1.06108 |
| M1 path geometry | 1.05115 | 1.05844 | 1.04771 | 1.05712 |
| M2 geometry + t3-only TT | 1.02378 | 1.06073 | 1.00634 | 1.02917 |
| M3 cross-OD label history (unsafe 'habit's semantics) | 1.01716 | 1.05253 | 1.00047 | 1.02282 |
| M4 **within-OD** history | **0.98886** | **1.02400** | **0.97228** | **0.99325** |

M2–M4 improvements >0 for 5/5 participant and 5/5 OD folds; M2 accuracy on person folds .492, M4 .531. Source data and models were previously exposed, no prospective statistical significance claimed. Stable preferences, heterogeneous route perception and sequential effects all remain rivals. Lyon has no valid contemporaneous live-human independent group-welfare outcome, hence no group-welfare MAE. Old 2017 exact C-node costs cannot transfer.

## Actual engineering result
Read-only original source recovered; source-specific Python+SciPy softmax code / 2 aggregate JSON fold-score results / 12 unittest checks / Korean scientific report in chat file `RITHM-2.6_P8-E2_Lyon_Recovered_Source_Choice_Court_20261011.zip` with SHA-256 `b9fa533c1de18ea752b6afd0e7e46cb50584d3b2e371ef58ac5de04d72de53f4`. No participant-level raw CSV or copyrighted manuscript redistributed in code ZIP. Reproduce using original user Drive ZIP at above exact source path. **12/12 tests PASS.**

**Research direction:** public data directly first, institutional outreach not a prerequisite; future test must distinguish stable individual choice heterogeneity from true lagged choice dependence and seek a genuinely new source with live multi-person simultaneous welfare data. Exposure history is scientific evidence, not administrative nuisance. RITHM-2.6 remains OPEN.
