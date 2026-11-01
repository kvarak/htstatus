# Project Progress

Current status only. History lives in Git (`git log`) and [CHANGELOG.md](../CHANGELOG.md).

## Status (October 2026)

- **App**: Flask blueprints + Jinja2/Bootstrap 4 templates, PostgreSQL, custom CHPP client. Runs as a Docker image (published by CI) on a Raspberry Pi; cron deploys new images after a database backup (see [DEPLOYMENT.md](../DEPLOYMENT.md)).
- **Tests**: ~475 pytest tests plus Node unit tests (`node --test tests/js/`), ~73% coverage; every template is compile-checked; CI runs lint, file format, CHPP policy and the full suite on PostgreSQL. Tests needing a developer environment are marked `local_only`.
- **CHPP policy**: Only login, OAuth callback and `/update` call Hattrick (`make check-chpp`).
- **Quality gates**: `make test-all` runs tests, file format, lint, template lint, bandit and the CHPP check and prints a summary.
- **Backlog**: Code-health items in [backlog.md](backlog.md) (split `utils.py`, drop `setup_*` globals, long routes, overlapping test files); feature ideas in [features.md](features.md).

## Recent work (October-November 2026)

- Production moved to Docker (INFRA-090): gunicorn image on ghcr.io, PostgreSQL 17 container, automatic deploys with a backup first, nightly off-site backups (the old backup job had never worked); old systemd/git-checkout deploy and its scripts removed.
- Deep cleanup: removed dead routes/pages, functions, CHPP endpoints, JS, CSS and existence-only tests; one `current_team()` lookup for all pages; stats page logic moved to `app/team_stats.py`; fixed the crashing update error page and the welcome tour.
- Fixed sold players staying in the team, non-atomic team updates, sessions without a user row, unbounded error log, formation rating and tactical position weights.
- Refactored the update and login flows, roster/timeline queries, activity tracking and changelog rendering; removed the model registry and Flask-Bootstrap.
- Trimmed tooling and docs for hobby scale (no Redis, no quality-intelligence reporting, one docker-compose file, rewritten DEPLOYMENT.md).
