#!/bin/sh
# Apply database migrations, then start the server. A failed migration stops
# the container, so the app never runs on a half-migrated schema.
set -e
python scripts/database/apply_migrations.py
exec "$@"
