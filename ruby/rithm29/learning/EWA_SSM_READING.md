# EWA-lite × SSM learning laboratory — 2026-10-30
**Original:** Noussair & Qiao, Online Appendices A.1–A.2 and B.1, https://drive.google.com/file/d/1xwIj82h_LTrgffv2w4XtJs2KDc8980RW/view. This laboratory **learns from the original**, it does not claim reproduction of the paper's experimental fit.

### What is implemented
- EWA-lite observation-equivalents N(t), action attractions, surprise-based phi, reinforcement delta, softmax lambda; uninformed type's uniformly weighted *compatible* other-A-counts from own chosen route and payoff.
- SSM5 / SSM1–9 with replacement; informed has reconstructed alternative payoffs, uninformed samples only options actually previously chosen.
- Unit tests `ruby test_learning_models.rb` and synthetic demo `ruby compare_synthetic.rb`; the demo requires no personal data and writes `synthetic_model_comparison.csv`.

### Scientific boundary
The appendix's published simulation tables and the author empirical scores are NOT reproduced. Tie breaking, value support endpoints, rounding, and time reset across experimental blocks need source-level reconciliation. The available mounted original experiment CSV inside Data and code files.zip has zero-filled bytes, preventing actual re-fit/CV in this runtime. Earlier 48-group CV numbers derive from an oracle-features exploratory model, not these behavioral learners. Recover original rows before grouped held-out predictions.

### Bigger question
The observed low switch rate does not identify learning, habit, or Bayesian forecasting. Simon's aspiration and Lipman's perception frames plus Fudenberg–Kreps self-confirmation and online partial feedback point to informative intervention: perturb congestion and measure what subjects believed about never-chosen routes, then evaluate adaptation and collective welfare.
