---
name: docker-hosting
description: 'Host and deploy a hobby web app with Docker Compose: a multi-stage Dockerfile, one docker-compose.yml for dev, CI and production, Makefile wrappers, and a GitHub Actions job that publishes a multi-arch image to ghcr.io. The server (usually a Raspberry Pi behind an HTTPS reverse proxy) only pulls and restarts. Use when containerizing an app, setting up or changing deployment/hosting, adding a database service, or moving an existing app (with live data) off a git-checkout/systemd deploy.'
license: MIT
---

# Docker hosting

## Overview

The server runs `docker compose`. It never builds the app, runs a package manager or keeps a git checkout of it. CI builds and tests the image, then publishes it to GitHub Container Registry. A deploy pulls the new image and restarts the container; a rollback pins an older tag.

The same `docker-compose.yml` is used for local development (built locally), for CI checks (a `test` profile) and in production (with the published image). Keep it simple: this is a hobby setup on one machine, not Kubernetes.

## When to use

- A new app needs to run somewhere ("how do I host this?")
- Containerizing an existing app, or replacing a git pull + venv + systemd deploy
- Adding a database or another service to a compose setup
- CI should publish an image for a Raspberry Pi

## Two shapes

| | Stateless app | App with a database |
|---|---|---|
| Services | `app` only | `db` + `web` (+ `test` profile) |
| Dockerfile | single stage is fine | stages `base` → `test` and `runtime` |
| Data | none | named volumes (database, uploads) |
| Start-up | the server | entrypoint: migrations, then `exec` the server |

Start from the stateless shape and add only what the app needs.

## Building blocks

### 1. Dockerfile (multi-stage when there is a test stage)

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

FROM base AS test
COPY requirements.txt requirements-dev.txt ./
RUN pip install -r requirements.txt -r requirements-dev.txt
COPY . .
CMD ["sh", "-c", "<lint> && <format check> && <tests>"]

FROM base AS runtime
RUN useradd --system --uid 10001 --create-home app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
# .git is not in the build context, so the version comes in as a build arg
ARG GIT_SHA=""
ENV GIT_SHA=${GIT_SHA}
USER app
EXPOSE 8000
ENTRYPOINT ["sh", "docker/entrypoint.sh"]
CMD ["gunicorn", "<module>:app", "--config", "gunicorn.conf.py"]
```

- **Dependencies:** install them before `COPY . .` so code changes don't reinstall everything.
- **Build-time setup:** steps that need settings during the build (e.g. collecting static files) get a dummy value, marked in a comment as never used at runtime.
- **Writable paths:** create them (`mkdir` + `chown app`) before `USER app`, and mount a volume there.
- **Python apps:** run a real WSGI server (gunicorn), never the dev server.
- **Workers:** `gunicorn.conf.py` reads `GUNICORN_WORKERS` from the environment (2 on a Pi), logs to stdout and stderr, and redacts secrets from request paths if URLs carry them.
- **Go and other compiled apps:** a single stage that builds the binary is fine; pass the version with `-ldflags "-X main.commit=${GIT_SHA}"`.

`docker/entrypoint.sh`:

```sh
#!/bin/sh
set -e
<run migrations>          # fails -> container stops, never serves a half-migrated schema
exec "$@"
```

### 2. .dockerignore

Keep secrets and clutter out of the build context and the image:

```
.git
.env
.env.*
!.env.example
**/__pycache__
.venv
.pytest_cache
.ruff_cache
htmlcov
Dockerfile
docker-compose.yml
Makefile
plan.md
<local data, media, large unused assets>
```

### 3. docker-compose.yml

```yaml
services:
  db:
    image: postgres:17-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-app}
      POSTGRES_USER: ${POSTGRES_USER:-app}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Set POSTGRES_PASSWORD in .env}
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U \"$$POSTGRES_USER\" -d \"$$POSTGRES_DB\""]
      interval: 5s
      timeout: 3s
      retries: 20

  web:
    build:
      context: .
      target: runtime
    image: ${WEB_IMAGE:-app-web:local}
    restart: unless-stopped
    env_file: .env
    environment:
      POSTGRES_HOST: db
      # Optional features are off unless set, e.g. analytics:
      GOATCOUNTER_URL: ${GOATCOUNTER_URL:-}
    ports:
      - "127.0.0.1:8000:8000"     # only the local reverse proxy reaches it
    # A TCP connect proves the server accepts requests without adding lines to the access log
    healthcheck:
      test: ["CMD", "python", "-c", "import socket; socket.create_connection(('127.0.0.1', 8000), 2)"]
      interval: 5s
      timeout: 3s
      retries: 20
    depends_on:
      db:
        condition: service_healthy

  # Lint and tests. Only started by `make check`.
  test:
    profiles: ["test"]
    build:
      context: .
      target: test
    image: app-test:local
    env_file: .env
    environment:
      POSTGRES_HOST: db
    depends_on:
      db:
        condition: service_healthy

