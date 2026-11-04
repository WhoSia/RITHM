# RITHM-2.10 P3-R8 — Joint Activity and Welfare Audit

Date: 2026-11-04 KST. Exact mathematical restrictions and exploratory model comparisons; causal mechanism not identified.

Original source is the author-approved Noussair-Qiao route-choice CSV in Drive, SHA-256 d36520564b60ba5281e7b571d2ecfd94e055b9ab7f78bd4e9eaf762844d0f8bb. Original person-level rows remain private.

Main question: Can the original 40-period generative Small Sample models explain the transition dynamics of a group currently at the socially optimal allocation (four of six people on A), instead of only matching treatment-level mean congestion costs?

Ruby implementations: activity_mixture.rb, ssm_joint_falsifier.rb and their exact rational unit tests. The original author-rule SSM generators ssm_generative.rb and ssm_activity.rb now additionally measure gross route switching and opposing cancellations without changing random draws.
