#!/usr/bin/env bash
# Daily PostgreSQL backup (NFR-06). Run from cron on the server, e.g.:
#   0 3 * * * /home/ubuntu/tilqor/deploy/backup.sh >> /home/ubuntu/backups/backup.log 2>&1
set -euo pipefail

cd "$(dirname "$0")/.."
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
KEEP_DAYS="${KEEP_DAYS:-14}"

mkdir -p "$BACKUP_DIR"
file="$BACKUP_DIR/tilqor-$(date -u +%Y%m%d-%H%M%S).sql.gz"

docker compose -f docker-compose.prod.yml exec -T db \
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner' | gzip > "$file.tmp"
mv "$file.tmp" "$file"

find "$BACKUP_DIR" -name 'tilqor-*.sql.gz' -mtime +"$KEEP_DAYS" -delete
echo "$(date -u +%FT%TZ) backup ok: $file ($(du -h "$file" | cut -f1))"
