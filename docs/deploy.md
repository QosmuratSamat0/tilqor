# Deployment (TIL-34)

The frontend runs on GitHub Pages; EC2 hosts the API, Swagger UI and Django admin.
Stage 2 (TIL-34) prepares the domain switch described in the owner checklist below.

| Part | Choice |
|---|---|
| Server | AWS EC2 t3.small (2 GB) or Lightsail, Ubuntu 24.04 LTS, Frankfurt, static IPv4 (Elastic IP) |
| Size | 2 GB RAM + 2 GB swap for stage 1; 2 vCPU / 4 GB for the NFR-05 load test (TIL-35) |
| Stack | [`docker-compose.prod.yml`](../docker-compose.prod.yml): PostgreSQL 16, Django + gunicorn ([`Dockerfile.prod`](../src/backend/Dockerfile.prod)), Caddy |
| Image | built by GitHub Actions, stored in GHCR as `ghcr.io/qosmuratsamat0/tilqor-backend:<commit-sha>` |
| HTTPS | Caddy gets a Let's Encrypt certificate and redirects HTTP to HTTPS (NFR-03) |
| Address | Frontend `https://tilqor.samatk.me`; API `https://api.tilqor.samatk.me` after the owner switches DNS and configuration |
| Backups | [`deploy/backup.sh`](../deploy/backup.sh) daily from cron, 14 days kept (NFR-06) |

The server keeps **no source code**. It has Docker, a GHCR login, and `~/tilqor` with the compose file,
`deploy/` and `.env`, all written by the Deploy workflow.

## 1. Prepare the server (once)
Firewall (EC2 security group): SSH (22) from anywhere (GitHub Actions runners change IPs; login is key-only),
HTTP (80) and HTTPS (443) from anywhere. Then on the server:

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-v2
sudo usermod -aG docker ubuntu        # log out and in again
docker login ghcr.io -u <github-user>  # token with read:packages, so the server can pull the private image
```

Deploy key for GitHub Actions (a separate key, not a personal one):

```bash
ssh-keygen -t ed25519 -N "" -C github-deploy -f ~/.ssh/github_deploy
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys
cat ~/.ssh/github_deploy               # copy into the DEPLOY_SSH_KEY secret, then: rm ~/.ssh/github_deploy
```

## 2. GitHub secrets (once)
**Settings → Secrets and variables → Actions**, added by the repository owner, never committed:

| Secret | Value |
|---|---|
| `DEPLOY_HOST` | the server's static IP |
| `DEPLOY_USER` | `ubuntu` |
| `DEPLOY_SSH_KEY` | the private deploy key from step 1 |

`GITHUB_TOKEN` (push to GHCR) is provided by GitHub automatically.

## 3. Deploy: manual button
Backend deploys never run automatically. **Actions → Deploy → Run workflow** (branch: normally `main`) runs
[`deploy.yml`](../.github/workflows/deploy.yml):

1. build the image and push `tilqor-backend:<commit-sha>` to GHCR;
2. copy `docker-compose.prod.yml` and `deploy/` to `~/tilqor` on the server;
3. [`deploy/init-env.sh`](../deploy/init-env.sh): on the first deploy only, create `.env` with secrets generated on the server;
4. [`deploy/deploy.sh <sha>`](../deploy/deploy.sh): pull the image, restart, wait up to 3 minutes for `/api/health/`; the job fails otherwise.

`init-env.sh` never overwrites an existing `.env`. For a fresh server with the new API domain,
run `API_HOST=api.tilqor.samatk.me ./deploy/init-env.sh` from `~/tilqor` before the first Deploy.
Without `API_HOST`, it keeps the stage 1 `<public-ip>.sslip.io` fallback with cross-origin settings off.
For an existing server, update `.env` using the owner checklist instead.

The button appears only after `deploy.yml` is on `main`.

After the first deploy, create the administrator on the server:

```bash
cd ~/tilqor && docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

Check: `https://<site>/api/health/` returns `{"status": "ok", "database": "ok"}`;
`https://<site>/api/docs/` and `https://<site>/admin/` open; `http://<site>/` redirects to HTTPS.

Rollback: `~/tilqor/deploy/deploy.sh <older-sha>` on the server (tags are listed on the GHCR package page).

## 4. Backups
```bash
mkdir -p ~/backups
crontab -e
# add:
0 3 * * * /home/ubuntu/tilqor/deploy/backup.sh >> /home/ubuntu/backups/backup.log 2>&1
```

Off-server copy: download the latest file to a team computer, for example
`scp -i <key.pem> ubuntu@<ip>:~/backups/tilqor-*.sql.gz .`

## 5. Restore test (NFR-06)
Restore into a new empty database, record the time and row counts, then remove it:

