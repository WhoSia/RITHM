# RITHM-2.7 P29 — Finite-Memory Congestion Automata, Observation Legality and Mean-Payoff Welfare

2026-10-13. **RITHM-2.7 remains the only active Flowing mainline; RITHM-2.6 remains closed.**

## Research scope decision

Exclude *all new human recruitment and all proposals to recruit experimental participants* from the RITHM research program. Continue to analyze existing public human-choice and traffic-sensor datasets, without pretending that missing advice-view/causal-compliance logs have been obtained. Primary scientific engine becomes theoretical computer science: automata, formal verification, strategy synthesis under partial observation, algorithmic congestion games, finite-state stochastic dynamics and computable welfare bounds. Connections to market/pricing/resource allocation are examples for theory, not tested economic results. Primary implementation languages: Ruby / Rust / Go / C++ / R; old Python code maintained as legacy replication.

## Formal class of candidate models

Let D be finite driver/agent set; R_i finite valid paths; n_t edge/path occupancy; m_{i,t} agent's finite memory; z_t incident/supply disturbance; a_t information-message policy; o_{i,t}=O_i(n_t,z_t,a_{\le t}, receipt/event-clock) agent-specific *legally observable* data. A transition relation T maps (n_t,m_t,z_t,a_t) and available local actions into next state, constrained by route feasibility and information timing. For robust analysis with unobserved compliance, use a nondeterministic relation T(s,a) \subseteq S, not a fictitious uniquely fitted behavioral response. Social one-stage cost C(s), e.g. original network's exact quadratic route occupancy cost, yields infinite-horizon objective

    L(pi,T) = sup_{paths consistent with pi,T} limsup_{H->infinity} (1/H) sum_{t=0}^{H-1} C(s_t).

A finite controller may have q memory states. Joint state expands to at most |S|q for deterministic aggregate models (far more if person-level memories are included). Choose a controller only from policies measurable with respect to the information partition, not hidden z or source receipts unavailable at decision time. Candidate property specifications include safety C(s)<=B, repeated accessibility, stabilization, and optimal worst-case long-run mean cost. **Complexity and decidability depend on model encoding, observability, randomness and number of agents and must not be stated generically.**

## Minimal Go-verified constructed witness

Restricted *constructed* two-route 12-unit network: x\in{0,...,12} users on first branch; C(x)=192+2(x-6)^2 (existing P5 algebra). This example is **not** the published three-route full-source cost and **not** estimated from new humans. Two deliberately explicit deterministic feedback controllers:

- Naive threshold: if x<=6, x'=x+1, else x'=x-1. For any x_0=0..12, there is a transient followed by period-two cycle (6,7), so steady long-run cost (C(6)+C(7))/2=(192+194)/2=193.
- Guarded equilibrium stop: if x<6, x'=x+1; if x>6, x'=x-1; else x'=6. All 13 initial states reach absorbing x=6, so long-run cost 192.

**Result:** adding the zero-deviation guard improves average long-run cost from 193 to 192 in this constructed example, a difference of one group cost unit per stage, even though both use only current x and no memory. This is a basic baseline **not a novel theorem** and does not show a general benefit from finite memory. It motivates a proper P30 adversarial *partial observation* counterexample where identical visible occupancy but different hidden incident/memory state requires a nontrivial controller state or has a sharp unavoidable regret bound.

### Exact deterministic finite-state lemma

Any deterministic update F:S->S on finite S enters a cycle of length at most |S| after fewer than |S| transient steps. For finite bounded integer-valued C, the limiting average exists and equals the rational cycle mean sum C(s)/cycle length. For a nondeterministic/adversarial transition relation, finite-path eventual periodicity of *every* path is false; use graph/mean-payoff game reasoning and explicitly qualify strategy/observation scope.

Go 2/2 unit tests PASSED locally, including all 13 legal initial states and exact cost table; `go run main.go` emits all 26 controller/initial-state trajectories and cycle-cost receipts in `exact_results.json`. GitHub Actions NOT run. No recruitment, field deployment, source acquisition or causal effect claimed.

## Prior art and falsifiers

- Rosenthal potential congestion games, Wardrop/network equilibrium, Price of Anarchy and Markov congestion games (Li et al. 2023, doi:10.1016/j.automatica.2023.110879).
- Cominetti, Dose, Scarsini 2021/2024, demand-dependent PoA (doi:10.1007/s10107-021-01701-7).
- Chotibut et al., arXiv 1906.02486, instability and cycles under multiplicative-weights dynamics. 
- Logit dynamics' Gibbs stationary laws (Kleer 2023, doi:10.1287/moor.2022.1322).

None of the generic finite-graph cycle lemma, cost identity or threshold example is new. Genuine RITHM hypotheses for later stage: (i) legal observation partition alters what intervention can be guaranteed; (ii) finite memory can separate otherwise observation-equivalent guidance policies; (iii) data-derived transition-support uncertainty admits certified mean-payoff bounds; (iv) pricing and traffic share demonstrably equivalent game constructions under declared assumptions, not by analogy alone.

## P30 frozen next experiment — no recruited humans

1. Specify true finite hidden-state traffic automaton with delay, incident, actual advice availability and delayed occupancy; disclose which state is unobserved.
2. Enumerate memoryless versus 1–2-bit finite-memory observation-based controllers and check safety/mean-payoff over *all consistent environment transitions* rather than over one handpicked trace.
3. First derive source-free exact bounds; then estimate only permissible transition uncertainty sets from the 2017 human panel and 2025 Seoul sensors as distinct cohorts. Do not combine them into one fictional event-log. Validate controller results on source-held-out folds as exploratory, not causal welfare.
4. Prove an interesting theorem only after checking prior art and counterexamples; benchmark brute-force explicit state graphs against compressed symbolic representations, tracking encoding-dependent complexity.

**Status:** Formal TCS pivot and finite deterministic baseline PASS; real partial-observation synthesis, novel theorem, human-reaction identification, causal welfare benefit and economic field transfer remain HOLD.