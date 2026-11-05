# RITHM-2.10 P3-R10 — Rare Desynchronization, Metastable Escape, and Finite-Horizon Congestion Welfare
**Date:** 2026-11-05 (Asia/Seoul). **Status:** exact mathematical reference model and pre-empirical theory audit. **Novelty not certified**, synchronization schedule not identified in the original six-person experiment.

## Problem and assumptions
Six distinct route-selecting actors choose A or B; the physical group cost is `C(n)=n²+2(6−n)²=24+3(n−4)²` with optimal Nash occupancy n=4. The oracle snapshot model assumes **all agents know every current route choice**, and strict individual best responses are calculated holding others' present choices fixed. This information exceeds what some original human participants possessed; the model is deliberately a strong, transparent COUNTERFACTUAL rather than a calibrated laboratory learning mechanism.

At each group time:
- with independent probability s in [0,1], **all six agents simultaneously** execute their stale-snapshot strict best responses;
- with probability r=1−s, **one uniformly chosen actor** executes their unilateral strict best response.
All responses are deterministic conditional on who updates; there is no payoff-learning uncertainty or further external shock after the initial one.

An original single-person mistake at efficient n=4 moves the system to n=3 or n=5. State 4 is then absorbing. The seven possible A-occupancy values (0...6) form an exact Markov chain, with transient set `S=[0,1,2,3,5,6]`. For any n, `P_s(n,m)=s I[m=T_all(n)]+(1−s)P_one(n,m)`. Both components are probability distributions; `P_s(4,4)=1`. The full original experiment's policy and observed behavioral probabilities DO NOT specify s.

## Exact result: a quadratic escape-time singularity
For every **s<1**, every transient state has a strictly positive probability path to state 4 using a finite sequence of one-actor updates; the finite Markov chain therefore absorbs almost surely with finite mean. At **s=1**, the initial n=3 or 5 enters the perpetual deterministic cycle n=0↔6 and never reaches state 4.

The exact rational transient linear system `(I-Q_s)t=1`, with `Q_s=P_s[S,S]`, yields for an initial n=3:
```
E[T_4|n_0=3] =
2(s+2)(s+5)(5s^2−12s−5) /
{5(s−1)^2(5s+1)(2s^3−9s²+11s−10)}.
```
Consequently, setting r=1−s and taking r→0+,
```
E[T_4|n_0=3]=12/(5r²)+4/(5r)−7/5+O(r).
```
The n=5 case has the same **leading coefficient 12/5** with different lower-order corrections. The leading term has an intuitive renewal interpretation: once near the extreme two-cycle, to escape from n=6 through n=5 to absorbing n=4 requires two sequential one-actor periods. Those two occur with probability order r²; the second correct actor is selected with probability 5/6. Each unsuccessful oscillation takes approximately two time steps, giving the leading expected time `2 / ((5/6)r²)=12/(5r²)`. The exact coefficient is independently verified by symbolic elimination, rational Gaussian elimination and near-boundary checks.

This is a **fixed six-person conditional protocol theorem**, not a universal scaling exponent for all congestion games or update schedules. For larger N or different costs, the minimum asynchronous escape path may have a different length and scaling exponent.

## Exact finite-horizon calculations (n0=3)
| sync s | E time to reach n=4 | P(n40=4) | Total expected excess congestion, periods 0..39 | Discounted infinite-horizon excess beta=0.9 |
|---:|---:|---:|---:|---:|
| 0 | 2.0000 | 0.999999999999 | 6.0000 | 5.4545 |
| 0.5 | 9.4286 | 0.976692 | 170.6341 | 74.4156 |
| 0.9 | 246.4813 | 0.184090 | 974.9353 | 229.8116 |
| 0.99 | 24078.5877 | 0.006598 | 1147.3399 | 261.6862 |
| 1 | never | 0 | 1155.0000 | 264.4737 |

These **are not fitted empirical forecasts**; they are exact rational computations for the hypothesized update-clock protocol with a single exogenous initial misrouting and no subsequent errors. The 40-period horizon was chosen to compare interpretation with the experiment's duration but is not based on its 40-period participants' measured clock probabilities.

## Noncommuting limits, and research interpretation
Let `A_T(s)=T^(-1) sum_{t=0}^{T-1} E[C(n_t)-24]`, initial n0=3. At every fixed s<1, eventual absorption implies `lim_{T→∞} A_T(s)=0`. At s=1, perpetual 0↔6 gives `lim_{T→∞} A_T(1)=30` (the initial t=0 contributes a vanishing fraction). Therefore
```
lim_{s↑1} lim_{T→∞} A_T(s) = 0,
lim_{T→∞} lim_{s↑1} A_T(s) = 30.
```
Long-run almost-sure stability alone does **not** imply adequate finite-horizon stability, welfare efficiency or bounded recovery time uniformly in s. This is an elementary singular perturbation reference result rather than a newly proved universal economic theorem. The metastability here refers only to the synthetic near-synchronous finite Markov chain.

