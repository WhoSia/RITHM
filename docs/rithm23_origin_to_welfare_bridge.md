# RITHM-2.3 — Founding-to-Welfare Reconstruction, Exact Traffic-Cost Bridge & Prospective Identification Boundary

**Status:** RITHM-2.3 OPEN; exploratory structural/accounting analysis; no 2.4 stage opening, manuscript freeze, new GitHub Actions workflow, or PR/bot. 2026-10-10 (Asia/Seoul).

## 1. Recover the *correct* founding program, not a retrospective legend

Historical witness hierarchy: exported initial chat `04_RITHM/1.json` (archaeology receipt SHA256 `bb96ce9e7b4c28be837b998a74aebac84e023de4c85f4ef06d740b8b811390ec`), 2026-07-28 RITHM formal specification and research charter, the original 16-file session archive `RITHM_20261004.zip` (2026-07-28→2026-09-11), Notion's `Origin & Drift Audit`, `Recovered Theory Ancestors` and RITHM-2.0, 2.1, 2.2, 2.3 canonical pages. **Authority warning:** old charter is an early corrective repair, not an initial constraint uttered in the earliest conversation. Archived historical work is not automatically current scientific authority.

Initial RITHM name proposed 2026-07-28 11:42:11 KST, and user adopted RITHM-0 at 11:47:19 KST. Founding question: delayed/noisy guidance, route-choice switching friction, memory, feedback and trust may generate *human–network hysteresis*, even when aggregate route costs are known. Do not confuse traffic-network simulator timeouts with human adaptation timescales.

Six recovered, **different** ancestor statuses:

1. **Choice-only observational equivalence (R0.1): constitutional survivor.** Routing actions without extra information cannot generally identify delayed belief vs habit vs switching friction vs trust.
2. **Four adaptation timescales** (physical flow F, behavior B, algorithm A, institutions I): `UNREFUTED_ABSTRACTION`. Modern 2.3 examines only a small F–B interface; it has not measured algorithmic or infrastructure rates.
3. **RITHM-CEM: intended versus executed choices**: credible unrefuted proposal; not empirically implemented or validated in 2.3. Distinguishing advice, intention and actual execution is a plausible future measurement design.
4. **Metastability, quasipotentials and rare route-regime escapes:** historically developed formal possibilities, *not* currently measured by six 20-round human stages. Do not decorate current results with unmeasured barriers.
5. **Directional congruence universal scalar** and **S02.6 phase/hybrid prospective prediction:** negative ancestor claims remain failed or held; local descriptive geometries are not universal laws.
6. **Administrative HANK and traffic simulation branches** are legitimate RITHM expansion, yet must never silently displace its original human route-choice explanandum.

### Version spine
- **2.0:** 2023 Ashraf experiment, 1,000 group rounds, exact payoff identity `W(s)=-36+66s-5s²`; observed expected welfare 160.126 vs best 181. The full cost of suboptimal occupancy includes both mean allocation and variation, but does not identify habit or causal policy value.
- **2.1:** actual information timing and 18-person group treatment assignments; `more route switching ⇒ more welfare` is false, as 118/990 adjacent rounds cancel directionally, and timing/assignment confound welfare comparisons.
- **2.2:** person-history predictive gains fail to transfer reliably to independently combined group distribution/welfare; a second human 3-route experiment establishes masked gross turnover and falsifies naïve universal positive imitation after conditioning on current common shock. Classical coupling bounds formalize the marginal-to-joint welfare gap.
- **2.3:** first and second decision fork information sets, independent-group same-session negative controls, actually experienced own cost, and shared accident histories separate strong *structural* mechanisms, but causal belief/habit/trust identification is still HOLD.

## 2. New exact 2017 network audit — publication reconciliation

Original 2017 CC BY 4.0 published experiment: Wijayaratna et al., PLOS ONE 12:e0184191, DOI `10.1371/journal.pone.0184191`, original 1.2 MB participant-level S2 XLSX `10.1371/journal.pone.0184191.s002`.

Each group consists of 12 people. Define route occupancies `n1` (A–B–D), `n2` (A–C–B–D), `n3` (A–C–D) and accident `z∈{0,1}`. Original network is consistent with integer route costs:

```
c1 = 10 + n1 + n2
c2 = 13 + n2 + 19*z
c3 = 22 - n1
n1 + n2 + n3 = 12
C  = 264 - 24*n1 - 9*n2 + 2*n1**2 + 2*n1*n2 + n2**2 + 19*z*n2
```

