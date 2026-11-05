# Ackermann & Röglin — On the Convergence Time of the Best Response Dynamics in Player-specific Congestion Games

**Exact uploaded bytes:** [Drive arXiv 0805.1130v1](https://drive.google.com/file/d/1xWTPXUM_oZ7visIGUv0mN3VC__JeyXNM/view). Header says arXiv version 1 uploaded **2008-05-08**, but the PDF manuscript text also prints **2018-11-09**. This inconsistency is explicitly preserved in canonical filename, not silently repaired as a final journal version.

## Results and scope
Player-specific singleton congestion games allow player-dependent resource delay functions; unlike standard shared-cost Rosenthal potential games, particular best response schedules can cycle. Theorem 2 shows every best response schedule for certain player-specific **tree resource networks** terminates within a quadratic resource-count bound. Cycle-class random best-response procedures have expected polynomial time under further conditions. Authors also discuss games for which random selection may be extremely slow (conjecture supported by numerical experiments).

## RITHM boundary
The six-actor A/B game uses COMMON resource costs A=n and B=2(N−n): a standard atomic congestion potential game. Its strict **single-agent** best response cannot cycle, unlike some player-specific games; our pathological oscillation arises from all agents simultaneously responding to a stale snapshot. No contradiction with the paper's standard Rosenthal potential observation. Also the paper counts best-response moves/updates under specific activation models, which may differ from wall-clock time per collective stage.

## Open mathematical comparison
How do absorption-time exponents depend on minimum rare-activation path length and permitted multi-agent activation schedule? Similar stochastic bottleneck asymptotics may be classical Markov-chain theory; exact coefficient and a new finite-time experimental implication would need comparison, not a priority assertion.