volumes:
  db-data:
```

- **Required secrets:** use `${VAR:?message}`; never give a password a default.
- **Optional settings:** use `${VAR:-}`, with a comment saying what an empty value means.
- **`image:` next to `build:`:** development builds `*:local`, and production sets `WEB_IMAGE` to the ghcr.io tag and runs with `--no-build`.
- **Ports:** bind to `127.0.0.1` when a reverse proxy (with HTTPS) runs on the same host. A stateless app that is published directly can map a plain port (`"8080:8080"`).
- **Dev-only tools** (pgAdmin and the like) go behind their own profile.
- **No `container_name`:** the compose project name keeps containers apart. When a service is removed, run `up --remove-orphans` once.

### 4. .env.example

This is the only configuration file. Copy it to `.env` (gitignored) and fill it in. Every variable gets a one-line comment, and secrets say how to generate them:

```sh
# Copy to .env and fill in real values. Never commit .env.
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(50))"
SECRET_KEY=replace-with-a-long-random-value
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=replace-with-a-database-password
# Optional self-hosted GoatCounter pageview tracking. Leave empty to turn it off.
GOATCOUNTER_URL=
GUNICORN_WORKERS=3
# Image run by `docker compose up`. Set to a ghcr.io image to run the published build.
WEB_IMAGE=app-web:local
```

### 5. Makefile (thin wrappers, same commands everywhere)

```make
COMPOSE ?= docker compose
.PHONY: serve stop check migrate logs deploy

# Ctrl+C stops following the logs; the services keep running until `make stop`.
serve: .env
	$(COMPOSE) up -d --build --wait
	$(COMPOSE) logs -f --tail=20

stop: .env
	$(COMPOSE) stop

check: .env
	$(COMPOSE) --profile test run --rm --build test

migrate: .env
	$(COMPOSE) run --rm web <migrate command>

logs: .env
	$(COMPOSE) logs -f

# On the server: run the published image (WEB_IMAGE in .env).
deploy: .env
	$(COMPOSE) pull web
	$(COMPOSE) up -d --no-build --wait

.env:
	@echo "Missing .env. Run: cp .env.example .env, then edit it." && exit 1
```

### 6. CI: check, then publish (`.github/workflows/<app>.yml`)

```yaml
name: <app>
on:
  pull_request:
  push:
    branches: [main]
permissions:
  contents: read

