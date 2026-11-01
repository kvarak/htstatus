---
name: docker-hosting
description: 'Host and deploy a hobby web app with Docker: a multi-stage Dockerfile with an allow-list .dockerignore, a dev docker-compose.yml, a separate production compose folder (compose + .env + update.sh + backup.sh) on the server, and a GitHub Actions job that publishes a multi-arch image to ghcr.io. The server (usually a Raspberry Pi behind an HTTPS reverse proxy) only pulls and restarts; cron deploys new images after a backup. Use when containerizing an app, setting up or changing deployment/hosting, adding a database service, checking a published image, or moving an existing app (with live data) off a git-checkout/systemd deploy.'
license: MIT
---

# Docker hosting

## Overview

CI tests every push. On `main` it builds the image and publishes it to GitHub Container Registry, tagged `latest` and the commit SHA. The server never builds the app, runs a package manager or keeps a git checkout of it. It has one folder per app:

```
<app dir>/
  docker-compose.yml   # copy of deploy/docker-compose.yml from the repo
  .env                 # settings and secrets (chmod 600), from deploy/.env.example
  update.sh            # cron: pull; if the image changed, back up, then restart
  backup.sh            # cron: nightly pg_dump (+ optional copy to another host)
  data/                # bind-mounted files the app writes (uploads, caches)
  backups/
```

The repo has two compose files:
- **`docker-compose.yml`** (repo root) for development and running tests in the image.
- **`deploy/docker-compose.yml`** for production. It is versioned in the repo but copied to the server; it has no `build:` section.

Keep it simple: this is a hobby setup on one machine, not Kubernetes.

## When to use

- A new app needs to run somewhere ("how do I host this?")
- Containerizing an existing app, or replacing a git pull + venv + systemd deploy
- Adding a database or another service
- CI should publish an image for a Raspberry Pi
- Checking that a published image or a CI run is what we expect

## Two shapes

| | Stateless app | App with a database |
|---|---|---|
| Services | `app` only | `db` + `web` (+ `test` profile in the dev compose) |
| Dockerfile | single stage is fine | stages `base` → `test` and `runtime` |
| Data | none (`read_only: true`, `tmpfs: /tmp`, `cap_drop: ALL`) | named volume for the database, bind mount `./data/...` for files |
| Start-up | the server | entrypoint: migrations, then `exec` the server |
| Backups | none | `backup.sh` nightly and before each new image |

Start from the stateless shape and add only what the app needs.

## Rules that save time

- **Read freely, ask before changing servers or git.** Read-only `git` and `ssh` (looking at files, logs, `docker compose ps`, read-only SQL, dumps) are fine. Anything that changes a server or the repo (edits, restarts, `up`/`down`, crontab, database writes, commits, tags, pushes) needs the user's permission first. The user commits and pushes.
- **Nothing personal in the repo.** Hostnames, backup hosts, domains, image owners and paths go in the server's `.env` or in placeholders in the docs (`<app dir>`, `<server>`, `<your domain>`, `ghcr.io/<owner>/...`). Scripts read them from `.env`. Optional ones, like an off-site backup host, are skipped when empty.
- **The image has no `.git`.**
  - Pass the version as a build arg: `APP_VERSION=$(git describe --tags)`, which needs `fetch-depth: 0` in CI. The app reads `APP_VERSION` before falling back to git.
  - Generate git-derived files (changelog JSON etc.) in CI before the build, and keep them out of `.dockerignore`'s exclusions even if `.gitignore` excludes them.
