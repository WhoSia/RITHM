# Wijayaratna et al. 2017 — source-derived cost and route inputs for RITHM-2.3

Original open-access experiment: https://doi.org/10.1371/journal.pone.0184191
Original author S2 workbook: https://doi.org/10.1371/journal.pone.0184191.s002
Copyright 2017 Wijayaratna, Dixit, Denant-Boemont & Waller; CC BY 4.0. These two CSVs are compact derivative research representations, **not** the author workbook.

The `routes` CSV contains 24 session×group×stage rows encoding 240 ordered choices each as a base-3 integer, subject order ascending within each 20-round stage; plus 20-bit actual incident sequence and raw realized total cost.

The `costs_packed` CSV has **no header** and fields: session,group,stage,cost_code,source_aggregate_cost. One character per subject-round in the same order as route choices. `Cost = 11 + base36_digit_value`. All 5,760 rows and all 24 group-stage realized source costs have been checked against the original S2 workbook. Some original source records contain inconsistent same-route/same-round costs; RITHM never silently rewrites them.

Use only experienced cost through t−1 to predict t. Under NoInfo, current incident status was not revealed to individual participants. This data does not identify cognitive learning or beneficial coordination. Six laboratory sessions are the conservative independent cluster units.
