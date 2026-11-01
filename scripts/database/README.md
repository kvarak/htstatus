# Database scripts

Migration and diagnostic helpers. Production backups are made by `deploy/backup.sh` on the server (see [DEPLOYMENT.md](../../DEPLOYMENT.md)).

| Script | Make target | Purpose |
|---|---|---|
| `apply_migrations.py` | `make db-upgrade` | Run Alembic migrations to head on `DATABASE_URL` (also the Docker entrypoint) |
| `copy_production_db.sh` | `make db-copy-production` | Replace the local dev database with a copy of production (read-only on production; `PROD_SERVER` and `PROD_APP_DIR` in `.env`) |
| `check_errors.py` | | Production error log CLI (`--recent N`, `--details ID`); in Docker: `docker compose exec web python scripts/database/check_errors.py` |
| `test_db_connection.py` | | Check that the configured database is reachable |

Test a new migration on real data: `make db-copy-production`, then `make db-upgrade`, then click through the app.
