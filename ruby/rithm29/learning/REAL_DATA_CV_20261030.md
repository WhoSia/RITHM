# RITHM 2.9 — EWA-lite and SSM on original route-choice participants (2026-10-30)

## Scientific objective

Learn the mechanisms behind informed participants switching less late in the 40-period experiment. This is **behavioral reverse engineering**, not a historical code-audit court: good predictive scores are constraints on candidate explanations, not identifications of cognitive algorithms.

## Sources

- Original unmodified author ZIP (4 CSV, 6 R files): https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view ; Drive folder https://drive.google.com/drive/folders/1uAP-eAE_yQ-mal8tUUW60ljIEsABO0Il ; SHA256 `e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953`
- Original author manuscript: https://drive.google.com/file/d/1rTL9qTpYV6zwee6pC3nZy64H07oSWzlK/view
- Author Online Appendices A.1/A.2 (EWA), B.1 (SSM), A.4 (MLE): https://drive.google.com/file/d/1xwIj82h_LTrgffv2w4XtJs2KDc8980RW/view
- Study Notion record: https://app.notion.com/p/409ef561cf9281f4ab69f336058504d4

## Analysis design

Original author `data_task_all_switch_230705.csv`: 50,160 rows. Restrict to trt=1,2,3; exclude sessions 2,101; keep section<=4; 34,560 choices in 864 subject-treatment-blocks, 144 six-person group-blocks and 24 sessions.

Use `GroupKFold(6)` blocked on **whole session**, because same people may appear in several treatment blocks of their session. Fit EWA lambda from training sessions only, then predict unseen sessions. Predictions are one-step conditional on **observed** previous choices and feedback; not counterfactual free-running agent trajectories. EWA uninformed updates do not see actual other-route congestion, but average uniformly over the six OTHER-player A counts compatible with own chosen route and realized payoff. Informed updates use prior total A counts to compute a unilateral-deviation payoff under fixed opponents.

## Out-of-session predictive results

| Model | log loss | Brier | accuracy |
|:--|--:|--:|--:|
| Training treatment/feedback-stratum route frequency | 0.639645 | 0.223684 | 0.664062 |
| Markov previous-own-route, fitted from train | 0.558546 | 0.186956 | 0.734028 |
| EWA-lite, lambda fitted from train | **0.538685** | **0.180986** | 0.729745 |
| SSM5, with separately fitted train-only lapse | 0.617271 | 0.213275 | 0.695168 |
| SSM1–9, with separately fitted train-only lapse | 0.617881 | 0.213461 | 0.695341 |

**Uncalibrated original SSM**: exact 0/1 probability predictions conflict with some observed choices, so unmodified log-loss is infinite. Its Brier was 0.219904 (SSM5) / 0.218128 (SSM1–9). The fitted random-choice lapse is an **explicit extension** to obtain finite log-loss, NOT part of the authors' SSM5 rule. SSM predictive probabilities were estimated by deterministic Monte Carlo seed 20261030 with Q=1536 for SSM5 and at least 200 draws per q for 1..9; the q=1..9 choice is marginally averaged per time step, rather than posterior learning of a fixed latent per-person q. Do not claim exact author SSM likelihood reproduction.

6 EWA held-out lambda training estimates: 0.302542, 0.313549, 0.308715, 0.310350, 0.309566, 0.308258. Whole-data **independent Ruby MLE**: 0.3088344939, logloss in-sample 0.5385452. This matches original Appendix A.4 segment 1–3 aggregate reported lambda 0.31. Treatment-specific independent estimates No 0.282890 vs original rounded 0.28; Partial 0.303033 vs 0.30; Full 0.349074 vs 0.35.

Independent Ruby whole-session CV `ewa_session_cv.rb` returned logloss EWA 0.53868469745 / Markov 0.55854648714, Brier EWA 0.18098582341 / Markov 0.18695592857, agreeing with Python. Separate 12-step 2-type Python/Ruby attraction-difference replay max error <8e-14; removing all unrevealed congestion data from the uninformed input leaves predictions unchanged.

Paired 24-session *weighted* bootstrap, 20,000 replicates (descriptive predictive precision):
- EWA − Markov log loss -0.019862; percentile 95% range [-0.028758,-0.011019].
- EWA − Markov Brier -0.005970; percentile 95% range [-0.009612,-0.002355].

**Counterevidence to global dominance:** Full-information early (periods 2–10) EWA loss 0.617593 > Markov 0.581715; Full late (31–40) EWA 0.430037 < Markov 0.478689. EWA can win average and lose in a meaningful subgroup. The sign-reversal deserves causal-mechanism exploration, not a new PASS/HOLD.

## Sharp observational-equivalence example

Under the paper's `c_A=n_A`, `c_B=2n_B` and travel value support [6,16], after choosing A and seeing payoff 5:
- World W0: 0 of five others choose A, value 6, A cost 1, alternative B cost 12; B payoff -6.
- World W5: all five others choose A, value 11, A cost 6, alternative B cost 2; B payoff 9.

Both deliver identical observed own action and payoff, yet differ on the rational unilateral deviation. A policy based only on that observation switches with probability p. Worst-case regret max(11p,4(1-p)) is minimized at p=4/15 with loss 44/15. Independent Ruby exact rational and Python 15,001-point grid checks were executed. This is a **constructed local information lower bound**, NOT an original authors' theorem or observed human regret. Prior observational history / beliefs / strategic joint changes may modify its applicability.

## Deeper reading and next experiment

Ho–Camerer–Chong (2007): one-parameter EWA self-tunes attention and experience. Ho–Wang–Camerer (2008): different permissible counterfactual-payoff estimates under partial information. Lieder–Griffiths (2019) resource-rational cognition and Kahneman–Klein (2009) feedback validity caution against treating forecast score as the true cognitive mechanism. Fudenberg–Kreps (1995) on/off-path learning. All source donor theories, no unverified novelty promotion.

Next: formalize SSM1–9 person-persistent latent q and integrate posterior on q; quantify MC uncertainty; compare EWA vs Markov *conditional residuals* after unforeseen congestion changes; then design an external randomized shock and forecast-belief elicitation. Add joint congestion/social welfare evaluation because one-step accurate individual prediction alone does not determine welfare.

## Commands

From `ruby/rithm29/learning` in this repo, with the local author CSV:
```sh
ruby test_learning_models.rb
ruby offpath_identifiability.rb
ruby ewa_real_mle.rb /path/to/data_task_all_switch_230705.csv
ruby ewa_session_cv.rb /path/to/data_task_all_switch_230705.csv
```

Python full EWA/SSM analysis code, fold scores, bootstrap, and per-choice predictions are part of the **research ZIP available in this ChatGPT conversation**. Raw original experiment CSV is not re-committed to GitHub; access original authenticated Drive file.
