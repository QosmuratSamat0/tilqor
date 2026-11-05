Simulation: shows model behaviour under the stated assumptions; it makes no claims about real users.

# Synthetic records + simulation — pipeline check, not a result

## Simulation: main comparison

| Simulation method | Correct / decided (accuracy) | Correct / all | Unresolved | Counted votes / decided |
|---|---|---|---|---|
| weighted | 119 / 126 (94.44%) | 119 / 135 (88.15%) | 9 / 135 (6.67%) | 3.17 |
| baseline | 127 / 135 (94.07%) | 127 / 135 (94.07%) | 0 / 135 (0.00%) | 3.07 |

## Simulation: agreement and paired comparison

Nominal Krippendorff alpha: **0.419342**.
Pairable units: 135; values: 675.
Agreement uses every supplied counted non-control vote, including votes unused after an early decision; abstentions are missing.

Accuracy difference (weighted − baseline): 0.37 pp.
95% paired-record bootstrap CI: [-0.63 pp, 2.05 pp].
Resamples: 2000; seed: 20261103; undefined draws: 0.
Each paired resample recomputes both correct/decided ratios. Reputation is not relearned.

## Simulation: H1/H2 pipeline check

H1: supported in this run: weighted accuracy is higher than baseline.

H2: weighted leaves 9 unresolved vs 0 for baseline; higher moderator cost observed.

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
| reviewer-04 | careful | 85.00% | 5.00% |
| reviewer-05 | careful | 85.00% | 5.00% |
| reviewer-06 | average | 70.00% | 5.00% |
| reviewer-07 | average | 70.00% | 5.00% |
| reviewer-08 | average | 70.00% | 5.00% |
| reviewer-09 | average | 70.00% | 5.00% |
| reviewer-10 | average | 70.00% | 5.00% |

Seed: 20261103; assumed control share: 0.1.

## Simulation: control-task accuracy (weighted replay)

| Simulation reviewer | Correct / counted | Accuracy | Abstentions |
|---|---|---|---|
| reviewer-01 | 7 / 7 | 100.00% | 1 |
| reviewer-02 | 5 / 7 | 71.43% | 0 |
| reviewer-03 | 6 / 6 | 100.00% | 1 |
| reviewer-04 | 9 / 9 | 100.00% | 0 |
| reviewer-05 | 6 / 8 | 75.00% | 1 |
| reviewer-06 | 4 / 7 | 57.14% | 0 |
| reviewer-07 | 7 / 9 | 77.78% | 0 |
| reviewer-08 | 5 / 6 | 83.33% | 1 |
| reviewer-09 | 5 / 10 | 50.00% | 0 |
| reviewer-10 | 4 / 6 | 66.67% | 0 |

## Simulation: accuracy by error_type

| Simulation group | Method | Correct / decided | Accuracy | Correct / all | Unresolved |
|---|---|---|---|---|---|
| (unspecified) | weighted | 58 / 61 | 95.08% | 58 / 67 (86.57%) | 6 |
| grammar | weighted | 21 / 23 | 91.30% | 21 / 24 (87.50%) | 1 |
| russian_connector | weighted | 25 / 26 | 96.15% | 25 / 26 (96.15%) | 0 |
| wrong_term | weighted | 15 / 16 | 93.75% | 15 / 18 (83.33%) | 2 |
| (unspecified) | baseline | 64 / 67 | 95.52% | 64 / 67 (95.52%) | 0 |
| grammar | baseline | 21 / 24 | 87.50% | 21 / 24 (87.50%) | 0 |
| russian_connector | baseline | 25 / 26 | 96.15% | 25 / 26 (96.15%) | 0 |
| wrong_term | baseline | 17 / 18 | 94.44% | 17 / 18 (94.44%) | 0 |

## Simulation: accuracy by domain

| Simulation group | Method | Correct / decided | Accuracy | Correct / all | Unresolved |
|---|---|---|---|---|---|
| engineering | weighted | 27 / 27 | 100.00% | 27 / 29 (93.10%) | 2 |
| everyday | weighted | 32 / 36 | 88.89% | 32 / 38 (84.21%) | 2 |
| it | weighted | 31 / 32 | 96.88% | 31 / 35 (88.57%) | 3 |
| medicine | weighted | 29 / 31 | 93.55% | 29 / 33 (87.88%) | 2 |
| engineering | baseline | 29 / 29 | 100.00% | 29 / 29 (100.00%) | 0 |
| everyday | baseline | 34 / 38 | 89.47% | 34 / 38 (89.47%) | 0 |
| it | baseline | 33 / 35 | 94.29% | 33 / 35 (94.29%) | 0 |
| medicine | baseline | 31 / 33 | 93.94% | 31 / 33 (93.94%) | 0 |

## Processing and provenance

Scenario: reliable; input label: simulation.
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
| records: data\evaluation\runs\reliable\votes.records.csv | `5312210b13a58b999b5da592908d91bd6b389ba5301b026af123bfef459d990d` |
| votes: data\evaluation\runs\reliable\votes.csv | `830385721a857c51e13321cc2f7c9bfee2d2a8e1877430a56b6853f6a89d5a9c` |
| quality: data\evaluation\quality.json | `8609f3e2150d675e0c9d113406b77ff572c5aa9806ce8031626a3c3ec01e2562` |
| simulation_metadata: data\evaluation\runs\reliable\votes.meta.json | `de0dbefa7e1875c94731121139b7072bb5f6b8614cd173969fe361a05c366d6b` |

## Limitations and validation

The sample is small; reference labels can be wrong. The interval is exploratory, not proof of superiority. No settings were tuned to these outputs.
The bootstrap describes fixed replay outcomes; it does not model learning uncertainty, reviewer dependence, or new reviewer populations.
Alpha is tested against an exact hand-calculated fraction and [Krippendorff's published missing-data example](https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff%27s%20Alpha-Reliability.pdf), section C, pp. 4–5 (printed 0.743).