- **Lock or pin dependencies.** Install production dependencies from a tracked lock file, or from a pinned `requirements.txt` if the lock file isn't committed. Pin the test stage's tools (linters, formatters, pytest) to the versions used locally, or their formatting will drift and fail `check`.
- **Readable files for a non-root user.** `COPY` keeps the checkout's modes. macOS checkouts often have `drwx------` folders, so the non-root user gets "Permission denied" at runtime. Run `chmod -R a+rX,go-w .` after copying. The code stays root-owned and read-only.
- **Real server.** Run gunicorn (or the language's equivalent), never a dev server.
  - Raise the timeout for slow requests that call external APIs (default 30 s).
  - Log paths without query strings, so tokens and ids stay out of the logs.
- **Port.** Bind to `127.0.0.1:<port>` behind the reverse proxy. When replacing an old service, reuse its port so the proxy config doesn't change.
- **Keep CI actions on current major versions**, or Node deprecation warnings pile up. Check with `curl -s https://api.github.com/repos/<action>/releases/latest`.

## Building blocks

### 1. Dockerfile

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

# Lint and tests (dev compose `test` service). Tool versions pinned to the local ones.
FROM base AS test
COPY requirements.txt ./
RUN pip install -r requirements.txt && pip install pytest==X ruff==Y black==Z
COPY . .
CMD ["sh", "-c", "<lint> && <format check> && <tests>"]

FROM base AS runtime
RUN useradd --system --uid 10001 --create-home app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
# Drop test-only files and scripts the server doesn't need; code read-only for the app user
RUN rm -rf tests \
    && find scripts -type f ! -name apply_migrations.py -delete && find scripts -type d -empty -delete \
    && chmod -R a+rX,go-w .
# Writable data dirs (bind-mounted in production)
RUN mkdir -p instance && chown app:app instance
ARG APP_VERSION=""
ENV APP_VERSION=${APP_VERSION} FLASK_ENV=production
USER app
EXPOSE 8000
ENTRYPOINT ["sh", "docker/entrypoint.sh"]
CMD ["gunicorn", "<module>:<app or factory()>", "--config", "gunicorn.conf.py"]
```

- **Order:** install dependencies before `COPY . .`, so code changes don't reinstall everything.
- **Build-time settings:** steps that need settings at build time (e.g. collecting static files) get a dummy value, with a comment saying it's never used at runtime.
- **Compiled apps (Go etc.):** a single stage that builds the binary is enough; pass the version with `-ldflags "-X main.commit=${GIT_SHA}"`.

`docker/entrypoint.sh`:
```sh
#!/bin/sh
set -e
<run migrations>          # fails -> container stops, never serves a half-migrated schema
exec "$@"
```

`gunicorn.conf.py`:
```python
import os
bind = "0.0.0.0:8000"
workers = int(os.environ.get("GUNICORN_WORKERS", "2"))   # 2 on a Pi
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "120"))
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(t)s "%(m)s %(U)s %(H)s" %(s)s %(b)s %(L)ss'   # %(U)s: no query string
```

### 2. .dockerignore (allow-list)

A block-list misses things like a database dump or a backups folder lying in the checkout. Allow only what the image needs:

```
*
!app/
!migrations/
!requirements.txt
!gunicorn.conf.py
!docker/entrypoint.sh
!scripts/
!tests/              # test stage only; removed in runtime
**/__pycache__
scripts/database/backups
<large local clutter under allowed folders>
```

### 3. Dev docker-compose.yml (repo root)

Add the app next to the existing dev database, behind profiles so `docker compose up db` doesn't start them:

```yaml
  web:
    build: {context: ., target: runtime}
    image: ${WEB_IMAGE:-app-web:local}
    env_file: .env
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}   # the dev .env says localhost
    ports: ["127.0.0.1:${WEB_PORT:-8000}:8000"]
    depends_on: {db: {condition: service_healthy}}
    profiles: [web]

  test:
    build: {context: ., target: test}
    environment:
      TEST_DATABASE_URL: postgresql://...@db:5432/app_test
      CI: "true"                       # skip tests that need the developer environment
    depends_on: {db: {condition: service_healthy}}
    profiles: [test]
