# RITHM 2.9 — retrospective six-fold inertia experiment, 2026-10-31
Source: Noussair–Qiao pre-existing 34,560 choice trajectories, 24 sessions, GroupKFold 6x4 session splits inherited from prior model replay. Period 1 excluded: 33,696 person decisions, 5,616 six-person group transitions. **No new human participation.**
For participant i, p'_it = sigmoid(logit(p_EWA,it) + kappa*(2 a_i,t-1−1)), kappa>=0. p_EWA is source-feasible precomputed OOF prediction. Golden section train session only optimizes individual logloss for kappa in [0,8], with explicit kappa=0 null check. Folds kappa: 0.435729, 0.498123, 0.465303, 0.468980, 0.449945, 0.432932.

| Metric (transition-only period 2..40) | EWA | EWA + inertia |
|--|--:|--:|
| Individual choice logloss | 0.534724 | **0.517964** |
| (U,D) joint logloss | 2.068429 | **1.967869** |
| Six-player A-count logloss | 1.482458 | **1.438414** |
| Expected switchers per group | 2.046334 | **1.585998** |
| Mean predicted congestion cost | 4.661606 | **4.557828** |
Observed switchers per group 1.586360; realized mean cost 4.499199. All metrics aggregate six equally-sized heldout session folds. Improvement is exploratory: same historical sessions guided earlier model creation. One-step predictions condition on realized past actions, not simulation of full dynamics. Difference between earlier 5,760 all-period count score and 5,616 transition-only score MUST be retained. No identification of participant's actual psychological inertia, no controlled causal effect.

Ruby 3.3.8: inertia_calibration.rb test 4/59 pass; new inertia_fit.rb test 3/3 pass. Additional full pipeline `inertia_cv.rb` and fold score `scores.csv` attached with this-turn research deliverable. Keep GitHub canonical simulation separate from legacy retired scripts.

Open gate: cluster uncertainty by whole session; contest train-only baselines including Markov and treatment-level count prior on matching 5,616 periods; nested full-session model selection to correct reused-data exploration. RITHM 2.9 remains open, 2.10 not promoted.
