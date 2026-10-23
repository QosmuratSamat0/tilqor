# Architecture

Task: [TIL-6](https://qosmuratsamat.youtrack.cloud/issue/TIL-6). Status: **draft** for pre-defense-1.

This document describes the components of Tilqor and how data flows between them. It is based on the [proposal](proposal.md), the [technology comparison](tech-comparison.md) and the requirements (TIL-11, `requirements.md`).

## 1. Diagrams

| Diagram | Source (editable) | Image |
|---|---|---|
| System context | [`context.puml`](../diagrams/src/context.puml) | [`context.png`](../diagrams/png/context.png) |
| Use cases | [`use-case.puml`](../diagrams/src/use-case.puml) | [`use-case.png`](../diagrams/png/use-case.png) |
| Components (draft) | [`components.puml`](../diagrams/src/components.puml) | [`components.png`](../diagrams/png/components.png) |

Sources are written in PlantUML. To regenerate the images:

```bash
docker run --rm -v "$PWD/diagrams:/data" plantuml/plantuml -tpng -o /data/png /data/src/*.puml
```

## 2. System context

Tilqor is one web system. Five kinds of people use it:

- **Visitor:** browses the dictionary and the daily catalogue, downloads accepted data.
- **Participant:** submits translations and term variants.
- **Reviewer:** reviews other people's contributions and answers control tasks.
- **Moderator / admin:** resolves disputes, manages tasks, roles and quality settings.
- **NLP researcher:** uses the exported dataset; in the system this is a visitor who downloads data.

External systems:

- **Sentence sources** (for example Tatoeba or OPUS): Russian source sentences are imported with their licence and attribution (FR-06). Licences must be checked before import (risk R-01).
- **AI service** (optional, FR-23): near-duplicate suggestions only. It can be disabled and never accepts or rejects data.

## 3. Components

The system has three parts: a single-page frontend, a Django backend and a PostgreSQL database. They communicate through a REST API with JSON over HTTPS ([technology comparison](tech-comparison.md), Decision 3).

| Component | Responsibility | Requirements |
|---|---|---|
| Frontend SPA (Vite + React, preliminary) | Task, translation, review, dictionary and catalogue screens | FR-03 – FR-05, FR-08 – FR-10, FR-17 – FR-19 |
| REST API (DRF) | Single entry point; authentication and permission checks on the server | FR-01, FR-02, NFR-03 |
| Accounts and roles | Registration, sign-in, roles: participant, reviewer, moderator/admin | FR-01, FR-02 |
| Tasks and contributions | Tasks by domain and type, blind submission, term variants, versions, status of own submissions | FR-03 – FR-08, FR-13 |
| Automatic checks | Length, duplicates, Kazakh letters, Russian connectors | FR-07 |
| Verification engine: review queue | Gives versions to independent reviewers, escalates after 5 votes | FR-09, FR-10, FR-12 |
| Verification engine: decision rule | Weighted share ≥ 0.66 and at least 2 people | FR-11 |
| Verification engine: reputation and control tasks | Weight updates, control tasks with known answers | FR-14, FR-15 |
| Verification engine: settings | Versioned thresholds and weight values | FR-24 |
| Dictionary and daily catalogue | Search, recommended variant, top words, word of the day, connector hints; accepted records only | FR-17 – FR-19 |
| Export | CSV and JSON of accepted, permission-cleared records with licence metadata | FR-20, NFR-12 |
| Admin and moderation (Django admin) | Escalated records, tasks, withdrawal, roles and settings | FR-12, FR-21, FR-24 |
| Evaluation command | Compares the weighted model with a simple majority baseline; Krippendorff's alpha | FR-25, FR-26 |
| Near-duplicate suggestions (optional) | Calls the optional AI service | FR-23 |
| PostgreSQL | Users, sentences, tasks, contribution versions, reviews, terms, settings, audit data | NFR-01, NFR-02 |

## 4. Main data flow

1. A participant opens a task and submits a translation or term variant. The frontend sends it to the REST API.
2. **Automatic checks** reject empty, too long or duplicate text and warn about missing Kazakh letters or Russian connectors (FR-07). The contribution is stored as a new **version** with status `submitted`.
3. The **review queue** gives the version to reviewers who are not its author (FR-09). Control tasks are mixed in without being marked (FR-15).
4. After each counted vote from the 3rd to the 5th, the **decision rule** computes the weighted shares. A decision is made only if one share is ≥ 0.66 and at least 2 people voted for it (FR-11). The vote, the decision, the record status and the reputation update are saved in **one database transaction** (NFR-02).
5. If there is still no decision after 5 votes, the record goes to a **moderator** (FR-12).
6. An `accepted` version becomes visible in the **dictionary** and the **daily catalogue** and can be **exported** if its licence metadata is resolved (FR-17 – FR-20). A `needs_edit` version can be edited, which creates a new version with no inherited votes (FR-13).

Record statuses: `submitted` → `in_review` → `accepted`, `rejected` or `needs_edit`.

## 5. Consistency between requirements, use cases and components

| Use case (use-case diagram) | Requirements | Component |
|---|---|---|
| Register and sign in | FR-01 | Accounts and roles |
| Choose a task | FR-03 | Tasks and contributions |
| Translate a sentence (blind) | FR-04, FR-07 | Tasks and contributions, Automatic checks |
| Choose or suggest a term variant | FR-05, FR-07 | Tasks and contributions, Automatic checks |
| See the status of own submissions | FR-08 | Tasks and contributions |
| Edit a version marked `needs_edit` | FR-13 | Tasks and contributions |
| Review a contribution | FR-09, FR-10 | Review queue |
| Answer a control task | FR-15 | Reputation and control tasks |
| Weighted decision and reputation update | FR-11, FR-14 | Decision rule, Reputation and control tasks |
| Resolve an escalated record | FR-12 | Admin and moderation, Review queue |
| Manage tasks and withdraw content | FR-21 | Admin and moderation |
| Manage roles and settings | FR-02, FR-24 | Admin and moderation, Settings |
| Search the dictionary | FR-17, FR-18 | Dictionary and daily catalogue |
| View the daily catalogue | FR-19 | Dictionary and daily catalogue |
| Download accepted data | FR-20 | Export |
| Run the evaluation | FR-25, FR-26 | Evaluation command |

Requirements not shown as separate use cases: FR-06 (provenance metadata, part of submission and import), FR-16 (audit history, stored by the verification engine), FR-22 (points and ranking, Should), FR-23 (optional AI) and the non-functional requirements.

## 6. Open points of this draft

- The frontend technology is preliminary (technology comparison, Decision 4).
- Deployment (Docker Compose services, CI pipeline) will be added to the component diagram after the first runnable version.
- Requirement IDs refer to the TIL-11 pull request; if IDs change during its review, this document must be updated.
