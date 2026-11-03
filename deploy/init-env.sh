#!/usr/bin/env bash
# Create ~/tilqor/.env on the first deploy; never overwrite an existing one.
# Secrets are generated on the server and never leave it.
set -euo pipefail

cd "$(dirname "$0")/.."
if [ -f .env ]; then
  echo ".env exists, keeping it"
  exit 0
fi

secret() { python3 -c "import secrets; print(secrets.token_urlsafe($1))"; }
site="$(curl -fsS https://checkip.amazonaws.com).sslip.io"

umask 077
cat > .env <<EOF
SITE_ADDRESS=$site
DJANGO_SECRET_KEY=$(secret 50)
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=$site
DJANGO_CSRF_TRUSTED_ORIGINS=https://$site
DJANGO_SECURE_PROXY=true
DJANGO_SECURE_HSTS_SECONDS=86400
GUNICORN_WORKERS=3
POSTGRES_DB=tilqor
POSTGRES_USER=tilqor
POSTGRES_PASSWORD=$(secret 32)
POSTGRES_HOST=db
POSTGRES_PORT=5432
EOF
echo "created .env for https://$site"
