# RITHM-2.7 P27 — Observed Human Routing, Assumption-Conditioned Welfare Sets & External Exposure Gate

**2026-10-13 · Same sole active RITHM-2.7 Flowing mainline · no standalone new generation.** This analysis does not claim to observe a new intervention, participant advice reading, trust, traffic sensor receipt, or policy-induced choice. All numerical results are conditional exact finite optimization around previously recorded route profiles.

## Primitive research question

What **extra restriction on actual eligible human route responses** would suffice to determine the sign of an additional guidance policy's *group* travel-cost effect, and what original human experiments could measure advice actually displayed/read and the resulting group cost?

## Exact source custody and units

Original Wijayaratna, Dixit, Denant-Boemont & Waller (2017), *An experimental study of the Online Information Paradox*, PLOS ONE DOI **10.1371/journal.pone.0184191**. Its original open-access S2 spreadsheet is retained in the owner's Drive; previously verified original XLSX SHA-256 `f2047f7c2ae8999a9f0660f3b5c192aea171b715284bf2aa05b40c10b902d863`. This stage starts from the prior source-verified de-identified compact human choices [`data/rithm23_wijayaratna2017_routes.csv`](https://github.com/WhoSia/RITHM/blob/main/data/rithm23_wijayaratna2017_routes.csv), SHA-256 `5926158a1a83172b1a4e119eb369140299a43fbceb2b1ba0321710c0f6723484`, **24 group-treatment panels, 480 group-rounds, 6 historical sessions** (not 480 independent subjects). A native Ruby script reconstructs **only group-level counts**. Do not put the source full individual XLSX, a fake advice receipt, or person's identity in output archives.

The 24 panels carry original `group_stage_total_cost` summaries whose values differ from reconstructed *theoretical route-flow group cost* in **five panels**. These discrepancies are **preserved, logged and not silently overwritten**. Older audits already locate six individual group-round anomalous original raw Cost sums. Current optimization consistently uses the published *theoretical* network cost, not the individual's raw Cost or observed field times.

The original experimental treatment is information **offered at node C** to people entering A–C. It is not a time-stamped verified screen view or exogenous encouragement conditional on C entry. Experimental Info vs Blind differences cannot be rebranded as a new randomized policy evaluation. The separate 2025 Seoul source does not identify any of these same human subjects or their advice events.

## Source-fixed intervention object

For each actual original 2017 group-round, let `n1,n2,n3` be observed counts on A–B–D, A–C–B–D, A–C–D with total 12; let `z∈{0,1}` be actual incident on C–B; `q=n2+n3` is original A–C arrivals. Fix `n1`, `q`, `z` and the other group members' choices, then permit **an additional hypothetical downstream C-branch adjustment** of at most `k∈{0,1,2}` eligible original C entrants. All group-round extrema independently attainable as finite hypothetical assignments given their own original state, but minima/maxima across all rounds need not be attainable by ONE durable multi-round adaptive advice policy. No claim of actual uptake.

The published original network equation is exactly

`C(n1,n2,z) = 264 − 24 n1 − 9 n2 + 2 n1² + 2 n1 n2 + n2² + 19 z n2`.

Define `gain = C(original state) − C(state after hypothetical C-stage change)`, so positive gain is group cost reduction.

Enumerate `m∈[max(0,n2−k), min(q,n2+k)]∩Z` for unrestricted switches, with `n3'=q−m`. The sharp attainable finite set of gain values is `{C(n1,n2,z)−C(n1,m,z): m in feasible set}`. Include the no-change `m=n2` option. Three **explicitly assumed**, unverified behavior contracts:

1. **UNRESTRICTED** — a new advice may induce ≤k eligible C–B↔C–D switches in either direction, irrespective of incident.
2. **INCIDENT_AVOID_ONLY** — when `z=1`, ≤k *observed C–B entrants* can switch to C–D, and when `z=0`, nobody changes. No other drivers react. This is a strong directional **response exclusion**, NOT inferred from observed historical incident response.
3. **STATE_DIRECTION** — when `z=1` only C–B→C–D switches, and when `z=0` only C–D→C–B switches are permitted. This second normal-day encouragement is substantive and potentially harmful.

