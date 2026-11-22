# INFRA-094: Next game scouting — retention + function to submit

The scouting feature (FEAT-008, `app/opponents.py`) downloads upcoming opponents'
matches at Update so the matches page can show their recent form, head-to-head and
setup. Two problems: those opponent matches were kept forever, and no approved CHPP
function covered opponent data.

## Done (code)

- `prune_opponent_matches()` runs at the end of each Update (`app/blueprints/team.py`).
  It keeps every match involving a HattrickPlanner team (own history and head-to-head)
  and, for teams that are a **current upcoming opponent**, their last 10 finished
  matches per setup filter (league / cup / all). Everything else fetched only for
  scouting is deleted, so the Match table stays bounded.

## To do (you) — submit the function to Hattrick

Opponent data needs an approved function ([docs/CHPP.md](../../docs/CHPP.md)). Submit
the functional description below on the CHPP portal before relying on this in
production, and adjust the wording if CHPP staff ask.

## Functional description (submit)

Title: **Next game scouting**

> For each of the user's own upcoming matches, show the opponent as a scouting card:
> their recent results (league, cup and overall), the head-to-head record against the
> user's team, and which formations and tactics the opponent has used lately. Read
> only, opponent data limited to the next opponent of an upcoming match, fetched only
> when the user clicks "Update data".

Xml files: **matches, matchdetails**

- `matches`: the opponent's recent finished results (score, date, match type).
- `matchdetails` (with `matchEvents` off): only to read the opponent's formation and
  tactic for each of their last 10 finished matches.

## Feature record ([docs/CHPP.md](../../docs/CHPP.md))

- **Feature name:** Next game scouting
- **User story:** before an upcoming match, the manager sees the opponent's recent
  form, the head-to-head, and the opponent's usual formation/tactic — so they can
  prepare — all from data fetched at the last "Update data".
- **CHPP resources:** `matches` and `matchdetails` for each current upcoming
  opponent. Both are only fetched during Update.
- **Data shown:** opponent's last 10 finished matches per filter (league / cup / all)
  with result and setup, the head-to-head with the user's team, and formation/tactic
  usage shares.
- **Data stored:** the opponent's matches (result + the opponent side's formation and
  tactic) in the shared `Match` table. Pruned each Update to the current opponents'
  last 10 finished matches per filter; matches involving a HattrickPlanner team are
  kept as normal history.
- **Opponent data:** yes — this is the sensitive part. Scoped to the next opponent of
  an upcoming match, roughly the last season of finished matches, and not kept once
  the team is no longer an upcoming opponent.
- **Free, public, English:** yes. Hattrick words via the usual helpers.
- **User-initiated downloads:** yes, only during "Update data". No timers or jobs.
- **Hattrick write actions:** none.
- **CHPP category:** opponent data, read only — needs this function approved.

## When approved

Delete the INFRA-094 line in [todo.md](../todo.md) and this file; the retention code
and docs stay.
