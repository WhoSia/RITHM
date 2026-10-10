# RITHM-2.6 P7 — Initial-Conditions-Corrected Joint Staged Route Choice, Sharp Missing-C-Choice Bounds & Untouched Group-Welfare Transfer

2026-10-11. Original-human six-session exploratory numerical court. RITHM-2.6 OPEN. **No demonstrated causal habit, new general theorem, or new truly external independent group welfare score.**

Sources: [original 2017 experiment](https://doi.org/10.1371/journal.pone.0184191) · [2017 S2 original participant XLSX](https://docs.google.com/spreadsheets/d/1Kv-fWLa6kP_tv9PpgNDUYIV3oiC-zmRc/edit) · [P1–P7 canonical Notion](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021) · [P7 Research OS Harvest](https://app.notion.com/p/3f5ef561cf928127a7dbf7e7b6dde6d1)

## Conditional shared-effect joint staged likelihood

Original source 2017 six sessions, 12 groups of 12 humans, 5,760 human decisions, 480 group-rounds; exactly 4 incidents per 20-period group-arm panel; S2 SHA256 f2047f7c2ae8999a9f0660f3b5c192aea171b715284bf2aa05b40c10b902d863. Keep six published individual-cost source anomalies separate from route-count-based original group C cost.

Initial A1 response is conditioned upon, not double-counted. Latent a_i | y_A1 ~ Normal(gamma*(y_A1-.5),sig^2). Model A(t>=2): logit p_A=x_A*beta_A+a_i. Model C (only actually eligible A–C entrants): logit p_C=x_C*beta_C+lambda*a_i. Current shock enters only at C when ONLINE, never A or offline C. Joint observed likelihood integrates shared a_i via 9-point Gauss–Hermite and L-BFGS-B; all six held-out fits converged. No counterfactual C decision is assigned to historical A–B entrants as a labeled outcome. However group welfare prediction extrapolates p(C|A–C) to anyone who might enter C under a different first-stage policy: this extrapolation is NOT empirically identified. Lagged common congestion state may be endogenous; this is a restricted Wooldridge-inspired likelihood working model, not a completed strict-exogeneity causal estimator.

## All matched scores 2–20 (six original sessions, five training vs one held out)

| P6/P7 model | First-stage logloss | Eligible node-C logloss | Final 3-route logloss | Preincident group MAE (independent people) | Train-only conditional-shock group cost calibration MAE |
|--|--:|--:|--:|--:|--:|
| P6 STATE | .666175 | .546658 | .999065 | 12.860869 | 12.466254 |
| P6 older history + last | .626775 | .500031 | .931121 | 12.691907 | 12.357156 |
| **P6 plus first choice + C eligible history** | **.626311** | **.498962** | **.929999** | **12.695040** | **12.330329** |
| P7 shared latent individual effect | .629784 | .509076 | .939630 | 12.921752 | 12.509932 |

Compared with best matched P6, P7 full route logloss +.009632 in six of six held-out sessions. Source group MAE after training shock-bias calibration +.179603 in five of six sessions. Illustrative six-session paired t95 difference interval [-.107821,.467027] includes zero. All full P7 fits converged. This is a genuine **negative model-prediction result**, not demonstration that all dynamic correlated-effects methods fail. All current P6/P7 teacher-force the heldout participant's past choices, so these are not trajectory-freerun policy forecasts.

## Sharp observationally equivalent counterfactual C choices

At occupancy (6,0,6), original total group cost C=192 with or without incident. Under hypothetical exogenous diversion of one A–B person to A–C while others fixed, her choice C–D results in C=194 for z=0 or1; choice C–B results in C=196 if z=0, C=215 if z=1. These conditional choices never observed for a former A–B entrant. All such choices compatible with same original A–B history. At shock chance .2, sharp source-witness expected cost effect [2,39/5]=[2,7.8] units, attained. No group-wide actual policy impact identified, no new general Fréchet theorem.

## External group transfer is still BLOCKED DATA

Ten original prior-art PDFs all validated by first-page source and moved/renamed from user Drive 00_INTAKE to canonical 10_PAPERS. Titles: Yu–Gao 2019, Wooldridge 2005, Honoré–Kyriazidou 2000, Noussair–Qiao (published 2025, supplied author revised manuscript 2026-07-24), Unnikrishnan–Waller 2009, Manski 1993, Brock–Durlauf 2001, Ben-Elia–Shiftan 2010, Lu–Gao–Ben-Elia 2011, Bartl et al 2022 (supplied arXiv v2, not final journal PDF). This enhances prior-art authority but is NOT participant-level raw data. Existing Ashraf 2023 18-person 2-route data studied since 2.0 have nonhomologous two-node action and monetary payoff, and cannot validate this C-stage policy predictor as-is. Noussair–Qiao supplementary raw data exist according to publisher but have NOT been downloaded and independently group-normalized in this stage.

**Frozen external validation gate:** acquire entirely new original participant×round×group data and codebook; verify source and cluster randomized assignment, select matched stage outcome mapping before reading outcomes, freeze model and hyperparameters, compare the STATE/CLOCK and P6 and P7 decision logloss AND expected group-welfare MAE with simple-intercept and full residual competitors, report group-level uncertainty and full 20-round simulated cost separate from one-step observed-history. If experimental network has no actual node-C recourse, mark exact staged-policy transfer not applicable and test only welfare algebra with correct new cost function.

## Reproducibility and safety

The self-contained CHAT research package, not the Git repository, contains rithm26_p7_joint_cre.py, rithm26_p7_matched_baseline.py, p7_identification_bound.py, P6 parser/feature dependencies, machine-readable full fold results, exact gradient check and **30/30 combined P6+P7 regression passes**. Neither the source person XLSX nor any original PDF is included. The original P7 test expectation for a zero fixed-coefficient yet nondegenerate latent variance was incorrect; fixed the TEST contract, reran 30 tests PASS. No GitHub Actions run; this documentation commit explicitly uses skip CI.

**VERDICT:** P7 joint source-staged estimator fit PASS, source time legality PASS, personal-route predictive victory FAIL, group welfare predictive victory FAIL, sharp local C nonentrant potential-branch witness PASS, ten original-literature PDFs canonicalized PASS, fresh external group confirmation BLOCKED, causal habit and social interference effect and general novel theory HOLD. **RITHM-2.6 OPEN.**