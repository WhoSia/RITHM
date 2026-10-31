# Whole-session held-out simultaneous switch distribution
N=5,616 group-periods, 144 six-person group-treatment blocks each 39 transitions. Candidate categorical baselines trained on the other five session folds, Jeffreys 0.5 count smoothing, with three settings (pooled, treatment, treatment×early period<=10). EWA independent-convolution switch predictions from pre-existing exact previous-route states.

|Model|Count logloss|seven-class Brier|mean forecast switches|
|---|---:|---:|---:|
|EWA|1.520214|0.750358|2.046334|
|pooled empirical|1.523993|0.759237|1.587417|
|treatment empirical|1.518904|0.756826|1.589525|
|treatment×early/late empirical|1.517294|0.756391|1.592465|
Actual mean 1.586360. New score computations based on 5,616 actual source group-periods; identical session-heldout protocol but candidate baselines formed after data exploration. EWA minus treatment-phase logloss +.00291998; session bootstrap 20k replications (seed 20261031), 95% percentile [-.02727576,.03290868], 14/24 sessions favor empirical. No evidence of robust count-logloss superiority; EWA scores better Brier. Mean switcher bias remains prominent. **No new participants**.