```bash
~/tilqor/deploy/restore.sh ~/backups/<file>.sql.gz tilqor_restore_test
cd ~/tilqor && docker compose -f docker-compose.prod.yml exec db sh -c 'dropdb -U "$POSTGRES_USER" tilqor_restore_test'
```

Restoring over the live database: stop the backend, drop and recreate the `tilqor` database,
restore with `restore.sh` into `tilqor`, start the backend again.

## Frontend (GitHub Pages)

[`pages.yml`](../.github/workflows/pages.yml) builds on pushes to `main` that change `src/frontend/**`
or the Pages workflow itself; it also has a manual `workflow_dispatch` trigger. It uses Node 22,
`npm ci` and `npm run build`, then uploads `src/frontend/dist` and deploys to the `github-pages`
environment. Backend releases remain on the manual **Deploy** button.

The build reads the repository **variable** `VITE_API_BASE_URL=https://api.tilqor.samatk.me`.
It is public configuration embedded in the bundle, not a secret. Changing the variable requires
another Pages build. In development leave it empty: requests stay relative and use the existing
Vite `/api` proxy. Both API requests and CSV/JSON export links use the same URL helper.

The workflow copies `dist/index.html` to `dist/404.html` so direct visits to SPA routes such as
`/tasks` render the application (GitHub Pages still returns HTTP 404 for these fallback responses).
No `CNAME` file is needed with the Actions source; set the custom domain in Pages settings.

The two HTTPS origins share the site `samatk.me`. Fetch includes credentials and the API allows
credentialed CORS only for the frontend origin. The CSRF cookie uses `.tilqor.samatk.me` so the
frontend can read it and send `X-CSRFToken`; the session cookie remains host-only on the API,
`HttpOnly`, `Secure`, `SameSite=Lax`. See [ADR 0006](adr/0006-frontend-on-github-pages.md).

### Owner checklist

These changes are performed by the owner; repository work does not change DNS, server
configuration or GitHub settings. Configure Pages and the repository variable before the first
Pages build (normally triggered by merging to `main`); run the backend Deploy after merging.

1. At the `samatk.me` registrar, set `CNAME tilqor → qosmuratsamat0.github.io` and
   `A api.tilqor → 63.181.85.65`.
2. Repository **Settings → Pages**: Source = **GitHub Actions**, Custom domain = `tilqor.samatk.me`;
   enable **Enforce HTTPS** after the certificate is issued.
3. Repository **Settings → Secrets and variables → Actions → Variables**:
   `VITE_API_BASE_URL=https://api.tilqor.samatk.me`. Set it before the first Pages build.
4. Update the existing server `~/tilqor/.env` (preserve its secrets and database settings):

   ```dotenv
   SITE_ADDRESS=api.tilqor.samatk.me
   DJANGO_ALLOWED_HOSTS=api.tilqor.samatk.me
   DJANGO_CSRF_TRUSTED_ORIGINS=https://tilqor.samatk.me,https://api.tilqor.samatk.me
   DJANGO_CORS_ALLOWED_ORIGINS=https://tilqor.samatk.me
   DJANGO_CSRF_COOKIE_DOMAIN=.tilqor.samatk.me
   ```

   Then run **Actions → Deploy → Run workflow** for `main`; Caddy gets a new API certificate.
5. Check `https://api.tilqor.samatk.me/api/health/`, `/api/docs/` and `/admin/`.
   On `https://tilqor.samatk.me`, register, sign in, reload `/tasks`, submit a translation and
   download CSV. After switching, `63.181.85.65.sslip.io` is no longer used.

### Local cross-origin check

Save the local `.env` before testing, then temporarily set `DJANGO_DEBUG=true`,
`DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`, `DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:4173`,
`DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:4173` and leave `DJANGO_CSRF_COOKIE_DOMAIN` empty
(localhost cookies are shared across ports). Use the local compose stack, never production:

```bash
docker compose up -d --build db backend
cd src/frontend
VITE_API_BASE_URL=http://localhost:8000 npm run build
npx vite preview --port 4173
```

Open `http://localhost:4173`, register, sign out and in, open a task, submit a translation,
reload a deep link and download CSV. Inspect one POST response for
`Access-Control-Allow-Origin: http://localhost:4173` and `Access-Control-Allow-Credentials: true`.
Restore `.env` and recreate the backend container after checking. Rebuild the frontend with the
production API URL before using its bundle for production verification.

## 6. Notes
- AWS free-plan credits end on 2027-02-10; upgrade the plan before that date if the server is still needed.
- The production `.env` exists only on the server. A leaked key or password must be replaced there and the stack restarted.
- The GHCR login on the server uses a personal token; when it expires, pulls fail until `docker login ghcr.io` is repeated.