## Original human source conditional exact results

**N=480 source group-rounds; each line is a uniform mean across historically observed group-round states, not inference over 480 independent groups and not a policy-effect estimate.** Improvement means `baseline minus hypothetical policy total cost` in original source cost units.

| Contract | k | Both signs feasible in same original group-round | Any improvement feasible | Any harm feasible | Sharp mean lower gain | Sharp mean upper gain |
|---|---:|---:|---:|---:|---:|---:|
| UNRESTRICTED | 0 | 0 | 0 | 0 | 0 | 0 |
| UNRESTRICTED | 1 | 369 | 376 | 472 | −10.645833 | +6.845833 |
| UNRESTRICTED | 2 | 369 | 376 | 473 | −22.200000 | +11.366667 |
| INCIDENT_AVOID_ONLY | 1 | 0 | 46 | **0** | **0** | **+2.233333** |
| INCIDENT_AVOID_ONLY | 2 | 0 | 46 | **0** | **0** | **+3.720833** |
| STATE_DIRECTION | 1 | 0 | 47 | 371 | **−6.116667** | **+2.237500** |
| STATE_DIRECTION | 2 | 0 | 47 | 376 | −12.766667 | +3.725000 |

The strongest source-informed contrast is the **fragility of the sign to changing the behavior contract**. Incident avoidance alone cannot hurt in this *particular fixed-upstream, original quadratic network*, while instructing extra C–B use in normal states reintroduces harm. It would be misleading to announce that data confirmed “online guidance improves welfare”: the critical monotone direction and lack of outside reactions have been **assumed**. For INCIDENT_AVOID_ONLY k=1, conditional split: information-armed 240 historical group-rounds have mean possible gain `[0,+0.166667]` and blind-armed 240 have `[0,+4.300000]`; this is **remaining local C–B-switch headroom** in already realized historical routes, NOT the causal effect of adding new information or a treatment comparison.

### Simple proof (no novelty claim)

For one actual C–B driver to move from `n2` to `n2−1`, while keeping `n1,z,q` fixed,

`C(n1,n2,z)−C(n1,n2−1,z) = 2(n1+n2) + 19z − 10`.

At an incident (`z=1`) with `n2≥1`, this equals `2(n1+n2)+9>0`; repeated C–B→C–D reductions remain beneficial until `n2=0`. It follows that the lower bound of incident-avoid-only gain is exactly **0** and every actual switch strictly improves original-network group cost. The **strictly positive lower bound is not established** because no switch remains a permissible response. For normal-day C–D→C–B, cost increment equals `2(n1+n2)−8`, often positive on observed states. These facts are direct algebra, not a new general traffic theorem or evidence about real-world vehicle welfare.

## Explicit independent data acquisition gate (not fulfilled)

