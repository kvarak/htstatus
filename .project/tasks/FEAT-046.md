# FEAT-046: Remake the statistics page (lots of stats, and fix what's wrong)

Rework `/stats` into a richer, more fun "club dashboard": more numbers and charts a
Hattrick data geek actually enjoys, built from data we already store. Along the way,
fix the correctness bugs the current page has (the kit is the obvious one).

## Why

The current page ([app/blueprints/stats.py](../../app/blueprints/stats.py),
[app/team_stats.py](../../app/team_stats.py),
[app/templates/stats.html](../../app/templates/stats.html)) shows a handful of
squad averages, three tables and a few charts, and some of it is wrong or thin.
We have years of player snapshots and match data sitting unused.

## Deep-dive: what's wrong today

- **Kits (the reported bug).** The tile is titled "Kits & Logo" and labelled "Home
  Kit", but:
  - Only the home kit (`dress_uri`, from `DressURI`) is stored and shown. The away
    kit (`DressAlternateURI`) is parsed into `CHPPTeam.dress_alternate_uri` but
    thrown away — the `Team` model has no column for it. So "Kits" (plural) only
    ever shows one kit.
  - The kit/logo can go **stale**: `Team.update_competition_data` skips `None`
    values ([models.py](../../models.py)), so if a kit or logo is removed in
    Hattrick the old image sticks around.
  - Hattrick's kit URIs can come back as `http://res.hattrick.org/kits/...` (see
    [docs/chpp/api-reference-matchdetails.md](../../docs/chpp/api-reference-matchdetails.md));
    embedded on our HTTPS page they're blocked as mixed content → a broken/"wrong"
    kit. Normalise to `https://`.
- **Stale cup data.** Same `None`-skip bug: when a team is knocked out of the cup,
  CHPP omits the cup fields, so `cup_cup_name` keeps its old value. The "Cup" tile
  then shows the old cup name with "Eliminated". Cup fields should be cleared when
  absent.
- **Misleading metrics.**
  - "Goals per Match" = `sum(current_team_goals) / sum(current_team_matches)` over
    all players — that's goals per *player-appearance*, not team goals per match.
    Either rename it or compute real team goals/match from stored `Match` rows.
  - "Team Skill Averages" averages `leadership` together with the seven playing
    skills, mixing concepts. Leadership isn't a playing skill.
- **Thin content.** No use of our `Match` / `MatchPositionMinutes` history, no
  skill-growth-over-time, no form/experience/specialty breakdowns, no TSI/wage
  trends, no "who trained" — all of which we already have stored.

## Feature record ([docs/CHPP.md](../../docs/CHPP.md))

- **Feature name:** Team statistics (dashboard)
- **User story:** a manager opens "Stats" and sees a rich dashboard about their own
  team(s) — squad make-up, age/country/specialty spread, skill averages, TSI and
  wage totals and how they've moved over time, scoring, and a summary of their
  matches — all from data already fetched at "Update data".
- **CHPP resources:** none new for the core remake. Everything comes from data we
  already store: player snapshots (`Players`, many rows per player over time),
  matches (`Match`, `MatchPlay`), minutes (`MatchPositionMinutes`), training
  (`TrainingWeek`) and the team competition row (`Team`). Page views stay
  database-only; `make check-chpp` must still pass.
- **Data shown:** squad composition and age/country/specialty distributions; team
  and top-11 skill averages; TSI/wage totals and trends; scoring and match summary;
  skill growth over time from the snapshots.
- **Data stored:** nothing new for the core remake. If we add the away kit, store
  `dress_alternate_uri` on `Team` (new nullable column, Alembic migration).
- **Opponent data:** none. Own team(s) only.
- **Free, public, English:** yes. Hattrick words via `ht_term` / `column_label` /
  `level_text`, so the user's language and level format apply.
- **User-initiated downloads:** none added. No new CHPP calls.
- **Hattrick write actions:** none.
- **CHPP category:** own-team, read only, and no new XML files, so **no new
  functional description is required** for the core remake. Any stat that would need
  data we don't fetch yet (e.g. finances, fan mood → see FEAT-045, league standings
  over time, match ratings beyond what's stored) must go through an approved
  function first — out of scope here.

## Scope for "good enough"

1. Fix the bugs above (kit plural/away kit, stale cup/kit via `None`-skip, http→https
   kit, metric labels, leadership out of playing-skill average).
2. Add stats that use already-stored history and need no new CHPP calls, e.g.:
   - Skill growth over time per skill (from `Players` snapshots).
   - TSI and total wage over time.
   - Squad value/age "pyramid", specialty and form/experience spread.
   - Real match summary from `Match`/`MatchPlay` (played, W/D/L, goals for/against,
     goals per match done properly), minutes from `MatchPositionMinutes`.
3. Keep the one-look UI (poster tiles, `page_header`, no hard-coded colours, charts
   via `chartColor`), and keep it fast (a few bounded DB queries).

Build it in small steps with tests, newest/most-wrong things first. Don't add a stat
that needs CHPP data we don't already store without an approved function.
