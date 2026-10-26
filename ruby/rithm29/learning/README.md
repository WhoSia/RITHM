# Learning, self-confirmation and adaptability: empirical bridge

## Research question

Does an informed participant's lower late-period route switching reflect successful learning, stable-but-fragile self-confirmation, habit, or strategic forecasting? **Switching prediction is not mechanism identification.**

## Primary-method donors

- Fudenberg & Kreps (1995), *Learning in Extensive-Form Games I: Self-Confirming Equilibria*: on-path observations can validate beliefs while off-path beliefs remain wrong. Canonical Drive: https://drive.google.com/file/d/1rGaoxbbfjLOU_MFSA9w5nO9t2ugT5Qpg/view
- Simon (1955), *A Behavioral Model of Rational Choice*: aspiration/satisficing. Drive: https://drive.google.com/file/d/14mO0Mr8-BNMSNDg-yvjbyVOBe1ZvXB7e/view
- Hart & Mas-Colell (2003), *Uncoupled Dynamics Do Not Lead to Nash Equilibrium*: convergence limitations for uncoupled dynamics under specified classes; does not imply nonconvergence in this experiment. Drive: https://drive.google.com/file/d/1lIb3tXPXhAbG9Y2U4AnLJDDFxDHNV9dH/view
- Fudenberg & Levine (2009), *Learning and Equilibrium*: https://scholar.harvard.edu/files/fudenberg/files/learning_and_equilibrium.pdf
- MIT course, *Learning with bandit feedback*: https://www.mit.edu/~6.7980/bandit.html . Explore/exploit and partial observation are methods, not evidence human players use EXP3.

## Exploratory calculations (2026-10-26)

Recovered author file: data_task_all_switch_230705.csv from the user-authorized ZIP. Partial treatment trt=2, exclude sessions 2 and 101, section<=4, periods 1..40. 48 independent (session,section,Group) clusters. Prediction rows periods 3..40: n=10,944. 6-fold GroupKFold by cluster (train/test groups disjoint), logistic regression with standardized features within training folds and common C=1.

Log loss:
- informed + period + interaction: 0.592993
- prior switching, previous route (inertia): 0.528139
- previous experienced costs, cost asymmetry, state familiarities: 0.509742
- add prior aggregate congestion changes: 0.509101

Brier scores: 0.201698; 0.176777; 0.170153; 0.170031.

The experience+social-proxy difference is small. **Not** a claim that strategic behavior is absent. The observational treatment contrast is post-treatment confounded by routes and shared congestion histories. Learning and habit are not identified by predictive performance. Familiarity uses previously encountered aggregate counts; late periods 31..40 leave only 18/2880 (0.625%) observations with <=1 prior exposure of the lag state, so there is severe lack of unfamiliar-state support.

## Ruby scope

`history_features.rb` computes past-only experience summaries for a *single participant*, and `test_history_features.rb` verifies no future leakage on a synthetic four-row fixture. Ruby is a minimal reproducibility primitive, not a replication of scikit-learn logistic CV. The separate Python exploratory analysis is the source of the four quantitative CV scores. The six-player experiment is not interchangeable with the theoretical two-player XOR game.

## Next discriminating experiment

Vary a truly exogenous change in route costs; measure forward beliefs and counterfactual route forecasts separately; randomize observation of public vs private signals and information saturation; distinguish stability, shock adaptation and regret. An unobserved prior option cannot be coded as *known* to the subject.
