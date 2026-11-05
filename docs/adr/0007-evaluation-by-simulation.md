# 0007. Evaluate the quality model by reproducible vote simulation

- **Status:** Accepted
- **Date:** 2026-11-06
- **Source:** [TIL-26](https://qosmuratsamat.youtrack.cloud/issue/TIL-26), supplied task;
  [verification plan §6](../verification-plan.md#6-evaluation-of-the-quality-model),
  option B selected 2026-11-03; FR-25 and FR-26

## Context

There is no real reviewer group available before the MVP. The TIL-25 reference-labelled
dataset is expected on 2026-11-14. Evaluation infrastructure can be built now with
explicitly synthetic records, but simulated decisions cannot establish real-user
performance. Both methods must receive the same votes and expose their review cost.
Decision and reputation rules already exist as pure functions in `verification.domain`.

## Decision

Use option B: generate fixed-seed reviewer votes from assumptions frozen before runs,
then compare sequential weighted replay and a sequential strict-majority baseline on
the same ordered raw ballots. Reuse `verification.domain.decisions.evaluate` and
`verification.domain.reputation.updated_weight`; settings are read only from frozen
JSON, not database state.

The three prescribed profile distributions live in `data/evaluation/simulation/`:
mixed (3 careful, 4 average, 3 random), reliable (5 careful, 5 average), noisy
(2 careful, 3 average, 5 random). Assumed accuracies are 0.85, 0.70 and 0.33;
abstention rate is 0.05, control share 0.10, and seed 20261103. These are inputs,
not measured reviewer abilities. A finite reviewer pool is sampled without replacement;
if it cannot supply five counted votes, generation fails instead of redrawing a
conditionally easier record.

Shuffle records and choose controls with that same seeded RNG. Save an ordered
`votes.records.csv` snapshot and `votes.meta.json` beside `votes.csv`. Replay processes
whole records, in its supplied CSV file order; `make evaluate` supplies the shuffled
snapshot. Passing the original CSV explicitly preserves its original order. Record
and vote hashes in the sidecar prevent accidentally mixing runs. Control count rounds
records × share to the nearest integer, half up.

Weighted decisions use current reviewer weights as snapshots after each counted vote
from the configured minimum through maximum. The first qualifying outcome stops that
record. Standard reputation updates happen once, against that final outcome. For
escalations **simulation assumes a moderator resolves with the reference label** and
updates standard reputation against it; the automatic outcome still counts as unresolved.
An incomplete record without an automatic decision or escalation does not finalize.
Control votes update weights against the reference (+0.05 / −0.20 by default), up to
the counted-vote limit, without a standard update. Both methods exclude controls from
accuracy, unresolved rates, review cost and agreement.

The baseline uses unit weights, no reputation and no control-task learning. It checks
for more than half of counted votes after each vote from 3 to 5, stopping at the first
majority; no majority at five is unresolved. A 2–2 prefix cannot occur under this
minimum without an earlier majority; the tie rule is separately tested at minimum four.

Report correct/decided and correct/all, unresolved counts/rates, votes per decided
record, control accuracy, breakdowns, and nominal Krippendorff alpha on all raw
non-control votes (including unused tails). Alpha uses coincidence matrices, excludes
units with fewer than two pairable values, and reports undefined samples with a reason.
A hand-derived fraction and the published missing-data example validate the calculation.

Use a paired-record percentile bootstrap with 2000 draws and a fixed seed. Each draw
recomputes both correct/decided ratios on the same sampled records; it does not relearn
reputation. An undefined denominator is explicit, not silently dropped from the interval.

## Alternatives

- **Option A, real reviewers:** preferred later when a group exists. Import their votes
  through the same `votes.csv` interface and use `--label real`, with an optional JSON
  array of known control IDs. Because the CSV has no actual moderator decisions, real-vote
  escalations do not receive an invented reference-based reputation update. Such an
  update is the simulation assumption above. A real labelled dataset with simulated
  votes still uses `--label simulation`.
- **Non-sequential majority on all votes:** rejected because it consumes all votes while
  the weighted model may stop early, making cost comparisons unequal.
- **Copy model rules into evaluation or load current database settings:** rejected because
  duplicated rules may drift and live settings prevent a frozen, reproducible comparison.

## Consequences

- `apps.evaluation` has no models or migrations, and its domain has no Django imports.
  It adds no runtime or development dependency. Commands run without a database.
- Every simulated report starts with the mandatory limitation statement and labels
  every table Simulation. Profile accuracies appear under Assumptions. Synthetic
  fixture runs are pipeline checks, never the TIL-25 dataset or empirical results.
- JSON artifacts retain input SHA-256, record outcomes, settings, seed, software
  versions, Git commit and implementation hash. Timestamps are omitted for byte stability.
  Reproduction requires the same inputs, code and commit; later commits naturally change
  the recorded Git provenance even if predictions are unchanged.
- Whole-record processing and oracle moderator resolutions simplify real asynchronous
  behaviour. Control share, assumed reviewer profiles, finite pool and the small sample
  limit all claims. The bootstrap conditions on this fixed replay, not a new population.
- H1 failures and the moderator cost in H2 must be reported. Do not tune the settings
  against the synthetic demo and present the tuned outcome as independent validation.
