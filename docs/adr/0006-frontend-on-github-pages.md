# 0006. Frontend on GitHub Pages with a same-site API subdomain

- **Status:** Accepted
- **Date:** 2026-11-04
- **Source:** [TIL-34](https://qosmuratsamat.youtrack.cloud/issue/TIL-34), stage 2;
  amends [0004](0004-session-csrf-authentication.md)

## Context
The React SPA needs free static hosting under the project's own domain. The existing small EC2
server continues to run Django, PostgreSQL and Caddy. Separate frontend and backend hosting
creates different origins, while authentication still uses cookie sessions and CSRF protection.

## Decision
Host the SPA at `https://tilqor.samatk.me` on GitHub Pages and the API at
`https://api.tilqor.samatk.me` behind the existing Caddy reverse proxy. These HTTPS origins are
same-site, so requests use `credentials: "include"` and cookies keep `SameSite=Lax`.

Allow credentialed CORS only from the frontend origin and trust both origins for CSRF.
Set the readable CSRF cookie domain to `.tilqor.samatk.me`; keep the session cookie host-only,
`HttpOnly` and `Secure`. Frontend requests and export links share a build-time API base URL.

Alternatives considered:

- Serve `dist` through Caddy on EC2: retains same-origin requests, but couples static hosting
  and releases to the server. Pages supplies free static hosting and independent frontend releases.
- Keep an sslip.io API with the custom frontend domain: creates cross-site cookies and would
  require different cookie policies subject to third-party cookie restrictions. Rejected.

## Consequences
- CORS, CSRF trusted origins and the shared CSRF cookie domain must match the deployment.
- Frontend changes deploy automatically after merging to `main`; backend deployments stay manual.
- The Pages build embeds the repository variable `VITE_API_BASE_URL`. Changing it requires a rebuild.
- Pages uses a copy of `index.html` as `404.html` for SPA deep links. These pages render the SPA
  but retain an HTTP 404 status on direct navigation.
- DNS and certificates for both domains must be configured before switching; the old sslip.io
  address is retired after the switch. The server continues to serve API docs and Django admin.
- Number 0006 was available and is used here; the planned TIL-26 evaluation ADR takes the next
  available number.
