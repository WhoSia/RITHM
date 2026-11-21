# RITHM P3-R59 prior-art addendum — source acquisition and novelty gate

2026-11-21 KST. This note **supplements rather than rewrites** the byte-sealed R59 ZIP and original report.

## Held in the user's Research OS

**Erik Talvitie (2014), _Model Regularization for Stable Sample Rollouts_** — [verified user Drive PDF](https://drive.google.com/file/d/1uX5iZngnoogPxdUaLE0RuonlFIS7DpkW/view). The original abstract explicitly identifies the mechanism in which an imperfect simulator receives its **own flawed samples as its next inputs**, permitting errors to compound, and evaluates “hallucinated replay” as a corrective training method. This materially pre-empts broad novelty claims for R59's “teacher-forced one-step score is insufficient for a rollout” argument. It does **not** include R59's original-author traffic-data cohort, 24-session treatment-matched forecasting or linked actor carryover audit.

**Noussair & Qiao**, _Congestion Information and Efficiency: An Experiment_ — [user Drive author paper](https://drive.google.com/file/d/1rTL9qTpYV6zwee6pC3nZy64H07oSWzlK/view); [September 18, 2025 Appendix PDF](https://drive.google.com/file/d/1xwIj82h_LTrgffv2w4XtJs2KDc8980RW/view). Appendix A/B define the model-specific payoffs and inferred beliefs. Appendix **E already tests order/carryover effects**, particularly a decline in No-information cost in segment 3; cross-segment carryover itself is **not** R59 novelty.

## Original PDFs not located by exact-title Drive search

1. **Ross, Gordon & Bagnell (2011), _A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning_** — [peer-reviewed PMLR original](https://proceedings.mlr.press/v15/ross11a.html); [author PDF](https://proceedings.mlr.press/v15/ross11a/ross11a.pdf). Citable background for error compounding under policy-induced changes in sequential input distributions.
2. **Bengio, Vinyals, Jaitly & Shazeer (2015), _Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks_** — [NeurIPS record](https://proceedings.neurips.cc/paper/2015/hash/e995f98d56967d946471af29d7bf99f1-Abstract.html). Relevant in the teacher-forcing versus generated-history distinction.

**Status:** not found by exact-title Drive searches; this is **not** an assertion of absence from every Drive folder. The public official pages are verified references and the PDFs should be tracked in the outstanding-source register until the desired versions are actually acquired and read.

## Novelty boundary

R59's defensible claim is a **specific reproducible empirical falsification**, rather than a new general theorem: the same original 24-session traffic source, training-exclusive 23-session fits and legal information masks produce ranking reversals between one-period predictions and 40-step self-generated welfare forecasts, and a pooled macro match can hide incorrect Full-versus-No contrasts. A separate SHA-checked raw/enriched source cross-audit and matched original participants' within-group negative control improve the evidence discipline. Causal policy welfare, psychological inertia, independent switch-price κ and universal model ranking **remain unidentified**.

For the sealed code, empirical tables and source-free tests use [R59 main report](RITHM_R59_20261121.md). Original human rows are never published.
