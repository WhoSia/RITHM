# RITHM-2.10 P3-R59 — Reproduction, source boundaries and CLI

## Public unit tests (no human records required)

Python 3.11 and the isolated `numpy==2.2.6` dependency:

```sh
python -m pip install -r requirements-r59.txt
python -m unittest discover -s . -p 'test_r59_*.py' -v
python -m unittest discover -s . -p 'test_r58_*.py' -v
python r59_transport_counterexample.py
```

R59's 16 source-free tests guard streaming Appendix A EWA, original Appendix B sampling and participant-information walls, actual-vs-50:50 first-period starts, never revealing future Value before a choice, the 40-step two-state exact Markov witness, counterfactual inclusion of section 1's extra 20-period pilot, persistent person-section correlation's six-person within-group null, publication contracts, and original-blob SHA fail-closed. The previous 20 R58 tests remain available in this package for regression.

All numerical tables in the public output are **cohort aggregates**, with no original group, person, session ID, or privately observed Value tapes.

## Operator-only source replay

The author-provided archive is deliberately **NOT** included. It is owned in the research Drive, with byte SHA256:

```
e6adce2da4d1c01455e912aa15144f192108394cbec0bd7f767e2732dcec9953
```

Only a researcher authorized to use the source should execute:

```sh
python r59_independent_replay.py /restricted/original.zip > r59_original_source_parity.json
python r59_prior_exposure.py /restricted/original.zip > r59_prior_exposure_results.json
python r59_run.py /restricted/original.zip --initial-routes observed --repetitions 32 --seed 20261121 --output r59_observed_primary.json
python r59_run.py /restricted/original.zip --initial-routes fair --repetitions 32 --seed 20261121 --output r59_fair_primary.json
python r59_run.py /restricted/original.zip --initial-routes observed --repetitions 32 --seed 20261122 --output r59_observed_seed2_32.json
python r59_run.py /restricted/original.zip --initial-routes fair --repetitions 32 --seed 20261122 --output r59_fair_seed2_32.json
python r59_run.py /restricted/original.zip --initial-routes fair --exogenous-values fresh_uniform --repetitions 32 --seed 20261121 --output r59_fair_fresh.json
python r59_run.py /restricted/original.zip --initial-routes fair --ssm-only --ssm-lapse 0 --repetitions 32 --seed 20261121 --output r59_fair_raw_ssm.json
python r59_results.py . --output r59_results.json
```

The reproduced script writes **aggregates only**. The operator must not publish any private `original.zip` or inline actor/individual observations. All six simulations train EWA λ and the private behavioral comparator **on the other 23 sessions** for each heldout session. They produce 40 simultaneous decisions in sequence using generated prior choices/payoff history. Each simulation scores **period-end congestion**, not imagined intermediate choices.

The primary `.02` SSM lapse is researcher-added to compare with R58, while the zero-lapse SSM scenario uses the author's original sample rule. `--initial-routes observed` reuses the actual t=1 choices (conditional origin); `--initial-routes fair` draws all t1 routes 50:50 (model-autonomous origin). With `--exogenous-values tape`, the original participant's external Value(t) is supplied only **after** that participant's generated route choice; `fresh_uniform` uses a new generator over the 101 observed 0.1-point Value levels from 6.0 to 16.0.

The released aggregate's 24-session resampling intervals describe a **finite historical sample** and do not estimate causal information-treatment or behavioral mechanism effects. `κ` is a symbolic per-switch *resource* parameter that must be justified externally; MSE crossover thresholds are **not** measured or recommended resource prices.

## Archive and GitHub parity

The `SHA256_MANIFEST.json` lists exact hashes and lengths of the included source-free members. The `r59_results.json` has 24-session/144-section/5,616-transition summary and six scenario comparisons. Check member sizes and SHA256 before trusting any byte-stable build. Do not use GitHub Actions PASS as evidence of a remote replay of the private human source; its default CI has no original human ZIP.

Prior art: Noussair–Qiao Appendix A/B/E, Ross–Gordon–Bagnell (2011) DAgger and autoregressive distribution shift, Bengio et al. (2015) scheduled sampling. Formal proof here is an educational finite-state exact construction, **not a newly discovered general theorem**.
