# Deployment

HattrickPlanner runs on a small Linux server (a Raspberry Pi with a 64-bit OS is enough) behind a reverse proxy that terminates HTTPS (e.g. nginx with Let's Encrypt).

**Moving to Docker (INFRA-090).** The target setup is described first. Until the [cut-over](#cut-over-from-the-old-setup) is done, production still runs the [old setup](#old-setup-until-the-cut-over) at the end of this file.

## Docker setup

CI tests every push. On `main` it also builds the image for amd64 and arm64 and publishes it to `ghcr.io/<github owner>/htstatus-web`, tagged `latest` and the commit SHA. The server never builds anything: it pulls the image and restarts.

On the server, everything lives in one folder (called `<app dir>` below, e.g. `~/htplanner`):

| File | What it is |
|---|---|
| `docker-compose.yml` | Copy of [deploy/docker-compose.yml](deploy/docker-compose.yml): PostgreSQL 17 (`db`, named volume `db-data`) and the app (`web`, gunicorn on `127.0.0.1:$WEB_PORT`) |
| `.env` | Settings and secrets, from [deploy/.env.example](deploy/.env.example) (`chmod 600`) |
| `update.sh` | Cron every 15 min: pulls the image; if it changed, runs `backup.sh` first, then restarts `web` |
| `backup.sh` | Cron nightly: `pg_dump` to `backups/` (`BACKUP_KEEP_DAYS`); with `BACKUP_REMOTE` set, also copied over ssh to another host |
| `data/instance/` | Data fetched at Update (transfer bids, series, Hattrick terms); owned by uid 10001 |

The container runs the migrations every time it starts. If one fails, the container stops instead of serving a half-migrated database.

The reverse proxy forwards your domain to `http://127.0.0.1:$WEB_PORT` (default 5000), passing the `Host` header. `CALLBACK_URL` in `.env` must be `https://<your domain>/login`, the URL registered for your CHPP app.

### Day to day (on the server, in `<app dir>`)

| Task | Command |
|---|---|
| Deploy now | `./update.sh` (otherwise cron does it within 15 min of CI publishing) |
| Roll back | Set `WEB_IMAGE` in `.env` to the `:<good commit sha>` tag, then `docker compose up -d` (and restore the backup `update.sh` made, if a migration ran) |
| Logs | `docker compose logs -f web` |
| Status | `docker compose ps` |
| Backup now | `./backup.sh` |
| Restore | `docker compose stop web`, then `gunzip -c backups/<file>.sql.gz \| docker compose exec -T db psql -U htplanner -d htplanner`, then `docker compose start web` (restore into an empty database, see the cut-over steps) |
| Database shell | `docker compose exec db psql -U htplanner htplanner` |
| Errors | admin `/debug` page (production errors are stored in the database) |

`docker compose down` keeps the database; **`docker compose down -v` deletes it. Never use `-v` here.**

### Locally

`make docker-up` builds the production image and runs it on http://localhost:5010 (`WEB_PORT=5011 make docker-up` if the dev server uses 5010) against the dev database. `make docker-check` runs lint and tests inside the image. The usual uv workflow (`make dev`, `make test-all`) is unchanged.

## Cut-over from the old setup

The old setup has a systemd service `htstatus` running the app from a git checkout (`<old checkout>` below) on port 5000, and the `htplanner` database in the host's PostgreSQL. These steps were rehearsed locally with a production dump: all tables and row counts matched, migrations ran, and every page rendered for a real user.

**0. Publish the image** (no downtime)
1. Push to `main` and wait for the CI "Docker image" job.
2. Either make the package public (GitHub → Packages → `htstatus-web` → Package settings → Change visibility), or run `docker login ghcr.io` once on the server with a token that has `read:packages`.
3. On the server: `docker pull ghcr.io/<github owner>/htstatus-web:latest`.

**1. Prepare the folder** (no downtime)
```bash
mkdir -p <app dir>/data/instance <app dir>/backups && cd <app dir>
# from your machine: scp deploy/{docker-compose.yml,update.sh,backup.sh,table_counts.sql,.env.example} <server>:<app dir>/
cp .env.example .env && chmod 600 .env
# .env: copy SECRET_KEY (keeps everyone logged in), CONSUMER_KEY, CONSUMER_SECRETS and CALLBACK_URL
#       from <old checkout>/.env; set WEB_IMAGE, a new POSTGRES_PASSWORD (letters and digits),
#       BACKUP_REMOTE if you copy backups to another host, and WEB_PORT=5001 for now
sudo chown -R 10001:10001 data/instance
```

**2. Dry run next to the live site** (no downtime)
```bash
docker compose up -d --wait db
sudo -u postgres pg_dump --no-owner --no-privileges htplanner | docker compose exec -T db psql -q -v ON_ERROR_STOP=1 -U htplanner -d htplanner
sudo -u postgres psql -At htplanner < table_counts.sql > counts_old.txt
docker compose exec -T db psql -At -U htplanner htplanner < table_counts.sql | diff - counts_old.txt && echo COUNTS MATCH
docker compose up -d --wait web && curl -sI http://127.0.0.1:5001/ | head -1      # expect 200
docker compose logs web | tail -20
./backup.sh                                                                  # checks backups (and the off-site copy) work
```
Then empty the database again for the real copy:
```bash
docker compose stop web
docker compose exec -T db psql -U htplanner -d postgres -c "DROP DATABASE htplanner WITH (FORCE)" -c "CREATE DATABASE htplanner"
```

**3. Switch** (the site is down for a minute or two)
```bash
sudo systemctl stop htstatus                                   # nothing writes to the old database now
sudo -u postgres pg_dump --no-owner --no-privileges htplanner > backups/cutover_old_htplanner.sql
docker compose exec -T db psql -q -v ON_ERROR_STOP=1 -U htplanner -d htplanner < backups/cutover_old_htplanner.sql
sudo -u postgres psql -At htplanner < table_counts.sql > counts_old.txt
docker compose exec -T db psql -At -U htplanner htplanner < table_counts.sql | diff - counts_old.txt && echo COUNTS MATCH
sudo cp -a <old checkout>/instance/. data/instance/ && sudo chown -R 10001:10001 data/instance
sed -i 's/^WEB_PORT=.*/WEB_PORT=5000/' .env
docker compose up -d --wait && curl -sI http://127.0.0.1:5000/ | head -1           # expect 200
```
Keep `backups/cutover_old_htplanner.sql` somewhere safe (another host too). Then open your site, log in, open a few pages and run Update once. The reverse proxy needs no change if it already pointed at port 5000.

**4. Make it permanent**
```bash
sudo systemctl disable htstatus        # must not start on reboot and take port 5000
crontab -e
#   remove the old backup and log-rotation lines for <old checkout>
#   add:    0 2 * * * <app dir>/backup.sh >> <app dir>/backup.log 2>&1
#   add:    */15 * * * * PATH=/usr/local/bin:/usr/bin:/bin <app dir>/update.sh >> <app dir>/update.log 2>&1
```
Use absolute paths in crontab (e.g. `/home/<user>/htplanner`).

**If something is wrong** (at any point before step 4, or soon after it):
```bash
cd <app dir> && docker compose stop web
sudo systemctl enable --now htstatus   # the old database was never changed
```
Anything written in the new setup after the switch is lost in this case. If needed, dump it from the `db` container first.

**5. Later (after a couple of weeks without problems).** Remove the old setup:
- the systemd unit and `<old checkout>`;
- the `htplanner` database in the host PostgreSQL (dump it once more first);
- `make deploy`/`deploy-*`, `scripts/deployment/` and the old backup script and target from the repo;
- then make this file Docker-only.

## Releasing

A release is a git tag (`3.24`). The footer version and the /changes page come from tags.

1. Write the notes by hand: a user section in `RELEASES.md`, a technical one in `RELEASES-INTERNAL.md`, and `[Unreleased]` → `[X.Y] - date` in `CHANGELOG.md`. Use top-level `- ` bullets in `RELEASES.md`; the /changes page ignores indented ones.
2. Commit them ("Update release documentation for vX.Y").
3. Run `make release-tag VERSION=X.Y MESSAGE="..."`, then `make release-docs` to check that /changes picks up the release (the generated JSON is not committed).
4. Push the commit and the tag (`git push && git push origin X.Y`). CI builds the image with that version and /changes data; the server picks it up within 15 minutes (or run `./update.sh` there). Until the cut-over: `make deploy`.

## Old setup (until the cut-over)

From your development machine, with the code committed and pushed:

```bash
make deploy                  # runs scripts/deployment/deploy.sh --run (dry-run if not pushed)
FORCE_DEPLOY=true make deploy  # deploy even with unpushed/uncommitted changes
./scripts/deployment/deploy.sh --run --major   # also rotate SECRET_KEY
```

`deploy.sh` reads `DEPLOY_SERVER`, `DEPLOY_REPO_PATH`, `DEPLOY_GIT_BRANCH` and `DEPLOY_USER` from your local `.env` and runs these Makefile targets on the server over SSH:

| Target | What it does |
|---|---|
| `deploy-prepare` | Installs `jq` and `uv` if missing |
| `deploy-sync` | `git reset --hard` to the deploy branch, `uv sync` |
| `deploy-docs` | Regenerates the changelog / release docs |
| `deploy-migrate` | Applies database migrations (`scripts/database/apply_migrations.py`) |
| `deploy-finalize` | Clears caches and `sudo systemctl restart htstatus` |

You can run any of them by hand on the server when something goes wrong.

### Configuration

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

### Service

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

### Database safety

The database is the one thing that must not break.

- **Before a migration:** `make db-backup` (full dump via `scripts/database/backup_database.py`).
- **Nightly backups:** cron on the server runs `make db-backup-auto`, which copies a backup to the backup host over ssh; see [scripts/database/README.md](scripts/database/README.md).
- **Restore:** `make db-restore BACKUP_FILE=path/to/backup.sql`.
- **Migrations:** create with `make db-migrate MESSAGE="..."`, review the generated file, test locally (`make db-upgrade` against a copy of production via `scripts/database/restore_production_backup.sh`), then deploy.

### Rolling back

```bash
# on the server
sudo systemctl stop htstatus
git reset --hard <previous good commit>
make db-restore BACKUP_FILE=<backup from before the deploy>   # only if a migration ran
sudo systemctl start htstatus
```

### Troubleshooting

- **App won't start:** `sudo journalctl -u htstatus -n 100`; check `.env` and that `config.py` exists.
- **Login fails:** `CALLBACK_URL` must match the URL registered for the CHPP app.
- **Database errors:** `uv run python scripts/database/test_db_connection.py`, then `make deploy-migrate`.
