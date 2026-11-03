# Deployment (TIL-34)

Stage 1 deploys the backend (API, Swagger UI, Django admin). The frontend is added in stage 2 (TIL-24).

| Part | Choice |
|---|---|
| Server | AWS EC2 t3.small (2 GB) or Lightsail, Ubuntu 24.04 LTS, Frankfurt, static IPv4 (Elastic IP) |
| Size | 2 GB RAM + 2 GB swap for stage 1; 2 vCPU / 4 GB for the NFR-05 load test (TIL-35) |
| Stack | [`docker-compose.prod.yml`](../docker-compose.prod.yml): PostgreSQL 16, Django + gunicorn ([`Dockerfile.prod`](../src/backend/Dockerfile.prod)), Caddy |
| Image | built by GitHub Actions, stored in GHCR as `ghcr.io/qosmuratsamat0/tilqor-backend:<commit-sha>` |
| HTTPS | Caddy gets a Let's Encrypt certificate and redirects HTTP to HTTPS (NFR-03) |
| Address | `<static-ip>.sslip.io` until the project has its own domain |
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
Deploys never run automatically. **Actions → Deploy → Run workflow** (branch: normally `main`) runs
[`deploy.yml`](../.github/workflows/deploy.yml):

1. build the image and push `tilqor-backend:<commit-sha>` to GHCR;
2. copy `docker-compose.prod.yml` and `deploy/` to `~/tilqor` on the server;
3. [`deploy/init-env.sh`](../deploy/init-env.sh): on the first deploy only, create `.env` with secrets generated on the server;
4. [`deploy/deploy.sh <sha>`](../deploy/deploy.sh): pull the image, restart, wait up to 3 minutes for `/api/health/`; the job fails otherwise.

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

## 6. Notes
- AWS free-plan credits end on 2027-02-10; upgrade the plan before that date if the server is still needed.
- `.env` exists only on the server. A leaked key or password must be replaced there and the stack restarted.
- The GHCR login on the server uses a personal token; when it expires, pulls fail until `docker login ghcr.io` is repeated.
