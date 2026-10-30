# Exact SSM q=1 on original observations

No new human participation. Noussair–Qiao source-only 34,560 existing participant choices, 24 sessions.

When both routes have histories A={a_i}, B={b_j}, exact sample-one P(A) = sum_{i,j} [1(a_i>b_j)+0.5*1(a_i=b_j)]/(|A||B|). Without histories of both alternatives predict 0.5. Only source-feasible past own payoff and chosen route are read by uninformed; informed additionally reconstruct the foregone payoff using past aggregate traffic and a unilateral deviation. No Monte Carlo is needed for q=1.

Identical 6-fold whole-session splits as previous experiments. Training-only fit of an explicit lapse eta: folds 0.231081, 0.222984, 0.222736, 0.214486, 0.216426, 0.233747. Heldout q=1+lapse: logloss **0.6387653**, Brier **0.2224165**, accuracy **0.6949942**. The **unmodified exact q=1** logloss is **0.9740666**, Brier **0.2214896**, showing lapse improves logloss but worsens Brier (non-trivial scoring-rule tradeoff). Reference: EWA original 0.5386847/0.1809858; Markov 0.5585465/0.1869559; previous MC SSM5+lapse 0.6172709/0.2132746. These scores come from actually executed local script `ssm_q1_exact.py` and full 34,560-row `ssm_q1_exact_predictions.csv`; files can be recovered from current chat artifact, not committed raw participant data.

**Scientific limitation:** q=1 exact rule should not be identified with all commonly-used meanings of probability matching: in this route-specific independent-draw formulation, P(A) is a pairwise payoff-order probability and does not generally equal the historical frequency of choosing A. The Erev–Roth 2014 comparison calls sample-of-one a probability-matching generalization in their setting; no universal equivalence is asserted here. The exact q1 rule is a small-sample mechanistic benchmark, not a fitted/identified psychological mechanism. Full SSM1–9 with persistent latent participant q_i and posterior-updated q_i remains for future computation. Check group dependence and selective exploration.

Research note: https://app.notion.com/p/409ef561cf9281f4ab69f336058504d4
