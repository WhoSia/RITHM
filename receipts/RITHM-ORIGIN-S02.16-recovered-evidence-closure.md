# S02.16 — Recovered-evidence closure (2026-10-09)

## Terminal judgment

- Stage: `CLOSED — CONDITIONAL_POSITIVE_EVIDENCE / NATIVE_ADMISSION_HOLD`.
- Four frozen TNEG simulation data sets passed independent source/frame integrity; three have original runner receipts. P000 was reconstructed from complete original TripInfo XML after an observed kernel child exit status 0, but its original supervisor did not write an exit code or status receipt.
- The presealed four-native-receipt gate is **not met**. Do not promote the conditional result to an unqualified `PASS-TELEPORT-ROBUST`.
- A separate, fully source-reconciled recovered-evidence court recorded `PASS-TNEG-CURVATURE` **conditional on explicit p000 recovery provenance**; `native_four_receipt_gate=false`.

## Frozen metric and result

Eligible frame: 45,822 source IDs, SHA-256 `e62c94e400e4e868c8ec2d3f734801c56dd0ba03fa2c050f32e223e876c43293`; source commit `360682800b120fe0e439afa598eaa04ea0c9f42a`, SUMO `time-to-teleport=-1`, seed 42, horizon 50400 s. Burden is `(arrival-or-horizon) - activation_time`, with horizon imputation for absent or invalid arrivals. Each `B(p)` is averaged over exactly 45,822 IDs.

| p | B_T120 | B_TNEG | R_TNEG | XML materialized | XML absent |
| --- | ---: | ---: | ---: | ---: | ---: |
| 000 | 6744.900342630178 | 13177.165231766401 | 0 | 39068 | 6754 |
| 030 | 6552.030105626119 | 10853.947574309284 | -0.17630633118696115 | 43649 | 2173 |
| 070 | 6531.009995198813 | 10285.45485247261 | -0.2194485937174635 | 44199 | 1623 |
| 100 | 6528.603536510846 | 9582.613384400507 | -0.27278642895821403 | 44533 | 1289 |

`C=[R(1)-R(.70)]-[R(.30)-R(0)]` is a prespecified nonlocal endpoint-increment contrast, not a general curvature theorem. `C_TNEG=0.12296849594621062`, `C_T120=0.028238190134892482`, `delta_C=+0.09473030581131814`, `epsilon=0.005` (no retuning). Under the explicitly conditional recovered-evidence convention, the contrast is positive and above epsilon.

## Evidentiary boundaries

P000 original XML SHA-256 `0f5b52d154d51e0269e3bb08670da5b71077703c6fefcb3cf9a515f9602af65c`, reconstructed TSV SHA-256 `86f2d4c58b2a7d91164f382f0abd35699428065daf6a0ed37bc2c233266459b0`. P000 has 21,768 XML-present arrivals that are invalid/unfinished and, together with 6,754 XML-absent source IDs, 28,522 of 45,822 outcomes (62.245%) imputed to horizon. XML materialization is not completion at destination.

Independent four-cell ID/numeric audit passed, plus full XML-to-TSV reconciliation in separate recovered-evidence court. Conditional court JSON SHA-256 `4eb332ed0077bf92a42df02c2d9eb27a70e4357aa8f9ce5c30cbd36a54cf1fef`; original scorer and frozen run directory untouched.

38 archived source evidence files passed full internal manifest verification; archive SHA-256 `8330e5cb1e34cea4532445f4bd11988204ea76fbc0c02775a9321bac1595c72c`. User reports identical Windows copy SHA; Google Drive cloud sync is not independently verified by the connector.

This supports only bounded SUMO/MoST model-internal, horizon-imputed burden sensitivity to removing teleport. There is no field-policy identification, uncensored-trip-time estimand, multi-seed uncertainty estimate, or universal convexity claim. The stage is concluded with the native admission limitation preserved; no automatic follow-up teleport sweep or fresh server run. Return to Generation-II rival-mechanism and cross-ecology strategic review under a new prospectively authorized stage.
