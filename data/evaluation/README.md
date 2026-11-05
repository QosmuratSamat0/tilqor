# Reproducible quality-model evaluation

TIL-26 implements FR-25/FR-26 using pure Python plus the existing Django command
runner. It adds no dependency, model or migration. Commands do not query the DB;
`make check` still needs local PostgreSQL for the rest of the backend suite.
See [ADR 0007](../../docs/adr/0007-evaluation-by-simulation.md) for decisions and
limitations, and [the synthetic demo](runs/synthetic-demo/report.md) for a pipeline
check. No real-user performance claim follows from those files.

## Run on a labelled records file

```sh
make evaluate RECORDS=tests/backend/evaluation/fixtures/records_synthetic.csv
```

This runs the mixed, reliable and noisy scenarios into `runs/<scenario>/`. When
TIL-25 arrives, substitute its actual CSV path for `RECORDS`; the same command
runs the evaluation. Real reference labels with simulated votes still require
the **simulation** label. The current fixture is not the TIL-25 dataset.

All three scenarios were fixed before demo runs. Their seed is 20261103; assumed
abstention rate 0.05 and control share 0.10. These assumed profiles are stored in
`simulation/*.json`, not estimated from the output.

### Simulation assumptions

| Simulation scenario | Careful (0.85) | Average (0.70) | Random (0.33) |
|---|---|---|---|
| mixed | 3 | 4 | 3 |
| reliable | 5 | 5 | 0 |
| noisy | 2 | 3 | 5 |

For a single scenario:

```sh
python src/backend/manage.py simulate_votes --records path/to/records.csv --profiles data/evaluation/simulation/mixed.json --out path/to/run/votes.csv
python src/backend/manage.py evaluate --records path/to/run/votes.records.csv --votes path/to/run/votes.csv --quality data/evaluation/quality.json --label simulation --out path/to/run
```

Use `.venv`'s Python when it is not activated. The simulation emits three files:

- `votes.csv`: `record_id,seq,reviewer_id,decision`, retaining abstentions.
- `votes.records.csv`: shuffled, frozen copy of the records, with the standard
  13 columns; extra input columns are ignored. The input file is never rewritten.
- `votes.meta.json`: seed, complete assumed profiles, control IDs, generation
  order, source/snapshot/vote/profile hashes. Keep this sidecar with its votes.

The evaluator always honors its supplied records file order. The Make target
uses the shuffled snapshot. Passing the original input explicitly is supported,
but changes reputation's processing order and thus may change the outcomes.

Both methods see the same ordered votes and stop independently. The weighted
method reuses `verification.domain`; the baseline checks strict majority after
each counted vote from 3 to 5. Neither counts abstentions. Control records are
excluded from both methods' accuracy/cost and raw agreement. Weighted controls
use all votes up to its counted limit and apply only control reputation updates.
The simulation assumes moderators resolve escalations with reference decisions
for reputation, while automatic escalations remain unresolved for accuracy.

`quality.json` freezes threshold, vote/support limits, weight bounds and update
steps from requirements §4. Decimal settings are encoded as strings to preserve
their exact values. Live database settings and persisted reviewer profiles are
never used. Everyone starts at the frozen initial weight for each run.

## Real votes later

```sh
python src/backend/manage.py evaluate --records path/to/records.csv --votes path/to/real-votes.csv --quality data/evaluation/quality.json --label real --out path/to/real-run
```

If real reviews include controls, pass `--controls path/to/control-ids.json` with
a JSON array of record IDs, for example `["record-12", "record-19"]`. Otherwise
no controls are assumed. `--seed` sets the bootstrap seed; the default is
20261103, or the simulation seed for simulated inputs. Generated simulation
sidecars cannot be relabelled real. Real vote CSVs do not contain moderator
resolutions, so real replay does not invent reputation updates for escalations.

Records require nonempty unique `id` and an exact `reference_decision` of
`accept`, `reject` or `edit`. Optional `type` and `error_type` must use their
documented codes if supplied; domain and error type are preserved for breakdowns.
Votes require a known record ID, positive integer sequence, unique sequence and
reviewer per record, and an exact decision including `dont_know`. Sequences are
sorted numerically. Missing reviews remain unresolved. CSV errors identify the
file and physical line; malformed JSON identifies its syntax line, while schema
errors identify the document and offending field. No English/Kazakh text is used
to determine correctness: only the supplied reference labels are used.

## Outputs and interpretation

Each run produces `report.md` and `results.json`. JSON includes both per-record
outcomes, used sequence numbers and weighted snapshots, final weights, metrics,
control counts, bootstrap CI, hashes, settings, seed, software versions, Git
commit and implementation hash. Alpha uses all supplied counted non-control
votes, including votes unused after a method's early decision.

Accuracy is correct/decided. Correct/all also exposes unresolved cases, which
count as not correct. Undefined denominators and degenerate alpha have null
values; alpha includes the reason. The 95% interval resamples paired non-control
records 2000 times, recomputing each method's ratio with its own decided
denominator. It does not rerun reputation learning. If a draw's ratio is
undefined, the interval is reported undefined rather than silently excluding it.

The report starts with the required simulation limitation statement. Every
simulated table is labelled Simulation, with reviewer accuracies under Assumptions.
The synthetic title is **Synthetic records + simulation — pipeline check, not a
result**. A real labelled CSV does not itself make generated votes empirical.

To regenerate the synthetic fixture (150 records: 75 accept, 38 reject, 37 edit):

```sh
python scripts/generate_evaluation_fixture.py --seed 20261103
make evaluate-synthetic-demo
```

Its text columns contain `synthetic`; the generator and fixed seed are stored in
the repository. The domain suite includes an exact hand-worked alpha example
(4/9) and the original [Krippendorff missing-data example](https://www.asc.upenn.edu/sites/default/files/2021-03/Computing%20Krippendorff%27s%20Alpha-Reliability.pdf)
(section C, pp. 4–5; exact 113/152, printed 0.743). No third-party statistics
implementation supplies the expected values.

## Reproducibility

The three-scenario Make command was run twice at source commit
`be7ec55c0f607117128b8e18fe1724617d93eaec`. All 15 emitted files were byte-identical
(votes, ordered snapshots, metadata, Markdown and JSON). The matching result
hashes are in [runs/reproducibility.sha256](runs/reproducibility.sha256):

```sh
sha256sum --check data/evaluation/runs/reproducibility.sha256
```

Outputs omit wall-clock timestamps. Repeat with the same input paths, contents,
implementation, Python version and Git commit for identical artifacts. A new Git
commit changes the recorded provenance even when predictions stay unchanged;
the stored runs record their actual generation commit, before the later artifact
commit. No source settings were tuned to the synthetic outputs.
