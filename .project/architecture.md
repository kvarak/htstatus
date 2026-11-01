# HattrickPlanner Architecture

A Flask + PostgreSQL web app for Hattrick managers. It syncs a team's players and matches from the Hattrick CHPP API and shows player development, statistics, training, formations and the league table. Hosting: [DEPLOYMENT.md](../DEPLOYMENT.md).

## Layout

| Path | What |
|---|---|
| `app/factory.py` | App factory: config, extensions, blueprint registration |
| `app/blueprints/` | Routes by feature: `auth` (login/OAuth), `main` (home, settings, admin `/debug`, changes), `team` (the Update action), `player`, `stats`, `training`, `matches` (also formations), `series`, `compare`, `feedback` |
| `app/api/players.py` | JSON API (bulk group assignment) |
| `app/chpp/` | Own CHPP client: OAuth 1.0, XML parsing (`CHPP` in `client.py`) |
| `app/auth_utils.py` | `@require_authentication`, `get_current_user()`, `current_team()`, `@track_activity` |
| `app/roster.py`, `app/team_stats.py`, `app/utils.py` | Roster queries, stats calculations, shared helpers (`create_page`, `dprint`, contributions, match downloads) |
| `app/translations.py`, `app/instance_cache.py` | Hattrick's own terms per language, cached as JSON in `instance/` (also transfer bids and series data) |
| `models.py` | SQLAlchemy models (`User`, `Players`, `Team`, `Match`, `MatchPlay`, `Group`, `PlayerSetting`, `Feedback*`, `ErrorLog`, ...) |
| `migrations/` | Alembic migrations |
| `app/templates/`, `app/static/` | Jinja2 + Bootstrap 4 (CDN), CSS, Chart.js |
| `tests/` | pytest (PostgreSQL, CHPP mocked) and `tests/js/` (node --test) |
| `Dockerfile`, `deploy/` | Production image and the server's compose/update/backup files |

## Hattrick data model

- A **user** (Hattrick manager, `User.ht_id`) owns one or more **teams**; a team owns **players**.
- `Players` rows are snapshots: one row per player per Update (`data_date`); `Players.owner` is the team id, `0` once sold. `app/roster.py` gets the latest/oldest record per player.
- Session: `current_user_id` = user id, `all_teams` / `all_team_names` = the user's team ids and names. Never use a user id where a team id is expected.

## CHPP usage (rate-limited, expensive)

CHPP is called **only** at login/OAuth callback and on the explicit Update (`/update`). Page views, settings, voting and admin checks use the session and the database. `make check-chpp` (in `make test-all` and CI) enforces this.

## UI conventions

- One look, a flat "football poster": tokens in `:root` of `base.html`, Bootstrap remap in `static/css/theme.css`, dark mode in `dark-mode.css` (all rules under `html.dark-mode`, brown surfaces). Poster colors `--brown`, `--green`, `--sand`, `--cream`, `--orange` are the same in both modes; semantic tokens map onto them: green `--primary` for actions/our team, burnt orange `--accent2` for links/selection/info; red/amber only for errors and bad values. No hard-coded colors in templates. Flat: no gradients or shadows, small radius.
- Every page starts with `page_header` from `templates/_page.html` (a brown title tile); the footer comes from `_skeleton.html`.
- `_page.html` also has `icon(name)` (flat SVG icons from `static/img/icons.svg`, colored by the text color; use them instead of emoji in headings) and `scoreboard(home, away, home_goals, away_goals, us, meta)` for match headers. Big numbers use `.scoreboard-number` (Oswald, self-hosted in `static/fonts/`, OFL). Dashboard-style blocks use `.mosaic` with `.tile` / `.tile-brown|green|sand|orange`.
- The page background is `static/img/pattern.svg` used as a CSS mask, colored by `--pattern`. Images are cache-first in `static/sw.js`: bump its cache version when changing `icons.svg` or `pattern.svg`.
- Charts take colors from `chartColor(i, alpha)` / `CHART_DANGER` in `static/js/chart-utils.js` (country charts keep flag colors).
- Show skills and levels with `column_label`, `ht_term`, `specialty_name`, `level_text`/`level_hint`, so the user's language and level format apply.
- CSS by function: `ui-components.css`, `utilities.css`, `layout.css`, `charts.css`, `animations.css`; feature files `timeline.css`, `formations.css`, `player-table-enhanced.css` (`components.css` imports them).

## Database rules

The production database is the most important asset.
- Schema changes only through Alembic migrations (`make db-migrate`), reviewed, and tested on a copy of production (`make db-copy-production`, then `make db-upgrade`).
- Keep migrations backward compatible: add nullable columns or columns with defaults, add indexes; don't drop, rename or make columns non-nullable while code still uses them.
- Production runs the migrations when a new image starts, right after `update.sh` made a backup.

## Configuration

Everything comes from environment variables (`.env` locally, the server's `.env` in production): CHPP credentials, database, `SECRET_KEY`, `ADMIN_HT_ID`, `GOATCOUNTER_URL`, `DEBUG_LEVEL`. `config.py` (from `config.py.example`) has `Config` and `TestConfig`. Never commit secrets.
