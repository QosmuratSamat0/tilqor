#!/usr/bin/env bash
# Deploy a backend image from GHCR and check that the site answers.
#   deploy/deploy.sh <tag>     tag = commit SHA from the Deploy workflow; an older SHA rolls back
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <image-tag>" >&2
  exit 2
fi
tag="$1"

cd "$(dirname "$0")/.."
compose="docker compose -f docker-compose.prod.yml"

# Remember the deployed tag in .env, so later compose commands use the same image.
sed -i '/^IMAGE_TAG=/d' .env
echo "IMAGE_TAG=$tag" >> .env

$compose pull backend
$compose up -d --no-build

site="$(grep '^SITE_ADDRESS=' .env | cut -d= -f2)"
# Up to 3 minutes: on the first deploy Caddy also obtains the HTTPS certificate.
for _ in $(seq 1 90); do
  if curl -fsS "https://$site/api/health/" > /dev/null; then
    echo "deployed $tag: https://$site/api/health/ ok"
    docker image prune -f > /dev/null
    exit 0
  fi
  sleep 2
done

echo "health check failed for $tag" >&2
$compose logs --tail 50 backend >&2
exit 1
