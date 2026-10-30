# EWA-lite ablation, existing author data only — 2026-10-30

**Research design constraint:** NO new human participants, new behavioral elicitation or recruitment. Research using already-collected original Noussair & Qiao experiments and public sources only.

## Actual executed original-data test

Source `data_task_all_switch_230705.csv` from original author ZIP archived in RITHM lab Drive. Original author exclusions leave 34,560 route choices across 24 distinct experiment sessions. Each EWA variant is evaluated using the same six whole-session heldout folds, with the free lambda parameter fitted on training sessions only. The prediction task is next choice *conditional on observed participant histories*, not freely simulated strategic joint dynamics.

| Variant | OOS logloss | Brier | accuracy |
|--|--:|--:|--:|
| **Reinforce actual chosen route only**; retain original phi | **0.515469** | **0.171639** | **0.741725** |
| Uninformed: substitute most recently earned unchosen-route payoff | 0.537084 | 0.180605 | 0.726881 |
| Authors' original EWA-lite | 0.538685 | 0.180986 | 0.729745 |
| No experience discount: phi=1 | 0.551266 | 0.185681 | 0.722367 |
| Constant phi=0.5 | 0.551339 | 0.185753 | 0.721672 |
| Reinforce both strategies regardless of realized payoff | 0.594066 | 0.203609 | 0.692361 |

- Chosen-only vs original Δlogloss **−0.0232152**. 23 of 24 sessions independently favor chosen-only.
- Session weighted bootstrap 20,000 replications exploratory 95% percentile interval: **[−0.0286137,−0.0177518]**.
- Original EWA independent trajectory reproduces saved first-pass probabilities with maximum difference **1.11e−16**.
- Full info periods 2–10: original 0.61759 vs chosen-only 0.59265; periods 31–40: 0.43004 vs 0.40331.
- Partial uninformed original 0.57667 vs chosen-only 0.54485; Partial informed 0.51771 vs chosen-only 0.49821.

**Interpretation boundaries:** The predictive advantage of not reinforcing unchosen options challenges the assumption that more off-path reinforcement necessarily improves forecasts. It does NOT identify actual cognition, evidence of no counterfactual reasoning, or population-level welfare. The candidate model was selected during exploratory work and should be evaluated in genuinely untouched data or via explicitly nested/honest CV before a confirmatory claim. Original EWA fits primary source Appendix A.4 parameter estimates well; ablation fit is a different, restricted theory.

## Reproduce

An accompanying analysis archive was produced in the research session: `RITHM29_EWA_Ablation_20261030.zip` containing `ewa_ablation.py`, `ewa_ablation_scores.csv`, `ewa_ablation_strata.csv`, `ewa_ablation_session_losses.csv`. ZIP SHA256 `a1d038cd574a0afd327f3b13215abb8588c67976ba1d7d0237847e7ec2da2a5e`, CRC PASS. Requires original author's CSV, pandas, NumPy, SciPy, scikit-learn and existing `analyze_real.py` from earlier attached research bundle. Raw experiment data is not committed to GitHub.

## Next source-only research tasks

1. **SSM1–9 persistent latent sample size q_i** across whole subject sequence: correct individual-level likelihood/posterior vs periodwise prior mixture.
2. **Exact probability / MC precision** rather than treating 1536 Monte Carlo samples as exact.
3. Explore individual learning-type heterogeneity using pre-existing longitudinal data, limiting overfit at 40 periods/person.
4. Assess joint six-person congestion count distributions and cost forecasts; respect social interference.
5. Test information-limited belief identification using existing data and formal observability bounds.

Notion lab record: https://app.notion.com/p/409ef561cf9281f4ab69f336058504d4 .
