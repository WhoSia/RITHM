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

## B. Exact atomic congestion game: Nash equilibrium and physical adjustment clocks

In the actual six-person cost table, each A user pays n and each B user pays 2(6−n). An atomic unilateral switch A→B changes that person's cost by `14−3n`, and B→A changes it by `3n−11`. The exact Rosenthal congestion potential is

`Phi(n)=n(n+1)/2+(6−n)(7−n)`.

Only n=4 is a pure Nash **occupancy**; all 15 player-identity profiles with four A and two B are pure Nash. The group cost `C(n)=24+3(n−4)²` is also uniquely socially minimized at n=4. At n=4, unilateral A→B costs the mover +2 and B→A +1, so every strict best responder stays, irrespective of the update clock.

**Synchronization reference theorem.** Suppose every actor knows a shared PREVIOUS/current snapshot of all other agents' routes and calculates a unilateral best response ASSUMING others keep that snapshot, but everyone updates simultaneously. The deterministic next-occupancy map is:
`T(0)=T(1)=T(2)=T(3)=6, T(4)=4, T(5)=T(6)=0.`
Hence any initial n≠4 enters the perpetual two-cycle 0↔6, while n=4 remains fixed. The two-cycle's time-average group cost is `(C(0)+C(6))/2=(72+36)/2=54`, compared with the efficient group cost24, i.e. mean excess30 each period.

By contrast, one uniformly sampled actor per period strict best-responding to that same current snapshot produces a monotone, almost-surely absorbing process at n=4. Expected selected-player update opportunities to first hit n=4 are 5.7 from n=0 and 2.2 from n=6 (geometric holding times, because a selected agent already on the locally preferable route makes no change). The underlying payoff table and strict unilateral behavior are identical; *adjustment synchronization alone* changes system-level stability conditional on a departure from the equilibrium.

**General-N extension (N divisible by 3).** Costs per A actor n, per B actor 2(N−n). The social optimum and unique Nash occupancy are both n*=2N/3. Perfect snapshot-synchronous strict best response generates the extreme two-cycle 0↔N; group costs are 2N² and N², average 3N²/2. Optimal group cost is 2N²/3, so the exact dynamic cycle-to-optimum ratio is **9/4** and mean excess **5N²/6**. For N not divisible by 3 the Nash-state uniqueness fails in some cases (e.g. N=5 has n=3 and 4 Nash occupancies, of which only n=3 is socially optimal). This is a deliberately limited theorem: no universal population result, and no originality claim against traffic and best-response synchronization literature.

**Crucial failure-to-explain boundary:** this deterministic clock variation alone CANNOT explain the real experiment's early P(no switch|n=4)=.2208, since in the exact Nash state all players stay under strict known-state best response. A separate shock/uncertainty/misbelief/learning mechanism is required to EXPLAIN exits from the optimum; update synchronization only controls propagation of departures. Also, not every original participant had access to the shared full group snapshot, and even informed participants could not know opponents' simultaneous next moves. Therefore these are **oracle and frozen-opponent comparison models**, not valid reconstructions of the laboratory information sets.

Ruby: [atomic Nash potential](p3/atomic_nash_potential.rb), [exact finite-six clock map](p3/adjustment_clocks.rb), [general-N extension](p3/general_adjustment_clocks.rb), and separate exhaustive Minitest files. Independent local Ruby passed 3 tests/187 assertions for six-person identities and 2 tests/258 assertions for general-N potential and cycle ratio.

## C. The indefinite macro afterlife of ONE mistaken micro-choice

Start from the efficient n=4 Nash configuration. A single mistaken A→B action takes n to 3, or a B→A action takes it to 5. The shock occurs ONCE; from the next period onward, agents strictly best respond to their current shared snapshot without further mistakes.

For the n=3 case, all-at-once updates yield the infinite sequence 3→6→0→6→0→..., with excess costs 3,12,48,12,48,... . For discount factor beta in [0,1), the exact discounted congestion excess, measured from the first post-shock state, is

`V_sync(3;beta)=3+(12 beta+48 beta²)/(1−beta²)`.

For n=5, the sequence is 5→0→6→0→..., with

`V_sync(5;beta)=3+(48 beta+12 beta²)/(1−beta²)`.

If exactly one actor is chosen uniformly each period to strictly best respond, n=3 remains at 3 until one of the 3 currently-B actors is chosen (success probability 3/6), then n=4 forever. Similarly from n=5, the probability of picking one of the 5 currently-A actors is 5/6. The geometric waiting-time values are:

`V_async(3;beta)=3/(1−beta/2)` and `V_async(5;beta)=3/(1−beta/6)`.

At beta=0.9 these equal approximately **264.47 vs 5.45** for n=3 and **281.53 vs 3.53** for n=5. As beta tends toward 1, the synchronized present value diverges while the asynchronous n=3 value tends toward **6** and n=5 toward **3.6**. This makes the two-causal-stage modeling architecture explicit: (I) a noisy/incomplete-information rule generates rare exits; (II) the adjustment protocol amplifies or absorbs those exits and determines future welfare.

It is a **synthetic counterexample** in an atomic congestion model with oracle stale-state observations. It does NOT prove that the source humans share a clock, that subjective switching disutility is social resource cost, or that synchronization-induced oscillations are novel relative to the existing day-to-day traffic and endogenous-learning literature. A robust thesis needs an empirically grounded protocol variation and a prediction differentiating observation delay, private uncertainty and concurrent intention formation.

Ruby [shock afterlife](p3/shock_afterlife.rb) and [Rational test](p3/test_shock_afterlife.rb). Independent local rational checker: 2 runs/7 assertions, zero failures; the published source Minitest tests further edge cases. Remote Actions success not established.
