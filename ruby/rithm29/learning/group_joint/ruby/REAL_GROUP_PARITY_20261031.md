# 2026-10-31 Ruby full group scoring audit

Original existing dataset: 34,560 source-feasible individual one-step out-of-fold predictions. Ruby replay aggregates 5,616 group-periods (144 blocks × 39 transitions). Participant history is keyed by treatment, session, section, group and actor; current-period six actions are reserved for scoring, not for input to forecasting.

Independent Python comparison on (trt,session,section,Group,Period), one-to-one, exactly 5,616 rows:
- max |P_Ruby(U,D)-P_Python(U,D)| = 2.22e-16
- max |P_Ruby(cancellation)-P_Python(cancellation)| = 3.33e-16
- max |E_Ruby(switchers)-E_Python(switchers)| = 2.22e-15
- all observed U,D,S, cancellations and keys matched exactly.

Ruby EWA independent product model scores *among transition periods only* (t>=2): observed (U,D) logloss 2.0684287662; count N logloss 1.4824580712; 7-class Brier 0.7330304052; mean predicted cost 4.6616063806 vs actual mean cost 4.4991987179; mean predicted switchers 2.0463339968 vs actual 1.5863603989; predicted cancellation rate 0.3568033167 vs observed 0.2752849003.

Important denominator: these costs/scores are for 5,616 transitions **not all 5,760 periods**; never compare without matching period inclusion.

Repro regression identified an older local ZIP of group_scoring.rb that had no cancellation fields even though current GitHub file has them. Fixed local artifact by retrieving expected fields and added regression check to GitHub. This is packaging/version drift, not a defect in the directional probability model. Primary repository code remains canonical.

No participant recruitment, independent heldout data or causal mechanism identification occurred. The results validate numerical implementation; they do not show that EWA is behaviorally correct.
