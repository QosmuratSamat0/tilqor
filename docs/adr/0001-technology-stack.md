# 0001. Django + DRF, PostgreSQL, REST API with a single-page frontend

- **Status:** Accepted
- **Date:** 2026-10-22
- **Source:** [Technology comparison](../tech-comparison.md) (TIL-5)

## Context
The project is data-heavy: it needs an ORM, migrations, transactions, roles and a moderator interface.
Voting needs transactions and constraints; the dictionary needs text search. The core screens are interactive.

## Decision
- Server: **Django + Django REST Framework**.
- Storage: **PostgreSQL**.
- Interaction: **REST API (DRF) + a single-page frontend**.

The criteria and the compared options (FastAPI, Node.js; MySQL, MongoDB; GraphQL, server-rendered pages)
are in the technology comparison.

## Consequences
- Django admin is used as the moderator and administrator interface.
- The team works on the quality model instead of infrastructure.
- The frontend is a separate application that talks to the API only.
