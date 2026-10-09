# RITHM-2.0 — Information timing and human-group welfare

## Source and question

Ashraf, Brown, Burris & Vitaku (2023), *Economic Inquiry* 61(4), 818–850,
[DOI:10.1111/ecin.13143](https://doi.org/10.1111/ecin.13143).
Replications: openICPSR project 185222, V2.
Read the **original** `study1.csv` and authors' `traffic_01.do` / README;
do not commit person-level source data to this repository.

Study 1: ten *live, interacting groups* of eighteen humans, each playing
one hundred rounds. All receive chosen-road payoff only in periods 1–50.
In periods 51–100, session treatments are: Control (two sessions, none
informed), All (two, all eighteen informed), Frequent-4 (three, four
**pre-period** highest-frequency switchers informed), and Infrequent-4
(three, four **pre-period** lowest-frequency switchers informed).
Ties at the fourth person's switch-count boundary are allowed.
The code checks those histories. Selecting on baseline switching makes
naive informed-versus-uninformed within-session comparisons **confounded by
design**; aggregate treatment comparison has only ten session units.

## Descriptive reconstruction of original 1,000 group-rounds

* 18,000 individual choices, 1,000 group-round payoffs; full author
  reward function verified in the existing `rithm20.py`.
* Social optimum: 7 on side road, W=181; unique pure Nash: 6 on side
  road, W=180.
* Observed E[side]=5.986, Var(side)=3.957804, E[W]=160.126.
* 181 - E[W] = 1.08498 (mean allocation) + 19.78902 (occupancy
  dispersion), with 94.8% of the **descriptive** observed shortfall in the
  second component.
* Of 990 consecutive within-session group transitions, 118 have some
  individual switching but zero net side-occupancy change.

## Baseline-to-late (rounds 1–50 vs 51–100)

These values are mean **within-session late-minus-early group payoff**
in experimental currency units per group-round, then equally averaged
over sessions in each treatment. This is NOT a randomized individual
comparison and has no standard-error/causal interpretation.

| Regime | Session IDs | Mean change in W | Change vs Control |
| --- | --- | ---: | ---: |
| Control | 1, 2 | +12.230 | 0 |
| All | 3, 4 | +2.390 | -9.840 |
| Frequent-4 | 5, 6, 7 | -0.187 | -12.417 |
| Infrequent-4 | 8, 9, 10 | +0.813 | -11.417 |

The **untreated** groups themselves improved strongly over the same
period. Hence a naive after-onset comparison would mistake learning and
shared time for an information effect. With only two control groups,
session 1's gain (+19.56) has high leverage; both groups must be shown
and no strong treatment claim made. Study 1 is consistent with the
authors' report that aggregate information effects were inconclusive.

## Assignment, transport and limits

The four-person regimens deliberately select people by pre-intervention
switching behavior. Randomizing which individual is informed is not
supported in those arms. In Study 2, contemporary individuals face
prerecorded group occupancy; its information-induced route switching
cannot be treated as a live network-welfare effect. The observed group
welfare outcome is governed by the exact congestion/payoff game
function, not a direct physical-road travel-time measurement.

The live-group descriptive contrasts are restricted to the first
Study 1 sample (ten group sessions, not 18,000 independent groups).
No claim is made that guidance **caused** welfare harm, nor that
individual habit was the source of group instability. A new causal
study must specify a defensible session-level assignment model,
precommit a test and seek independent interacting-human replication.

## Reproduce

```shell
python rithm20.py path/to/study1.csv --strict-source
python rithm20_information.py path/to/study1.csv --strict-source
python -m unittest discover -s tests -v
```

CI runs fully synthetic fixtures only; human source files are deliberately
not present in the repository. Python is the primary parser/controller,
base R is the separate payoff/arithmetic auditor, Stata `.do` is historical
paper-origin analysis only. No new polyglot runtime without an identified
reason.

## Next version proposal (not opened)

`RITHM-2.1 — When Route Switching Fails to Help: Information Timing,
Endogenous Congestion Volatility & Private–Social Welfare Divergence`.

This is a research-question direction, not a confirmed causal mechanism.