```

If the project already has a Makefile workflow, add `docker-*` targets instead of renaming existing ones:
- `docker-build` (pass `--build-arg APP_VERSION=$(git describe --tags)`)
- `docker-up` (build, `up -d --wait`)
- `docker-logs`
- `docker-check` (`--profile test run --rm --build test`)

### 4. Production deploy/docker-compose.yml

```yaml
services:
  db:
    image: postgres:17-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in .env}
    volumes: [db-data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      retries: 20
    logging: &logging
      driver: json-file
      options: {max-size: "10m", max-file: "3"}

  web:
    image: ${WEB_IMAGE:?Set WEB_IMAGE in .env}
    restart: unless-stopped
    env_file: .env
    environment:
      DATABASE_URL: postgresql://app:${POSTGRES_PASSWORD}@db:5432/app   # password: letters and digits (goes into a URL)
    ports: ["127.0.0.1:${WEB_PORT:-8000}:8000"]
    volumes: [./data/instance:/app/instance]   # owned by uid 10001: sudo chown -R 10001:10001 data/instance
    # A TCP connect proves the server accepts requests without adding lines to the access log
    healthcheck:
      test: ["CMD", "python", "-c", "import socket; socket.create_connection(('127.0.0.1', 8000), 2)"]
      interval: 10s
      retries: 20
    depends_on: {db: {condition: service_healthy}}
    logging: *logging

volumes:
  db-data:
```

- **Required settings:** `${VAR:?}`; secrets never get defaults.
- **Optional settings:** `${VAR:-}`, with a comment saying what an empty value means.
- **No `container_name`:** the folder name keeps apps apart. After removing a service, run `up --remove-orphans` once.
- **Stateless apps:** add `read_only: true`, `tmpfs: [/tmp]`, `security_opt: [no-new-privileges:true]` and `cap_drop: [ALL]`.

### 5. deploy/.env.example

This is the only place for settings. One comment per variable, and secrets say how to generate them:

```sh
# Copy to .env next to docker-compose.yml (chmod 600). Never commit .env.
# Generate with: python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=replace-with-a-long-random-value
POSTGRES_PASSWORD=replace-with-letters-and-digits
CALLBACK_URL=https://app.example.com/login
GUNICORN_WORKERS=2
# Image to run (CI publishes ghcr.io/<github owner>/<app>-web); pin a SHA tag to roll back
WEB_IMAGE=ghcr.io/<github-owner>/<app>-web:latest
WEB_PORT=8000
BACKUP_KEEP_DAYS=14
# Optional off-site copy over ssh (key login): user@host or an ssh alias; empty = local only
BACKUP_REMOTE=
BACKUP_REMOTE_DIR=backup/<app>
BACKUP_REMOTE_KEEP_DAYS=30
```

### 6. update.sh and backup.sh

Scripts read single keys from `.env` with `sed`. Sourcing `.env` would break on secrets that contain shell characters.

```sh
#!/bin/sh
# update.sh: cron */15. Back up before a new image (it may migrate), then restart.
set -e
cd "$(dirname "$0")"
image=$(sed -n 's/^WEB_IMAGE=//p' .env | tail -n 1)
docker compose pull -q web
latest=$(docker image inspect -f '{{.Id}}' "$image")
running=$(docker inspect -f '{{.Image}}' "$(docker compose ps -q web)" 2>/dev/null || true)
# Compare with the RUNNING container, not "did the pull change something":
# a run that failed after pulling (e.g. backup) is then retried next time.
if [ "$running" != "$latest" ]; then
    ./backup.sh
    docker compose up -d --wait
    docker image prune -f >/dev/null
fi
```

```sh
#!/bin/sh
# backup.sh: cron nightly, and from update.sh.
set -e
cd "$(dirname "$0")"
umask 077
setting() { sed -n "s/^$1=//p" .env | tail -n 1; }
remote=$(setting BACKUP_REMOTE)
keep=$(setting BACKUP_KEEP_DAYS)
mkdir -p backups
file="backups/app_$(date +%Y-%m-%d_%H%M).sql.gz"
docker compose exec -T db pg_dump -U app -d app --no-owner | gzip > "$file.tmp" && mv "$file.tmp" "$file"
find backups -name "app_*.sql.gz" -mtime +"${keep:-14}" -delete
if [ -n "$remote" ]; then
    dir=$(setting BACKUP_REMOTE_DIR)
    ssh -o BatchMode=yes "$remote" "mkdir -p $dir" && scp -q "$file" "$remote:$dir/"
fi
```

For stateless apps, `update.sh` is just `pull -q`, `up -d` and `image prune -f`.

### 7. CI: check, then publish

Keep the existing test and lint jobs if they work. Add the image job after them; pull requests only build, `main` also pushes:

```yaml
  docker:
    needs: [lint, test]
    runs-on: ubuntu-latest
    permissions: {contents: read, packages: write}
    env:
      PUBLISH: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    steps:
      - uses: actions/checkout@v7
        with: {fetch-depth: 0}                       # tags, for git describe
      - run: <generate git-derived files>            # the image has no .git
      - id: meta
        run: |
          echo "image=ghcr.io/${GITHUB_REPOSITORY_OWNER,,}/<app>-web" >> "$GITHUB_OUTPUT"
          echo "version=$(git describe --tags)" >> "$GITHUB_OUTPUT"
      - uses: docker/login-action@v4
        if: env.PUBLISH == 'true'
        with: {registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}"}
      - uses: docker/setup-qemu-action@v4            # arm64 on the x86 runner
      - uses: docker/setup-buildx-action@v4
      - uses: docker/build-push-action@v7
        with:
          context: .
          target: runtime
          build-args: APP_VERSION=${{ steps.meta.outputs.version }}
          platforms: linux/amd64,linux/arm64
          push: ${{ env.PUBLISH == 'true' }}
          tags: |
            ${{ steps.meta.outputs.image }}:latest
            ${{ steps.meta.outputs.image }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

- **Image names:** must be lowercase (`,,`).
- **Rollback:** the SHA tag is what you roll back to.
- **Platforms:**
  - amd64 and arm64 cover PCs and a Pi with a 64-bit OS (`uname -m` → `aarch64`).
  - Add `linux/arm/v7` only if every dependency has 32-bit ARM builds. psycopg2/psycopg has none; a static Go binary is fine.
- **Package access:** a new ghcr package may be private. Make it public, or run `docker login ghcr.io` on the server with a `read:packages` token.

## Checking a CI run and the published image

- **Run and jobs:**
  - `curl -s https://api.github.com/repos/<owner>/<repo>/actions/runs/<id>/jobs` shows each step's conclusion.
  - `.../check-runs/<job id>/annotations` shows the warnings (e.g. deprecated Node versions).
- **Anonymous pull works?**
  ```sh
  TOKEN=$(curl -s "https://ghcr.io/token?scope=repository:<owner>/<app>-web:pull" | python3 -c "import json,sys; print(json.load(sys.stdin)['token'])")
  curl -s -H "Authorization: Bearer $TOKEN" -H "Accept: application/vnd.oci.image.index.v1+json" https://ghcr.io/v2/<owner>/<app>-web/manifests/latest
  ```
  Expect amd64 and arm64. Extra `unknown/unknown` entries are build attestations, which is normal.
- **Inside the image:**
  - `docker image inspect` the user, entrypoint and env (`APP_VERSION`);
  - `docker run --rm --entrypoint sh <image> -c 'ls -la /app; find scripts -type f'`: there should be no `.env`, `.git`, tests, dumps, backups or dev scripts.

## Server day-to-day (in `<app dir>`)

| Task | Command |
|---|---|
| Deploy now | `./update.sh` (cron does it within 15 min of CI publishing) |
| Roll back | `WEB_IMAGE=...:<good sha>` in `.env`, then `docker compose up -d` (restore the pre-deploy backup if a migration ran) |
| Logs / status | `docker compose logs -f web` / `docker compose ps` |
| Backup now | `./backup.sh` |
| Restore | `docker compose stop web`, empty the database, `gunzip -c backups/<file> \| docker compose exec -T db psql -U app -d app`, `docker compose start web` |
| One-off command | `docker compose exec web <cmd>` / `docker compose run --rm web <cmd>` |

`docker compose down` keeps named volumes. **`down -v` deletes the database: never run it in production.**

## Moving an existing app (with live data) onto this

The database is the one thing that must not break.

1. **Look first (read-only).** On the server, check:
   - the architecture, Docker and compose versions, and free disk and memory;
   - how the app runs now (systemd unit, port) and what the reverse proxy points at;
   - the cron jobs (backups, log rotation) and the database version and size;
   - the folders the app writes to (caches, uploads);
   - the PostgreSQL image version already cached for other apps.
2. **Build in parallel.** Add the Dockerfile, compose files, deploy folder and CI next to the old deploy. Get the checks green, and the image published.
3. **Rehearse locally with a production copy.** Take a fresh dump (read-only on production):
   ```sh
   ssh <server> 'sudo -u postgres pg_dump --no-owner --no-privileges <db>' | gzip > prod.sql.gz
   ```
   Restore it into a fresh `db` with `psql -v ON_ERROR_STOP=1`. Then:
   - compare every table's row count, and check that each sequence is ≥ its column's max id;
   - start `web` (migrations must run) and open every page as a real user;
   - check that a backup in `backup.sh`'s format restores into a scratch database.

   Delete the copy afterwards: it contains user data.

   ```sql
   -- table_counts.sql: "table|count" per table; diff the output of old and new
   SELECT string_agg(format('SELECT %L, count(*) FROM %I', tablename, tablename), ' UNION ALL ' ORDER BY tablename) AS q
   FROM pg_tables WHERE schemaname = 'public' \gset
   :q
   ```
   Recent `pg_dump` builds write `\restrict` lines that older `psql` rejects. Restore with the same `postgres` image version the server will use.
4. **Dry run on the server, next to the live site.** Use a second port (`WEB_PORT=5001`): restore, compare counts, start, `curl`, run `./backup.sh` once. Then empty the database again (`DROP DATABASE ... WITH (FORCE)` / `CREATE DATABASE`).
5. **Switch.** The site is down for a minute or two:
   - stop the old service, so nothing writes any more;
   - dump, restore with `ON_ERROR_STOP`, and diff the row counts;
   - copy the data folders, then `chown 10001`;
   - set the old port and `up -d --wait`.

   Keep the old `SECRET_KEY` (sessions stay valid) and the CHPP/OAuth `CALLBACK_URL`. Keep the cut-over dump somewhere safe (`chmod 600`: it has user data).

   **Run the switch as a script file on the server** (`scp` it, then `bash cutover.sh </dev/null`), with `set -euo pipefail` and a `trap ... ERR` that stops `web` and restarts the old service. Never pipe a script over `ssh ... 'bash -s' <<EOF`: `docker compose exec -T` forwards stdin, so the first `exec` silently swallows the rest of the script.
6. **Rollback:** `docker compose stop web` and re-enable the old service. The old database was never changed; only data written since the switch is lost.
7. **Make it permanent:**
   - disable the old service (it must not take the port on reboot);
   - save the old crontab, then replace its lines with `backup.sh` and `update.sh`, using absolute paths and `PATH=/usr/local/bin:/usr/bin:/bin`;
   - test `update.sh` the way cron runs it: `env -i HOME=$HOME PATH=/usr/local/bin:/usr/bin:/bin ./update.sh`.
   - Also check that the old backup job actually worked; it may have been failing quietly.
8. **After a couple of weeks:**
   - remove the old checkout, unit and database (dump once more first), plus the old deploy scripts and targets;
   - make DEPLOYMENT.md Docker-only.

## Checklist

- [ ] No personal hostnames, paths or domains in the repo; they live in the server's `.env`
- [ ] `.dockerignore` is an allow-list; the image has no `.env`, `.git`, tests, dumps or dev scripts
- [ ] Image runs as a non-root user; code readable (`chmod a+rX`) but not writable
- [ ] Version (`APP_VERSION`) and git-derived files come from CI
- [ ] Production dependencies installed from a lock or pinned file; test tools pinned
- [ ] Migrations run in the entrypoint, and a failure stops the container
- [ ] Healthchecks on `db` and `web`; `web` waits for a healthy `db`; log size limits
- [ ] CI publishes `latest` + SHA for amd64/arm64 after the tests, with current action versions
- [ ] The port is bound to `127.0.0.1` behind the reverse proxy
- [ ] `update.sh` backs up before a new image and retries after failures; `backup.sh` runs nightly
- [ ] Cut-over rehearsed on a production copy (counts, sequences, every page, backup restore) and on the server next to the live site