The executed code checks every one of 91 nonnegative integer configurations `n1+n2+n3=12` in both shock states. The original 5,760 recorded costs versus the network formula: 5,713/5,760 exact, 47 mismatches confined to six entire group-round records. Source rows remain **unchanged**. These six records include 3 cells previously flagged because participants on the same recorded route were charged inconsistent costs; the other inconsistent *network* records would not have been caught by simply comparing people on the same road. In all 24 group-treatment stages, original S2 realized cost total is unchanged and independently source-audited.

| Group-round mean total cost | PLOS ONE Table 5 | Reconstructed from routes/network (this work) | Individual S2 `Cost` sum |
| --- | ---: | ---: | ---: |
| NoInfo | 210.629 | **210.62916667** | 210.86250000 |
| Info | 219.163 | **219.16250000** | 219.12500000 |
| Difference | +8.534 | **+8.53333333** | +8.26250000 |

Published values are rounded to three decimals (half-up at the exact 219.1625 tie). Thus the paper's aggregate TSTC values are **quantitatively reconstructed at published precision from the participant paths and network costs**. The inconsistent individual `Cost` field accounts for the previous 2.2 publication-vs-S2 discrepancy. The underlying data-generation or transcription cause is **not established**.

## 3. Exact micro-to-network welfare identity

Substitute `n3=12−n1−n2`. For random route occupancy and accident, linear expectation + variance accounting gives the **exact** identity

```
E[C] = C(E[n1], E[n2], E[z]) + Var(n1) + Var(n3) + 19*Cov(z, n2).
```

Proof: the quadratic part `2 n1²+2 n1*n2+n2² = n1²+(n1+n2)²`, and `n1+n2=12-n3`. The stochastic penalty is therefore `Var(n1)+Var(n3)≥0`, and the shock response appears in `E[z*n2]=E[z]E[n2]+Cov(z,n2)`. This is an exact **accounting identity**, not a new theorem, a causal decomposition, a claim of peer imitation, or a universal model of all traffic networks.

Observed sample decomposition, Info minus NoInfo, each 240 group rounds:

| Exact descriptive component | Info−NoInfo (travel-cost units/group-round) |
| --- | ---: |
| Network cost evaluated at treatment-level mean occupancies and 20% accident chance | **+20.39112847** |
| Additional congestion volatility `Var(n1)+Var(n3)` | **+3.89637153** |
| Shock-responsive route-2 joint allocation `19 Cov(z,n2)` | **−15.75416667** |
| **Total cost contrast** | **+8.53333333** |

All six lab sessions display mean-occupancy term positive, congestion variance term positive, incident–risk route covariance term negative, and net Info−NoInfo structural cost positive. These were tested **after inspecting these same six sessions repeatedly**; six-session t5 intervals and sign consistency are exploratory descriptions, not pristine confirmatory tests. Treating all 480 rounds as statistically independent would be pseudoreplication. The experiment also changes decision staging between treatments, so do not label either individual component as an identified causal mediation effect.

The source field `Cost` gives +8.2625 rather than +8.5333 because it disagrees with the model in six rounds. Both remain archived and visible; published network-reconstruction is preferred *for replication of Table 5*, source field is preferred *for questions about the literal participant record.*

### A completely exact fixed-marginal example

Let twelve individuals each choose A–B–D with marginal probability 1/2, else A–C–D, with no accidents and no A–C–B–D. All cases have **identical individual choice marginals**, `E[n1]=6`; only their joint coupling differs:

| Compatible joint choice law | Var(n1) | Expected total travel cost |
| --- | ---: | ---: |
| Six people on each route, exactly | 0 | **192** |
| Twelve independent equal-probability choices | 3 | **198** |
| All twelve act in the same direction | 36 | **264** |

Same individual choice probabilities, **72 units** spread in expected group cost. This is a basic coupling example and illustrates exactly why 2.2 personal prediction gains cannot guarantee group welfare gains.

## 4. Why this does not yet show real traffic hysteresis

The paper uses 20-round treatment stages, and these group occupancy variances are cross-round quantities. They do **not** estimate attraction basins, escape times, long-horizon infrastructure lock-in, algorithm trust decay or route-execution mismatch. The original RITHM founding hypothesis concerns delayed adjustment and path dependence over time, not just a convex static cost penalty. Next work needs **joint dynamic** and **prospective intervention** evidence.

