# Deployment

HattrickPlanner runs on a Raspberry Pi (`glader.local`) as a systemd service (`htstatus`) with a local PostgreSQL database. There is no Docker in production; `docker-compose.yml` is only for local development.

## Deploying

From your development machine, with the code committed and pushed:

```bash
make deploy                  # runs scripts/deployment/deploy.sh --run (dry-run if not pushed)
FORCE_DEPLOY=true make deploy  # deploy even with unpushed/uncommitted changes
./scripts/deployment/deploy.sh --run --major   # also rotate SECRET_KEY
```

`deploy.sh` reads `DEPLOY_SERVER`, `DEPLOY_REPO_PATH`, `DEPLOY_GIT_BRANCH` and `DEPLOY_USER` from your local `.env` and runs these Makefile targets on the Pi over SSH:

| Target | What it does |
|---|---|
| `deploy-prepare` | Installs `jq` and `uv` if missing |
| `deploy-sync` | `git reset --hard` to the deploy branch, `uv sync` |
| `deploy-docs` | Regenerates the changelog / release docs |
| `deploy-migrate` | Applies database migrations (`scripts/database/apply_migrations.py`) |
| `deploy-finalize` | Clears caches and `sudo systemctl restart htstatus` |

You can run any of them by hand on the Pi when something goes wrong.

## Configuration on the Pi

The app reads everything from `.env` in the repo directory (see `.env.example` and `config.py`). The important ones:

```bash
SECRET_KEY=...            # uv run python -c 'import secrets; print(secrets.token_hex(32))'
CONSUMER_KEY=...          # Hattrick CHPP credentials
CONSUMER_SECRETS=...
CALLBACK_URL=https://<your-domain>/login
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/htplanner
FLASK_ENV=production      # enables the database error log
DEBUG_LEVEL=0
```

Copy `config.py.example` to `config.py` on a fresh checkout.

## Service

`/etc/systemd/system/htstatus.service` runs the app with uv, for example:

```ini
[Unit]
Description=HattrickPlanner
After=network.target postgresql.service

[Service]
User=<user>
WorkingDirectory=<repo path>
ExecStart=<home>/.local/bin/uv run python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Logs: `sudo journalctl -u htstatus -f`. Production errors are also stored in the database and shown on the admin `/debug` page (or `uv run python scripts/database/check_errors.py`).

## Database safety

The database is the one thing that must not break.

- **Before a migration:** `make db-backup` (full dump via `scripts/database/backup_database.py`).
- **Nightly backups:** cron on the Pi runs `make db-backup-auto`, which copies a backup to `kloker.local`; see [scripts/database/README.md](scripts/database/README.md).
- **Restore:** `make db-restore BACKUP_FILE=path/to/backup.sql`.
- **Migrations:** create with `make db-migrate MESSAGE="..."`, review the generated file, test locally (`make db-upgrade` against a copy of production via `scripts/database/restore_production_backup.sh`), then deploy.

## Rolling back

```bash
# on the Pi
sudo systemctl stop htstatus
git reset --hard <previous good commit>
make db-restore BACKUP_FILE=<backup from before the deploy>   # only if a migration ran
sudo systemctl start htstatus
```

## Troubleshooting

- **App won't start:** `sudo journalctl -u htstatus -n 100`; check `.env` and that `config.py` exists.
- **Login fails:** `CALLBACK_URL` must match the URL registered for the CHPP app.
- **Database errors:** `uv run python scripts/database/test_db_connection.py`, then `make deploy-migrate`.
