# 2026-11-01 — Real-source sixfold empirical joint-switch baseline (Ruby)

## Data and leakage contract
Noussair–Qiao original `data_task_all_switch_230705.csv` from Drive ZIP: https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view . Filter trt 1..3; exclude sessions 2 and 101; periods 1..39. For each (session,section,Group,period) exactly six participant rows, with prev A count, switch B->A and A->B, and next A count cross-checked by the identity next_A=prev_A+up-down. 24 sessions; 5616 grouped transitions; session sizes 117/234/351.

Session assignment: sorted session IDs, index modulo 6; each heldout fold has four sessions, training uses other 20 sessions, no same-session learning. This split is newly defined and is NOT asserted identical to prior EWA folds. Predictor inputs are study-level treatment and previous A count; it MUST NOT be presented as legal actor-level information under uninformed treatments. Hence the empirical joint model is an ORACLE-STATE comparative descriptive group baseline, not a deployable individual forecast.

## Results — independent local Ruby execution; not GitHub Actions
Joint U,D heldout log loss:
- feasible-support global frequency baseline: 2.210806869264398
- conditional on treatment and previous A count, hierarchical-smoothed baseline: 1.998812313586529
Pooled delta: -0.21199455567786907.

Next A-count heldout log loss:
- feasible-support global frequency baseline: 1.6141032273028992
- conditional baseline: 1.4122911599141166
Pooled delta: -0.20181206738878266.

Conditional better in 24/24 sessions for both outcomes. The global predictor is itself conditioned on feasible support through previous A count; do not call it a completely unconditional model. These are within-study exploratory out-of-fold results, not a claim of population transfer.

## Important comparison HOLD
Prior archive reported EWA+inertia pooled joint loss ~1.967869, count loss ~1.438414, using earlier folds and a different predictor artifact. Although their numerical magnitudes resemble these results, comparisons are NOT controlled: fold assignments, cross-validation implementation, observation inclusion and group-information set must be aligned; do not claim either beats the other.

## GitHub source
- [Ruby train-only baseline](https://github.com/WhoSia/RITHM/blob/main/ruby/rithm29/learning/group_joint/ruby/empirical_group_baseline.rb), commit 9e3deaaffe300e02ab797ba75e2630478c33e491.
- [Minitest](https://github.com/WhoSia/RITHM/blob/main/ruby/rithm29/learning/group_joint/ruby/test_empirical_group_baseline.rb), commit c92c039606f673b20dc9debf75f866f88ca5834f.
- Local draft test: 2 runs, 13 assertions, 0 failures, 0 errors. GitHub-published text was slightly refactored in naming; full checked-out commit replay is not independently certified.

## Next
Rebuild one-step EWA probabilities or recover historical predictions with stable source SHA. Use exact matching folds, same group-period index and frozen actor information sets. Quantify group residual dependence and per-session paired uncertainty; retain Ruby as mainline.
