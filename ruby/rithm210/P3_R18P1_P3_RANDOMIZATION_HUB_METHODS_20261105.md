# RITHM-2.10 P3-R18-P1/P2/P3 — Randomization Validity, Exact Sign Test, Truthful Timestamped Protocol

2026-11-05 KST. **Synthetic methods/implementation and connected-tool audit; no new subjects, trial, causal effect or novelty claim.**

## I. Scope and independent methodological review

R17F replaces the degenerate synchronous refresh factorial by a truthful sequential-only 2×2 crossing (a) previous-period versus current-period initial signal and (b) refreshing true occupancy after each completed microdecision versus freezing the initial report. Each of 6 labelled participants acts exactly once per macro-round. Session/independent group, not person, is the experimental randomization unit. Do not condition inferential comparisons on occupancy realized after assignment, and do not assume no cross-cluster interference without controlling the environment.

External scientific retrieval: Consensus searched day-to-day traffic learning/feedback and cluster interference. It returned and the paper record was fetched for **Viviano et al. (2023), _Causal clustering: design of cluster experiments under network interference_** ([Consensus paper](https://consensus.app/papers/causal-clustering-design-of-cluster-experiments-under-viviano-lei/164e932ddbe858c69af52855d7a8a282/)). That paper develops clustering choices under spillovers; not a validation of RITHM's specific four-arm treatment. Related 2026 Yang et al. reinforcement learning route choice remains a serious prior-art constraint. Wolfram Language was invoked to cross-check the 4-arm Gaussian power approximation, with m_unrounded≈68.7185 clusters per arm for historical σ=29.58918599, target interaction δ=20, α=.05, nominal power .80, hence **69/arm**. A first Wolfram input had a syntax error and was discarded; this corrected independent evaluation succeeded.

**MCP-Hub audit:** Render My Workspace was queried live. Active configured services include `mcp-hub-gateway`, `mcp-hub-semgrep`, `mcp-hub-repomix`, `mcp-hub-arxiv`, Playwright, Mermaid, AntV and others. [MCP-Hub platform branch README](https://github.com/WhoSia/MCP-Hub/blob/platform/standalone-hub/README.md) documents public bounded MCP and a bearer-protected private Gateway with original-engine proxy tools. These deployments are **not automatically exposed as callable tools in this ChatGPT session**, and the named 'Ponytail' tool was not found in accessible tool manifests, Render services, or plugin catalog. Thus this output DOES NOT claim a Ponytail, private Semgrep proxy, DeepSeek or MCP-Hub native tools/call execution. Actual specialized connected calls here: Consensus search+fetch, Wolfram computation, Render workspace and service inventories, GitHub code and commits, plugin discovery. Native Gateway health/registry HTTP GET through web search failed; this is not proof of server outage. No secrets requested or sent.

## II. R18-P1 group-level four-arm inference, not individual-level pseudo replication

Let Y_g(a) denote complete 40-period welfare for randomized session g in arm a, with arm labels LF=lagged/no feedback, LR=lagged/feedback, CF=current/no feedback, CR=current/feedback. Intended finite-population interaction is τ=E[Y(CR)−Y(CF)−Y(LR)+Y(LF)]. Equal arm size m, cluster-mean estimator `tauhat=mean(CR)−mean(CF)−mean(LR)+mean(LF)`.

The source-free [Ruby R18 randomization inference](p3/r18_randomization_inference.rb):
- validates equal **independent session** counts across all four arms and finite cluster outcomes;
- computes the interaction estimate and its conservative Neyman-style variance estimate `sum_arm(s²_arm/m)` when m≥2. This omits unknown finite-population treatment-effect heterogeneity covariance, and is not a design-valid small-sample t confidence interval by itself;
- enumerates **all 24 (one/arm)** or **2520 (two/arm)** balanced labelled four-arm assignments for the **Fisher sharp-null** that no arm changes any cluster outcome;
- for larger n uses a seeded uniform balanced permutation Monte Carlo with add-one p-estimator, not a confidence interval nor a test of the weak null E[tau]=0.

No observed human trial outcome was used in the Fisher tests. The example labels and costs in source-free tests are synthetic fixtures.

## III. R18-P2 analytic reduction and an unusually important small-trial gate

The two-sided randomization statistic depends only on each session's **positive versus negative coefficient** in the interaction (+ for LF/CR, − for LR/CF), not on its label *within* each sign pair. Under equal-arm complete randomization, all `choose(4m,2m)` sign partitions are equally likely.

For n=4m independent clusters, `tauhat=(2*sum_{positive}Y−sum_all Y)/m`. Every unique sign partition has `choose(2m,m)^2` identically-valued four-arm assignments. Hence sign-reduced exact sharp-null enumeration and full labelled allocation yield EXACTLY the same two-sided p-value, with far fewer evaluations.

Because every sign partition has a sign-flipped partner with the same |tauhat|, the smallest attainable two-sided **exact Fisher** p under this balanced design is bounded below by **2/choose(n,n/2)** (ties can make it larger). Thus:
- 4 clusters (one/arm): 24 four-arm allocations but only 6 sign partitions; **p_min = 1/3**. One/arm CANNOT reject the Fisher sharp null at 5% no matter how large the contrast.
- 8 clusters (two/arm): 2,520 four-arm allocations but only 70 sign partitions; **p_min = 1/35≈.0285714**, so a 5% rejection can become combinatorially possible under extreme allocation.
- 24 clusters (six/arm): choose(24,12)=2,704,156 sign partitions; theoretical minimum ≈7.4×10^-7, but this is a **resolution bound, not a guarantee of useful power**. R18-P0's historical σ gives MDE ~67.7 total-cost units at 6/arm under crude Gaussian planning.

[Sign-reduced Ruby](p3/r18_sign_reduction.rb) and [tests](p3/test_r18_sign_reduction.rb) check the formula and exact four-arm enumeration parity for n=4 and n=8. This elementary randomization combinatorics is not itself a claimed novel statistical theorem.

## IV. R18-P3 implementation acceptance criteria for a truthful sequential experiment

[Ruby protocol audit](p3/r18_truthful_signal_audit.rb) verifies a complete six-microaction log:
1. Each of six actor IDs appears exactly once; each may either retain route or flip only their own route bit.
2. `before_mask` of every event matches the previous event's `after_mask`; no silent manipulation or duplicate turn.
3. An initial **truthful previous-period** report is labelled `:previous_period`; a truthful **current-period** report is labelled `:current_period`; its value equals the matching occupancy before the round.
4. With within-round feedback enabled, every actor AFTER the first receives the actual occupancy AFTER the previous microaction and before their own. With feedback disabled the original report remains frozen, including its truthful timestamp.
5. Any impossible reported occupancy, incorrect timestamp, missing microaction, duplicated actor, nonacting-player route flip or broken trace raises an error. Synthetic acceptance fixtures cover all 4 R17F arms.

Critically, protocol observability is not psychological mechanism identification. A real experiment still needs independently logged signals, timestamps, random order, timing of randomization relative to baseline state, participant consent, group-isolated sessions, stable rules and a completed independent pilot.

## V. Actual implementation evidence and limits

GitHub code committed as multiple human-authored units:
- [R18-P1 estimator and Fisher sharp-null tests](p3/r18_randomization_inference.rb), [test](p3/test_r18_randomization_inference.rb).
- [R18-P2 sign-reduced exact test](p3/r18_sign_reduction.rb), [test](p3/test_r18_sign_reduction.rb).
- [R18-P3 nondeceptive protocol audit](p3/r18_truthful_signal_audit.rb), [test](p3/test_r18_truthful_signal_audit.rb).
- Read-only CI workflow updated to include all new tests; no bot-author commits.

A separate Ruby3.3.8 local implementation of equivalent mathematical and event-log logic was actually executed: **15 tests / 53 assertions / 0 failures**. The GitHub published files have not been downloaded byte-for-byte and executed in the container, so published-SHA exact parity and remote GitHub Actions PASS remain HOLD. This report is NOT a trial protocol approval. The science gap remains external group-randomized evidence and fair original author SSM/EWA comparisons.

**Date-folder raw-byte archival proof:** [Original R18-P1–P3 Markdown in Google Drive](https://drive.google.com/file/d/1sfkr5IcagzfOqwEEOzadeiefUjTqe0GY/view?usp=drivesdk), under `공유드라이브 → 하고 있는 거 → 20261105 김우준의 사유`. Uploaded as text/markdown and downloaded again through authenticated Drive connector. Exact source/retrieved SHA256 **`c1ad36fadb88f427c5179eebb7f4dfac5dcc5725e5b8a191651a4e6c9f5c4f8d`**, 3821 raw bytes. This GitHub research record is the extended English analysis; the Drive file is a Korean human-readable digest with separate bytes. No deletion/move of historical evidence.

## VI. Research-manager gate

R18-P4 should prioritize (i) unit of randomization and interference assumptions, (ii) pre-treatment occupancy/history measurement, (iii) masked/pre-registered outcomes including full 40-period excess welfare, (iv) power feasibility under at least two realistic variance/effect scenarios, (v) honest information delivery and record verification, and (vi) preregistering a single primary estimand before recruitment. A small synthetic p-value is not a human finding; a historical one-step forecast or an unexposed MCP tool is not independent evidence. No paper-level causal or novel mechanism claim is promoted.
