Simulation: shows model behaviour under the stated assumptions; it makes no claims about real users.

# Synthetic records + simulation — pipeline check, not a result

## Simulation: main comparison

| Simulation method | Correct / decided (accuracy) | Correct / all | Unresolved | Counted votes / decided |
|---|---|---|---|---|
| weighted | 104 / 115 (90.43%) | 104 / 135 (77.04%) | 20 / 135 (14.81%) | 3.17 |
| baseline | 109 / 126 (86.51%) | 109 / 135 (80.74%) | 9 / 135 (6.67%) | 3.13 |

## Simulation: agreement and paired comparison

Nominal Krippendorff alpha: **0.213308**.
Pairable units: 135; values: 675.
Agreement uses every supplied counted non-control vote, including votes unused after an early decision; abstentions are missing.

Accuracy difference (weighted − baseline): 3.93 pp.
95% paired-record bootstrap CI: [0.11 pp, 8.25 pp].
Resamples: 2000; seed: 20261103; undefined draws: 0.
Each paired resample recomputes both correct/decided ratios. Reputation is not relearned.

## Simulation: H1/H2 pipeline check

H1: supported in this run: weighted accuracy is higher than baseline.

H2: weighted leaves 20 unresolved vs 9 for baseline; higher moderator cost observed.

Synthetic records: a pipeline check only, not a TIL-25 dataset result or evidence about real reviewers.

## Assumptions

Control records: 15; excluded from both methods' accuracy and cost metrics.
Records are processed whole, in the input CSV file order. Both methods receive the same ordered raw votes; each stops independently.
Baseline: strict majority after each counted vote from 3 to 5; no reputation or control-task learning.
The simulated moderator resolves weighted escalations with the reference label for standard reputation updates; the automatic outcome remains unresolved for accuracy.
Finite reviewer pools are sampled without replacement. Exhaustion fails explicitly; no conditioned redraw replaces abstentions.
Control count rounds records × control share to the nearest integer, half up. Control votes receive only control updates, up to the counted-vote limit.

## Simulation: Assumptions — reviewer profiles

| Simulation reviewer | Assumed profile | Assumed accuracy | Assumed don't-know rate |
|---|---|---|---|
| reviewer-01 | careful | 85.00% | 5.00% |
| reviewer-02 | careful | 85.00% | 5.00% |
| reviewer-03 | careful | 85.00% | 5.00% |
| reviewer-04 | average | 70.00% | 5.00% |
| reviewer-05 | average | 70.00% | 5.00% |
| reviewer-06 | average | 70.00% | 5.00% |
| reviewer-07 | average | 70.00% | 5.00% |
| reviewer-08 | random | 33.00% | 5.00% |
| reviewer-09 | random | 33.00% | 5.00% |
| reviewer-10 | random | 33.00% | 5.00% |

Seed: 20261103; assumed control share: 0.1.

## Simulation: control-task accuracy (weighted replay)

| Simulation reviewer | Correct / counted | Accuracy | Abstentions |
|---|---|---|---|
| reviewer-01 | 3 / 7 | 42.86% | 1 |
| reviewer-02 | 7 / 7 | 100.00% | 1 |
| reviewer-03 | 6 / 7 | 85.71% | 1 |
| reviewer-04 | 5 / 10 | 50.00% | 0 |
| reviewer-05 | 11 / 11 | 100.00% | 0 |
| reviewer-06 | 2 / 4 | 50.00% | 0 |
| reviewer-07 | 7 / 8 | 87.50% | 0 |
| reviewer-08 | 4 / 8 | 50.00% | 2 |
| reviewer-09 | 3 / 6 | 50.00% | 0 |
| reviewer-10 | 2 / 7 | 28.57% | 0 |

## Simulation: accuracy by error_type

