# RITHM-2.6 P17 — Phase-Robust Mesoscopic Externalities & Commodity-CPU Control Candidates

**2026-10-12 · source-conditioned real six-day envelope; separate SYNTHETIC static traffic game. RITHM-2.6 OPEN.**

## 1. Research question and scientific authority

P15–P16 established correlated 5-min source phase patterns and unresolved origin: under exact 10-min conservation, replacing two bins by (y0+δ,y1−δ) retains their 10-min sum. **No independent sensor has certified the true latent 5-min vehicle counts.** This paper asks what macro *proxy* conclusions survive that observational nullspace, and how to compute a separate micro-to-macro model efficiently on ordinary CPUs.

The original [Seoul city 2025 source](https://data.seoul.go.kr/dataList/OA-22351/F/1/datasetView.do) consists of original user's 38 sharded CSVs. We REHASHED AND RE-READ EXACTLY FOUR original H1 parts **005,009,011,012** (2,027,915 source records); never claim original deleted CP949 full-file SHA revalidation. Dates **20250212, 20250323, 20250416, 20250418, 20250419, 20250421** were selected and used during P15/P16, hence NOT new independent holdouts. The four accepted part SHA256 digests are embedded in executable source. Source-identical route/link + adjacent 10-min pairs only, no missing q imputation.

## 2. P17-A — Sharp *conditional* source phase proxy interval

For each eligible pair j, nonnegative source count y0,y1 and fixed positive source speed s0,s1, set T=y0+y1. Condition on conserved total and integer latent q0∈[0,T], q1=T−q0, optional per-pair bound b and global budget Σ|q0−y0|≤B. The algebraic proxy **P(q)=Σ(q0/s0+q1/s1)** is in vehicle-hours PER KM (link length omitted), **not actual group travel time**. Since each unit of transfer has constant slope 1/s0−1/s1, sorting per-pair absolute slopes and consuming the integer budget greedily attains the EXACT min and max of this uncoupled budget-polytope objective, O(P logP) time. The two extrema generally use different allocations. No spatial junction conservation constraint or speed-flow feedback is enforced: this is a conditional relaxation, not physical traffic feasibility or a confidence region.

To make an auditable scenario, choose B as P16's **hypothetical near-flat latent model** minimum transfer budget: Σ floor(|y1−y0|/2), not empirically measured miscounts. Reconstructed source:

| Original day | Valid paired source observations | Hypothetical B (section-passages reassigned) | Conditional min P change | Conditional max P change | 10min source spatial CV² mean |
|---|---:|---:|---:|---:|---:|
| 2025-02-12 | 25,632 | 215,731 | −1.15% | +1.21% | 0.1675 |
| 2025-03-23 | 25,596 | 789,180 | −2.69% | +2.87% | 0.1961 |
| 2025-04-16 | 25,209 | 973,384 | −3.29% | +3.58% | 0.1871 |
| **2025-04-18** | **25,384** | **1,169,133** | **−3.64%** | **+3.91%** | **0.1800** |
| 2025-04-19 | 25,624 | 1,101,039 | −2.90% | +3.16% | 0.1805 |
| 2025-04-21 | 25,632 | 229,771 | −1.28% | +1.35% | 0.1653 |

Example Apr18 fixed-source-speed P_y=238,755.263 vehicle-h/km summed over section/time events, conditional min=230,073.841 and max=248,083.496. Reassigning *every pair* to its closest integer-balanced flow (more specific alternative) changes P by only **+0.159%**, not either sharp extremum. These are scenario sensitivity numbers, not error bars or actual measured societal cost. Same-publisher speed may itself be alias-contaminated or change if traffic flow changes.

Phase-invariant spatial feature: T_e,k=y_e,2k+y_e,2k+1 and source \`CV²_k = (Σ_e(T_e,k−mean T_k)²/n_k)/(mean T_k)²\`. Any within-pair (δ,−δ) leaves each T_e,k unchanged, so the feature is exactly INVARIANT to this P16 nullspace. P17 computes average CV² over 144 10min clock bins. Counts may still be biased at 10min, link capacity heterogeneous; this is NOT a true calibrated MFD or welfare feature.

## 3. P17-B — Micro inefficiencies, mesoscopic dispersion and efficient exact local effects

Under STATIC **identical homogeneous affine link latency** τ(q)=a+bq, q∈nonnegative integers, Q=Σq and n links:

**Σ_e q_e τ(q_e) = aQ + bQ²/n + b Σ_e(q_e−Q/n)²**.

Fixed total flow Q does NOT determine modeled cost: dispersion pays the exact surcharge b*n*Var(q). For a=10,b=2, sources (20,20) and (0,40) share Q=40 but latter incurs an extra **1600** units. This classical variance identity is not an empirical assertion about Seoul link detector passages, which need not measure instantaneous occupancy and have varying capacities and lengths.

Independent classical **Braess paradox** static 40-driver integer source model: s→u and v→t cost q; s→v and u→t cost 45; u→v shortcut cost 0. All-shortcut 40-route state has private path cost 80 and group 3200; one unilateral reroute to upper causes that driver's cost to worsen 80→85 even as total drops by 34 due to congestion relief of the remaining drivers. Without shortcut, 20 upper/20 lower yields group cost 2600. Exhaustive enumeration 861 integer assignments with shortcut finds minimal group cost **2588** (e.g. upper17/lower17/shortcut6). A greedy individual rerouter accepting only strict SOCIAL cost improvements attains 2588 after 34 accepted moves on this toy. **No general convergence-to-global-optimum claim on arbitrary graphs**.

For static separable link group cost g_e(q)=q τ_e(q), an atomic R→R' switch exact social delta only touches symmetric-difference edges: Σ_e in R'\\R [g_e(q+1)-g_e(q)] + Σ_e in R\\R' [g_e(q−1)-g_e(q)]. Complexity O(number changed edges) versus O(E) full graph rescan; exact local updates are inappropriate for delayed spillback or physical wave propagation without additional model evidence.

## 4. Ordinary CPU reproducibility

Deterministic synthetic benchmark (seed 20261012; **not real traffic forecast**): 10,000 static edges, 700 candidate switches. Three repeats median exact local-update time **0.00536s**, full-graph recomputation median **1.542s**, median run-wise speed ratio **303.8×**; each computed total change matched within float tolerance. For 25,000 synthetic paired readings, sharp budget envelopes median **0.0788s** on current CPU. Machine-specific timings, Python scheduling and cache effects prohibit universal speed claims. No GPU, high-end traffic simulation, human interventions or SUMO required.

Pure test contracts 9/9 local PASS: 140 random exhaustive integer budget small cases, 200 exact static route recomputations, 21 demand sizes for Braess greedy vs exhaustive, source input guards, and variance identity. Source script rehashed and read six prior known source days. The GitHub changes are [skip ci], so not Actions-confirmed.

## 5. Material 2025–2026 literature and novelty limits

- [2026 explicit two-region MFD perimeter MPC](https://doi.org/10.1080/21680566.2026.2631628): offline policy lookup reduces online cost — prior art, not our novelty.
- [2025 MFD optimal control computational-efficiency study](https://dergipark.org.tr/en/pub/estubtda/article/1656397): collision with generic 'efficient traffic control' claims.
- [2025 stochastic fundamental diagram micro-macroscopic model](https://doi.org/10.1016/j.commtr.2025.100163): uncertainty in aggregate flow, cannot assume one deterministic global law.
- [2025 efficient detour-aware local routing](https://doi.org/10.1103/gdpb-5j92): localized feedback already studied.
- [2026 percolation/hysteresis](https://doi.org/10.1016/j.trb.2026.103545) and [2023 non-unimodal urban MFD from hierarchical streets](https://doi.org/10.1016/j.trb.2023.05.002): spatially heterogeneous macro behavior is not captured by universal identical-edge toy.
- [2025 urban MFD MPC scalable routing](https://doi.org/10.1016/j.trip.2025.101816): further prior art for practical regional guidance.

P17's contribution is a **typed, falsifiable bridge** between P15's source-specific operator nonidentification, exact integer phase-proxy envelopes, source-phase-INVARIANT coarse features and a computationally verified STATIC micro-to-macro externality baseline. Braess, Jensen, marginal cost routing, sorting-based budget allocation, and MFD are established ideas; don't present any as a newly discovered theorem.

## 6. Open falsification and next phase

Priority P18: (i) coarsen source to 10min invariant flow and test *future* speed surprises in a prespecified true source-heldout period, (ii) reject invalid detector-link-to-network adjacency inference without original topology/capacity keys, (iii) add independently calibrated confidence bounds for source mean speed/count and junction conservation; if absent, robust *actuation* certificate refuses guidance. A CPU-friendly 2–3-region MFD with source-conditional hysteresis and uncertainty may be tested against persistence and same-time baselines, BUT must first establish actual link geometries and density/occupancy semantics. No current real intervention, no instrument license, no true group-human welfare measurement.

**P17 VERDICT:** FOUR ORIGINAL SOURCE SHA PASS / SIX HISTORICAL DAYS RECALCULATED / INTEGER SHARP BUDGET CONTRACT PASS / PHASE-INVARIANT COARSE MOMENT PASS / SYNTHETIC BRAESS AND EXACT VARIANCE PASS / COMMODITY-CPU LOCALITY DEMO PASS / HUMAN WELFARE AND SOURCE SENSOR-ERROR MECHANISM HOLD / RITHM-2.6 OPEN.
