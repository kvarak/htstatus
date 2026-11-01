# Scripts

Most scripts are run through the Makefile (`make help`). Run scripts from the project root; Python scripts with `uv run python ...`.

| Script | Used by | Purpose |
|---|---|---|
| `run.sh` | manual | Start the Flask server (production-style) |
| `changelog.sh` | `make changelog` | Build `app/static/changelog*.json` for the Changes page |
| `check-chpp-usage.sh` | `make check-chpp`, CI | Fail if CHPP is called outside login/OAuth/update |
| `get-next-task-id.sh` | manual | Next free task ID, e.g. `./scripts/get-next-task-id.sh BUG` |
| `release/detect_version_changes.sh` | `make release-detect` | Checks whether commits since the last tag warrant a release |
| `deployment/deploy.sh` | `make deploy` | Deploy to the Pi over SSH |
| `database/*` | `make db-*` | Backups, restore, migrations, user cleanup, error log CLI; see [database/README.md](database/README.md) |
