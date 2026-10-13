# RITHM-2.7 P24 — Source-Observed Human Route-Marginal Audit

**2026-10-13 · empirical descriptive supplement to synthetic P24.** This uses REAL 2017 participant route assignments from the already source-checked [Wijayaratna S2 compact representation](../data/rithm23_wijayaratna2017_routes.csv), not the Seoul 2025 sensor and NOT a real receipt/advice event.

Decode 24 group-treatment panels, each containing 20 group rounds of 12 real human route decisions. Reconstruct the hypothetical upstream A-C detector `q=n2+n3` from choices and the original 2017 network's group COST FORMULA. `q` is **virtual**: there was no separately logged physical upstream detector in this analysis. Incident `z` is observed retrospectively, not assumed known to no-information participants.

**Result:** 6 independent sessions, 24 group-treatment panels, 480 group-rounds. At `q=8,z=0`, 101 recorded group-rounds yield route-count-defined group costs from **200 to 256**, depending on the unobserved downstream split. Even within fixed session, group, treatment stage, virtual q and incident, **82 distinct matched strata** contain different realized theoretical costs. The 82 are NOT independent treatment trials.

Example: session `150923_0937`, group 1, no-information stage 2: at period 2, `(n1,n2,n3)=(4,3,5)`, `C=206`; at period 12, `(4,1,7)`, `C=200`. Both have q=8, z=0. These are **different periods**, not counterfactual effects.

Source-integrity warning: the earlier RITHM human-source audit documented six individual recorded-cost inconsistencies (five panel total residuals). This check deliberately computes the original paper's **route-count theoretical cost**, not a silently repaired sum of individual recorded costs.

[Source-derived executable](../tools/traffic_sources/p24_human_source_gate.py) · [GitHub smoke regression](../tests/test_p24_human_source_gate.py). A separate offline source audit replayed four contract checks locally (4/4 PASS); the committed smoke test and GitHub Actions are not claimed to have run here. No interventional causal welfare claim follows. P24 synthetic response sign bound and real-source partial-observation ambiguity remain separate evidence classes.

**Gate:** authenticated receipt + delivered guidance + individually eligible route choices + independently measured group costs + exogenous intervention. RITHM-2.6 OPEN; 2.7 METHODS P1; causal human welfare HOLD.
