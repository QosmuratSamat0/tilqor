# Risks and Milestones

Project: Tilqor - Development of a Crowdsourcing Platform for Collecting and Verifying Kazakh Language Data with Daily Language Practice and Terminology Glossary Modules.

Task: [TIL-4 - Risks and milestones](https://qosmuratsamat.youtrack.cloud/issue/TIL-4/Risks-and-milestones)

Document owner: Dovutbekov Ulykbek.

Task due date: 2026-10-23.

Last updated: 2026-10-23.

## 1. Planning basis

This document covers risks, project milestones, task dependencies, and responsibility allocation. Risk ratings are initial planning estimates, not measured probabilities. Review them after the user survey, architectural decisions, and each pre-defense.

The [proposal](proposal.md) excludes a real-user pilot. Evaluation is limited to a small test with 5-10 people and 100-200 records with reference labels, for example from a Kazakh teacher. If real votes are unavailable, use a clearly labelled simulation with documented vote-generation assumptions and a fixed seed. Report actual sample sizes and limitations; simulated votes are not evidence of real-user participation, usability, or production performance.

Team roles follow the [proposal](proposal.md). The task owners for TIL-4, TIL-8, and TIL-16 are reflected in Section 5; implementation allocations remain proposals for team agreement. The initial submission and pre-defense-1 are scheduled for 2026-10-24, as confirmed in the TIL-4 PR review. Dates of the later defenses remain TBD until the academic schedule is confirmed.

## 2. Risk assessment

Probability: Low = unlikely under the current plan; Medium = plausible; High = likely without preventive action.

Impact: Low = limited rework within one task; Medium = delay or reduced quality in one module; High = failure of a mandatory workflow, loss of data, or inability to deliver or release the planned result.

Risk owners monitor the warning signs and coordinate the response. All risks below are open at the time of writing.

| ID | Risk | Probability | Impact | Mitigation and response | Warning sign | Proposed owner |
|---|---|---|---|---|---|---|
| R-01 | Sentence sources or contributed content have unclear or incompatible licenses, preventing redistribution of the dataset. | Medium | High | Record the source URL, license and version, attribution, and changes for reused content. Check terms before importing sentences. Exclude content with unresolved rights. Preserve required attribution and ShareAlike conditions in exports containing adapted material. | A candidate source has no clear license, or an export loses source attribution. | Ulykbek |
| R-02 | Too few participants or records are available for the bounded evaluation. | High | High | Arrange the small test with 5-10 people and prepare 100-200 permitted records with reference labels. If real votes are unavailable, use a clearly labelled simulation; report actual participation, record counts, and sample limitations. | Fewer than 5 people or 100 reference-labelled records are available, or planned review sessions cannot be completed. | Abylaikhan |
| R-03 | Incorrect translations, definitions, or examples are accepted. | High | High | Define review criteria, require independent review, prevent self-approval, and audit accepted samples. Return disputed or failed records to review. | Sample audits identify incorrect accepted records or reviewers frequently disagree. | Ulykbek |
| R-04 | Reviewers disagree about terminology and verification becomes inconsistent. | High | Medium | Document how alternatives and subject areas are handled. Keep review reasons and version history. Escalate unresolved cases to a moderator and seek supervisor or language specialist input where necessary. | Similar submissions receive contradictory decisions or disputes remain unresolved. | Ulykbek |
| R-05 | Spam, duplicate submissions, or coordinated voting distort the data. | Medium | High | Add submission limits, duplicate checks, reporting, and moderation. Prevent repeated votes by one account on the same review and inspect suspicious activity. | Repeated identical entries, bursts of votes, or repeated abuse reports appear. | Samat |
| R-06 | The review queue cannot be completed within the bounded test sessions. | Medium | High | Limit the evaluation to 100-200 records, track pending items, and arrange review sessions among the 5-10 participants. If using simulated votes, record unresolved cases separately. Keep unverified data out of accepted-data views. | Pending records exceed the remaining session capacity or the agreed review time; the report omits unresolved cases. | Ulykbek |
| R-07 | Collecting data, verification, daily practice, and the glossary exceed the available development time. | High | High | Prioritize one complete workflow from submission to verified glossary entry and practice use. Freeze mandatory scope before implementation. Defer optional features and review progress weekly. | Mandatory work repeatedly misses its planned completion or optional work delays the core workflow. | Samat |
| R-08 | Modules use incompatible API contracts, data models, or record statuses. | Medium | High | Agree on the schema, statuses, and API contracts before parallel implementation. Integrate a small complete workflow early and check it after contract changes. | Frontend and backend disagree on fields or unverified records appear in practice. | Samat |
| R-09 | Database failure or a faulty migration causes loss of submissions and review history. | Low | High | Preserve a database snapshot and the evaluation fixtures before the small test or simulation, validate migrations against a test database, and document recovery steps. Plan automated backups and a timed restoration exercise as operational follow-up. Restore the last verified snapshot if recovery is required. | The evaluation snapshot is missing or unreadable, recovery steps are undocumented, or a migration removes expected records. | Samat |
| R-10 | Personal information is exposed through public profiles, datasets, logs, or repository files. | Medium | High | Minimize collected personal information, separate account data from public exports, restrict privileged access, and review exports and commits. Remove exposed information and revoke affected credentials if an incident occurs. | An export contains account details or logs and commits contain confidential values. | Samat |
| R-11 | The small test or simulation does not produce reproducible evidence about the quality model. | Medium | High | Before evaluation, freeze the 100-200 reference-labelled records and define comparison with simple unweighted majority voting without control tasks. Report accuracy, unresolved cases, and Krippendorff's alpha, with an explicit reason when alpha is undefined. Record whether votes come from 5-10 real participants or a simulation, including its fixed seed and assumptions. Measure completion, review time, and usability only with real participants; report missing evidence and sample limitations. | Reference labels or baseline conditions are missing, vote provenance is unclear, or results cannot be reproduced. | Abylaikhan |
| R-12 | Unclear ownership or unavailable team members delay dependent tasks. | Medium | Medium | Assign one accountable owner to each work item, keep progress and blockers in YouTrack, and document setup and handovers. Reassign blocked work during the weekly review. | A mandatory task has no owner or a blocker remains unresolved across reviews. | Samat |

### Data licensing controls for R-01

Wikipedia text commonly uses CC BY-SA 4.0, but the license of each actual source must be checked. Reuse requires compliance with applicable attribution requirements; sharing adapted CC BY-SA material also triggers ShareAlike conditions. A dataset containing adapted source sentences must preserve those obligations. Do not assume that all content from a website has one license, or that collecting different sources automatically makes their licenses compatible.

Before including a source in a downloadable dataset, record its URL, retrieval date, license and version, attribution, modifications, and intended export treatment. Keep unresolved sources out of imports and exports. Apply an explicit contribution agreement to user submissions before accepting content for redistribution.

References:

- [Wikimedia content reuse guidance](https://www.mediawiki.org/wiki/Wikimedia_APIs/Content_reuse)
- [Creative Commons Attribution-ShareAlike 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.en)
- [Creative Commons ShareAlike interpretation](https://wiki.creativecommons.org/wiki/ShareAlike_interpretation)

## 3. Project milestones

The task deadline is 2026-10-23. The initial submission and pre-defense-1 are scheduled for 2026-10-24. Dates for pre-defense-2 and final-pre-defense have not been supplied; those TBD dates must be replaced with the academic schedule before all dated-milestones criteria can be marked complete.

| Milestone | Date | Deliverables and exit criteria | Coordinator |
|---|---|---|---|
| Risks and milestones document | 2026-10-23 | TIL-4 document prepared, reviewed by another team member, and linked from YouTrack; unresolved schedule information recorded. | Ulykbek |
| Initial submission preparation | 2026-10-24 | README, proposal and scope, literature review, system and technology comparisons, initial requirements, diagrams, prototype, evaluation plan, YouTrack planning, and supervisor feedback are collected in the repository. | Samat |
| pre-defense-1 | 2026-10-24 | Initial submission reviewed; required deliverables checked; known limitations recorded; the submitted commit identified by the tag `pre-defense-1`. | Samat |
| pre-defense-2 | TBD - academic date not supplied | Integrated submission, verification, glossary, and daily practice workflows demonstrated; initial results from the small test (5-10 people, 100-200 reference-labelled records) or a clearly labelled simulation available; actual sample sizes and limitations documented; submission tagged `pre-defense-2`. | Samat |
| final-pre-defense | TBD - academic date not supplied | Mandatory requirements verified, evaluation completed against the agreed baseline, documentation and setup instructions finalized, and critical defects resolved; submission tagged `final-pre-defense`. | Samat |

For each defense, provide the repository link, tag, completed work, known limitations, and outstanding tasks. Preserve previous submission tags.

## 4. Task dependencies

The repository documents TIL-1 (repository setup) and TIL-2 (survey template). [TIL-8](https://qosmuratsamat.youtrack.cloud/issue/TIL-8) is the separate user-survey task assigned to Ulykbek; it was reopened and its completion is not confirmed by the template. Survey responses and findings are submitted separately in [PR #8](https://github.com/QosmuratSamat0/tilqor/pull/8) for review; they are not yet part of the reviewed main baseline. This document addresses TIL-4. W-01 through W-10 below are local planning references, not invented YouTrack issue IDs. Map them to actual issues when the implementation backlog is available.

| Work item | Depends on | Reason and completion condition |
|---|---|---|
| TIL-2: survey template | TIL-1: repository setup | The questionnaire must be versioned and available for review. |
| TIL-8: conduct the user survey | TIL-2: survey template | Use the reviewed questionnaire; record real responses and evidence-based findings. |
| TIL-4: risks and milestones | TIL-1: repository setup | Store the document in the repository. Survey findings and confirmed dates trigger later updates. |
| W-01: scope and requirements | TIL-8: survey findings | Draft requirements may start earlier; baseline approval requires separating evidence from assumptions and defining acceptance criteria. |
| W-02: architecture, schema, and API contracts | W-01 | Define components, data ownership, statuses, and interfaces against the agreed requirements. |
| W-03: source licensing and contribution rules | W-01 | Establish permitted source use, attribution, export conditions, and contributor permissions before collecting reusable content. |
| W-04: accounts and data submission | W-02, W-03 | Implement access roles and submissions with the required provenance fields. |
| W-05: review and moderation | W-04 | Review stored submissions, prevent self-approval, handle disputes, and preserve decisions. |
| W-06: terminology glossary | W-05 | Publish accepted entries and keep pending or rejected records out of the accepted glossary. |
| W-07: daily practice catalogue | W-05, W-02 | Display top words, a word of the day, and connector hints from accepted content; do not depend on unverified submissions. Exercises and user-progress tracking are outside scope. |
| W-08: evaluation design and small-test preparation | W-01, TIL-8 | Prepare 100-200 permitted reference-labelled records, the majority baseline, metrics, and measurement procedure; arrange 5-10 participants or document the clearly labelled simulation and fixed seed before evaluation starts. Survey evidence remains separate from evaluation votes. |
| W-09: integration testing and bounded evaluation | W-06, W-07, W-08 | Check the complete workflow and collect reproducible results from the small test or clearly labelled simulation. Report actual people and record counts, vote provenance, unresolved cases, accuracy against reference labels, agreement, and limitations. |
| W-10: final evaluation and defense materials | W-09 | Analyze measured results, document limitations, and prepare the final submission. |

Critical implementation sequence: W-01 -> W-02 -> W-04 -> W-05 -> W-06/W-07 -> W-09 -> W-10. W-03 must finish before collecting reusable content; W-08 can proceed alongside implementation once requirements and survey findings are available.

## 5. Responsibility allocation

The [proposal](proposal.md) identifies Samat as Tech lead, architect; Alpamys as Analyst, UX lead and developer; and Ulykbek as Requirements and research lead, developer. Ulykbek owns TIL-4 and TIL-8, and Alpamys owns TIL-16 (README), as confirmed in the TIL-4 PR review. The implementation and evaluation allocations marked Proposed below remain subject to team agreement. Each actual issue must have one accountable owner; another team member reviews the work before merging.

| Team member | Responsibility | Deliverables / work items | Assignment status |
|---|---|---|---|
| Dovutbekov Ulykbek | Risk management and milestone planning | TIL-4, risk updates, dependency tracking, and schedule updates | Confirmed by TIL-4 |
| Dovutbekov Ulykbek | User survey | [TIL-8](https://qosmuratsamat.youtrack.cloud/issue/TIL-8): collect real responses and document verified findings separately from assumptions | Assigned to Ulykbek in YouTrack; task reopened |
| Kosmurat Samat | Tech lead, architect | Architecture, data quality model, DevOps, optional AI features, repository and YouTrack | Role defined in proposal |
| Alpamys Abylaikhan | Project README | [TIL-16](https://qosmuratsamat.youtrack.cloud/issue/TIL-16): maintain the README and its required project information | Assigned to Alpamys in YouTrack |
| Kosmurat Samat | Backend, integration, and release coordination | W-02, W-04; integration support for W-09; deployment, backups, and submission tags | Proposed |
| Alpamys Abylaikhan | Interface and evaluation | UI and prototype work; W-07 interface; W-08 and evaluation reporting in W-10 | Proposed |
| Dovutbekov Ulykbek | Data governance, verification, and glossary | W-03, W-05, W-06; moderation rules and data quality checks | Proposed |
| Konstantin N. Latuta | Supervisor feedback | Review scope, requirements, major decisions, and defense readiness; feedback recorded by the team | Supervisor identified in README; checkpoints to agree |

Samat coordinates W-01 with input from all three students. Work on shared workflows remains collaborative; the accountable owner coordinates completion and review.

## 6. Review and outstanding confirmations

Review risks and dependencies weekly, before each defense, and after changes to scope, data sources, architecture, or team availability. Update ratings and responses using observed evidence; link material changes to YouTrack tasks and reviewed repository changes.

Before closing all TIL-4 acceptance criteria:

- Obtain and enter the dates of `pre-defense-2` and `final-pre-defense`; `pre-defense-1` is confirmed for 2026-10-24.
- Confirm the proposed responsibility allocation with the team and reflect it in YouTrack.
- Replace local work references with YouTrack IDs as the corresponding issues become available.
- Obtain a team review of this document and link the resulting PR or commit in TIL-4.
