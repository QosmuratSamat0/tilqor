# Verification and evaluation plan

Task: [TIL-7](https://qosmuratsamat.youtrack.cloud/issue/TIL-7). Status: **plan** for pre-defense-1. No tests have been run and no results exist yet; this document says how they will be obtained.

Based on: [proposal](proposal.md), [requirements](requirements.md) (TIL-11), [architecture](architecture.md) (TIL-6), [risks](risks.md) (TIL-4) and [survey results](survey/results.md) (TIL-8).

## 1. What must be demonstrated

The aim of the project (proposal, §5) is a platform where users create and verify Kazakh language data with a **measurable data quality model**. The plan therefore has two parts:

1. **Verification:** the system does what the requirements say. Every Must requirement has an acceptance criterion in `requirements.md`; this plan says how each one is checked (§3–§5).
2. **Evaluation:** the weighted quality model gives better data than a simple baseline. This is the main research claim of the project and is measured separately (§6).

The survey (TIL-8) shows that users find the glossary and connector hints useful and prefer community voting with expert review of disputes. It does **not** show that the quality model works; that is measured here (survey assumption A1).

## 2. Test levels and tools

| Level | What is tested | Tool | Where it runs |
|---|---|---|---|
| Unit | Decision rule, reputation updates, control tasks, automatic checks, Krippendorff's alpha | `pytest` | Locally and in CI |
| API / integration | Permissions, blind submission, review queue, statuses, versions, export | `pytest-django`, DRF test client | Locally and in CI |
| Concurrency | One counted vote per reviewer, one final decision under parallel requests | `pytest` with parallel requests against PostgreSQL | Locally and in CI |
| Performance | Response time under MVP load | Locust (Python) | Reference environment (§5) |
| UI walkthrough | Core screens, mobile and desktop layout, keyboard use | Manual checklist; Playwright later if time allows | Before each pre-defense |
| Evaluation | Weighted model vs baseline on a frozen dataset | Evaluation command (FR-25, FR-26) | Reference environment (§6) |

All automated tests run on every pull request through GitHub Actions (NFR-09). An intentionally failing quality-model test must make CI fail.

## 3. Verification of the quality model (core)

These checks are deterministic: fixed inputs, known expected output. They cover the part of the system that is the main engineering contribution.

| Check | Input | Expected result | Requirement |
|---|---|---|---|
| Fewer than 3 votes | 2 counted votes | No decision, status stays `in_review` | FR-11 |
| Simple majority with equal weights | Weights 1, 1, 1; accept, accept, reject | `accepted` (A = 0.67) | FR-11 |
| One strong reviewer cannot decide alone | Weights 2, 0.5, 0.5; accept, reject, edit | No decision (A = 0.67, but only 1 person) | FR-11 |
| Reject and edit outcomes | Fixtures with R ≥ 0.66 and E ≥ 0.66 | `rejected` / `needs_edit` | FR-11 |
| "Don't know" is not counted | 3 counted votes + 1 "don't know" | Denominator uses only the 3 counted votes | FR-10 |
| Escalation | No outcome after 5 counted votes | Moderator queue; a 6th vote is refused | FR-12 |
| Self-review | Author tries to review own version | Refused by API and interface | FR-09 |
| Reputation update | Matching / non-matching vote on a finalized round | 1.00 → 1.05 / 1.00 → 0.90; bounds 0.50–2.00 | FR-14 |
| No double update | Finalization retried | Weight changes only once | FR-14 |
| Control tasks | Correct / wrong answer | +0.05 / −0.20; control status not visible before voting | FR-15 |
| Settings versioning | Settings changed during an active round | Active round keeps its old settings | FR-24 |
| New version after edit | Edit a `needs_edit` version | New version, no inherited votes, history kept | FR-13 |

## 4. Verification of the other requirements

| Area | Requirements | How it is checked |
|---|---|---|
| Accounts and permissions | FR-01, FR-02, NFR-03 | API tests per role: each forbidden action is refused and leaves data unchanged; passwords stored as hashes; CSRF check on state-changing requests |
| Tasks and contributions | FR-03 – FR-08 | API tests with fixtures for each domain and task type; blind submission: other variants are not returned before the user's own submission; automatic checks with empty, too long, duplicate and Russian-connector inputs |
| Dictionary and daily catalogue | FR-17 – FR-19 | Seed records in every status; only `accepted` records appear; word of the day is the same for the same date |
| Export | FR-20, NFR-01, NFR-04, NFR-12 | Export CSV and JSON from fixtures in every status; both files parse; same record IDs; all Kazakh letters preserved; no emails or tokens; licence and attribution present |
| Should / Could items | FR-16, FR-21, FR-22, FR-23, NFR-06, NFR-08, NFR-10, NFR-11 | Tested only if implemented; otherwise marked "deferred" with a reason |
| Reproducible setup | NFR-09 | A team member who did not write the code starts the project from a clean checkout using only the README and `config.example.env` |

## 5. Non-functional measurements and conditions

| Requirement | Metric | Target (from requirements) | Measurement conditions |
|---|---|---|---|
| NFR-02 | Counted votes per reviewer; final decisions per version | At most 1 vote per account, at most 5 counted votes, exactly 1 final decision | 5 reviewers submit in parallel to one version, one of them retries; test repeated 20 times |
| NFR-05 | p95 server response time; error rate | p95 ≤ 2 s for dictionary search and submission/review writes; < 1 % unexpected errors | 2 CPU cores, 4 GB RAM, 10,000 content versions, 20 concurrent sessions, 5-minute warm-cache run with Locust; export excluded |
| NFR-07 | Layout defects on core screens | No horizontal overflow, clipped actions or overlapping text | Viewports 360 × 800 and 1440 × 900; desktop at 200 % zoom |
| NFR-01 | Lost or replaced characters | 0 | Fixture with all Kazakh-specific letters (ә, ғ, қ, ң, ө, ұ, ү, һ, і) and Russian text, through submission, API and both export formats |

For each run, the hardware, dataset size, software versions and date are recorded next to the results. A missed target is reported as missed, not replaced with an unmeasured claim.

## 6. Evaluation of the quality model

### 6.1 Question

On the same set of votes, does the weighted model (reputation weights + control tasks + "at least 2 people" rule) decide records **more accurately** than a simple baseline?

### 6.2 Baseline

**Simple unweighted majority without control tasks** (FR-25): each counted vote has weight 1; a record is accepted, rejected or sent for editing if that outcome has more than half of the counted votes; ties stay unresolved. This is the method a basic crowdsourcing platform would use.

### 6.3 Data

| Item | Plan |
|---|---|
| Records | 100–200 ru → kk translations and term variants, frozen before the evaluation starts |
| Reference labels | Each record gets a reference decision (accept / reject / edit) from a Kazakh language teacher or another qualified person; the labeller is not one of the reviewers |
| Licence | Only sources with checked permission (risk R-01), or sentences written by the team |
| Error mix | Records include correct items and deliberately wrong ones (wrong term, Russian connector, grammar error), so that accuracy can be measured |

### 6.4 Votes: real or simulated

| Option | Description | Allowed claims |
|---|---|---|
| **A. Small real test (preferred)** | 5–10 people review the records through the platform | Results describe this group of real reviewers |
| **B. Simulation (fallback)** | Votes are generated by a script with reviewer profiles, e.g. a careful reviewer who is right 85 % of the time, an average one at 70 %, and a random clicker at 33 % (these numbers are assumptions, fixed before the run) | Results show how the model behaves **under these assumptions only**; no claims about real users |

If option B is used, every table and chart is labelled **"simulation"**, and the script, its parameters and the fixed random seed are stored in the repository.

### 6.5 Procedure

1. Freeze the dataset, reference labels and model settings; record their versions.
2. Collect votes (option A) or generate them (option B).
3. Run both methods on **exactly the same votes**, with the evaluation command (FR-25).
4. Compare each method's decisions with the reference labels.
5. Compute the metrics below and store the report with the input files.

Because both methods use the same votes, any difference comes from the decision method, not from different reviewers.

### 6.6 Metrics

| Metric | Definition | Requirement |
|---|---|---|
| Accuracy | Share of decided records whose decision equals the reference label | FR-25 |
| Unresolved rate | Share of records with no automatic decision (ties for the baseline, escalations for the weighted model) | FR-25 |
| Votes per decided record | Average number of counted votes needed for a decision (review cost) | — |
| Control-task accuracy | Share of correct answers on control tasks, per reviewer | FR-15 |
| Agreement | Krippendorff's alpha for nominal data on the raw votes; "don't know" is a missing value | FR-26 |

Krippendorff's alpha is chosen because records have different numbers of reviewers and some missing votes; Cohen's kappa works only for two raters, and Fleiss' kappa needs the same number of raters per record (proposal, §8). The alpha implementation is checked against a small hand-calculated example before use (FR-26: match within 0.000001).

### 6.7 How results are judged

The expected outcome, stated before measuring:

- **H1:** on the same votes, the weighted model's accuracy is **not lower** than the baseline's, and is higher when the votes include unreliable reviewers.
- **H2:** the weighted model may leave more records for moderators than the baseline leaves ties; this cost is reported, not hidden.

With 100–200 records the sample is small. Results are reported as counts and percentages, with a 95 % bootstrap confidence interval for the accuracy difference. No claim of statistical proof or of performance in production is made. If H1 is not supported, this is reported as a finding and the settings (threshold, weight steps) are reviewed.

## 7. Requirement status tracking

Each requirement gets one status in the test report: **not tested**, **passed**, **failed** or **deferred** (with a reason, Should / Could only). A requirement is marked **passed** only after its acceptance check has actually been run, with a link to the test or report.

## 8. Schedule

| Milestone | Date | Verification deliverables |
|---|---|---|
| pre-defense-1 | 2026-10-24 | This plan |
| pre-defense-2 | TBD (academic schedule) | Unit and API tests for the quality model (§3) in CI; first evaluation run on the frozen dataset (option A or labelled option B) |
| final-pre-defense | TBD (academic schedule) | Full test report with status of every requirement (§7); NFR measurements (§5); final evaluation report (§6) |

## 9. Limitations

- The evaluation dataset is small (100–200 records) and the reviewer group is small (5–10 people), so results are exploratory.
- Reference labels come from one or a few people and may contain their own errors.
- A simulation shows only the behaviour of the model under stated assumptions.
- Performance is measured on one reference environment, not on production infrastructure.