| Simulation group | Method | Correct / decided | Accuracy | Correct / all | Unresolved |
|---|---|---|---|---|---|
| (unspecified) | weighted | 51 / 56 | 91.07% | 51 / 67 (76.12%) | 11 |
| grammar | weighted | 20 / 22 | 90.91% | 20 / 24 (83.33%) | 2 |
| russian_connector | weighted | 20 / 21 | 95.24% | 20 / 26 (76.92%) | 5 |
| wrong_term | weighted | 13 / 16 | 81.25% | 13 / 18 (72.22%) | 2 |
| (unspecified) | baseline | 56 / 62 | 90.32% | 56 / 67 (83.58%) | 5 |
| grammar | baseline | 19 / 23 | 82.61% | 19 / 24 (79.17%) | 1 |
| russian_connector | baseline | 20 / 24 | 83.33% | 20 / 26 (76.92%) | 2 |
| wrong_term | baseline | 14 / 17 | 82.35% | 14 / 18 (77.78%) | 1 |

## Simulation: accuracy by domain

| Simulation group | Method | Correct / decided | Accuracy | Correct / all | Unresolved |
|---|---|---|---|---|---|
| engineering | weighted | 20 / 22 | 90.91% | 20 / 29 (68.97%) | 7 |
| everyday | weighted | 29 / 33 | 87.88% | 29 / 38 (76.32%) | 5 |
| it | weighted | 28 / 31 | 90.32% | 28 / 35 (80.00%) | 4 |
| medicine | weighted | 27 / 29 | 93.10% | 27 / 33 (81.82%) | 4 |
| engineering | baseline | 20 / 25 | 80.00% | 20 / 29 (68.97%) | 4 |
| everyday | baseline | 33 / 37 | 89.19% | 33 / 38 (86.84%) | 1 |
| it | baseline | 29 / 34 | 85.29% | 29 / 35 (82.86%) | 1 |
| medicine | baseline | 27 / 30 | 90.00% | 27 / 33 (81.82%) | 3 |

## Processing and provenance

Scenario: mixed; input label: simulation.
Git commit: `be7ec55c0f607117128b8e18fe1724617d93eaec`.
Implementation SHA-256: `014f4fb6847584ae588cf702b68b647918b00a96e26ad44686cd4a1d71f46a01`.
Python: 3.12.10; Django: 5.2.18.
Execution timestamps are omitted so identical inputs, implementation and commit produce byte-identical artifacts.

Frozen quality settings:

```json
{
  "control_correct_step": "0.05",
  "control_wrong_step": "0.20",
  "match_step": "0.05",
  "max_votes": 5,
  "min_supporters": 2,
  "min_votes": 3,
  "mismatch_step": "0.10",
  "threshold": "0.66",
  "weight_initial": "1.00",
  "weight_max": "2.00",
  "weight_min": "0.50"
}
```

## Simulation: input SHA-256

| Simulation input | SHA-256 |
|---|---|
| records: data\evaluation\runs\mixed\votes.records.csv | `5312210b13a58b999b5da592908d91bd6b389ba5301b026af123bfef459d990d` |
| votes: data\evaluation\runs\mixed\votes.csv | `a2c81868563dc339a19ec3670fd559570dadf952a102115e18fbfc5dff5c122e` |
| quality: data\evaluation\quality.json | `8609f3e2150d675e0c9d113406b77ff572c5aa9806ce8031626a3c3ec01e2562` |
| simulation_metadata: data\evaluation\runs\mixed\votes.meta.json | `d19914285d7dc2b333cdfb0cb94bc7ff6e0077691be5348b4d18af851abd35e0` |

## Limitations and validation

The sample is small; reference labels can be wrong. The interval is exploratory, not proof of superiority. No settings were tuned to these outputs.
The bootstrap describes fixed replay outcomes; it does not model learning uncertainty, reviewer dependence, or new reviewer populations.
Alpha is tested against an exact hand-calculated fraction and [Krippendorff's published missing-data example](https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff%27s%20Alpha-Reliability.pdf), section C, pp. 4–5 (printed 0.743).
