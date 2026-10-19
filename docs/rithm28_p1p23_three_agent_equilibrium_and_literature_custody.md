# RITHM P1-P23 — Three-Agent Endogenous Inspection: Pure-Equilibrium Multiplicity and Literature Custody

2026-10-19. **Synthetic constructed game; theorem/novelty HOLD.** The first end-to-end Ruby code and exhaustive tests are [three_agent.rb](../ruby/rithm28/p1p23/three_agent.rb) and [test_three_agent.rb](../ruby/rithm28/p1p23/test_three_agent.rb).

## Reproduced exact equilibrium values
Three players start (A,A,B). Binary hidden shock z=0/1 equiprobable, cost of A for each user n_A+z, of B n_B. Any player who changes from initial route pays k=3/4. Any player who purchases perfect state information pays q=1/16. Six **pure contingent plans** per player: no information fixed A/B or bought signal with an A/B action prescribed under each z; 216 complete plan profiles. At Nash equilibrium nobody can profit by unilaterally replacing their entire contingent plan, including their inspection decision.

Exactly **three pure equilibria**:
1. A stays A; B initial-A player purchases signal and uses A if z=0, B if z=1; initial-B agent stays B. Symmetric variation interchanges first two. Aggregate all-in expected cost **95/16** per equilibrium.
2. Both initial-A agents purchase signal and use A if z=0, B if z=1; initially-B agent also buys information and uses B if z=0, A if z=1. Aggregate all-in expected cost **109/16**.

For fixed baseline (A,A,B) in both shock states, no search or switching, expected aggregate cost is **6**. Thus the same fully strategic *pure-plan* game contains equilibria both below and above the baseline. This **is not a paradox for all equilibria**; equilibrium selection matters. Cost figures INCLUDE all inspection and switching fees, avoiding the previous welfare metric ambiguity.

The earlier 2-active-player P1-P22 court fixed third person to route B, hence excluded equilibrium (2), and its claim of no welfare-inferior equilibrium was true only inside that restricted game. P1-P21's level-0 simultaneous all-to-B conjecture is neither an equilibrium nor a legitimate general theorem.

### Formal falsification and remaining gaps
- Formal game is atomic, finite, binary world, risk-neutral, public common prior, perfect signal purchased privately; social objective sum of individual route latency plus all fees; no actual human empirical identification.
- Exact pure-strategy Nash check is over the six **contingent plans** per player. The 'depth' setting in code merely limits what deviations are inspected and is **NOT** a cognitive-depth model of human players.
- **Mixed Nash equilibria not computed.** Existence or stability of the displayed pure equilibria under trembling-hand refinements, information precision changes, repeated dynamics or changes in the third player's initial path remains unknown.
- Strong novelty competition: Castiglioni et al. (2021), *Signaling in Bayesian Network Congestion Games*, https://ojs.aaai.org/index.php/AAAI/article/view/16663 ; Griesbach et al. (2024), *Information Design for Congestion Games with Unknown Demand*, https://arxiv.org/pdf/2310.08314 ; Das/Kamenica/Mirka, *Reducing Congestion Through Information Design*, author manuscript https://www.cs.cornell.edu/~rmirka/reducing-congestion-information-2.pdf ; Zeng et al. (2026), *Joint Information Design and Pricing for Transportation Information Service*, author SSRN https://doi.org/10.2139/ssrn.4789552 . **ALL FOUR are DRIVE UNCONFIRMED at this audit.** Ashraf et al. (2023) is DRIVE PRESENT in 10_PAPERS; do not mislabel missing.

## Distinct cognitive costs, source and proof fences
A priced perfect observation is not computational step complexity. A limited-deviation *checker* is not an actual limited-computation rational agent. Next create an explicit finite computational operation alphabet with input-dependent resource budget and a consistent stopping/value-of-information rule. Model a repeated game with group-cost feedback and exact finite state, and distinguish equilibrium welfare, ex-post action welfare and paid information expenses.

## Source recovery status — email custody
**Gmail SENT checked 2026-10-19:** an October 19 10:35 KST thank-you/permission acknowledgment to Prof Liang Qiao was indeed sent (Gmail message 1a151cce405d66a2), but its content does not mention NUL-only source CSV/R scripts or ask for replacement. No later sent request was found in the checked Gmail search. Do NOT send duplicate thank-you. One carefully worded factual source-integrity inquiry remains **UNSENT / WAIT**, to be sent only if the user explicitly requests. The 20.2MiB ZIP is preserved unchanged and checksum-verified; essential experiment files CRC-consistent all NUL; Qiao–Noussair paper/data could be valuable if intact.
