# Database scripts

Development and migration helpers for the local dev database. Production backups are made by `deploy/backup.sh` on the server (see [DEPLOYMENT.md](../../DEPLOYMENT.md)).

| Script | Make target | Purpose |
|---|---|---|
| `apply_migrations.py` | `make db-apply` | Run Alembic migrations to head (also the Docker entrypoint) |
| `upgrade_local_database.sh` | `make db-upgrade` | Migrate the local dev database |
| `copy_production_db.sh` | `make db-copy-production` | Replace the local dev database with a copy of production (read-only on production; `PROD_SERVER` and `PROD_APP_DIR` in `.env`) |
| `backup_database.py` | `make db-backup` | Full dump of the database in `DATABASE_URL` |
| `restore_database.py` | `make db-restore BACKUP_FILE=...` | Restore such a dump |
| `check_errors.py` | | Production error log CLI (`--recent N`, `--details ID`); in Docker: `docker compose exec web python scripts/database/check_errors.py` |
| `test_db_connection.py` | | Check that the configured database is reachable |
| `db_utils.py` | | Shared helpers for the Python scripts |

Test a new migration on real data: `make db-copy-production`, then `make db-upgrade`, then click through the app.
