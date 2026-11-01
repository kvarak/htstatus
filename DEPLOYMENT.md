# Deployment

HattrickPlanner runs on a small Linux server (a Raspberry Pi with a 64-bit OS is enough) behind a reverse proxy that terminates HTTPS (e.g. nginx with Let's Encrypt).

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

The reverse proxy forwards your domain to `http://127.0.0.1:$WEB_PORT` (default 5000), passing the `Host` header. `CALLBACK_URL` in `.env` must be `https://<your domain>/login`, the URL registered for your CHPP app. The app also takes its public address from it (canonical links, `/robots.txt`, `/sitemap.xml`, link previews).

### Day to day (on the server, in `<app dir>`)

| Task | Command |
|---|---|
| Deploy now | `./update.sh` (otherwise cron does it within 15 min of CI publishing) |
| Roll back | Set `WEB_IMAGE` in `.env` to the `:<good commit sha>` tag, then `docker compose up -d` (and restore the backup `update.sh` made, if a migration ran) |
| Logs | `docker compose logs -f web` |
| Status | `docker compose ps` |
| Backup now | `./backup.sh` |
| Restore | `docker compose stop web`, then `gunzip -c backups/<file>.sql.gz \| docker compose exec -T db psql -U htplanner -d htplanner`, then `docker compose start web` (into an empty database, see Database safety) |
| Database shell | `docker compose exec db psql -U htplanner htplanner` |
| Errors | admin `/debug` page (production errors are stored in the database) |

`docker compose down` keeps the database; **`docker compose down -v` deletes it. Never use `-v` here.**

### Locally

`make docker-up` builds the production image and runs it on http://localhost:5010 (`WEB_PORT=5011 make docker-up` if the dev server uses 5010) against the dev database. `make docker-check` runs lint and tests inside the image. The usual uv workflow (`make dev`, `make test-all`) is unchanged.

## Setting up a server

1. Install Docker with the compose plugin, and put the reverse proxy in front of `http://127.0.0.1:<WEB_PORT>`.
2. Copy the deploy files and create `.env`:
   ```bash
   mkdir -p <app dir>/data/instance <app dir>/backups
   scp deploy/{docker-compose.yml,update.sh,backup.sh,table_counts.sql,.env.example} <server>:<app dir>/
   cd <app dir> && cp .env.example .env && chmod 600 .env    # fill in every value
   sudo chown -R 10001:10001 data/instance
   ```
3. If the package is private, run `docker login ghcr.io` once (token with `read:packages`).
4. Load the database from a backup: a brand-new empty database isn't supported yet (INFRA-091).
   ```bash
   docker compose up -d --wait db
   gunzip -c <backup>.sql.gz | docker compose exec -T db psql -q -v ON_ERROR_STOP=1 -U htplanner -d htplanner
   docker compose up -d --wait && curl -sI http://127.0.0.1:<WEB_PORT>/ | head -1
   ```
5. Add to the crontab (absolute paths):
   ```
   0 2 * * * PATH=/usr/local/bin:/usr/bin:/bin <app dir>/backup.sh >> <app dir>/backup.log 2>&1
   */15 * * * * PATH=/usr/local/bin:/usr/bin:/bin <app dir>/update.sh >> <app dir>/update.log 2>&1
   ```
   Then run `./backup.sh` once by hand to check it (and the off-site copy) works.

To move the app to another server, take a fresh backup on the old one (`./backup.sh`), stop it (`docker compose stop web`), and follow these steps with that backup. Compare `table_counts.sql` output on both before switching the proxy.

## Releasing

A release is a git tag (`3.24`). The footer version and the /changes page come from tags.

1. Write the notes by hand: a user section in `RELEASES.md`, and a technical one in `RELEASES-INTERNAL.md`. Use top-level `- ` bullets in `RELEASES.md`; the /changes page ignores indented ones.
2. Commit them ("Update release documentation for vX.Y").
3. Run `make release-tag VERSION=X.Y MESSAGE="..."`, then `make changelog` to check that /changes picks up the release (the generated JSON is not committed).
4. Push the commit and the tag together (`git push --atomic origin main X.Y`), so CI sees the tag when it computes the version. CI builds the image with that version and /changes data; the server picks it up within 15 minutes (or run `./update.sh` there).

## Database safety

The database is the one thing that must not break.

- **Before every deploy:** `update.sh` runs `backup.sh` before it starts a new image. A new image runs the migrations when it starts, and a failed migration stops the container.
- **Nightly:** cron runs `backup.sh` (kept `BACKUP_KEEP_DAYS` days locally, plus the optional off-site copy).
- **New migrations:** create with `make db-migrate MESSAGE="..."` and review the file. Test it on real data: `make db-copy-production` (copies the production database into the local dev database; needs `PROD_SERVER` and `PROD_APP_DIR` in your local `.env`), then `make db-upgrade` and click through the app.
- **Restore:** see "Day to day" above. Restore into an empty database (`DROP DATABASE htplanner WITH (FORCE)` / `CREATE DATABASE htplanner` in `docker compose exec db psql -U htplanner -d postgres`).

## Troubleshooting

- **The app doesn't start:** `docker compose logs web`. A migration error stops the container: restore the backup `update.sh` made just before, and pin the previous image (`WEB_IMAGE=...:<sha>`).
- **Login fails:** `CALLBACK_URL` must match the URL registered for the CHPP app.
- **No new version after a push:** check the CI "Docker image" job, then `update.log` on the server.
- **Errors in production:** the admin `/debug` page, or `docker compose exec web python scripts/database/check_errors.py`.
