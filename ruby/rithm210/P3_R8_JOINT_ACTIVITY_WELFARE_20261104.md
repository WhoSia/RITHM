# RITHM-2.10 P3-R8 — Joint Activity and Welfare Audit

Date: 2026-11-04 KST. Exact mathematical restrictions and exploratory model comparisons; causal mechanism not identified.

Original source is the author-approved Noussair-Qiao route-choice CSV in Drive, SHA-256 d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb. Original person-level rows remain private.

Main question: Can the original 40-period generative Small Sample models explain the transition dynamics of a group currently at the socially optimal allocation (four of six people on A), instead of only matching treatment-level mean congestion costs?

Ruby implementations: activity_mixture.rb, ssm_joint_falsifier.rb and their exact rational unit tests. The original author-rule SSM generators ssm_generative.rb and ssm_activity.rb now additionally measure gross route switching and opposing cancellations without changing random draws.

## Four observed-versus-generative moments at current A occupancy n=4

| Event / welfare outcome | Actual Full early (N=154) | Actual Full late (N=257) | SSM5 10k groups early | SSM5 10k groups late |
|---|---:|---:|---:|---:|
| No gross switches | .22077922 | .58365759 | .60177773 | .50317535 |
| Mean gross switches | 1.35714286 | .58365759 | .90465550 | 1.21639338 |
| P(opposing cancelled transitions) | .15584416 | .07782101 | .10641850 | .15045639 |
| Mean next excess congestion cost | 3.01948052 | 1.33073930 | 1.73527967 | 1.95103224 |

All four changes between early and late have opposite signs, with SSM1-9 following the same qualitative pattern. Authors' original 40-period SSM5 and SSM1-9 aggregate Table 7 remained replicated to within .03 across 48 mean/SD measurements. The diagnostic is conditional on being in n=4, and therefore simulated and actual group histories need not have the same distribution. No causal information effect or new psychological law is established. Seed 20261104, 10,000 generated games per scenario. A 1,000-game test did not reliably reproduce all four directions, so the regression test uses 10,000 games; local 2 tests, 10 assertions passed.

## One-step freeze-only benchmark and its cross-moment restrictions

Let Q(u,d) be a baseline turnover distribution. A group-wide stopping state of probability z in [0,1] produces P_z(u,d) = z I(u=d=0) + (1-z) Q(u,d). This is a specified mixture, not a measured psychological mechanism. The no-switch rate cannot decrease below Q(0,0), every nonzero turnover-event probability is multiplied by (1-z), and expected gross switches, opposing cancellation and expected congestion-cost DRIFT all scale by (1-z). At n=4 current cost is zero, so the expected next excess cost itself scales by (1-z).

SSM5 Full early Q(0,0)=.60177773 already exceeds observed .22077922: no nonnegative freeze probability can repair the early mismatch. In Full late, SSM5 Q(0,0)=.50317535 is below observed .58365759; the exactly fitted late freeze is z=.16199325. It then predicts next excess cost 1.63497819 against observed 1.33073930, raw error +.30423889. A 20,000 whole-session exploratory bootstrap for observed-minus-frozen late welfare is [-.6968,+.1991], **including zero**, so this second error is not a statistically established contradiction. The difference between the observed and SSM5 late-minus-early no-switch change is +.46148075, with exploratory original-session bootstrap [.31841961,.58837208] excluding simulation MC and researcher selection uncertainty.

Rational local verification: activity_mixture 5 tests/16 assertions, ssm_joint_falsifier 2 tests/6 assertions, all pass. The frozen mixture remains a negative-control hypothesis; this does not prove an alternative strategic or cognitive micro-mechanism.

## Scientific novelty and literature custody

The original authors already modeled small-sample reinforcement and the early/late information-efficiency change. Direct rivals from the Research OS Drive collection: Erev & Roth (2014), Camerer & Ho (1999), Ho, Camerer & Chong (2007), Brock & Durlauf (2001), Fudenberg & Levine (1993), and Arthur (1989). These sources cover prior-experience sampling, reinforcement/belief mixtures, social choice interactions, self-confirming belief formation and path dependence. Our freeze benchmark is no novel theory. Strongest next target is a mechanism predicting a simultaneous change in P(no switches), P(opposing cancellation), E(gross switching) and E(next excess cost), with an information-admissible rule, robust heldout tests and an explicit temporal dynamics claim.

Targeted Drive filename searches did not confirm the following exact works; absence not certified: Fudenberg & Levine 2022 (DOI 10.1257/mic.20200106), Benaim/Hofbauer/Sorin 2005 (10.1137/S0363012904439301), McKelvey/Palfrey 1995 (10.1006/game.1995.1023), Kandori/Mailath/Rob 1993 (10.2307/2951777), Young 1993 (10.2307/2951778), Brock/Hommes 1997 (10.2307/2171879), Galla/Farmer 2013 (10.1073/pnas.1109672110). Preserve a missing-literature table instead of claiming files have been obtained.

GitHub Ruby code was committed under the authenticated WhoSia account; github-actions[bot] must never author source commits. Actions source-only tests do not verify participant-data replication; exact checked-out SHA replay and remote Actions run PASS remain unverified. No participant-level original data in the public repository.
