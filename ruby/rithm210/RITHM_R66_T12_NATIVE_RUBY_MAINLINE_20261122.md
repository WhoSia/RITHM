# RITHM-2.10 R66-T12 — Native Ruby Revision-Clock Intervention & Finite-Horizon Welfare

**2026-11-22 Asia/Seoul. Research director status: synthetic mathematical results verified locally; prospective human causal experiment NOT conducted.**

## Repositor(y) policy

**MAIN ONLY.** The user requested all future edits on `main`. Before T12, `main` was fast-forwarded to the full T11 branch (63 ahead / 0 behind), and `main` / T11 branch compared identical afterward. The three T7/T8/T11 branches are historical ancestors and can be manually deleted by the user after checking. A fourth branch, `research/rithm-2.0-information-paths`, diverged with five unique historical commits; original information-timing docs were already byte-identical on main; the old `rithm20_information.py` and `rithm20.py` were copied to main for preservation, without replacing newer main tests or README. No branch has been deleted, and no bot commit author is allowed.

## Why Ruby

The repository's own research charter explicitly identifies **Ruby + Minitest as the mainline**. Recent T7–T11 commits put many Python files under `ruby/`, a language-architecture drift. T12 re-centers the theory engine in actual Ruby 3.3 Rational arithmetic, stdlib, and Minitest, with **no Python runtime needed** for these deterministic results. Legacy Python remains as source-data reader and comparison baseline. Execute `cd ruby/rithm210/p3 && ruby -I. -e 'Dir["test_r66_t12_*.rb"].sort.each { |f| require_relative f }'`; run `ruby r66_t12_cli.rb` for human-readable JSON.

## Precisely matched per-actor revision opportunities

Six labelled actors, two routes, and original paper's social congestion excess `L(n_A)=3(n_A-4)^2`. The *hypothetical* probability of actually switching conditional on being eligible follows the existing T5 rule (A→B and B→A rates each depend on previous occupancy; effective effort=1). Three independent-across-period **opportunity schedules** all give EVERY actor inclusion probability exactly 1/2, at EVERY occupancy:

| Schedule | Joint eligibility probability for pair | Pair covariance | Structural rule |
|---|---:|---:|---|
| Shared clock | 1/2 | +1/4 | All six eligible or none, equal probabilities |
| IID activation | 1/4 | 0 | Each eligible independently with probability 1/2 |
| Fixed 3-of-6 staggered | 1/5 | -1/20 | Choose uniformly 3 of 6 each period |

The actual event of switching has conditional probability `Pr(flip_i |n)= (1/2)*r_i(n)`, same in all schemes; **expected one-step gross switches** at fixed n match exactly. Information quality, timing and psychological behavior are **not** identified from this opportunity mechanism; using it as an intervention *model* requires extra assumptions.

## Exact one-step expected social cost identity

For n of six on route A, conditional revision rates a(n) and b(n), equal actor-eligibility marginals and **exchangeable** eligibility laws, define (J_2) as pairwise simultaneous eligibility probability and `B(n)=C(n,2)a² + C(6-n,2)b² - n(6-n)ab`. Then exact expected immediate cost difference between schedules P,Q is

`E[L(N_next)|P,n] - E[L(N_next)|Q,n] = 6*(J2(P)-J2(Q))*B(n)`.

This follows directly by expanding the quadratic squared net group flow, not a generally new theorem. Minitest checks all 7 occupancies × all 3 schedule comparisons exactly as Rational, plus effort-scaling and invalid comparability.

At the optimal 4:2 initial occupancy, **common minus independent immediate excess cost = -3/5000**, slightly favorable. But at initial A=5, this gap is **117/50 = +2.34**, strongly unfavorable. One-step sign is state-dependent.

## Exact 40-period predictions: feedback propagation

Ruby enumerates all 64 labelled eligibility masks, uses an exact two-arm binomial convolution to aggregate to 7 occupancy states, and propagates the 7×7 rational transition kernel for 40 periods. An independent, differently implemented full 64-labelled-flip oracle matches every row for all 3 schedules and selected fractional efforts.

| Initial A | 40-period common clock congestion excess | IID clock | Fixed 3-of-6 |
|---|---:|---:|---:|
| 4 | 43.193024304 | 18.257639492 | **15.963873626** |
| 5 | 71.517923506 | 27.093565720 | **23.036388** |

At initial A=4, cumulative gross changes: shared 8.474830462, IID 5.759228621, 3-of-6 5.480346223. Thus for any **nonnegative per-actual-switch physical resource fee**, the fixed-three schedule dominates the other two in the simulated initial-A=4, H=40 scenario; it does NOT claim universal policy dominance across all game regimes or human populations. Strict first-period priority may reverse at long horizons.

Exact final probability of 4:2: common .760558401, IID .865251539, fixed-three .875566014. These differences reflect **only** chosen schedule correlation plus repeated toy revisions, no new empirical treatment effect.

## Tests and reproducibility

Local Ruby version: 3.3.8. Deterministic Minitest suite: **21 tests / 169 assertions / 0 failures / 0 errors**. The independently enumerated 64-labelled oracle tests validate that the seven-state kernel has not implicitly assumed independent action-opportunity choices. Tests also cover deterministic no-revision behavior, per-actor marginal equality, gross switching, fee identity and expected-cost pair covariance. Remote GitHub Actions uses read-only checkout and Ruby/setup-ruby; **no assertion of remote CI PASS without fetched job logs**.

This analysis is synthetic and theoretical, not a replay of an independently recruited cohort. The underlying 24 human sessions were extensively explored in T3–T11; no fresh human-data p-values are claimed here.

## Research-director judgment & prospective controlled study

A randomized experiment should assign **independent six-person groups** (not individual rows) to shared versus staggered information-release *timing*, holding information quality, content, total individual exposure, payment and duration fixed as far as feasible. Distinguish:
1. An *opportunity to revise* from actually *seeing information* and from *choosing to switch*.
2. Private effort/disutility versus real social resources spent on adjustment.
3. One-period fit versus full 40-period welfare.
4. Randomized schedule mechanism from information-induced individual cognition, which must be separately measured.
5. Both amplifying and stabilizing feedback cases. Contrarian responses and latent-type selection remain competing mechanisms.

In this small finite game, matched one-person activation rates do not guarantee matched whole-system welfare. Precise pairwise activation covariance supplies the one-step cost difference, but multi-step welfare depends on the resulting transition graph. Next T13 should derive sharp **resource-fee and schedule-horizon phase boundaries** and evaluate them under independent counterexample cases, then bridge to a preregistered ethically reviewed human protocol or newly obtained genuinely independent cohort. Do not overclaim a novel theorem.
