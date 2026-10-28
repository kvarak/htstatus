# HattrickPlanner – Copilot Instructions

Flask + PostgreSQL app for Hattrick team management (uses the CHPP API). Production runs on a Raspberry Pi ("glader pi").

Before non-trivial work, read the relevant docs below instead of guessing.

## Project management (`.project/`)

- [goals.md](../.project/goals.md): project objectives and success metrics
- [architecture.md](../.project/architecture.md): system structure, components, data flow
- [backlog.md](../.project/backlog.md): improvements, bug fixes, refactoring, tests, infra (P1–P3); add newly found issues here
- [features.md](../.project/features.md): planned new user-facing features (FEAT-/UI- items); never mix into the backlog
- [progress.md](../.project/progress.md): current status; update it when a task is completed
- [tasks/](../.project/tasks/): detailed specs per task ID (e.g. `FEAT-xxx.md`, `REFACTOR-xxx.md`)
- [prompts.json](../.project/prompts.json): UI/framework guidelines for AI assistants

## Repo root docs

- [README.md](../README.md): setup and quick start
- [TECHNICAL.md](../TECHNICAL.md): implementation patterns, design decisions, Hattrick ownership hierarchy
- [DEPLOYMENT.md](../DEPLOYMENT.md): production deployment and operations
- [CHANGELOG.md](../CHANGELOG.md), [RELEASES.md](../RELEASES.md), [RELEASES-INTERNAL.md](../RELEASES-INTERNAL.md): release history
- [docs/CHPP-ENFORCEMENT.md](../docs/CHPP-ENFORCEMENT.md): CHPP API usage policy (must be followed)
- [Makefile](../Makefile): the entry point for all tasks (`make help`)

## AI tooling (`.github/`)

- [agents/htplanner-ai-agent.md](agents/htplanner-ai-agent.md): full development and UI standards
- [skills/](skills/): project skills (e.g. `refactor`)

## Code map

- `app/factory.py`: app creation; `app/blueprints/`: routes (team update in `team.py`, player list in `player.py`)
- `app/chpp/`: custom CHPP client; `app/utils.py`: shared helpers
- `models.py`: SQLAlchemy models; `migrations/`: Alembic (`make db-migrate` / `make db-upgrade`)
- `tests/`: pytest against Postgres (`make services` first)

## Workflow

- Use `uv` and `make`: `make test-single FILE=tests/...`, `make test-python`, `make lint`, `make check-chpp`, `make test-all` (full quality gate)
- The `Players` table holds one row per player per `data_date`. `owner` is the team ID; players who leave get `owner=0` and `old_owner=<team>`
- Routes: use `@require_authentication`, `@track_activity("<page>")` and `get_current_user()` from `app/auth_utils.py` (never query the logged-in User by hand); admin checks use `user.is_admin()`
- Tests that need the developer environment (`.env`, git tags, local DB settings) are marked `@pytest.mark.local_only` and skipped on CI (`CI` env var)
- Update the matching `.project/` docs (backlog/features/progress/tasks) and `CHANGELOG.md` when behavior changes
- When a task is done, delete it from backlog.md/features.md and delete its `.project/tasks/` file. Never create history/archive files: Git history is the archive
