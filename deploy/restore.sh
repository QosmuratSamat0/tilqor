#!/usr/bin/env bash
# Restore a backup into a NEW empty database and report the time (NFR-06 restore test).
#   deploy/restore.sh ~/backups/tilqor-20261103-030000.sql.gz tilqor_restore_test
# Restoring over the live database is a manual step described in docs/deploy.md.
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "usage: $0 <backup.sql.gz> <new_database_name>" >&2
  exit 2
fi
backup="$1"
target="$2"

cd "$(dirname "$0")/.."
compose="docker compose -f docker-compose.prod.yml"

start=$(date +%s)
$compose exec -T db sh -c "createdb -U \"\$POSTGRES_USER\" \"$target\""
gunzip -c "$backup" | $compose exec -T db \
  sh -c "psql -v ON_ERROR_STOP=1 -q -U \"\$POSTGRES_USER\" -d \"$target\"" > /dev/null
end=$(date +%s)

echo "restored $backup into $target in $((end - start)) s"
$compose exec -T db sh -c "psql -U \"\$POSTGRES_USER\" -d \"$target\" -c \
  'select (select count(*) from accounts_user) as users, (select count(*) from contributions_contributionversion) as versions, (select count(*) from verification_review) as reviews;'"
