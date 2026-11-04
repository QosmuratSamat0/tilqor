# Architecture decision records

An ADR is a short note about one decision: the context, what was decided, and what follows from it.
It explains *why* the code looks the way it does. ADRs are not rewritten: a changed decision gets a new ADR
that supersedes the old one.

## How to add one
1. Copy [`0000-template.md`](0000-template.md) to `NNNN-short-title.md` with the next number.
2. Fill it in; link the source (requirement, document, task or PR). Do not record decisions that were not taken.
3. Add it to the table below in the same PR as the change it describes.

## Records

| # | Decision | Status | Date |
|---|---|---|---|
| [0001](0001-technology-stack.md) | Django + DRF, PostgreSQL, REST API with a single-page frontend | Accepted | 2026-10-22 |
| [0002](0002-app-layering.md) | Layers inside a Django app: domain, services, selectors, api | Accepted | 2026-10-31 |
| [0003](0003-role-based-permissions.md) | The user role is the single source of Tilqor permissions | Accepted | 2026-10-31 |
| [0004](0004-session-csrf-authentication.md) | Cookie session + CSRF authentication for the API | Accepted; amended by 0006 | 2026-10-29 |
| [0005](0005-fr06-moved-to-til23.md) | FR-06 (contributor permission) is implemented in TIL-23, not TIL-22 | Accepted | 2026-11-02 |
| [0006](0006-frontend-on-github-pages.md) | Frontend on GitHub Pages with a same-site API subdomain | Accepted | 2026-11-04 |
