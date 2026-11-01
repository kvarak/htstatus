# HattrickPlanner Backlog

**Mindset**: Hobby project. Good enough is perfect. Only fix what actually bothers us (bugs, risk to the database, slowness we notice, code that's painful to change). No audits, no coverage-chasing, no process for its own sake.
**Scope**: Improvements, bug fixes, cleanup and infra. New features go in [features.md](features.md).
**Rule**: Pick whatever is most useful. When done, DELETE the line (and any `tasks/` file); Git history is the archive. Delete items that stop making sense, too.
**Task IDs**: `./scripts/get-next-task-id.sh <TYPE>` (BUG, REFACTOR, TEST, INFRA, UI, DOC). Estimates are optional.

---

## P1: Broken or risky 🔥

*Nothing right now*

## P2: Worth doing 🎯

- 🚀 **[INFRA-090]** Run production with Docker Compose: one compose file for dev, CI and production; CI publishes an amd64/arm64 image to ghcr.io, and the Pi runs app + PostgreSQL with `docker compose` instead of a git checkout, uv and systemd → [Details](tasks/INFRA-090.md)
- **[REFACTOR-121]** `app/utils.py` (~1460 lines) mixes match downloading/CHPP enhancement (`downloadMatches`, `downloadRecentMatches`, `fetch_enhanced_match_data`, `_process_matches_enhanced`) with small helpers; move the match download code to its own module so utils is just helpers
- **[REFACTOR-122]** Blueprints get `db`/columns through `setup_*_blueprint()` module globals (9 blueprints plus `initialize_utils`); import `db` and `app.constants` directly like `series`/`stats` do. Auth's injected `app`, `consumer_key` and `consumer_secret` are never read

## P3: When you're in that code anyway 🔧

- **[REFACTOR-120]** Feedback blueprint checks `access_key`/`current_user_id` by hand in 5 routes; use `@require_authentication` (and `get_current_user()`) like the other blueprints
- **[REFACTOR-123]** Route handlers of 110-170 lines (`main.settings`, `player.player`, `training.training`, `compare.compare_players`, `api.bulk_assign_players`, `main.admin`); pull the data preparation into tested helpers (like `app/team_stats.py`) when changing them
- **[TEST-119]** Overlapping test files (`test_utils`/`test_utils_simple`/`test_utils_coverage`/`test_utils_formatting`, `test_auth`/`test_auth_coverage`) with mock-heavy tests that pin implementation; merge per module and keep the behaviour tests

---

**Testing**: Add a test when fixing a bug or changing behaviour. No coverage targets beyond what CI already enforces (50%).
