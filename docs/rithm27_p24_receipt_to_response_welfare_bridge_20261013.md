# RITHM-2.7 P24 — Receipt-to-Response Welfare Bridge

**2026-10-13. Methods P1 / synthetic exact construction, no human causal claim.**

P23 identifies the receipt-admissible information set, not human route response. The founding RITHM question remains how delayed information interacts with individual persistence, congestion feedback and collective welfare.

The 2017 Wijayaratna et al. experiment has 12 travelers, three routes (A-B-D, A-C-B-D, A-C-D) and node-C downstream branching. Its route-cost geometry is
`C(n1,n2,z)=264-24n1-9n2+2n1^2+2n1*n2+n2^2+19*z*n2`, with `n1+n2+n3=12`.

**Toy counterexample:** Start `(n1,n2,n3)=(4,4,4)` at `z=0`. Fix the same hypothetical timely receipt, the same offered advice, and a toy upstream A-C sensor `q=n2+n3=8`. If one eligible C-stage driver does not change: `C=212`. If one C-B traveler switches to C-D: `(4,3,5), C=206`. If one C-D traveler switches to C-B: `(4,5,3), C=220`. All three have the same `q=8`. The *restricted* improvement set (baseline minus policy cost) is `{-8,0,6}`; its sharp interval hull is **[-8,+6]**. The outcomes are constructed behavioral potential worlds, not empirical estimates. Receipt legality alone cannot identify even the welfare-effect sign.

The example is stage-legal because A-C entrance is fixed and the potential actions differ only at C. It is not observationally equivalent for fully observed downstream route counts. The toy A-C sensor is NOT the Seoul 2025 LBL2000010 source; the 2017 people and 2025 detector records are NOT a linked causal cohort. No original provider/client receipt is available.

**Existing ancestors:** RITHM-2.5 passive/active observational equivalence; RITHM-2.6 P7 unobserved C-branch potential action; P23 synthetic informative receipt worlds. No new universal theorem claim.

**Next real-data gates:** reliable client receipt+version; actual advice exposure at node C; eligible driver choice and history; full route-specific realized flow and independently measured group travel time; independent intervention variation, session/group interference and precommitted welfare horizon. A six-session reanalysis is not independent replication.

**Status:** local Python witness and 12 local tests PASS; authenticated operational receipts, information-induced human behavior and collective causal welfare **HOLD**. 2.6 OPEN; 2.7 METHODS only.

2017 original: https://drive.google.com/file/d/16fc0fUDqGT1khOHw7KmMqROVF-bcX8H8/view
P23: https://github.com/WhoSia/RITHM/blob/main/docs/rithm27_p23_receipt_endogeneity_methods_20261013.md
