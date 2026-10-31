# Gross switching versus net changes in existing participant histories
An independent replay of `one_step_predictions.csv` grouped by (trt,session,section,Group,ID), lagged within each 40-period block, yields exactly 5,616 transitions of six people. Source identity checks: S=U+D, ΔN=U−D, S−|ΔN| always even.
- Average gross switches **1.5863603989** per 6-person period.
- Average absolute net A-count change **0.9944800570**.
- Average cancelled switches **0.5918803419** (so cancelled directional *pairs* average 0.2959401709).
- **1,546 / 5,616 = 27.52849%** group-periods show at least one opposing switch pair.
- S−|ΔN| frequency for 0,2,4,6: [4,070,1,431,114,1].
- By treatment (1,2,3), mean gross [1.661325,1.683226,1.414530], mean net [0.998932,1.034722,0.949786], cancelled switches [0.662393,0.648504,0.464744].
No causal attribution of churn to cognitive learning or information is possible merely from group averages; treat these as observational statistics.
