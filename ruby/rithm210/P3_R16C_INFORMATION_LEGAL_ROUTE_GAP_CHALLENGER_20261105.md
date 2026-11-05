# RITHM-2.10 P3-R16C — Information-Legal Route-Gap Challenger; Not Qi RDAB-SP

2026-11-05 KST. This is a direct original-source replay, not a confirmation-grade external experiment.

## Source and scoring scope
The author-approved [Noussair–Qiao raw ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view) supplies 24 original sessions, 5,616 six-person target group transitions (SHA256 of filtered source CSV `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`). **Only full-information treatment 3** is used for this new challenger (1,872 group transitions, 11,232 actor switches), because the model explicitly needs contemporaneous knowledge of BOTH routes' experienced costs; under treatments 1/2 the uninformed subjects could not lawfully access these values. Fold split: sorted 24 sessions, sixfold, 20 training and 4 entirely heldout sessions each. All reported scores refer to original observed source state and one-step switch labels, NOT unconstrained simulated 40-step counterfactuals.

Model specification: for route r∈{A,B}, p(switch|r,costs)=sigmoid(intercept_r+slope_r*(cost_current_route−cost_other_route)); c_A(n)=n, c_B(n)=2(6−n). Four fitted parameters across the two routes, with ridge 0.01 (un-normalized training likelihood) and a deterministic capped two-variable Newton solver. Six actor Bernoullis are independent conditional on observed Full-information group state. The two current costs come from the *observed* contemporaneous n for a Full-information subject, not from next-period outcome. All training rows from a heldout session are excluded.

**Critical prior art: This is a cost-gap, route-dependent logistic comparator inspired by the accessibility and route-specific switching questions in Qi et al. (2024); it is NOT a reproduction of their RDAB-SP equation.** The Qi model specifies route-specific reconsideration/inertia parameters and a separate logit destination attraction term, plus multiple scenarios, equilibrium predictions and policy examples. No Qi-paper-equivalent score or novel claim is asserted here.

## Real-data results

| Target | Groups | Baseline Markov joint U,D LL | Train-only epoch20 independent LL | Route-gap logistic independent LL |
| --- | ---: | ---: | ---: | ---: |
| Full information, periods1–10, all n | 480 | 2.148221 | **2.103428** | 2.173019 |
| Full information, periods11–29, all n | 912 | 1.875955 | **1.874984** | 1.905719 |
| Full information, periods30–39, all n | 480 | 1.666227 | **1.633371** | 1.774133 |
| Full information, all periods | 1,872 | 1.891990 | **1.871607** | 1.940517 |

New comparator next-occupancy logloss: early 1.542852, middle 1.375838, late 1.258470. Predicted next-period excess cost: early 3.133631 (actual 4.0125), middle 3.053216 (actual 2.838816), late 3.005031 (actual 2.06875). All models are trained using other sessions, but many modeling decisions arose from exploration of the same overall experiment. Small positive or negative differences are exploratory, not causal.

The route-gap logistic's coefficients across folds were close: for A incumbent, intercept approximately [-1.735,-1.636] and slope [0.139,0.163]; for B incumbent, intercept [-0.904,-0.804] and slope [0.131,0.143]. A positive cost-gap slope is interpretable as cost responsiveness but not direct identification of learning or deliberation.

Both local Ruby 3.3.8 and an independent SciPy BFGS Python implementation (used for numerical cross-verification only, not published as the mainline) matched the published aggregate joint logloss to >6 decimal places. Local synthetic Ruby test: 5 tests, 14 assertions, 0 failures. Source-specific data and row-level predictions are not committed.

## Consequences for RITHM publication strategy

R16B showed that the original epoch20 logloss improvement becomes negligible over all 5,616 groups; it is strongest for Full treatment. R16C shows that a simple treatment-legal route-specific cost-gap competitor does **not** recover Full epoch20's joint switching distribution at this original sample. It does not follow that epoch20 is the best feasible independent learner. In particular it is still crucial to implement **actual Qi RDAB-SP (not merely a cost-gap proxy)**, match original Noussair–Qiao SSM family and EWA learner on identical heldout sessions, and evaluate turnover, occupancy, finite-horizon welfare and policy stability. Genuine out-of-source prospective prediction is still missing.

The original research mission remains micro experience/information and legal learning/update schedules → collective adaptation dynamics → finite-horizon congestion welfare. An elementary logistic comparison alone is a reproducible negative-control research unit, not an independent publishable contribution.

## Files and verification
- [Full-info route-gap Ruby](p3/full_info_route_gap_logit.rb)
- [Synthetic test](p3/test_full_info_route_gap_logit.rb)
- [Earlier R16B all-state source evaluator](p3/all_state_epoch_cv.rb)
- [Qi 2024 canonical Drive](https://drive.google.com/file/d/1sC_O0U_T90IdUeHXA400sgQJn1mAl4ar/view)
- [R16A bibliographic audit](P3_R16A_00_INTAKE_PRIOR_ART_AND_EXACT_WELFARE_20261105.md)
- Experimental SHA checked in local R16C source module. Final GitHub Actions run+logs and exact remote checked-out HEAD execution remain **HOLD**.
