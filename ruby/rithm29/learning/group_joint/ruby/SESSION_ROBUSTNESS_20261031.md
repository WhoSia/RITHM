# RITHM 2.9 — 2026-10-31 session-clustered group robustness
Existing original Noussair–Qiao 24 sessions, 34,560 individual choices; period 2–40 only: 33,696 individuals, 5,616 groups. For each person use previously held-out EWA p and fold-specific train-only inertia κ, then independently convolve previous A and previous B route-switch Bernoullis into P(U,D), project to next A count. No current outcomes used in forecast.

**Executed** analysis from exact CSV `one_step_predictions.csv` in a standalone script `session_robustness.py`, independently reproducing previous numerical results. The 24 sessions contain **unequal** numbers of group transitions (117, 234 or 351). The pooled row-weighted contrast differs from the unweighted session-mean contrast used for bootstrap. State both explicitly.

| Metric | EWA | EWA+inertia | delta | sessions improved | 20,000 session-resample percentile 95% interval |
|--|--:|--:|--:|--:|--:|
| Joint U,D logloss | 2.0684287662 | 1.9678691070 | -0.1005596592 (row weighted) | 21/24 | session-unweighted delta -0.0976496557, [-0.13611804,-0.05362526] |
| A-count logloss | 1.4824580712 | 1.4384138349 | -0.0440442362 (row weighted) | 22/24 | session-unweighted delta -0.0428774737, [-0.05298785,-0.03277104] |
| A-count seven-category Brier | .7330304052 | .7192590234 | -.0137713817 | not evaluated | not evaluated |

**Audit note:** distinct treatments have different number of group-periods per session; do not equate unweighted session mean with row weighted aggregate even though there are 24 sessions. The bootstrap is on session means; these are not numerically identical and must not be conflated. Existing sample has already influenced model discovery; intervals exploratory rather than prospective confirmatory. Source file: attached `session_joint_robustness.csv` and script in current ChatGPT research artifact. No new human participants or new data.

Next: matched 5616-period strong group count baseline and Markov; then joint turnover baseline with training-only state-conditioned counts and smoothing. Version remains 2.9.
