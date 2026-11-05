# RITHM-2.10 P3-R18P4–P7 — Historical Evidence and Direction Audit
2026-11-05 KST. Exploratory, not an independent causal or publication finding.

## R18P4–P5: methods
- [40-period source-free trace auditor](p3/r18_round_chain_audit.rb): pre-allocation baseline, true previous/current report timestamps, six unique decisions each period, chronological state transitions and cumulative congestion cost. [Tests](p3/test_r18_round_chain_audit.rb): 4 runs/22 assertions locally.
- [Design feasibility](p3/r18_design_feasibility.rb): with historical session SD=29.589 and nominal normal approximation, target cost difference20 requires ~35 independent sessions per condition for a 2-condition feedback effect versus ~69 per condition for a DIFFERENT 4-condition interaction. These are not interchangeable estimands. [Tests](p3/test_r18_design_feasibility.rb): 3/12.
- [SHA-256 plan-draft manifest](p3/r18_preanalysis_manifest.rb): fixes 40 periods, a session-level analysis, preallocation observations, and the primary outcome. Not an externally registered trial. [Tests](p3/test_r18_preanalysis_manifest.rb): 4/10.

## R18P6–P7: actual source data
Original author-approved CSV SHA256 `d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb` verified. From 24 Full-information sessions, all 1,872 six-person groups checked; 1,824 complete consecutive-period group pairs t=2..39 preserve NumAnext(t−1)=NumA(t).

| Epoch | Pairs | Same prior/current occupancy | Different | Different share |
|---|---:|---:|---:|---:|
| Early | 432 | 133 | 299 | 69.21% |
| Middle | 912 | 320 | 592 | 64.91% |
| Late | 480 | 217 | 263 | 54.79% |
| All | 1824 | 670 | 1154 | 63.27% |

Late−early difference **−14.42 percentage points**, exploratory 24-whole-session 20,000-fold Ruby resampling 95% ~[−23.61,−5.58] pp. These are naturally evolving historical occupancies, not randomized feedback effects. Code: [coverage](p3/r18_observable_age_support.rb) and [cluster comparison](p3/r18_age_support_bootstrap.rb), each with source-free tests. No personal source rows published.

## MCP-Hub validation
The real [MCP-Hub Gateway source](https://github.com/WhoSia/MCP-Hub/blob/platform/standalone-hub/gateway/public-dev-tools.mjs) was fetched and its original public offline JavaScript helpers executed locally against synthetic patch and JSON fixtures, both status ok, no private text output. Render Gateway logs were read through connected tooling. Live authenticated Gateway MCP calls and Ponytail invocation remain **unavailable in this chat**. A patch-statistics tool is not a proof verifier.

## Critical historical and literature boundaries
[Drive Chat Archive 23.md](https://drive.google.com/file/d/1vJC9ZvUowaJmd4iJci1ycfYPU4sx-PlG/view), specifically the user's 2026-10-30 instruction, expressly **excludes recruiting new human participants**. Therefore prospective information-clock trials remain theoretical appendices, not the executable RITHM program. The founding objective is constrained information, memory, attention and friction → individual persistence and collective history/welfare, not laboratory administration.

Prior art: Noussair & Qiao (2025), DOI 10.1287/mnsc.2023.00056 already reported early/late congestion-information effects; Qi et al. 2023/2024 analyzed route inertia and probabilistic dynamics; Yang et al. (2026), DOI 10.3390/math14162910 compared learning models with EWA, Q-learning and mixed logit.

**Priority next:** recover original SSM q1..9, EWA/ablation and calibrated actor-history models from archived RITHM-2.9; compete on common 24-session source and exact information sets, then prove a genuinely distinct finite-memory/welfare identification result or report a bounded negative finding. The same source has already been inspected repeatedly, so heldout score improvements are exploratory. Independent theorem, external validation and causal mechanism identification remain HOLD.

[Complete 11,459-byte Korean evidence and paper-candidate audit on Google Drive](https://drive.google.com/file/d/1HjZKBKZ4FUcgMt2LH4uklYmur0B9vRp3/view); authenticated re-download SHA256 `a242a5d7be55b05f6945c449a1e60444bf7a776e403016eb04a4a9cedcc6a9ef`.