A decisive observational-equivalence warning: where all prior link-state and route-occupancy information is disclosed, personally experienced route cost may be determined by the same state information. It need not identify a separate *private reward-learning* channel. The previous 2.3 +19 accident cost shock does not establish a next-day switching effect, and the matched independent groups' same-session residual co-alignment remains an explanation about session-common factors, **not proven interpersonal imitation**.

## 5. Future discriminators, without spending GitHub Actions or opening 2.4

Use the current six sessions for **mechanism design**, not for creating new confirmatory p-values. Before new data arrive, fix and publish as a *draft* protocol, but defer any nontrivial outcome choices until the external unit/capacity and instructions are known:

1. **R0.1: private-payoff vs public-network-history equivalence.** In a new human experiment, independently vary the *information channel* for realized private cost/feedback and the shared network status; hold objective payoffs/network as comparable as ethically practicable. Falsifier: if the private-feedback manipulation has no incremental influence after shared history and enough power, a separately identifiable private reward-memory mechanism fails in that population.
2. **Choice–execution mismatch (CEM).** Record advice, stated intended route, executed route and actual experienced cost separately. If independently varied execution friction changes realized routes while intentions and information are fixed, choice-only inferences fail. This ancestor returns only as a prospective design, not as confirmed historical physics.
3. **Information timing and reliability.** Capture exactly when advice, congestion state and cost are delivered at each decision point. Do not let stage-two information leak into stage-one choice forecasts. A trust hypothesis requires actual variation/measurement of algorithm reliability rather than a renamed residual.
4. **Collective payoff / conditional dependence.** Require whole interacting-group and laboratory-session held-out scoring, positive gain over independent aggregation for **cost distribution**, and an independently interpretable change in traffic-cost outcome, not a new correlation p-value. In explicitly new independent samples, split exploration and final evaluation.
5. **Hysteresis / dynamics.** Declare distinct physical versus behavioral adaptation times, perturb guidance and withdraw it, and define persistence/recovery statistics in advance. Holding cost distribution fixed while varying information and feedback timing is especially valuable.

Primary output should be **one genuine discriminator**, not five new CI bots. Local deterministic unit tests suffice for the present algebra. Reconsider a **single GitHub Actions run** only for an unusually consequential admission step after a stable exact-head implementation. `Reason expensive, execute cheap` and human science over CI instrumentation.

## 6. RITHM-2.4 formal-name **proposal only**

**RITHM-2.4 — From Route Memory to Collective Traffic Hysteresis: Information Timing, Congestion–Shock Welfare Decomposition & Prospective Adaptive-Guidance Identification**

Stage classification: sustained scientific **Study**, no `Court` suffix (per Research OS naming contract); the actual object is unifying the 2.0–2.3 structural–behavioral evidence with a prospective falsifiable adaptation experiment. The name restores the founding route-choice/hysteresis question rather than claiming the missing psychological identification is solved. **RITHM-2.3 remains OPEN and RITHM-2.4 is NOT created.**

### Sources and canonical references

- [2017 original paper](https://doi.org/10.1371/journal.pone.0184191), [S2 participant workbook](https://doi.org/10.1371/journal.pone.0184191.s002).
- [RITHM-2.0 Notion](https://app.notion.com/p/3f4ef561cf9281da9fa5ef9084913994), [RITHM-2.1](https://app.notion.com/p/3f4ef561cf9281649dabd71b820b8f85), [RITHM-2.2](https://app.notion.com/p/3f4ef561cf928182b4ffce55b024f0b0), [RITHM-2.3](https://app.notion.com/p/3f4ef561cf92815da1a6d46bf60377d4).
- [Origin and Drift Audit](https://app.notion.com/p/3c8ef561cf92817fb611e2ca1b0d8844), [Original 16-file archive receipt](https://app.notion.com/p/3efef561cf92812ebe5dc874e4fa29b6), [Theory ancestor registry](https://app.notion.com/p/3efef561cf92818495edef81873205f6).

### Reproduction

```bash
python rithm23_welfare_bridge.py
python -m unittest discover -s tests -p 'test_*.py' -v
```

Original 2023 Ashraf CSV is **never** automatically included in GitHub; its optional live-data test skips on public clone. The core network/reconciliation tests do not skip and do not require GitHub Actions.