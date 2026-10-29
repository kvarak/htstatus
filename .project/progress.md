# Project Progress

Current status only. History lives in Git (`git log`) and [CHANGELOG.md](../CHANGELOG.md).

## Status (October 2026)

- **App**: Flask blueprints + Jinja2/Bootstrap 4 templates, PostgreSQL, custom CHPP client. Runs on a Raspberry Pi (see [DEPLOYMENT.md](../DEPLOYMENT.md)).
- **Tests**: ~525 tests (incl. Node unit tests for chart date filtering), ~67% coverage; CI runs lint, file format, CHPP policy and the full suite on PostgreSQL. Tests needing a developer environment are marked `local_only`.
- **CHPP policy**: Only login, OAuth callback and `/update` call Hattrick (`make check-chpp`).
- **Quality gates**: `make test-all` runs tests, file format, lint, template lint, bandit and the CHPP check and prints a summary.
- **Backlog**: Nothing open in [backlog.md](backlog.md); feature ideas in [features.md](features.md).

## Recent work (October 2026)

- Fixed sold players staying in the team, non-atomic team updates, sessions without a user row, unbounded error log, formation rating and tactical position weights.
- Refactored the update and login flows, roster/timeline queries, activity tracking and changelog rendering; removed the model registry and Flask-Bootstrap.
- Trimmed tooling and docs for hobby scale (no Redis, no quality-intelligence reporting, one docker-compose file, rewritten DEPLOYMENT.md).
