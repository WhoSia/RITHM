# RITHM 2.9 code retirement ledger — 2026-10-31

## Successfully retired one candidate after Drive archival

- Old source path: `src/rithm/legacy/rithm20.py` (RITHM 2.0 original descriptive 18-person route-choice model; **not** the current 2.9 six-player model).
- Original Git blob SHA: `96a1c53003dabf955c1ffa5dd050542d3ee0fe90`.
- Read-only historical text copy: [Drive RITHM archive](https://docs.google.com/document/d/1pgLAyaYiTQrIaiAg-9HXvhRD6Es2UPRfYaC0A1umH3Y/edit), in existing Research OS RITHM backup folder ID `16T5wRdLx_nSMgiMSZ7K1e6EugJqum9mJ`.
- Verified that archival Doc can be fetched, includes original source and Git blob SHA. Google Docs is a **textual snapshot**, not a byte-identical .py archive; exact bytes remain recoverable through Git commit history using the recorded blob SHA. Do not claim this is an independent raw-byte seal.
- Search of active GitHub repository for literal references `rithm20.py`, `legacy.rithm20`, `from .rithm20` returned none; static search is not a full dynamic-use proof.
- Deleted the original path from GitHub main in commit `7a1b213b00358c1c25248f8388b928bc3283d7f6`, AFTER document copy verification. Git history unchanged. Removal of this historical 18-player script does not touch modern 6-player original-data analysis.

## Not retired

- `ruby/rithm29/learning/learning_models.rb`, exact finite-grid SSM code and tests: still scientifically active.
- `ruby/rithm29/learning/group_joint/ruby/` direction, projection, scoring and replay modules: currently active, independent cross-language validation.
- Other `src/rithm/legacy/` files: **candidates only** pending specific full-source archive and call graph/CI review. No mass deletion on age or naming alone.

## Concurrent active Ruby development

Created `inertia_calibration.rb`: one-step historic choice-preserving shift `sigmoid(logit(p)+kappa*(2previous_a−1))` with stable evaluation, finite domain guards and kappa>=0. Output switch propensity is conditional on previous observed route. `kappa=0` exactly preserves original p; increasing kappa reduces switching for 0<p<1 with previous route fixed. Endpoints remain 0/1 exactly; this is a deliberate limit behavior, not fitted score.
Local Ruby 3.3.8 Minitest: 4 tests and 59 assertions pass, no errors or failures. GitHub commits `8685e22a863839474659619082f13b7dcc2b3192`, `f9bf8eaa8c926b43b010fb01294017cfce6a2272`.
No new model fit, no new study participants. Next fit kappa on train-only existing-data sessions and evaluate session-heldout loss and joint turnover.
