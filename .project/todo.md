# HattrickPlanner To Do

Hobby project: good enough is perfect. One line per item: the problem and what "good enough" looks like. A [tasks/](tasks/) file only when there's real context worth keeping. When an item is done or stops making sense, delete the line (and its task file); git history is the archive. IDs: `./scripts/get-next-task-id.sh <TYPE>` (FEAT, BUG, REFACTOR, TEST, INFRA, UI, DOC).

## Now

- **[INFRA-094]** Opponent matches from scouting (FEAT-008) are kept forever, and no approved function covers them. Good enough: Update keeps only what the scouting card needs (the next opponents' last 10 matches); a "Next game scouting" function submitted to Hattrick

## Next

- **[INFRA-091]** A fresh install can't start from an empty database (the old migration chain doesn't build the schema). Good enough: on an empty database, create the tables from the models and `alembic stamp head`; tested in CI
- **[FEAT-045]** Team mood: team spirit, confidence, fan mood and expectations, sponsor popularity for the own team in Hattrick's words, with the change since the last Update. Needs a "Team mood" function (Fans, Economy) approved first: [tasks/FEAT-045.md](tasks/FEAT-045.md)
- **[FEAT-044]** Coaching staff: fetch StaffList at Update so the training speed overview and Schum use the real coach and assistants. Needs StaffList added to the approved "Training log" function first
- **[FEAT-038]** Cycle plan: a saved plan per team (training type + weeks per phase, players full/half/not trained) on a timeline with dates and ages. Submit a "Training plan" function before release. Notes: [tasks/cycle-training.md](tasks/cycle-training.md)
- **[FEAT-039]** Cycle projection: expected skill level per player per week of the plan, from the measured speeds with Schum's formula as the fallback, shown as "around"
- **[FEAT-046]** Remake the `/stats` page into a richer, fun club dashboard (lots of stats from data we already store) and fix the current bugs: the kit (stale/http/only home kit shown), stale cup data, and misleading metrics. No new CHPP calls for the core remake: [tasks/FEAT-046.md](tasks/FEAT-046.md)
- **[REFACTOR-121]** `app/utils.py` (~1460 lines) mixes match downloading with small helpers. Good enough: match download code in its own module
- **[REFACTOR-122]** Blueprints get `db`/columns through `setup_*_blueprint()` globals. Good enough: import `db` and `app.constants` directly like `series`/`stats` do

## Maybe

- **[REFACTOR-120]** Feedback routes check login by hand; use `@require_authentication` like the other blueprints
- **[REFACTOR-123]** Route handlers of 110-170 lines; move the data preparation into tested helpers when changing them
- **[TEST-119]** Overlapping test files (`test_utils*`, `test_auth*`); merge per module when touching them
- **[DOC-037]** Smaller CHPP rule questions: the Hattrick login name is stored (`User.ht_user`), logout doesn't invalidate the token, `includeMatchInfo` may be unneeded, the admin training speed overview pools all teams. Decide each when it comes up; see [docs/CHPP.md](../docs/CHPP.md)

Testing: add a test when fixing a bug or changing behaviour.
