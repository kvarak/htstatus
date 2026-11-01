# HattrickPlanner – Copilot Instructions

Hobby Flask + PostgreSQL app for Hattrick managers (uses the Hattrick CHPP API). Good enough is perfect: simple, reliable, no enterprise patterns.

**Workspace layout:** the VS Code workspace root is the folder *above* the repo. The git repo is `htstatus-2.0/`; run `git`, `make`, `uv` and `./scripts/...` from there. All paths and links below are relative to the repo (`.github` in the workspace root is a symlink to `htstatus-2.0/.github`). `tmp/` in the workspace root is local scratch space outside git (e.g. `tmp/img-ideas/` design references).

## Hard rules

- **git and ssh: read freely, change only with permission.** Read-only commands are fine: `git status`/`log`/`diff`/`show`/`grep`, and ssh to look at a server (`ls`, `cat`, `docker compose ps`/`logs`, read-only SQL, `pg_dump` to read a database). Anything that changes state needs the user's explicit permission for the task at hand: commits, staging, checkout/reset, tags, push, branch or ref changes, and on servers editing files, restarting services, `docker compose up/down`, crontab or database writes. The user commits and pushes.
- **No hidden memory in git.** Never create, read or rely on `refs/agents/*` (or any other custom refs, notes or stashes) to remember things between sessions. Durable notes belong in `.project/` files the user can see.
- **The production database comes first.** Schema changes only through reviewed Alembic migrations, tested on a production copy (see architecture.md). Never touch production without permission.
- **CHPP only at login/OAuth and the explicit Update.** Never on page views, settings, voting or admin checks (`make check-chpp` enforces it).
- **Nothing personal in the repo.** Hostnames, domains, user ids, backup hosts and similar go in `.env` (documented in `.env.example` / `deploy/.env.example`), never in code, scripts or docs.
- **No secrets in git**, and no history/archive files: git history is the archive.

## Read first

- [.project/architecture.md](../.project/architecture.md): layout, data model, CHPP and UI conventions, database rules
- [.project/goals.md](../.project/goals.md): what the project is for
- [.project/backlog.md](../.project/backlog.md) (improvements, bugs, refactors, tests, infra) and [.project/features.md](../.project/features.md) (new features); details in [.project/tasks/](../.project/tasks/)
- [DEPLOYMENT.md](../DEPLOYMENT.md): hosting (Docker on a small server), releasing, database safety
- Skills: [refactor](skills/refactor/SKILL.md), [docker-hosting](skills/docker-hosting/SKILL.md)

## Working

- Understand the whole flow before changing it; look at similar code first. Prefer removing and simplifying over adding.
- Small verified steps: the narrowest test first (`make test-single FILE=...`), `make test-all` before calling a task done. Use `uv` (`uv run python ...`) and `make` (`make help`).
- To check pages in the browser, log in locally as the `ADMIN_HT_ID` user from `.env` with their teams from the dev database (sign a Flask session cookie with `SECRET_KEY`), so no CHPP call is needed. Never open `/update` for this.
- Ask when a decision changes behaviour, data or scope. Don't guess game rules that might be wrong for some users.
- Routes: `@require_authentication`, `@track_activity("<page>")`, `get_current_user()` and `current_team()` from `app/auth_utils.py`; admin checks with `user.is_admin()`.
- UI: follow the conventions in architecture.md (one look, `page_header`, no hard-coded colors, Hattrick terms via `column_label`/`level_text`).
- New player table column: append it to `ALL_COLUMNS` in `app/constants.py` (never to `COLUMNS_BEFORE_AUTO_ADD`); everyone gets it once.
- Add a test when fixing a bug or changing behaviour. Tests needing the developer environment are marked `@pytest.mark.local_only`.
- Backlog and features: one line per item about a real problem and what "good enough" looks like; IDs from `./scripts/get-next-task-id.sh <TYPE>` (BUG, REFACTOR, TEST, INFRA, UI, FEAT, DOC). When done, delete the line and its `tasks/` file.
- Hattrick: the 7 core skills are keeper, defender, playmaker, winger, passing, scorer, set pieces; position contributions are `calculateContribution` / `best_position` in `app/utils.py`.
- When done: update the docs that describe what changed (architecture.md, DEPLOYMENT.md, README.md), and summarise what the user still has to do (commit, push, deploy).
- User-visible changes go into the next release notes (RELEASES.md, RELEASES-INTERNAL.md) when releasing; see DEPLOYMENT.md "Releasing".
