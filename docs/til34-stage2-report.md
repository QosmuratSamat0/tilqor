# TIL-34 stage 2 implementation report

Date: 2026-11-04. Branch: `TIL-34-pages`.

Prepared the SPA for `https://tilqor.samatk.me` on GitHub Pages and the existing EC2 API for
`https://api.tilqor.samatk.me`. No push, PR, workflow run, server operation, DNS change or GitHub
settings change was performed.

- Backend: pinned `django-cors-headers==4.9.0`, placed its middleware first, added an environment
  allowlist, credentialed CORS and an optional CSRF cookie domain. An empty allowlist keeps
  cross-origin access off locally. Session cookies stay host-only, HttpOnly and SameSite=Lax;
  production cookies remain Secure. No API view or authentication logic changed.
- Frontend: shared `apiUrl()` uses build-time `VITE_API_BASE_URL` for requests and both export
  links; an empty base retains the Vite proxy. Fetch includes credentials and preserves the
  existing CSRF header logic.
- Pages: follows the owner's `short-url` workflow, uses Node 22 and npm cache, builds only frontend
  artifacts, copies `index.html` to `404.html`, and deploys automatically on relevant main pushes.
  The backend Deploy workflow remains manual.
- Server files: production example uses the API domain. `init-env.sh` accepts `API_HOST`, retains
  its IP/sslip.io fallback, and never overwrites `.env`. Caddy proxy logic is unchanged.
- Architecture: ADR 0006 was free and is used for this decision; ADR 0004 is amended in its header.
  The planned TIL-26 evaluation ADR must take the next available number.

