#!/bin/sh
# Copy the production database into the local dev database (replaces it), e.g.
# to test a migration on real data: make db-copy-production, then make db-upgrade.
# Production is only read. Settings come from .env:
#   PROD_SERVER    ssh target of the server (user@host or an ssh alias)
#   PROD_APP_DIR   folder with the production docker-compose.yml on it
set -eu
cd "$(dirname "$0")/../.."
setting() { sed -n "s/^$1=//p" .env | tail -n 1; }
server=$(setting PROD_SERVER)
app_dir=$(setting PROD_APP_DIR)
container=$(setting POSTGRES_CONTAINER)
container=${container:-htplanner_postgres}
db=$(setting POSTGRES_DB)
db=${db:-htplanner}
user=$(setting POSTGRES_USER)
user=${user:-htplanner}
[ -n "$server" ] && [ -n "$app_dir" ] || { echo "Set PROD_SERVER and PROD_APP_DIR in .env"; exit 1; }

printf "Replace local database '%s' with a copy of production from %s? [y/N] " "$db" "$server"
read -r answer
[ "$answer" = "y" ] || exit 1

dump=$(mktemp)
trap 'rm -f "$dump"' EXIT
ssh -o BatchMode=yes "$server" "cd $app_dir && docker compose exec -T db pg_dump -U htplanner -d htplanner --no-owner --no-privileges </dev/null" > "$dump"
grep -q "PostgreSQL database dump complete" "$dump" || { echo "Incomplete dump, local database not touched"; exit 1; }

docker exec "$container" psql -q -U "$user" -d postgres -c "DROP DATABASE IF EXISTS $db WITH (FORCE)" -c "CREATE DATABASE $db OWNER $user"
docker exec -i "$container" psql -q -v ON_ERROR_STOP=1 -U "$user" -d "$db" < "$dump" > /dev/null
echo "Done: $(docker exec "$container" psql -At -U "$user" -d "$db" -c 'select count(*) from players') player records, migration $(docker exec "$container" psql -At -U "$user" -d "$db" -c 'select version_num from alembic_version')"