## Implementation, validation and governance
[Exact rational Ruby chain](p3/mixed_clock_chain.rb) and [Minitest](p3/test_mixed_clock_chain.rb) have been executed locally under Ruby 3.3.8: **6 tests/51 assertions PASS**. [Independent closed-form Ruby](p3/mixed_clock_theorem.rb) and [formula-vs-solver tests](p3/test_mixed_clock_theorem.rb): **2 tests/12 assertions PASS**. Ruby tests cover stochasticity of all 7 rows, recovery of previously verified perfectly synchronous/asynchronous endpoint formulas, exact midpoint absorption times and finite-horizon probabilities. The source-only GitHub Actions YAML is updated, with `contents: read`; **actual remote workflow PASS and exact checked-out SHA replay not confirmed**. No user data, original paper PDF or individual human observations committed to GitHub; no `github-actions[bot]` source authorship.

## Scientific boundary and next research decision
The original laboratory participants cannot all observe exact opponents' present route choices; the toy process by construction makes n=4 fully absorbing. **Actual experiments show substantial early n=4 departures**, so there MUST be a separate behaviorally admissible explanation of errors, learning, forecast imperfections or private uncertainty. Using a fitted s alone to explain n=4 exits is mathematically impossible in this model. This motivates a two-layer next theory: (I) belief/experience updates create departures from efficient allocations, (II) stochastic coordination of adjustments can magnify or absorb those perturbations. Both layers need separate identification and joint-outcome predictions, not a single ad hoc inertia coefficient.

Strong prior-art comparison needed: original SSM5/SSM1–9, experience weighted attraction, QRE, Young stochastic conventions, Kandori-Mailath-Rob evolutionary equilibria, Benaim-Hofbauer-Sorin perturbations, and the more directly relevant day-to-day route-choice and behaviorally adaptive models (Qi et al. 2023, Yang et al. 2026, Wu et al. 2026). Updated 2026 inertia-based congestion updating research also directly challenges novelty. RITHM must identify a genuinely new finite-horizon empirical prediction, policy or experiment distinguishable from these baselines.

## Identifiability theorem — observable scheduling does not follow from optimal-state persistence

In the pure oracle mixed-clock model, for any **n!=4**, simultaneous stale-snapshot strict best response jumps to n=0 or n=6 (depending on the side of n=4), whereas any single-actor strict best response stays at n or changes occupancy by at most one. Their observed next-state supports are disjoint. Thus, with full aggregate occupancy n_t and n_(t+1) observed and **no additional behavioral noise**, one transition from any non-optimal n identifies the *realized schedule type* (all-at-once vs single actor). Conditional on n!=4, the log likelihood for mixture probability s reduces to the likelihood of a Bernoulli(s) observation, and its regular Fisher information for s in (0,1) is exactly `1/[s(1-s)]`.

At **n=4** both branches are deterministic self-loops, so every value of s gives the same next-state law P(4,4)=1, with Fisher information exactly **zero**. In particular, from n=4 persistence alone **s is not identifiable**, and no choice of s can reproduce the original experiment's positive n=4 turnover; this toy must be extended with an actor-information-feasible uncertainty/tremble/learning mechanism to be a plausible real behavioral model. When such behavior is added, the two update types' supports may overlap and the easy Bernoulli identification result no longer applies. This makes the original limited-information context not merely a minor implementation detail but central to structural identification.

[Clock identification Ruby](p3/mixed_clock_identification.rb) · [support and information tests](p3/test_mixed_clock_identification.rb). **3 additional locally executed Minitest runs / 34 assertions PASS**, combined P3-R10 **11 runs / 97 assertions** (original 6/51 + theorem 2/12 + identification 3/34). All source-only tests are in the read-only GitHub workflow; remote GitHub Actions success remains **unverified**.

## Closest newer paper comparisons
The direct [2026 original-paper prior-art audit](literature/p3r10_2026_direct_prior_art_identification.md) reviews *already held* Yang et al. (2026) (Full/Partial-information reinforcement route learning and FI equilibrium stability), Wu et al. (2026) (individual-level traffic parameter **identifiability under assumptions** and posterior consistency under stronger hypotheses), Qi et al. (2023) (laboratory route-dependent inertia and empirical convergence), and older stochastic/traffic dynamics. External publisher abstracts indicate an especially close **Inertia-based Strategy Updating Rule Design for Congestion Games and Its Application to NFV Networks**, dated **2026-11-05**, plus Heinrich et al. (2023) on playing order and best-response convergence. Precise theorem-level originality versus the recent paper is **NOT YET ESTABLISHED**. No retrieved abstract is treated as proof of a specific novel mathematical exponent.
