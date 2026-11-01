# INFRA-090: Production with Docker Compose

## Problem

Production runs from a git checkout on the Raspberry Pi: `deploy.sh` SSHes in, runs `git reset --hard`, `uv sync`, migrations and `systemctl restart`, against a PostgreSQL installed on the host. Every deploy builds the environment on the Pi, the service file and tools (uv, jq) are set up by hand, and the setup is hard to reproduce or move to another machine.

## Goal

The server only needs Docker. A deploy means pulling a new image and restarting the containers.

## Approach

Follow the `docker-hosting` skill (`.github/skills/docker-hosting/SKILL.md`), including its "Moving an existing app" steps.

### One compose file for development, CI and production

`docker-compose.yml` has these services:
- `db`:
  - PostgreSQL in a named volume, with a `pg_isready` healthcheck
  - `POSTGRES_PASSWORD` is required from `.env` (`${POSTGRES_PASSWORD:?...}`), so no default password reaches production
- `web`:
  - the app, built from the Dockerfile's `runtime` stage
  - `image: ${WEB_IMAGE:-htstatus-web:local}`: development builds locally, while production sets `WEB_IMAGE` to the published image and starts with `--no-build`
  - `env_file: .env`, `restart: unless-stopped`, published on `127.0.0.1:<port>` only (the reverse proxy in front adds HTTPS)
  - a TCP healthcheck (it doesn't add lines to the access log)
  - waits for `db` to be healthy
- `test`, under a `test` profile: lint and tests against the same `db`

The dev-only pgAdmin can stay as an opt-in profile.

### Multi-stage Dockerfile

- `base`: slim Python with production settings (no `.pyc`, unbuffered output)
- `test`: production and dev dependencies plus the code; runs ruff, black, djlint and pytest
- `runtime`:
  - production dependencies only
  - a non-root user
  - the git version passed in as a build arg, since `.git` is not in the image (the footer and changelog use it)
- **Entrypoint**: runs `scripts/database/apply_migrations.py` and then `exec`s the server, so migrations run on every start and a failed migration stops the container
- **Server**: gunicorn with a `gunicorn.conf.py`; the number of workers comes from `GUNICORN_WORKERS` (2 on the Pi)
- **.dockerignore**: keeps out tests (runtime stage only), docs, `htmlcov/`, `.venv/`, `.env` and local clutter

### Makefile

These targets are thin wrappers around `docker compose`:

| Target | What it runs |
|---|---|
| `serve` | `up -d --build --wait`, then follow the logs |
| `stop` | stop the services |
| `check` | the test service: lint and tests |
| `migrate` | run the migrations by hand |
| `logs` | follow the logs |
| `deploy` | on the server: `pull web && up -d --no-build` |

Each target fails with a clear message when `.env` is missing (`cp .env.example .env`).

### CI (GitHub Actions)

- **`check` job**: copies `.env.example` to `.env` and runs `make check`, the same command as locally
- **`publish` job**:
  - runs only on pushes to `main`, after `check` passes
  - builds the `runtime` stage for `linux/amd64` and `linux/arm64` with QEMU and Buildx
  - pushes `ghcr.io/kvarak/htstatus-web` with the tags `latest` and the commit SHA
- **No 32-bit ARM image**: psycopg2 has no 32-bit ARM build, so the Pi needs a 64-bit OS (`uname -m` prints `aarch64`)
- **Package access**: the ghcr package is either public, or the Pi logs in once with a `read:packages` token

### Deploy and rollback

- **Deploy**: `make deploy` on the Pi (or over SSH) pulls the image and restarts it
- **Rollback**: set `WEB_IMAGE=...:<previous SHA>` and restart
- **Removed**: `deploy.sh`, the `deploy-*` targets, the systemd unit and the uv/jq set-up on the Pi
- **Docs**: DEPLOYMENT.md (production `.env` settings, deploy, rollback, logs with `docker compose logs`), README.md and `.project/architecture.md`

## Database safety (must not break)

- **Cut-over**:
  - stop the old service and back up with `make db-backup`
  - restore the dump into the new postgres container
  - check the row counts against the old database before switching traffic
  - keep the old host database untouched until the new setup has run for a while
- **Backups**: the nightly backup and its copy to kloker keep working against the container (`docker compose exec postgres pg_dump`, or the backup script pointed at the container)
- **Data**: the database lives in a named volume (or a host path) that `docker compose down` does not delete; document that `down -v` deletes it
- **Migrations**: run in one place only (app start-up); a failed migration stops the app instead of starting it on a half-migrated schema

## Acceptance criteria

- A fresh 64-bit Pi with Docker runs the site from `docker-compose.yml` and `.env` alone
- `make check` gives the same result locally and on CI; CI publishes amd64 and arm64 images on every push to `main`
- Deploy and rollback are each one command and are documented in DEPLOYMENT.md
- Production data is migrated with verified counts, and the nightly backups still run
- `make test-all` passes; the local dev setup still works