jobs:
  check:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - run: cp .env.example .env
      - run: make check              # the same command as locally

  publish:
    needs: check
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - id: image
        run: echo "name=ghcr.io/${GITHUB_REPOSITORY_OWNER,,}/<app>-web" >> "$GITHUB_OUTPUT"
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      # QEMU emulates arm on the x86 runner so one image runs on PCs and Raspberry Pis
      - uses: docker/setup-qemu-action@v3
      - uses: docker/setup-buildx-action@v3
      - uses: docker/build-push-action@v6
        with:
          context: .
          target: runtime
          build-args: GIT_SHA=${{ github.sha }}
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ${{ steps.image.outputs.name }}:latest
            ${{ steps.image.outputs.name }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

- **Image names:** must be lowercase, hence the `,,`.
- **Tags:** `latest` plus the commit SHA. The SHA tag is what you roll back to.
- **Platforms:**
  - `linux/amd64` and `linux/arm64` cover a normal server and a Pi with a 64-bit OS (`uname -m` prints `aarch64`).
  - Add `linux/arm/v7` (32-bit Pi OS) only if every dependency builds there. psycopg2/psycopg has no 32-bit ARM wheels, so database-backed Python apps are 64-bit only. A static Go binary works fine.
- **Package access:** a new ghcr package is private. Either make it public in the package settings, or run `docker login ghcr.io` once on the server with a token that has `read:packages`.

## Server set-up and day-to-day

Fresh server (64-bit OS):

1. Install Docker and the compose plugin.
2. Put `docker-compose.yml` and `.env` in one directory, and set `WEB_IMAGE=ghcr.io/<owner>/<app>-web:latest`.
3. Run `docker compose pull && docker compose up -d --no-build --wait`.
4. Point the reverse proxy at `127.0.0.1:<port>`:
   - pass `Host` and `X-Forwarded-Proto`;
   - raise the body size limit if the app takes uploads (nginx: `client_max_body_size`).

| Task | Command |
|---|---|
| Deploy | `make deploy` (pull + `up -d --no-build`) |
| Roll back | `WEB_IMAGE=...:<previous sha>` in `.env`, then `make deploy` |
| Logs | `docker compose logs -f web` |
| Shell / one-off command | `docker compose exec web <cmd>` / `docker compose run --rm web <cmd>` |
| Database backup | `docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql` |
| Database restore | `docker compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB" < backup.sql` |

`docker compose down` keeps the named volumes. `down -v` deletes the data: never run it in production.

## Moving an existing app (with live data) onto this

The database is the one thing that must not break.

1. **Build in parallel.** Add the Dockerfile, compose file, `.env.example`, Makefile and CI next to the old deploy. Get `make check` green locally and on CI, and the image published.
2. **Rehearse.** Restore a production dump into a local `db` container, start `web` against it, and click through the app. Migrations must run cleanly on the copy.
3. **Cut over.**
   - Stop the old service.
   - Take a fresh backup with the existing backup tooling.
   - Restore it into the new `db` volume, and compare row counts for the main tables between the old and new databases.
   - Start `web`, then switch the reverse proxy to it.
4. **Keep the old setup.** Leave the old database and service files untouched (just stopped) until the new setup has run for a while.
5. **Backups.** Point nightly backups (cron) and their off-site copy at the container (`docker compose exec -T db pg_dump ...`). Test a restore once.
6. **Clean up.** Remove the old deploy scripts and Makefile targets, the systemd unit and the server-side tool installs. Update the deployment docs (DEPLOYMENT.md, README and architecture notes) in the same change.

## Checklist

- [ ] `make serve` works from a fresh clone after `cp .env.example .env`
- [ ] `make check` passes locally and on CI with the same command
- [ ] Image runs as a non-root user; `.env`, `.git` and tests are not in the runtime image
- [ ] Required secrets use `${VAR:?}`; optional features are off when empty
- [ ] Healthchecks on `db` and `web`; `web` waits for a healthy `db`
- [ ] Migrations run in the entrypoint, and a failure stops the container
- [ ] CI publishes `latest` + SHA for amd64/arm64 (arm/v7 only if all dependencies support it)
- [ ] The port is bound to `127.0.0.1` behind the reverse proxy
- [ ] Deploy, rollback, logs, backup and restore are each one documented command
- [ ] Data lives in named volumes, and nightly backups run against the container
