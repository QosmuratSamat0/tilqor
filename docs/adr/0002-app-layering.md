# 0002. Layers inside a Django app: domain, services, selectors, api

- **Status:** Accepted
- **Date:** 2026-10-31
- **Source:** TIL-21 (PR #18), applied again in TIL-22 (PR #19)

## Context
The quality model (weighted decision, reputation, control tasks) must be tested on many exact cases
and must stay consistent under concurrent votes (NFR-02). Putting it in views or models mixes rules,
database access and HTTP.

## Decision
Each app with business logic is split into:

| Layer | Contains | May use |
|---|---|---|
| `models.py` | tables and DB constraints | Django |
| `domain/` | pure rules on plain data | Python only, **no Django imports** |
| `services/` | one function per use case, `transaction.atomic`, row locks | models, domain |
| `selectors/` | read queries | models, domain |
| `api/` | serializers, thin views: validate → call → respond | services, selectors |

Services raise typed exceptions that carry an HTTP status (`400` / `403` / `409`); views turn them into responses.
In `contributions` the exception also names the affected field (FR-07).

## Consequences
- Rules are unit-tested without the database; API tests check permissions and wiring.
- Views stay short; a new interface (admin action, command) reuses the same services.
- More files per app; each file is kept under about 300 lines.
