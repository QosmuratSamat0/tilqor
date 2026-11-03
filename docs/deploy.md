# Deployment (TIL-34)

Stage 1 deploys the backend (API, Swagger UI, Django admin). The frontend is added in stage 2 (TIL-24).

| Part | Choice |
|---|---|
| Server | AWS (EC2 or Lightsail), Ubuntu 24.04 LTS, Frankfurt, static IPv4 (Elastic IP on EC2) |
| Size | 1–2 GB RAM for stage 1 (with 2 GB swap on 1 GB); 2 vCPU / 4 GB for the NFR-05 load test (TIL-35) |
| Stack | [`docker-compose.prod.yml`](../docker-compose.prod.yml): PostgreSQL 16, Django + gunicorn ([`Dockerfile.prod`](../src/backend/Dockerfile.prod)), Caddy |
| HTTPS | Caddy gets a Let's Encrypt certificate and redirects HTTP to HTTPS (NFR-03) |
| Address | `<static-ip>.sslip.io` until the project has its own domain |
| Backups | [`deploy/backup.sh`](../deploy/backup.sh) daily from cron, 14 days kept (NFR-06) |

## 1. Prepare the server (once)
Firewall (EC2 security group or Lightsail firewall): allow SSH (22), HTTP (80), HTTPS (443). Then on the server:

```bash
# 2 GB swap, needed on a 1 GB server so the image build does not run out of memory
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

sudo apt-get update && sudo apt-get install -y docker.io docker-compose-v2 git
sudo usermod -aG docker ubuntu   # log out and in again
git clone https://github.com/QosmuratSamat0/tilqor.git ~/tilqor
cd ~/tilqor
cp deploy/prod.example.env .env
nano .env                        # replace every change-me; never commit this file
```

## 2. Start or update
```bash
cd ~/tilqor
git pull
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser   # first time only
```

Check: `https://<site>/api/health/` returns `{"status": "ok", "database": "ok"}`;
`https://<site>/api/docs/` and `https://<site>/admin/` open; `http://<site>/` redirects to HTTPS.

## 3. Backups
```bash
chmod +x ~/tilqor/deploy/*.sh
mkdir -p ~/backups
crontab -e
# add:
0 3 * * * /home/ubuntu/tilqor/deploy/backup.sh >> /home/ubuntu/backups/backup.log 2>&1
```

Off-server copy: download the latest file to a team computer, for example
`scp -i <key.pem> ubuntu@<ip>:~/backups/tilqor-*.sql.gz .`

## 4. Restore test (NFR-06)
Restore into a new empty database, record the time and row counts, then remove it:

```bash
~/tilqor/deploy/restore.sh ~/backups/<file>.sql.gz tilqor_restore_test
docker compose -f docker-compose.prod.yml exec db sh -c 'dropdb -U "$POSTGRES_USER" tilqor_restore_test'
```

Restoring over the live database: stop the backend, drop and recreate the `tilqor` database,
restore with `restore.sh` into `tilqor`, start the backend again.

## 5. Notes
- AWS free-plan credits end on 2027-02-10; upgrade the plan before that date if the server is still needed.
- `.env` exists only on the server. A leaked key or password must be replaced there and the stack restarted.