The stable CORS version and built-in `x-csrftoken` allow-header were checked against the
[package metadata](https://pypi.org/project/django-cors-headers/4.9.0/).

## Verification

Commands ran locally on Windows with PowerShell (`npm.cmd` avoids the machine's script execution
policy). The installed Node version is 24.20.0; the Pages workflow selects Node 22.

Frontend command sequence, with the build-time environment variable set in PowerShell:

```powershell
cd src/frontend
npm.cmd ci
npm.cmd run lint
npm.cmd run typecheck
npm.cmd test -- --run
$env:VITE_API_BASE_URL='https://api.tilqor.samatk.me'
npm.cmd run build
```

Actual output:

```text
added 269 packages, and audited 270 packages in 49s

65 packages are looking for funding
  run `npm fund` for details

13 moderate severity vulnerabilities

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.

> tilqor-frontend@0.1.0 lint
> eslint .

> tilqor-frontend@0.1.0 typecheck
> tsc --noEmit

> tilqor-frontend@0.1.0 test
> vitest --run

 RUN  v5.1.0 C:/Users/qosmu/tilqor/src/frontend

 Test Files  10 passed (10)
      Tests  27 passed (27)
   Start at  22:47:04
   Duration  13.16s (environment 66%, setup 11%, tests 8%, import 7%, transform 7%, worker 1%)

> tilqor-frontend@0.1.0 build
> tsc --noEmit && vite build

vite v8.3.5 building client environment for production...
transforming...
✓ 130 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.49 kB │ gzip:   0.36 kB
dist/assets/index-Bwd4uohP.css   27.24 kB │ gzip:   4.62 kB
dist/assets/index-DI3RnrNO.js   380.26 kB │ gzip: 117.03 kB

✓ built in 882ms
```

The npm audit notice comes from the existing dependency lockfile; frontend dependencies were
not changed in this task.

`make check` ran through the installed GNU make executable. Actual output (progress dots omitted):

```text
.venv\Scripts\python.exe -m ruff check src/backend tests
All checks passed!
.venv\Scripts\python.exe src/backend/manage.py makemigrations --check --dry-run
No changes detected
.venv\Scripts\python.exe -m pytest -q
237 passed in 359.50s (0:05:59)
```

OpenAPI validation also exited successfully with no output:
`python src/backend/manage.py spectacular --validate --fail-on-warn --file .venv/til34-schema.yml`.

Local cross-origin check used `docker compose up -d --build db backend`, a Vite build with
`VITE_API_BASE_URL=http://localhost:8000`, and Vite preview on port 4173. Playwright drove the
installed Chrome against the real API with a temporary test user and translation task.
The local `.env` temporarily enabled the three localhost host/origin settings from the task,
debug HTTP cookies and an empty CSRF cookie domain. No network request was mocked.

Actual browser-check output:

```text
PASS register via browser: HTTP 201, credentialed CORS
PASS browser cookies: session HttpOnly + Lax; CSRF readable on localhost
PASS sign out via browser: HTTP 204
PASS sign in via browser: HTTP 200
PASS open task and submit translation via browser: HTTP 201
POST /api/tasks/<fixture>/contributions/ response headers:
Access-Control-Allow-Origin: http://localhost:4173
Access-Control-Allow-Credentials: true
PASS reload /tasks/<fixture>: task and authenticated session retained
PASS reload /tasks deep link
PASS CSV export via browser: dataset.csv, 558 bytes
PASS no browser JavaScript errors
```

The POST sent the readable CSRF cookie in `X-CSRFToken`. Browser checks confirmed that JavaScript
could not read the session cookie. The initial harness attempt used an incorrect language-button
selector; it was corrected before the successful full run, without changing application code.

Cleanup and restoration output:

```text
Local smoke-test fixtures removed
PASS original local .env restored byte-for-byte
Local backend recreated with restored configuration and stopped
PASS restored local backend configuration: CORS off, host-only CSRF cookie
```

The local database container was also stopped, matching the initial stopped state. The frontend
was rebuilt with the production API URL after the browser check. The requested command
`grep -o "api.tilqor.samatk.me" src/frontend/dist/assets/*.js | head -1` ran through Git Bash:

```text
api.tilqor.samatk.me
```

The workflow's fallback-copy step was repeated locally and checked:

```text
PASS Pages fallback: dist/404.html is byte-identical to dist/index.html
```

`dist/`, `.venv/`, browser-check logs and screenshots remain ignored local artifacts. Changed
tracked files use LF, and `git diff --check` passed. No `.env`, CNAME, robots file or node_modules
was added to the commits.

Additional checks passed: Pages workflow YAML structure and triggers; Bash syntax; isolated
`init-env.sh` runs for `api.tilqor.samatk.me`, a custom API host and an unset host/IP fallback.
Every initializer run also verified that a second run preserves the existing `.env` byte-for-byte.

## Owner checklist (not performed)

Configure Pages and the repository variable before the first automatic Pages build; run the
backend Deploy after merging this branch.

1. DNS at the `samatk.me` registrar: `CNAME tilqor → qosmuratsamat0.github.io`,
   `A api.tilqor → 63.181.85.65`.
2. Repository **Settings → Pages**: Source = **GitHub Actions**, Custom domain = `tilqor.samatk.me`;
   enable **Enforce HTTPS** after certificate issuance.
3. Repository **Settings → Secrets and variables → Actions → Variables**:
   `VITE_API_BASE_URL=https://api.tilqor.samatk.me` (variable, not secret).
4. Preserve secrets and database settings in the server's existing `~/tilqor/.env`, and set:

   ```dotenv
   SITE_ADDRESS=api.tilqor.samatk.me
   DJANGO_ALLOWED_HOSTS=api.tilqor.samatk.me
   DJANGO_CSRF_TRUSTED_ORIGINS=https://tilqor.samatk.me,https://api.tilqor.samatk.me
   DJANGO_CORS_ALLOWED_ORIGINS=https://tilqor.samatk.me
   DJANGO_CSRF_COOKIE_DOMAIN=.tilqor.samatk.me
   ```

   Run **Actions → Deploy → Run workflow** for `main`; Caddy obtains a new certificate.
5. Check API `/api/health/`, `/api/docs/`, `/admin/`; on the frontend, register, sign in, reload
   `/tasks`, submit a translation and download CSV. Retire `63.181.85.65.sslip.io` after switching.

Production DNS, certificate issuance, GitHub Pages hosting and production authentication still
require the owner's rollout. Direct SPA deep links on Pages render through `404.html` and retain
HTTP 404 status. See the [deployment guide](deploy.md) for repeatable local and production steps.
