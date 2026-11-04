# 0004. Cookie session + CSRF authentication for the API

- **Status:** Accepted; amended by [0006](0006-frontend-on-github-pages.md)
- **Date:** 2026-10-29
- **Source:** NFR-03; TIL-20 (PR #17), `REST_FRAMEWORK` and cookie settings in `config/settings.py`

## Context
NFR-03 requires that browser authentication material is not readable by client scripts and that
state-changing cookie-authenticated requests without valid CSRF protection are denied.
The frontend is served to a browser (ADR 0001).

## Decision
- DRF uses `SessionAuthentication` only; the default permission is `IsAuthenticated`.
- Session cookie: `HttpOnly`, `SameSite=Lax`, `Secure` outside debug. CSRF cookie: `SameSite=Lax`, `Secure` outside debug.
- Every state-changing request sends the CSRF token.

## Consequences
- No tokens are stored in browser JavaScript.
- The frontend must read the CSRF token and send it in the `X-CSRFToken` header.
- Public endpoints (health, and later the schema) set `AllowAny` explicitly.
