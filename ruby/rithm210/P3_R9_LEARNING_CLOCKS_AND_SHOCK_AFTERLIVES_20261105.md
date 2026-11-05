# RITHM-2.10 P3-R9 — Learning, Adjustment Clocks and Macro Congestion Afterlives

**2026-11-05 (KST).** Research status: exact congestion-game reference results, original-source exploratory group-welfare decomposition, ten behavior/economics literature source inspections (plus one science-history scan), and stronger originality screening. **No novel general theorem or causal learning mechanism is claimed yet.**

## Research reset
The project's long-run scientific question is NOT simply whether latent shocks or individual inertia improve joint route-switch forecast logloss. It is how **micro-level belief and learning errors arise, how the cadence and information of collective adjustment amplifies or dissipates them, and how the resulting stochastic occupancy path produces aggregate welfare loss**. A valid model must predict separately P(no gross switches), E(gross U+D), opposing cancellation, E(next congestion cost), and their time/treatment structure. The actual experiment has six stable actors per group over repeated decisions; the real group-cost functional is `C(n)=n²+2(6−n)²=24+3(n−4)²`.

Original human-data file custody: [author-approved ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view), `data_task_all_switch_230705.csv` SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`; filter treatments 1–3, exclude sessions 2/101, periods 1–39, yielding 24 sessions and 5,616 six-person group transitions. No participant-level rows are published on GitHub.

## A. Exact pairwise decomposition of the cost of reallocation
Let B→A count U, A→B count D, gross switches G=U+D. At current socially optimal state n=4, next occupancy n'=4+U−D gives

`L(n')=3(U−D)²=3[G+2{binom(U,2)+binom(D,2)−UD}]`.

This is an identity for every feasible six-person transition. Individual switches are a gross positive term, same-direction pairs further increase net occupancy deviation, and opposing pairs cancel flows and decrease the deviation. It is an algebraic welfare attribution, not a causal decomposition of why people switched.

Sealed original Full treatment, conditional current n=4:
| Moment | Early periods 1–10, 154 group transitions | Late periods 30–39, 257 transitions |
|---|---:|---:|
| E(gross switches) | 1.35714286 | 0.58365759 |
| E(same-direction pairs binom(U,2)+binom(D,2)) | 0.31818182 | 0.06614786 |
| E(opposing pairs UD) | 0.49350649 | 0.13618677 |
| E(pair balance same−opposing) | −0.17532468 | −0.07003891 |
| E(next excess group congestion cost) | 3.01948052 | 1.33073930 |

The observed cost decrease **1.68874122** decomposes exactly into **+2.32045581** from lower gross activity and **−0.63171459** from the simultaneous change in pair balance. Therefore the reduction in gross switches alone would overstate the welfare gain; the loss of opposing-flow cancellation offsets some of it. This is a precise interpretation of the previously collected joint U,D statistics.

Whole-session bootstrap: 24 original sessions, 20,000 complete-cluster resamples, fixed seed 20261105, recompute weighted conditional means after each resample; zero-support session×epoch×n=4 cells are kept at count zero rather than assigned outcome zero. Exploratory percentile95:
- next excess-cost decline 1.68874122, **[1.01035469,2.46637389]**;
- 3×gross-turnover contribution 2.32045581, **[1.49738875,3.06621418]**;
- 6×pair-balance contribution −0.63171459, **[−1.24137931,+0.05465655]**, **contains zero**;
- mean gross switching decline 0.77348527, **[0.49912958,1.02207139]**.
No prospective preregistration or family-wise multiple-testing correction, and the original data have been studied extensively. Do not claim that the negative pair-balance component is statistically established in isolation.

Ruby: [exact joint-pair welfare](p3/pairwise_welfare.rb), [feasible-state tests](p3/test_pairwise_welfare.rb), [original sealed source session audit](p3/pairwise_source_audit.rb), [synthetic/bootstrap tests](p3/test_pairwise_source_audit.rb). Independent original-CSV Ruby check verified all 5,616 source groups, displayed exact conditional moments and cluster intervals.
