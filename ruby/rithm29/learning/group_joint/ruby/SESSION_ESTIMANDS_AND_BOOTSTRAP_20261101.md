# Session-cluster inference contract — 2026-11-01

## Question
When source sessions contain unequal numbers of group transitions, the mean across sessions and mean across all group transitions are different estimands. Avoid attaching an equal-session bootstrap confidence interval to the pooled transition-level point estimate.

## Input contract
For every heldout session, provide one row with:
- n: positive integer number of scored heldout group transitions in that session;
- baseline: heldout mean log loss of the baseline model across exactly those transitions;
- candidate: heldout mean log loss of the candidate model across exactly those transitions.

Train candidate and baseline without using this heldout session. Preserve identical folds, loss units, transition eligibility, actor information restrictions and feature timing. For count and joint-switch heads, form *separate* inputs and inference tables.

## Estimands
equal_session = sum_s(candidate_s - baseline_s) / S.
transition_weighted = sum_s(n_s*(candidate_s-baseline_s)) / sum_s n_s.
A negative difference indicates a lower loss for the candidate.

The randomization is NOT a causal assignment test: resample whole paired sessions, with replacement, exactly S draws per bootstrap replicate, carrying n_s, baseline_s and candidate_s together. The transition-weighted estimator recomputes the denominator within each bootstrap sample. The percentile interval is exploratory and does not adjust for model selection or multiple comparisons.

## Source code and tests
- session_weighted_bootstrap.rb
- test_session_weighted_bootstrap.rb
Local independent Ruby 3.3.8 test execution on 2026-11-01: 3 runs, 9 assertions, zero failures/errors. The locally copied module and test match the newly authored GitHub contents; remote GitHub CI has not been established.

## Hard gates for scientific promotion
1. Produce immutable session-level rows from the original 24 sessions and fixed sixfold heldout assignments.
2. Recalculate both point estimands and 20,000-draw paired session bootstrap intervals, recording seed, session counts and distribution of n_s.
3. Compare EWA, EWA+inertia, Markov and a training-only smoothed joint-frequency baseline on the same heldout rows.
4. Examine whether group joint-switch residuals remain after accounting for individual inertia, avoiding unsupported causal interpretation.
5. Reconcile source-paper Table 8 p-value disagreements before using the original authors' inferential claims as validated ground truth.

## Provenance
Source archive: https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view
Research ledger: https://app.notion.com/p/3feef561cf9281bcbd77eeb6c983557e
