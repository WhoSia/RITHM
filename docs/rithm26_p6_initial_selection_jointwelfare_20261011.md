# RITHM-2.6 P6 — Selection at the information node, initial-condition proxies and joint group-welfare forecasting

2026-10-11. **Exploratory source-bound original-human predictive comparison** only. No identified causal habit effect, no new universally valid theorem, and no new untouched source test.

[Original 2017 author paper](https://doi.org/10.1371/journal.pone.0184191) · [Full original S2 workbook](https://docs.google.com/spreadsheets/d/1Kv-fWLa6kP_tv9PpgNDUYIV3oiC-zmRc/edit) · [P1–P6 Notion](https://app.notion.com/p/3f5ef561cf9281cf912ee6f52f532021) · [P6 parallel Harvest](https://app.notion.com/p/3f5ef561cf9281489be4c0d410e357dd)

Human source SHA256 f2047f7c2ae8999a9f0660f3b5c192aea171b715284bf2aa05b40c10b902d863. 6 original sessions, 12 groups of 12, 2 conditions ×20 rounds, 5,760 routes and 3,511 actual junction-C choices. Exactly 4 incidents per group-treatment sequence. Six original Cost-versus-count source anomalies retained. Person-level raw records or source XLSX NOT committed.

## Honest behavior and group-welfare results

| Model | A logloss | C logloss conditional A–C | Pre-incident independent group-cost MAE | Simple training-only intercept MAE | Joint residual calibration MAE |
|---|---:|---:|---:|---:|---:|
| Structure/clock | .666493 | .550630 | 12.807504 | 12.684420 | 12.406005 |
| Older choice propensity + immediate past | .629044 | .506456 | **12.681299** | 12.624710 | 12.375989 |
| Above + first observed choice + C eligibility history | .628568 | .505493 | 12.694375 | 12.599753 | **12.373013** |
| Above + experienced own cost | .629135 | .505210 | **12.818099, fails S0** | 12.699746 | 12.502330 |

Six leave-one-whole-session-out folds; no use of CURRENT shock upstream or in offline node C. Stage-C target only exists after A–C arrival; scoring on observed eligible people never fabricates counterfactual decisions. The initial observed response covariate is no more than a proxy and is NOT Wooldridge (2005) correlated random effects. Predicted group path probabilities combine P(AC) and P(CB|AC) with individual independence; alternative policy behavior of nonentrants not causally identified.

Quadratic traffic group welfare depends on covariance among named driver route indicators. Cross-residual D=[(actual X−pred X)^2−sum independent X Bernoulli variances]+[(actual Y−pred Y)^2−sum independent Y Bernoulli variances] is computed on other 5 sessions, separately by actual shock/arm, with fixed shrinkage n/(n+120), and shock integrated using legal finite-quota prior. It is NOT a pure covariance estimator because mean bias survives. A simpler train-only mean-residual intercept is an essential competing group baseline. For older+last MAE 12.6813 independent, 12.6247 simple intercept, 12.3760 joint residual; 6/6 external-session numerical improvements. Experiment/model development used all six folds; not prospective confirmation.

17/17 source-data, timing, eligibility, likelihood-factorization and group-model focused regression tests PASS. Reproducible code, machine JSON, audit logs and literature/paper portfolio available via chat-local ZIP; source XLSX must be obtained separately from Drive. The report is not an experiment or a new source dataset.

## 2.0–2.6 paper-prior-art gate

2.0–2.1 Ashraf 18-player payoff dispersion = exact descriptive quadratic algebra; 2.2–2.3 personal history ≠ robust group welfare improvement; 2.4 hysteresis and robust MDP count theorems classical predecessors; 2.5 named-memory coupling/trace-regret examples overlap with Fréchet/OT/PSR/Blackwell; 2.5-D nonabsorbing short benefit–long harm is synthetic and memory necessity falsified; 2.6 human stage/node-C timing and group welfare are promising ONLY if the model genuinely transfers to independent groups and goes beyond the existing routing-policy learning literature.

Direct collision papers: [Yu & Gao 2019](https://doi.org/10.1016/j.trc.2019.07.014), [Wooldridge 2005](https://doi.org/10.1002/jae.770), [Honoré–Kyriazidou 2000](https://doi.org/10.1111/1468-0262.00139), [Manski 1993](https://doi.org/10.2307/2298123), [Brock–Durlauf 2001](https://pdodds.w3.uvm.edu/files/papers/others/2001/brock2001.pdf), [Noussair–Qiao 2025](https://doi.org/10.1287/mnsc.2023.00056) and [Unnikrishnan–Waller 2009](https://doi.org/10.1007/s11067-009-9114-y). Their original PDF bytes were not found by indexed Drive title/author searches, not proof they are absent from every unindexed archive.

Next: actual correlated random effects with a valid conditional initial state likelihood, jointly modeled A-C entry and incident-contingent policy choice, genuine external group welfare holdout and model-selection discipline. The present P6 outcomes alone are not publishable general causal or prediction laws. **RITHM-2.6 OPEN.**