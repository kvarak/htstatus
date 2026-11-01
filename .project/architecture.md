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
| `app/training_log.py` | The team's weekly training (`TrainingWeek`), saved at Update; CHPP only gives this week and last week, so the table is the only history |
| `app/training_speed.py` | Measured training speed: skill-ups from the player snapshots and the effective training weeks between them (page view only, nothing stored) |
| `app/training_rules.py`, `app/match_minutes.py`, `app/trainees.py` | Which positions each training trains (from HO and the wiki; change only with a source), minutes per player and position from a match lineup, and who got trained per week |
| `app/translations.py`, `app/instance_cache.py` | Hattrick's own terms per language, cached as JSON in `instance/` (also transfer bids and series data) |
| `models.py` | SQLAlchemy models (`User`, `Players`, `Team`, `Match`, `MatchPlay`, `Group`, `PlayerSetting`, `TrainingWeek`, `MatchPositionMinutes`, `Feedback*`, `ErrorLog`, ...) |
| `migrations/` | Alembic migrations |
| `app/templates/`, `app/static/` | Jinja2 + Bootstrap 4 (CDN), CSS, Chart.js |
| `tests/` | pytest (PostgreSQL, CHPP mocked) and `tests/js/` (node --test) |
| `Dockerfile`, `deploy/` | Production image and the server's compose/update/backup files |

## Hattrick data model

- A **user** (Hattrick manager, `User.ht_id`) owns one or more **teams**; a team owns **players**.
- `Players` rows are snapshots: one row per player per Update (`data_date`); `Players.owner` is the team id, `0` once sold. `app/roster.py` gets the latest/oldest record per player.
- `TrainingWeek`: one row per team and training Thursday (`training_date`): type, intensity, stamina share, coach. The coming week is `planned` until an Update after it; finished weeks are never overwritten.
- `MatchPositionMinutes`: minutes per match, team, player and field role, calculated at Update from matchlineup 2.0 (orders) and matchdetails (red cards, injuries). A match counts for the training on the Thursday on or after it; only league, qualification, cup, friendly and Masters matches count.
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

## Search engines

`app/seo.py`: only `/`, `/changes` and `/login` are public (`PUBLIC_PAGES`, with their titles and descriptions); every other page gets `noindex` and is disallowed in `/robots.txt`. `/sitemap.xml`, canonical links and Open Graph/Twitter tags use the public address from `CALLBACK_URL`. The tags come from `templates/_seo_meta.html` (included by `_skeleton.html`); the home page also has WebApplication JSON-LD. The share image is `static/img/share.png` (1200×630). The site icon is the tactics-board icon on a brown tile: `static/img/icon.svg` (master) with PNG sizes, `apple-touch-icon.png`, a maskable version and `/favicon.ico`; regenerate the PNGs when the SVG changes and bump the cache version in `sw.js`. Never put team or player data in these tags.

## Database rules

The production database is the most important asset.
- Schema changes only through Alembic migrations (`make db-migrate`), reviewed, and tested on a copy of production (`make db-copy-production`, then `make db-upgrade`).
- Keep migrations backward compatible: add nullable columns or columns with defaults, add indexes; don't drop, rename or make columns non-nullable while code still uses them.
- Production runs the migrations when a new image starts, right after `update.sh` made a backup.

## Configuration

Everything comes from environment variables (`.env` locally, the server's `.env` in production): CHPP credentials, database, `SECRET_KEY`, `ADMIN_HT_ID`, `GOATCOUNTER_URL`, `DEBUG_LEVEL`. `config.py` (from `config.py.example`) has `Config` and `TestConfig`. Never commit secrets.
