# RITHM R66-T13 R2 — Critical Falsifiers, Lapse Sensitivity and No-Error Counterexample

**2026-11-22 / native Ruby / main only.** Supersedes the interim 26-test source-free package with **34 runs, 69 assertions**, all locally PASS in a fresh ZIP extraction. No private participant data and no new independent empirical validation.

## Falsifier 1: the initial 4:2 optimum is an absorbing state when mistakes vanish

Original six-person congestion excess: `L(n)=3(n-4)^2`. Toy revision rule: a positive individual benefit is required to switch when lapse=0, with private minimum benefit `kappa=2`, attention `q=1/2`. At the initial group-optimal occupancy n=4, neither type has any strictly profitable deviation, hence every schedule's expected H40 excess cost is exactly **0**. At nonzero lapse, the three schedules have different joint error correlations:

| lapse | shared clock | independent | fixed three | lowest |
|---|---:|---:|---:|---|
| 0 | 0 | 0 | 0 | tie |
| 1/100 | 43.87899 | 44.16491 | 44.21891 | shared |
| 1/50 | 64.56300 | 64.70483 | 64.72890 | shared |
| 1/20 | 99.77916 | 98.44854 | 98.19098 | fixed-three |

Therefore the earlier shared-clock advantage at kappa=2 is sensitive to the exact assumed lapse probability and can reverse. Calling it a robust structural law would be incorrect.

## Falsifier 2: a stronger attention × schedule interaction exists **without any mistakes**

Move the initial group to an inefficient occupancy n=5, set `kappa=0`, `lapse=0`, and allow only profitable individual changes (relative to current occupancy). Then one A-route actor has positive current benefit `g_A(5)=1` from moving B. Endogenous repeated group congestion feedback makes the 40-period outcomes:

| attention q | shared clock | independent | fixed three |
|---|---:|---:|---:|
| 1/2 | 19.338733 | 10.522869 | **9.364223** |
| 1 | 35.636532 | 9.672203 | **7.641180** |

**Higher attention raises aggregate losses under a shared clock while decreasing losses under independent or staggered clocks**, even when no one switches randomly in the sense of lapse. This is a *synthetic rational-payoff-direction* switching rule, not proof of perfectly rational repeated-game behavior or endogenous social welfare optimality.

## Critical limitation and next decision

The two falsifiers expose a problem of naive simple rules: some apparently strong policy findings are driven by background exploratory errors, whereas a related sign interaction survives in an initially inefficient state. Nonetheless the switching threshold is a step function, attention is exogenously assigned, and memory/habit are not modeled. A more meaningful RITHM theory must separate **(i) accidental error shocks, (ii) deliberate individually profitable revisions, (iii) latent actor state, and (iv) common information timing**. The T14 research gate is a prospectively testable restriction separating these explanations rather than yet another arbitrary grid that happens to produce an attractive ranking.

**Reproduce:** Ruby source-free Minitest `test_r66_t13_lapse_sensitivity.rb` and `test_r66_t13_off_equilibrium_attention.rb`, plus all other T13 tests, under `ruby/rithm210/p3`. All exact `Rational`. [Research T13 main report](RITHM_R66_T13_BEHAVIORAL_FRICTION_TAXONOMY_20261122.md); the full updated source-free ZIP is preserved in Drive and linked from the corresponding T13 Notion page.
