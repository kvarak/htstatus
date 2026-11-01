#!/bin/sh
# Pull the latest image; if it changed, back up the database first (the new
# image may run migrations on start), then recreate the web container.
# Run from cron every 15 minutes, or by hand to deploy now.
set -e
cd "$(dirname "$0")"
image=$(sed -n 's/^WEB_IMAGE=//p' .env | tail -n 1)
docker compose pull -q web
latest=$(docker image inspect -f '{{.Id}}' "$image")
running=$(docker inspect -f '{{.Image}}' "$(docker compose ps -q web)" 2>/dev/null || true)
# Compare with the running container, so a run that failed (e.g. backup) is retried.
if [ "$running" != "$latest" ]; then
    echo "$(date +'%F %T') new image, backing up before deploy"
    ./backup.sh
    docker compose up -d --wait
    docker image prune -f >/dev/null   # remove the old, now-untagged image layers
    echo "$(date +'%F %T') deployed $(docker compose exec -T web printenv APP_VERSION)"
fi
