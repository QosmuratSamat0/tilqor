# Technology comparison

Task: TIL-5.

This document compares alternatives for the key technical decisions of the project and explains each choice by the project needs.

## 1. Project needs that drive the choice

The needs below come from the proposal ([`proposal.md`](proposal.md)). Once the requirements (TIL-11) are merged, each need will be linked to its requirement ID.

| ID | Need | Source in the proposal |
|---|---|---|
| N1 | Relational data with many links: User, SourceSentence, Task, Contribution, Review, Term | §7 Roles and data |
| N2 | Consistent voting: a vote, the weighted decision, the record status and the reviewer weight must change together, without race conditions | §8 Decision rule, reviewer weight |
| N3 | Roles and permissions: participant, reviewer, moderator/admin | §7 Roles and data |
| N4 | A moderator interface for disputed records, without building a separate admin app | §8 Decision rule (moderator decides) |
| N5 | Dictionary search by term and variants | §7 Module 3 |
| N6 | Export of accepted records to CSV and JSON | §7 Module 4 |
| N7 | Quality metrics (Krippendorff's alpha, comparison with a baseline) computed from the stored votes | §8 Agreement metric, §9 |
| N8 | A web interface with interactive screens: blind translation, random order of variants, voting | §7 Module 1 |
| N9 | Realistic scope for a team of three before the final pre-defense; reproducible setup with Docker and CI | §12 |

Rating scale in the tables: **++** strong fit, **+** fit, **±** possible with extra work, **−** weak fit.

## 2. Decision 1: server platform

Options: **Django + Django REST Framework (Python)**, **FastAPI (Python)**, **Node.js with Express or NestJS (JavaScript / TypeScript)**.

| Criterion | Django + DRF | FastAPI | Node.js (Express / NestJS) |
|---|---|---|---|
| Built-in ORM and migrations (N1) | ++ built in | ± separate libraries (e.g. SQLAlchemy, Alembic) | ± separate libraries (e.g. Prisma, TypeORM) |
| Database transactions for voting (N2) | ++ transaction support in the ORM | + through the chosen ORM | + through the chosen ORM |
| Authentication, roles, permissions (N3) | ++ built in, plus DRF permissions | ± assembled from libraries | ± assembled from libraries |
| Ready-made admin interface (N4) | ++ Django admin | − none built in | − none built in |
| Data analysis for metrics (N7) | ++ Python ecosystem (e.g. pandas, a Krippendorff's alpha package) | ++ same Python ecosystem | ± fewer libraries for statistics |
| Amount of code the team must write (N9) | ++ least: many parts are built in | + more glue code | + more glue code |
| Async performance under high load | + enough for the expected load | ++ designed for async | ++ designed for async |

**Choice: Django + DRF.** The project is data-heavy and needs an ORM, migrations, transactions, roles and a moderator interface (N1–N4). Django has all of them built in, so the team spends time on the quality model, not on infrastructure (N9). FastAPI and Node.js are faster for highly concurrent APIs, but this project is not expected to have such a load, and that advantage does not outweigh the missing admin and auth.

## 3. Decision 2: data storage

Options: **PostgreSQL**, **MySQL**, **MongoDB**.

| Criterion | PostgreSQL | MySQL | MongoDB |
|---|---|---|---|
| Relational model with foreign keys (N1) | ++ | ++ | − document model; links are handled in code |
| Transactions and constraints for consistent voting (N2) | ++ | ++ (InnoDB) | + multi-document transactions exist but are not the main model |
| Fuzzy and text search for the dictionary (N5) | ++ full-text search and trigram search (`pg_trgm`) | + full-text search | + text indexes |
| Flexible fields (e.g. task metadata) | ++ `JSONB` | + `JSON` type | ++ native documents |
| Export and analytics with SQL (N6, N7) | ++ | ++ | ± aggregation pipeline instead of SQL |
| Support in Django | ++ best supported, plus PostgreSQL-specific fields in `django.contrib.postgres` | ++ supported | − not supported by Django out of the box; needs a separate third-party backend |

**Choice: PostgreSQL.** The data is relational and the voting needs transactions and constraints (N1, N2), which rules out MongoDB as the main store. Between PostgreSQL and MySQL, PostgreSQL adds trigram search for the dictionary (N5), `JSONB` for flexible task data and the PostgreSQL-specific features in Django.

## 4. Decision 3: interaction between components

Options: **REST API (DRF) + single-page frontend**, **GraphQL API + single-page frontend**, **server-rendered pages (Django templates) without a separate frontend**.

| Criterion | REST API + SPA | GraphQL + SPA | Server-rendered templates |
|---|---|---|---|
| Interactive screens: blind translation, voting without reload (N8) | ++ | ++ | ± possible with extra JavaScript |
| Fit with Django (N9) | ++ DRF is the standard for Django | ± needs an extra library (e.g. Graphene or Strawberry) | ++ built in |
| Simple and clear endpoints for tasks, votes, dictionary, export (N1, N6) | ++ | + one endpoint, more flexible queries, more complex setup | + |
| Export as files (CSV / JSON) (N6) | ++ plain HTTP download endpoints | ± files are usually served outside GraphQL anyway | ++ |
| Easy to test and document | ++ standard HTTP tests, OpenAPI | + | + |
| Separation of frontend and backend work in the team | ++ | ++ | − one codebase for both |
| Amount of work (N9) | + two parts | − two parts plus GraphQL schema | ++ least |

**Choice: REST API (DRF) + single-page frontend.** The core screens are interactive (N8), so a separate frontend gives a better experience than server-rendered pages. REST is the standard way to build an API with Django and is easy to test, while GraphQL adds complexity that the project does not need: the data is accessed in a few predictable ways (tasks, votes, dictionary, export).

## 5. Decision 4 (preliminary): frontend

The frontend is planned as **Vite + React**. This decision is **preliminary** and will be confirmed after the requirements and the prototype are reviewed.

| Criterion | Vite + React | Vite + Vue | Django templates + HTMX |
|---|---|---|---|
| Interactive screens (N8) | ++ | ++ | + |
| Ecosystem and examples | ++ | + | + |
| Works with the REST API from Decision 3 | ++ | ++ | − follows a different approach |

## 6. Supporting tools

These are not alternatives under comparison, but part of the chosen stack:

- **Docker / Docker Compose:** the same environment for every team member and for the demo (N9).
- **GitHub Actions:** CI that runs tests on every pull request (N9).

## 7. Summary

| Decision | Choice | Main reasons |
|---|---|---|
| Server platform | Django + DRF | ORM, migrations, transactions, auth and admin built in (N1–N4, N9) |
| Data storage | PostgreSQL | Relational data, transactions, trigram search, JSONB (N1, N2, N5) |
| Component interaction | REST API + SPA | Interactive screens, standard for Django, easy to test (N6, N8) |
| Frontend (preliminary) | Vite + React | Interactive UI over the REST API (N8) |

## 8. Limitations of this comparison

- The comparison is qualitative: no benchmarks were run.
- Need IDs (N1–N9) will be replaced with requirement IDs from TIL-11.
- The frontend choice is preliminary.
