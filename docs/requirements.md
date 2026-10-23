# Requirements Specification

Project: Tilqor - Crowdsourcing Platform for Collecting and Verifying Kazakh Language Data with Daily Language Practice and Terminology Glossary Modules.

Task: [TIL-11](https://qosmuratsamat.youtrack.cloud/issue/TIL-11), as identified in [the project proposal](proposal.md).

Owner: Dovutbekov Ulykbek.

Task due date: 2026-10-22.

Document prepared: 2026-10-23. This date records preparation and does not imply completion before the task deadline.

Status: initial specification for team and supervisor review; not a statement that the requirements have been implemented or validated with users.

## 1. Basis and scope

The [proposal](proposal.md) defines the product scope and quality model. The [survey template](survey/template.md) defines questions, not verified user needs. As of 2026-10-23, `docs/survey/` contains only the questionnaire template and a placeholder; no completed responses or results summary are published there. PR review reports that [TIL-8](https://qosmuratsamat.youtrack.cloud/issue/TIL-8) is marked done, so its reported status and the repository evidence are inconsistent. Add the actual anonymized responses and evidence-based summary to `docs/survey/` and trace any requirement changes to those findings; if the evidence is unavailable, reopen TIL-8 until it is supplied. The tracker status could not be independently checked because YouTrack requires sign-in. Requirements below remain engineering proposals derived from the proposal, not survey-validated needs.

The MVP covers Russian-to-Kazakh sentence contributions, Kazakh term variants, independent verification, a terminology dictionary, a daily practice catalogue, and accepted-data export in CSV and JSON. Daily practice means top words, a word of the day, and connector hints; an exercise engine and learning streaks are not required.

Audio collection, a native mobile application, model training, a production-scale user pilot, and complex gamification are out of scope. The limited evaluation described in the proposal may use real reviewers or explicitly labelled simulated votes. Basic AI assistance is optional.

The earlier [risk document](risks.md) mentions pilot activities. For this specification, the proposal's exclusion of a production pilot governs scope; evaluation means a bounded study or simulation, not a production rollout.

## 2. Priorities and actors

| Priority | Meaning |
|---|---|
| Must | Required for MVP acceptance. Any failed or untested Must criterion prevents MVP acceptance. |
| Should | Planned after Must requirements; may be deferred without blocking MVP acceptance, with a recorded reason and follow-up task. |
| Could | Optional; absence does not prevent MVP acceptance. |

The 38 requirements comprise **30 Must, 7 Should, and 1 Could**. For the three-person team, the mandatory scope is one complete contribution-to-publication workflow: accounts and permissions, task administration, submissions, independent weighted verification and control tasks, versioned decisions, dictionary and daily catalogue, accepted-data export, and reproducible evaluation against the majority baseline with Krippendorff's alpha. Security, privacy, Unicode fidelity, consistency, responsive layouts, reproducible setup, performance, and source attribution remain mandatory.

The deferred scope is explicit: full audit-history retrieval (FR-16), withdrawal of published content (FR-21), points and ranking (FR-22), a demonstrated backup restore within 60 minutes (NFR-06), the complete keyboard-accessibility walkthrough (NFR-08), structured logging with request tracing (NFR-10), and compatibility checks across the supported browsers (NFR-11) are Should. AI assistance (FR-23) is Could. Deliver and verify the Must workflow first; record each deferred item, reason, limitation, and follow-up task in the TIL-7 verification report.

Deferring FR-16 does not remove the decision, version, vote, weight-snapshot, and configuration records required by FR-10 through FR-15 and FR-24; only the consolidated audit-history retrieval is deferred. Deferring FR-21 does not defer task administration (FR-03), permission checks, or export eligibility (FR-06 and FR-20). NFR-02 checks points updates only when FR-22 is delivered; its vote and decision consistency checks remain mandatory.

| Actor | Permissions |
|---|---|
| Visitor | Browse public dictionary and daily catalogue; download permitted public datasets. |
| Participant | Visitor permissions plus submit content and see their own submission status. |
| Reviewer | Participant permissions plus review other people's contributions; reviewer eligibility is assigned by an administrator. |
| Moderator/admin | Resolve disputes, manage content eligibility and tasks; only an administrator may change roles or quality-model configuration. |

## 3. Functional requirements

### 3.1. Accounts, tasks, and contributions

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| FR-01 | Must | The system shall support account registration, sign-in, and sign-out. | A new account can sign in using valid credentials. Invalid credentials do not create a session. After sign-out, the former session cannot perform an authenticated submission. |
| FR-02 | Must | The system shall enforce actor permissions on the server. | A visitor cannot submit or review; a participant cannot invoke reviewer or moderator actions; a reviewer cannot change roles. Each denied API request leaves stored data unchanged. An administrator can assign and revoke reviewer access. |
| FR-03 | Must | The system shall list contribution tasks by domain and type and allow moderators to manage tasks. | With fixtures in IT, medicine, engineering, and everyday life, applying a domain and task-type filter returns only matching active tasks. An empty result has an explicit empty state. A moderator can create or deactivate a task; deactivated tasks reject new submissions. Participants and reviewers cannot manage tasks. |
| FR-04 | Must | A participant shall submit a Russian-to-Kazakh sentence variant using a blind submission flow. | Before submission, neither the interface nor participant-accessible task responses disclose other translations. A valid non-empty translation is saved with author, task, version, and timestamp; other variants become visible to that participant only after their first valid submission. |
| FR-05 | Must | A participant shall choose or suggest a Kazakh term variant. | A term task displays existing variants without vote counts and allows a new variant. Tests with a controlled random generator demonstrate that display order is shuffled rather than fixed. One account has at most one active preference per task; changing it replaces the previous preference. A preference alone cannot accept a term. |
| FR-06 | Must | The system shall record content provenance and contribution permission. | Submission requires contributor permission for the configured publication terms. A reused source requires a source reference, license identifier, and attribution metadata; original content is explicitly marked as original. A moderator cannot mark unresolved permission metadata as export-eligible. |
| FR-07 | Must | The system shall validate submissions and show actionable feedback. | Empty input, input exceeding the configured maximum, and an exact duplicate after Unicode NFC normalization and whitespace trimming are rejected without another record. Missing Kazakh-specific letters and configured Russian connectors produce warnings rather than automatic rejection of otherwise valid text. Feedback identifies the affected field. |
| FR-08 | Must | Participants shall see the status of their own submissions. | For fixtures in `submitted`, `in_review`, `accepted`, `rejected`, and `needs_edit`, the author sees the correct current status and available decision reason. Another participant cannot access the author's private account details through this view. |

### 3.2. Verification and quality control

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| FR-09 | Must | The system shall provide an independent review queue. | An eligible reviewer receives unresolved versions authored by other accounts. Self-review is denied through both the interface and API. A repeated request does not create a second counted review by the same account for the same version. |
| FR-10 | Must | Reviewers shall submit `accept`, `reject`, `edit`, or `don't know` decisions on each translation or term variant separately. | Each review records the reviewer, version, decision, timestamp, and weight snapshot. Reject/edit decisions require a non-empty reason. `Don't know` is stored but excluded from the counted-vote total and weighted-share denominator. |
| FR-11 | Must | The system shall compute a weighted decision using the configuration in Section 4. | With fewer than three counted reviews, no automatic final decision occurs. With weights 1, 1, 1 and decisions accept, accept, reject, the version becomes accepted. With weights 2, 0.5, 0.5 and decisions accept, reject, edit, acceptance is blocked because only one person supports it. Equivalent reject/edit fixtures produce the corresponding status when both threshold conditions hold. |
| FR-12 | Must | Unresolved versions shall receive additional independent reviews and then moderator escalation. | After three or four counted reviews without a qualifying outcome, the version stays in review and can receive another reviewer. After five counted reviews without an outcome, it enters the moderator queue; a sixth counted review is not accepted. An authorized moderator can resolve it with a recorded reason; a reviewer cannot perform that override. |
| FR-13 | Must | The system shall version edited content and preserve previous decisions. | Editing a `needs_edit` version creates a new submitted version with no inherited votes. The previous text, votes, and decision remain readable in its history. Editing accepted text cannot silently replace the accepted version; replacement content must pass verification. |
| FR-14 | Must | Reviewer reputation shall update once per finalized standard review using the configured increments and limits. | A new reviewer starts at 1.00. A matching vote changes 1.00 to 1.05, a non-matching vote changes 1.00 to 0.90, and abstention leaves it unchanged. Values remain within 0.50-2.00. Retrying finalization does not apply a second update, and later reputation changes do not alter stored vote snapshots. |
| FR-15 | Must | The system shall mix control tasks with known labels into the review queue. | A moderator can create a control item with a reference decision. Review responses do not disclose its control status or answer before voting. Correct and wrong answers change weight by +0.05 and -0.20 respectively, once only, within the same bounds; abstention leaves weight unchanged. Control votes cannot enter published content or receive an additional standard-review update. |
| FR-16 | Should | An audit history shall explain content and quality decisions. | For a sampled finalized version, an authorized moderator can retrieve its author, revisions, review decisions, weight snapshots, configuration version, automatic outcome, and any override with actor, timestamp, and reason. Ordinary participants cannot modify this history. |

### 3.3. Dictionary, daily catalogue, and export

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| FR-17 | Must | The dictionary shall support Kazakh term search and domain filtering. | Case-insensitive search over normalized Kazakh term text finds a seeded matching term; a domain filter excludes other domains. A public search returns accepted versions only. An authenticated contribution view may separately show variants labelled `in_review`; they are not presented as accepted dictionary results. |
| FR-18 | Must | A dictionary entry shall display a recommended accepted variant, alternatives, domain, definition, source, and status. | With an accepted fixture containing those fields, the entry displays them and clearly separates pending alternatives. Only accepted variants are eligible for recommendation; a moderator records the choice and reason when several variants qualify. |
| FR-19 | Must | The daily catalogue shall provide top words, a word of the day, and Kazakh connector hints from accepted eligible content. | A fixture with accepted words and connector examples populates all three sections. The word of the day is stable for the same configured calendar date and is the same for all visitors. A rejected or pending item never appears; empty eligible content produces an explicit empty state. |
| FR-20 | Must | The system shall export accepted, permission-cleared records in CSV and JSON. | Both formats contain the same eligible record IDs and include type, Russian source text where applicable, Kazakh text, domain, version, source reference, license, attribution, and modifications metadata. Fixtures marked pending, rejected, control-only, withdrawn, or permission-unresolved are excluded. Exported files parse successfully and preserve text. |
| FR-21 | Should | Moderators shall be able to withdraw published content. | Withdrawing an accepted version removes it from public dictionary, daily catalogue, and all newly generated exports while preserving its version and decision records. Previously downloaded files are outside this removal guarantee. |
| FR-22 | Should | The system shall provide basic contribution points and a public ranking. | Under the default rule of one point per accepted contribution version and zero points per vote, accepting a version adds one point exactly once. A repeated finalization adds no points; withdrawal removes that point. Ranking shows display names and scores without email addresses. |
| FR-23 | Could | The system may offer AI-assisted near-duplicate suggestions. | When enabled, a configured test pair produces a similarity suggestion that a reviewer can dismiss. AI output cannot accept, reject, or export a record. Disabling the feature or an unavailable AI service leaves manual submission and review usable. |

### 3.4. Administration and evaluation

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| FR-24 | Must | Administrators shall manage and version quality-model settings. | An administrator can save valid settings within the ranges in Section 4. Invalid weights or inconsistent minimum/maximum review counts are rejected. Active review rounds retain their configuration version; a new round uses the new settings. |
| FR-25 | Must | The evaluation shall compare weighted verification with an unweighted majority baseline. | Given a frozen labelled fixture and fixed seed where randomness is used, an evaluation command reports both methods' predicted outcomes, accuracy against reference labels, number of unresolved cases, and processing conditions. Ties in the baseline remain unresolved. The report states whether votes are real or simulated and does not claim that a simulation proves real-user performance. |
| FR-26 | Must | The evaluation shall report reviewer agreement using Krippendorff's alpha for nominal decisions. | On a documented fixture with reviewer IDs, item versions, missing votes, and reference expected output, the calculation matches the reference within 0.000001. Abstentions are missing ratings. An insufficient or degenerate sample reports an undefined result and reason rather than a fabricated score. |

## 4. Quality-model defaults and decision rules

These are proposed, testable defaults resolving the options in the proposal. They are not empirical findings or claims of supervisor approval. Approval and later changes must be recorded in the task and configuration history.

| Parameter / rule | Initial specification |
|---|---|
| Counted decisions | `accept`, `reject`, `edit`; `don't know` is an abstention. |
| Reviewer count | Minimum 3, maximum 5 counted reviews from distinct eligible non-authors per version. Abstentions do not consume a counted slot. |
| Weight | New reviewer 1.00; inclusive bounds 0.50-2.00. Capture current weight when a vote is recorded. |
| Outcome share | Sum of weight snapshots supporting one outcome divided by the sum for all counted votes. Compare the unrounded value with 0.66. |
| Minimum independent support | At least two distinct reviewers must support an automatically selected outcome. |
| Evaluation point | After each counted review from review 3 through review 5. The first qualifying outcome finalizes the round. If none qualifies at review 5, only a moderator resolves it. |
| Standard reputation change | +0.05 for a counted decision matching the final decision; -0.10 otherwise. Apply once when the round is finalized, including moderator resolution. |
| Control-task change | +0.05 for the reference decision; -0.20 otherwise. No standard-review change for the same control item. |
| Rounding | Persist weights to two decimal places; never round outcome shares before threshold comparison. |
| Record lifecycle | `submitted` -> `in_review` -> `accepted`, `rejected`, or `needs_edit`. A moderator queue is an escalation flag on `in_review`, not a sixth content status. |
| Withdrawal | A separate publication eligibility flag; it does not erase the accepted decision or its history. |
| Term selection | Participant preferences do not replace variant verification. A moderator selects the recommended variant from accepted variants with a recorded reason. |
| Weight/config changes | Do not recalculate finalized outcomes automatically. Reassessment requires an explicit new review round, retaining the old round. |

Each validation round operates on an immutable content version. Automatic acceptance requires resolved provenance metadata and contribution permission as well as a qualifying vote outcome. If metadata is unresolved, the item remains unpublished for moderator resolution; it must not silently appear in exports.

## 5. Non-functional requirements

Numeric values below are initial engineering acceptance targets, not measurements of the current application. Record actual infrastructure, dataset, browser versions, and tool versions with test results. Failure to meet a target must be reported rather than replaced with an unmeasured success claim.

| ID | Priority | Requirement | Acceptance criterion |
|---|---|---|---|
| NFR-01 | Must | Kazakh and Russian text shall retain Unicode fidelity across storage, API responses, and exports. | A fixture containing all Kazakh-specific Cyrillic letters and Russian text survives submission, retrieval, CSV export, and JSON export without replacement characters or lost letters. Comparison allows only documented NFC normalization and input trimming. |
| NFR-02 | Must | Concurrent requests shall preserve review and decision consistency. | With five eligible reviewers submitting concurrently to one version and one account retrying its request, there is at most one counted vote per account, no more than five counted votes, and one final decision with each reputation/points update applied once. Repeating the test does not violate these invariants. |
| NFR-03 | Must | Credentials and authenticated sessions shall be protected. | Stored passwords are non-reversible hashes; public deployment redirects HTTP to HTTPS; browser authentication material is not exposed to client scripts when cookie sessions are used; state-changing cookie-authenticated requests without valid CSRF protection are denied. Logs and API responses contain no passwords or session tokens. |
| NFR-04 | Must | Public data shall exclude private account information. | Export and public endpoint fixtures containing distinct email addresses, account credentials, and session values expose none of those fields. Public attribution uses only the contributor's agreed public identifier, and moderator-only endpoints reject non-moderators. |
| NFR-05 | Must | Common operations shall meet a defined performance target under representative MVP load. | On a recorded reference environment with 2 application CPU cores, 4 GB RAM, 10,000 content versions, and 20 concurrent sessions, a five-minute warm-cache run achieves p95 server response time <= 2 seconds for dictionary search and submission/review writes, with < 1% unexpected server errors. Report each operation separately; dataset export is excluded. |
| NFR-06 | Should | Backups shall support recovery of content and verification history. | During a scheduled daily-backup configuration test, restore a backup no more than 24 hours old to an empty database within 60 minutes on the recorded reference environment. Validate fixture users, versions, reviews, and decisions after restoration. Record failures and any missing interval. |
| NFR-07 | Must | Core screens shall work on mobile and desktop layouts. | At 360 x 800 and 1440 x 900 CSS pixels, sign-in, submission, review, dictionary, and catalogue screens have no page-level horizontal overflow, clipped form actions, or overlapping text. Core actions remain usable at 200% browser zoom in a desktop viewport. |
| NFR-08 | Should | Core interactions shall be usable with a keyboard and labelled controls. | A keyboard-only walkthrough can sign in, submit a contribution, submit a review, and search the dictionary. Each interactive element has an accessible name, visible focus, and a reachable action; errors are associated with fields and statuses are not conveyed by color alone. |
| NFR-09 | Must | Setup and validation shall be reproducible from the repository. | A reviewer using a clean checkout and placeholder configuration can start the documented environment, apply migrations, load non-personal test fixtures, and run automated checks without undocumented credentials. CI runs relevant checks on PRs; an intentionally failing quality-model test causes CI failure. |
| NFR-10 | Should | Failures shall be observable without leaking private data. | A forced API failure produces a generic user-facing error with a traceable request identifier. Authorized maintainers can locate the matching structured log entry; the entry contains no raw credentials or private submission payload. |
| NFR-11 | Should | Core workflows shall be compatible with the team's supported browsers. | Execute the core workflow checks on current stable Chrome and Firefox desktop versions at test time, and record exact versions and differences. Include the keyboard walkthrough when NFR-08 is delivered; otherwise record that check as deferred. Both browsers complete the delivered workflow without blocking browser-specific errors. |
| NFR-12 | Must | Source attribution and license metadata shall remain attached to exported content. | For fixtures with distinct approved source conditions, both export formats preserve each record's required attribution and license identifiers. Records with missing or unresolved rights metadata are absent, and an accompanying export manifest lists included source conditions and the approved release terms. |

## 6. Verification and traceability

The following groups guide architecture and the verification plan; they do not replace the acceptance criterion on each requirement.

| Area | Requirement IDs | Primary verification approach |
|---|---|---|
| Accounts and contributions | FR-01 through FR-08 | Role-based API checks and interface walkthroughs with controlled task fixtures. |
| Verification engine | FR-09 through FR-16, FR-24 | Deterministic decision fixtures, boundary cases, version history checks, and control-task checks. |
| Public data pipeline | FR-17 through FR-21, NFR-01, NFR-04, NFR-12 | Seed every status and permission state, inspect public views, and parse both export formats. |
| Optional engagement and AI | FR-22, FR-23 | Idempotent points checks and optional-service failure scenarios, if implemented. |
| Evaluation | FR-25, FR-26 | Frozen dataset, documented reference outputs, and reproducible report generation. |
| Operational quality | NFR-02, NFR-03, NFR-05 through NFR-11 | Concurrency, security, load, restoration, responsive, keyboard, CI, and logging checks. |

The verification plan (TIL-7) should reference these IDs and store evidence for each executed criterion. Record requirement status as not tested, passed, failed, or deferred; record a reason for any deferred Should/Could item. Do not mark an implemented feature as passed without executing its acceptance check.

## 7. Decisions requiring review

- Confirm the quality-model defaults, especially two-person minimum support, reputation updates, and control-task handling.
- Confirm the permission agreement, permitted sentence sources, and export release terms before accepting redistributable content. No dataset license is selected by this document.
- Confirm term recommendation rules and the catalogue selection policy. Proposed catalogue default: top words sorted by accepted-version counted-review support with stable ID tie-breaking; daily selection derived deterministically from the configured date and eligible IDs; connector hints use moderator-tagged accepted examples. Withdrawn content overrides date stability.
- Confirm the performance and recovery targets against the selected deployment environment before implementation acceptance.
- Resolve the reported TIL-8 completion/evidence mismatch: publish actual anonymized responses and a summary in `docs/survey/`, or reopen the task. Incorporate findings when available and record whether they change a requirement; do not treat the task's done status as survey evidence.

## 8. Document acceptance checklist

- [x] Functional requirements have stable IDs.
- [x] Non-functional requirements have stable IDs.
- [x] Every requirement has a priority and an observable acceptance criterion.
- [x] Scope follows the proposal, including a daily catalogue rather than exercises.
- [x] Proposed defaults and unverified assumptions are identified.
- [ ] Another team member has reviewed this specification.
- [ ] Supervisor feedback and any resulting changes have been recorded.
