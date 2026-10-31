# Source-only persistent latent q experiment, 2026-10-31

Using independently computed exact q=1..9 probabilities for all 34,560 participant choices, a uniform prior over *fixed* q_i is updated sequentially from each actually observed choice. Separate person-treatment-block boundaries (864 sequences, length 40) reset q prior. With train-only lapse chosen by maximizing the **individual full-sequence marginal likelihood** (logsumexp over nine q paths) within six whole-session folds, heldout one-step posterior predictive results:

- **Persistent q**: logloss **0.6078544055**, Brier **0.2091471189**, accuracy **0.6955729167**.
- Uniform q averaged per period, with separately fitted lapse: logloss **0.617754**, Brier **0.213398**.
- Fixed q=9 (lapse independently fitted): logloss **0.613382**, Brier **0.211823**.
- Prior MC q1..9: 0.617881 (not fully exact).
- EWA full model: 0.538685, EWA chosen-only ablation: ~0.515469 (earlier exploratory evaluation).

Lapse eta per training fold: 0.259563, 0.244611, 0.248492, 0.242114, 0.238316, 0.251869. Fold test loglosses respectively 0.579849, 0.615840, 0.613130, 0.614147, 0.624825, 0.599336.

**Mathematical distinction**: L_i(eta)=(1/9) Σ_q Π_t[(1-eta) P_q(y_it|history)+eta/2]. Each participant q posterior is proportional to cumulative path likelihood and is updated after observing the current choice. No future y leaks into predictions.

Caveats: this is a candidate developed while analyzing the same 24 historical sessions; out-of-session train/test separation prevents direct parameter leakage but is not confirmation independent of model discovery. q_i is held fixed within a 40-period person-treatment block, not necessarily across the same experimental subject's multiple blocks. We do NOT infer true individual memory size, establish incentive/welfare causality, or propose fresh human-subject research. Full reproducible Python and per-choice CSV in the contemporaneous chat artifact.
