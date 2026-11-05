Simulation: shows model behaviour under the stated assumptions; it makes no claims about real users.

# Synthetic records + simulation — pipeline check, not a result

## Simulation: main comparison

| Simulation method | Correct / decided (accuracy) | Correct / all | Unresolved | Counted votes / decided |
|---|---|---|---|---|
| weighted | 81 / 101 (80.20%) | 81 / 135 (60.00%) | 34 / 135 (25.19%) | 3.35 |
| baseline | 82 / 121 (67.77%) | 82 / 135 (60.74%) | 14 / 135 (10.37%) | 3.23 |

## Simulation: agreement and paired comparison

Nominal Krippendorff alpha: **0.073024**.
Pairable units: 135; values: 675.
Agreement uses every supplied counted non-control vote, including votes unused after an early decision; abstentions are missing.

Accuracy difference (weighted − baseline): 12.43 pp.
95% paired-record bootstrap CI: [6.05 pp, 19.17 pp].
Resamples: 2000; seed: 20261103; undefined draws: 0.
Each paired resample recomputes both correct/decided ratios. Reputation is not relearned.

## Simulation: H1/H2 pipeline check

H1: supported in this run: weighted accuracy is higher than baseline.

H2: weighted leaves 34 unresolved vs 14 for baseline; higher moderator cost observed.

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
| reviewer-03 | average | 70.00% | 5.00% |
| reviewer-04 | average | 70.00% | 5.00% |
| reviewer-05 | average | 70.00% | 5.00% |
| reviewer-06 | random | 33.00% | 5.00% |
| reviewer-07 | random | 33.00% | 5.00% |
| reviewer-08 | random | 33.00% | 5.00% |
| reviewer-09 | random | 33.00% | 5.00% |
| reviewer-10 | random | 33.00% | 5.00% |

Seed: 20261103; assumed control share: 0.1.

## Simulation: control-task accuracy (weighted replay)

| Simulation reviewer | Correct / counted | Accuracy | Abstentions |
|---|---|---|---|
| reviewer-01 | 5 / 6 | 83.33% | 0 |
| reviewer-02 | 5 / 9 | 55.56% | 0 |
| reviewer-03 | 2 / 3 | 66.67% | 1 |
| reviewer-04 | 9 / 11 | 81.82% | 0 |
| reviewer-05 | 7 / 9 | 77.78% | 1 |
| reviewer-06 | 5 / 9 | 55.56% | 0 |
| reviewer-07 | 3 / 8 | 37.50% | 0 |
| reviewer-08 | 2 / 9 | 22.22% | 1 |
| reviewer-09 | 4 / 6 | 66.67% | 1 |
| reviewer-10 | 3 / 5 | 60.00% | 1 |

## Simulation: accuracy by error_type

| Simulation group | Method | Correct / decided | Accuracy | Correct / all | Unresolved |
|---|---|---|---|---|---|
| (unspecified) | weighted | 39 / 47 | 82.98% | 39 / 67 (58.21%) | 20 |
| grammar | weighted | 15 / 20 | 75.00% | 15 / 24 (62.50%) | 4 |
| russian_connector | weighted | 17 / 18 | 94.44% | 17 / 26 (65.38%) | 8 |
| wrong_term | weighted | 10 / 16 | 62.50% | 10 / 18 (55.56%) | 2 |
| (unspecified) | baseline | 41 / 57 | 71.93% | 41 / 67 (61.19%) | 10 |
| grammar | baseline | 15 / 23 | 65.22% | 15 / 24 (62.50%) | 1 |
| russian_connector | baseline | 17 / 23 | 73.91% | 17 / 26 (65.38%) | 3 |
| wrong_term | baseline | 9 / 18 | 50.00% | 9 / 18 (50.00%) | 0 |

## Simulation: accuracy by domain

| Simulation group | Method | Correct / decided | Accuracy | Correct / all | Unresolved |
|---|---|---|---|---|---|
| engineering | weighted | 15 / 21 | 71.43% | 15 / 29 (51.72%) | 8 |
| everyday | weighted | 25 / 29 | 86.21% | 25 / 38 (65.79%) | 9 |
| it | weighted | 24 / 27 | 88.89% | 24 / 35 (68.57%) | 8 |
| medicine | weighted | 17 / 24 | 70.83% | 17 / 33 (51.52%) | 9 |
| engineering | baseline | 17 / 28 | 60.71% | 17 / 29 (58.62%) | 1 |
| everyday | baseline | 24 / 35 | 68.57% | 24 / 38 (63.16%) | 3 |
| it | baseline | 23 / 32 | 71.88% | 23 / 35 (65.71%) | 3 |
| medicine | baseline | 18 / 26 | 69.23% | 18 / 33 (54.55%) | 7 |

## Processing and provenance

Scenario: noisy; input label: simulation.
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
| records: data\evaluation\runs\noisy\votes.records.csv | `5312210b13a58b999b5da592908d91bd6b389ba5301b026af123bfef459d990d` |
| votes: data\evaluation\runs\noisy\votes.csv | `98f9ff70aeb8b58f8e6650f2c1a97bd3f330bd329fa7fdec3032cc03afaa6d8b` |
| quality: data\evaluation\quality.json | `8609f3e2150d675e0c9d113406b77ff572c5aa9806ce8031626a3c3ec01e2562` |
| simulation_metadata: data\evaluation\runs\noisy\votes.meta.json | `26ad9c6fb27d33ce885cabfb6c62e478be7dc6f170348a52ce78c4911e3f70c6` |

## Limitations and validation

The sample is small; reference labels can be wrong. The interval is exploratory, not proof of superiority. No settings were tuned to these outputs.
The bootstrap describes fixed replay outcomes; it does not model learning uncertainty, reviewer dependence, or new reviewer populations.
Alpha is tested against an exact hand-calculated fraction and [Krippendorff's published missing-data example](https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff%27s%20Alpha-Reliability.pdf), section C, pp. 4–5 (printed 0.743).
