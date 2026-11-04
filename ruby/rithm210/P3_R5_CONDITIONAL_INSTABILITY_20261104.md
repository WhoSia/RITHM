# RITHM-2.10 — P3-R5: Conditional Congestion Instability, Hidden Churn and Welfare Identification
**2026-11-04 KST.** Original six-person congestion experiment; exact identities and exploratory descriptive evidence. Causal treatment effects and theorem novelty **HOLD**.

## Scientific question
Once social cost is the target, which observable dynamic object drives the excess cost of repeatedly reallocating a stable group? Distinguish (i) current-state composition, (ii) conditional instability even at optimal occupancy, (iii) gross reallocation hidden by net occupancy, and (iv) actual resource cost of switching.

Original authorized [Noussair–Qiao ZIP](https://drive.google.com/file/d/1M3m0kCSEJ-FJfkx4g2dtcaro8MO7ZmsE/view), extracted `data_task_all_switch_230705.csv` SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb`. Eligible 24 sessions (excluding 2/101), treatments 1–3, periods 1–39: 5,616 six-person group transitions, 33,696 individual rows. Participant raw rows remain privately stored in Drive. Baseline cost exactly `L(n)=3(n−4)^2` where n is number on A. `NumAnext=n+U−D` is verified for every group.

## P3-R5a — Exact welfare drift from opposing gross flows
With B→A count U, A→B count D, and Δ=U−D:
`L(n+Δ)−L(n)=6(n−4)Δ+3Δ²`.
The latter quadratic term is nonnegative and captures net-occupancy changes; the former can be negative when motion corrects imbalance. They are **algebraic components, not causal estimates of psychological overreaction**.

Observed Full (480 group transitions in each 10-period epoch):
- Early: mean directional term **−6.7625**, quadratic **+6.6625**, net one-step excess change **−0.1000**, P(Δ=0)=**0.30625**.
- Late: mean directional **−4.0750**, quadratic **+4.0500**, net excess change **−0.0250**, P(Δ=0)=**0.445833**.
Large opposing terms nearly cancel. A one-step change must not be confused with early-minus-late *level* differences. [Ruby sealed-source audit](p3/turnover_welfare_drift.rb) and [exhaustive feasible-state Minitest](p3/test_turnover_welfare_drift.rb). Local Ruby 3.3.8: **4 tests / 203 assertions / zero failures**.

## P3-R5b — Conditional instability from exactly the optimal state
A change in the observed distribution of n could explain an aggregate welfare improvement without any change in conditional decision dynamics. Condition instead on **n_t=4**, where the current congestion loss is exactly zero and next-period cost is `3(U−D)^2`.

Full **early** 154 cases: mean next excess **3.01948052**, P(U−D=0)=**0.37662338**, P(U=D=0)=**0.22077922**, P(U=D>0)=**0.15584416**.
Full **late** 257 cases: mean next excess **1.33073930**, P(U−D=0)=**0.66147860**, P(U=D=0)=**0.58365759**, P(U=D>0)=**0.07782101**.
Full early−late conditional next cost decline **1.68874122**; 20,000 24-whole-session paired cluster bootstrap, seed 20261104, exploratory percentile 95% **[1.02501180,2.45535714]**.
P(no gross switches) early−late **−0.36287837**, CI **[−0.49184265,−0.22063574]**. Opposite-direction cancellation early−late **+0.07802314**, CI **[+0.00865091,+0.14837040]**.
The difference reflects *actual switching cessation*, not merely two directions cancelling at unchanged occupancy. Some session×epoch×n=4 cells have no observations; initial script failed by assuming all were nonempty. Corrected bootstrap retains zero-count cells and pools weighted numerators/denominators **after resampling whole sessions**; does not impute zero outcome. A source-free synthetic regression test guards this failure mode.
No condition n=4: early N170 mean next loss2.91176471, late N189 mean2.65079365; cross-treatment causal comparisons remain unestablished.

[Conditional Ruby](p3/conditional_instability.rb), [Minitest](p3/test_conditional_instability.rb). Local source test before two additional published assertions: 2 runs/7 assertions/0 failures. End-to-end raw-source audit rerun after missing-cell repair.

## P3-R5c — Common-state standardization
To prevent changing starting-state frequencies from mechanically generating the entire pattern, fix a *uniform reference distribution* over current n=3,4,5 (all have sufficient support). Calculate the mean next-period welfare conditional on each n and average the three states equally. This does **not** cover occupancy 0,1,2,6 and is not a general causal-standardization effect.
- No: early 3.28209230, late 2.93469851, decline **0.34739379**, exploratory 95% [−0.21707401,+0.91727365].
- Partial: early 2.83189445, late 2.57681348, decline **0.25508097**, CI [−0.28879745,+0.79807001].
- Full: early 3.63663949, late 2.38095350, decline **1.25568599**, CI **[0.65829866,1.85837610]**.
- Full minus No differences-in-declines **+0.90829220**, CI **[+0.01068233,+1.73564674]**.
20,000 whole-session bootstrap draws, seed20261104, recomputing conditional next-cost means and common reference weights. Multiple exploratory comparisons on an already extensively studied dataset, no randomization claim or multiplicity correction. This points to *conditional transition stability* in addition to composition, not identified learning or treatment causality.
[State-standardized Ruby](p3/state_standardized_instability.rb) and [Minitest](p3/test_state_standardized_instability.rb). Local tests before one additional published support check: 2 tests/4 assertions/zero failures.

## P3-R5d — Gross switching resource costs are only partially identified by occupancy
Current n and next m=n+U−D do not determine the number of individual switches G=U+D. The **sharp feasible set** is
`G ∈ {|m−n|, |m−n|+2, ..., min(n,6−m)+min(m,6−n)}`.
Proof: choose D=d between max(0,n−m) and min(n,6−m), then U=d+m−n and G=2d+m−n. All intermediate values in steps of 2 are attained.
For **hypothetical measured real resource cost theta≥0 per switch**, the occupancy-only total *next congestion excess plus switching resource cost* lies sharply between
`L(m)+theta|m−n|` and `L(m)+theta[min(n,6−m)+min(m,6−n)]`.
E.g. n=m=4 allows G∈{0,2,4}: identical congestion cost zero but social cost spans 0..4theta. This is an elementary identification observation, NOT an original theorem. The recorded experiment's Cost DOES NOT measure theta, so no real switching-resource expenditure is imputed, and private psychological disutility must not be equated with external social loss.

Original-source **observed** group mean gross and occupancy-invisible opposing turnover G−|Δ|:
- Full early gross **1.70416667**, extra hidden churn **0.60833333**; Full late gross **1.14166667**, hidden churn **0.35833333**.
- No early gross1.66250000, hidden0.63750000; No late gross1.63958333, hidden0.64583333.
- Partial early gross1.78125, hidden0.75416667; Partial late gross1.57291667, hidden0.59166667.
Full early−late gross decline **0.56250**, session bootstrap CI [0.35833333,0.77346939]; corresponding Full−No difference **0.53958333**, CI [0.30888889,0.77446809].
Full early−late occupancy-invisible cancelling churn decline **0.2500**, CI [0.1200,0.36666667]; Full−No cancellation decline **0.25833333**, CI [0.05957447,0.44583333]. 20,000 24-session resamples, seed20261104. Descriptive, not an experimental treatment causal effect.
Illustrative theta=1 *unmeasured*: Full next congestion excess+gross switching cost early 5.71667, late3.21042. It is a sensitivity value, not an observed or estimated real welfare expenditure.

[Exact bound Ruby](p3/churn_welfare_bounds.rb), [exhaustive all-49-(n,m) tests](p3/test_churn_welfare_bounds.rb) (local 4 tests, 66 assertions, zero failures); [cluster bootstrap](p3/churn_session_bootstrap.rb), [test](p3/test_churn_session_bootstrap.rb) (local 1 test, 4 assertions, zero failures).

## Novelty court and next P3-R6
The original [Noussair–Qiao paper](https://doi.org/10.1287/mnsc.2023.00056) already explains early Full information efficiency harm and late advantage, using Small Sample behavioral models. [Meneguzzer & Olivieri (2013)](https://doi.org/10.1016/j.sbspro.2013.10.593) study empirical day-to-day route volatility and nonpersistent equilibrium; [Srinivasan & Mahmassani (1999)](https://doi.org/10.3141/1676-06) study dynamic information, switching and indifference bands. Our algebra, conditional standardization and churn bounds **cannot independently establish scholarly novelty**.

The key new RESEARCH PROGRAM requirement: Explain in a unified mechanism why at identical optimal current state (n=4) next-period congestion volatility and actual gross switching both fall, and distinguish that from information regime timing and individual heterogeneity. A legitimate behavioral model must predict not only P(n_{t+1}) but P(U,D) or activity G, and then specify external vs private switching-resource costs. Compare original authors' Small Sample model with original-data EWA+inertia and current online-history model at precisely matched information sets, future-free folds, and heldout sessions. Then develop a separately justified network-level transport argument; this six-person group analysis is not a proven city/institution-scale welfare effect.

**Audit:** Raw participant data remain in Google Drive, not public GitHub. New Ruby sources and tests are separate GitHub WhoSia commits, Actions workflow runs read-only unit gates without bot-authored commits. Local original-CSV and independent Minitest runs performed. Byte-identical checked-out GitHub SHA source replay and actual Actions success run/job logs **not yet verified**: CI PASS remains HOLD. [Primary detailed Google Drive P3-R5 research record](https://docs.google.com/document/d/1__2ukO4WBkZNYzF82wwIfy1TAKYwBc_uNzSu6zd42BY/edit) and [Notion RITHM-2.10 charter](https://app.notion.com/p/40def561cf92812e9c51d5073aa70ef4).