- **Noussair & Qiao (2025)**, *Congestion Information and Efficiency: An Experiment*, *Management Science* **72(7):6229–6250**, DOI **10.1287/mnsc.2023.00056**. Publisher explicitly advertises supplemental appendices/**data files**; author's [research page](https://sites.google.com/view/liangqiao/research) links its online appendix. The independent 6-player experiment and published short-harm/long-benefit research are highly relevant to RITHM hysteresis and collective welfare. **But neither the verified person-by-round raw data bytes nor a per-person actual view/receipt field could be extracted in this round.** This is a **candidate + original article / appendix location, not an ingested, tested dataset**; previously studied in RITHM P7/P8. Crucial topology: signals are historical congestion information around group choice periods; **not** a C-stage incident signal while en-route. Any eventual test must be labeled cross-topology with a different information cut. No invented author dataset, sample-level fitted scores, or assumed view measurements.
- **Ashraf, Brown, Burris & Vitaku (2023)**, [ICPSR replication package](https://www.openicpsr.org/openicpsr/project/185222/version/V2/view), lists original `study1.csv` and `study2.csv`; **already used** in prior RITHM 2.0–2.3 and not an untouched new external witness. Different action/cost network; do not relabel as an independent C-stage validation.
- **Original Wijayaratna S2**, directly verified and studied repeatedly: route timestamp/choice ≠ rendered screen/actual attention. Do not claim a new external dataset from the same 6 sessions.

The missing research evidence remains a dataset with audited `experiment/group/session/person/period`, offer assignment and actual signal version, trusted **render** event before eligible decision time, preferably independent comprehension/attention instrument, original C-entry and post-exposure choice, independent realized group cost and verified randomization/carryover design.

## Identification hierarchy and possible independent experiment

- **Offer-policy ITT:** With group/session-level randomized offer and independently measured group welfare, group-cluster contrasts can identify an *offer assignment* effect under correct randomization, no across-group interference, stable outcome coding and accounted inter-period carryover. This does **not** require proving every individual's attention and does not identify “reading” mediation.
- **Delivered/rendered policy effect:** Requires independent event logs tied to a causal signal version, route-eligible time and consented subject. Even a render event does not certify cognitive reading or trust. Never define click after choosing as prior exposure.
- **Readership/compliance mechanism:** Requires richer attention/comprehension measures or a justified randomization-based IV design with exclusion/monotonicity/interference assumptions; a large C–B incident response association alone cannot tell the reader share.
- **Experienced welfare:** total observed costs for each randomized group and horizon, measured outside the advice predictor, plus individual switching and trust-history observables, needed for repeated hysteresis versus transient shock differentiation.

## Development-language switch — actual implementation, not cosmetic labeling

**Preferred authoring order and ownership:** **Ruby** controls source custody, extraction and run verification; **Rust** is the minimal zero-dependency exact integer cost-bound engine; **Go** is an operational source/time-integrity and comparable bound evaluator; **C++17** is a separately implemented low-level enumerator that must agree with Go; **R** is the statistics/group-level source audit. Existing **Python** remains legacy replay/read-only compatibility, not the lead technology or authority for new claims.

Actual this-stage execution in current tool container: **Ruby 3.3, Go 1.23 and C++17 compiled/executed PASS**, both source counts and 9 budget×policy bound rows agree. **Rust and R files authored but unexecuted** because neither `rustc`/`cargo` nor `Rscript` is installed in the analysis runtime. No simulated or claimed Rust/R compilation or R regression. The server environment owned by a friend is NOT modified to install compilers; executing future Rust/R on a permissioned user-owned machine requires independent setup and rerun. No CI claimed. Local Go exhaustive cost guarantee unit tests PASS for all 12-person allocations and source arrays, Ruby cross-language gates PASS, and C++ source compiled with warnings-as-errors.

## Scientific status / successor question

**SOURCE-DERIVED EXACT FINITE POLICY-RESPONSE SETS PASS; CROSS-LANGUAGE GO↔C++ INDEPENDENT CONSISTENCY PASS; ORIGINAL PANEL COST DISCREPANCIES PRESERVED; INDEPENDENT NEW HUMAN BY-PERSON DATA NOT ACQUIRED; ACTUAL INDIVIDUAL ADVICE VIEW/COMPLIANCE AND CAUSAL GROUP WELFARE HOLD; RITHM-2.7 OPEN.**

Next inside 2.7: (1) acquire original Noussair–Qiao participant data **if permissibly accessible**, checking native units and an exposure field rather than assuming they exist; or (2) move from purely directional switch assumptions to **defensible, externally measured compliance restrictions** with independent randomized group outcomes, pre-register an interference-aware long-run signed welfare estimand, and freeze P6/P25 rivals before seeing an external outcome.
