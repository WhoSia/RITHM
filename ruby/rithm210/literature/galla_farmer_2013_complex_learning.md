# P3-R9 Literature Note E — Galla & Farmer (2013) on Complicated Learning Games

**Verified original:** [Complex Dynamics in Learning Complicated Games, PNAS, DOI 10.1073/pnas.1109672110](https://drive.google.com/file/d/1BFTJ_yM2FOLuO_JsUGMZzralLRHId9F8/view). Original PDF and its substantial supplementary methods were reviewed through text.

## Main mathematical/scientific mechanisms
Two learning agents each have a **large set of alternative moves** (the paper's phase-diagram simulation has 50 moves/actor, with roughly 98 effective strategy-probability dimensions). Players use an experience-weighted attraction update, with memory-loss parameter alpha and a payoff-correlation structure Gamma. Numerical regimes include a unique stable fixed point, a large number of fixed points, and limit cycles or chaotic attractors. Stochastic and deterministic EWA variants are distinguished. The paper reports payoff intermittency in the chaotic regime.

## Limits
One cannot transplant the phase diagram or chaotic-attractor claim directly into a 6-person 2-route congestion game. The number of interacting agents, actions, game ensemble, payoff correlations and effective state dimension differ. Alpha=0 does not automatically mean zero uncertainty about others or a fixed laboratory signal structure. RITHM may use phase-transition methods but must prove its OWN transition matrix/bifurcation condition, not reuse Galla–Farmer's empirical phase boundaries.

## RITHM differential test
Measure a micro update's **conditional exit hazard from the n=4 Nash allocation**, the pairwise up/down turnover covariance and social congestion cost under changing information, learning and adjustment clocks. Prove or numerically refute co-movement of these quantities with attractor stability. The four observed moments are evidence; the phase diagram by itself would be prior-art recapitulation.
