# Original 5,760 group-period holdout scoring, 2026-10-31
All scores below from actually joined 34,560 prior individual one-step OOS predictions. Whole-session folds as in previous run.
|Independent product of individual model|Count logloss|Count Brier|MAE count|MAE cost|
|---|---:|---:|---:|---:|
|Training treatment/feedback route share|1.437170|0.724365|0.735476|0.538708|
|Markov|1.456224|0.728257|0.805784|0.512749|
|EWA-lite|1.492442|0.735747|0.875280|0.529797|
|SSM5+lapse|1.590373|0.760035|0.942541|0.695573|
|SSM persistent q+lapse|1.585735|0.756640|0.924614|0.675302|
|SSM q9+lapse|1.583556|0.758827|0.934046|0.681964|
A separate reference model uses training *group count frequencies per treatment* and evaluates whole-session leave-one-out, with symmetric 0.5 pseudocount per count: count logloss **1.415504**, Brier **0.716854**. This is a count-level historical frequency model, not a participant-level action model; its leave-one-session-out training regime is not identical to earlier six-fold evaluation, therefore do not make formal paired inference without common folds. Empirical pooled average actual group cost =4.502431, group count n=4 occurred 2352/5760=40.833%. Exact count counts n=0..6: [2,47,362,1255,2352,1446,296].
