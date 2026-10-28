# HattrickPlanner Backlog

**Mindset**: Hobby project. Good enough is perfect. Only fix what actually bothers us (bugs, risk to the database, slowness we notice, code that's painful to change). No audits, no coverage-chasing, no process for its own sake.
**Scope**: Improvements, bug fixes, cleanup and infra. New features go in [features.md](features.md).
**Rule**: Pick whatever is most useful. When done, DELETE the line (and any `tasks/` file); Git history is the archive. Delete items that stop making sense, too.
**Task IDs**: `./scripts/get-next-task-id.sh <TYPE>` (BUG, REFACTOR, TEST, INFRA, UI, DOC). Estimates are optional.

---

## P1: Broken or risky 🔥

*Nothing right now*

## P2: Worth doing 🎯

- **[UI-013]** Show progress while "Update" runs - The update takes a while with no feedback; a spinner/"working..." state is enough → [Details](tasks/UI-013.md)
- **[UI-019]** Formation page fixes - Overall rating ignores empty positions (bug); tooltips and colour-coding are nice extras → [Details](tasks/UI-019.md)
- **[REFACTOR-058]** Tidy up `calculateContribution` - It accepts two position formats; settle on one and add a few tests for the common positions (was TEST-036)
- **[REFACTOR-119]** Render the changelog in the template - `main.changes()` builds HTML in Python; pass entries to `changes.html` instead

## P3: When you're in that code anyway 🔧

- **[REFACTOR-117]** Break up `team.update()` (~570 lines) - Pull out a few helpers (build player record, save snapshot) next time the update needs changing. No big-bang rewrite
- **[REFACTOR-118]** Break up `login()` / OAuth callback (~240/310 lines) - Same idea: extract helpers when touching auth
- **[REFACTOR-029]** Drop the model registry - Import models directly; the registry adds a second way to do the same thing (was REFACTOR-028, REFACTOR-072)
- **[REFACTOR-103]** Drop Flask-Bootstrap - Templates mostly use Bootstrap 4 already; remove the dependency when template work happens (was REFACTOR-091) → [Details](tasks/REFACTOR-103.md)
- **[REFACTOR-116]** Timeline is query-heavy - `get_team_timeline()` runs 2 queries per player per week. Only worth fixing if the page feels slow
- **[REFACTOR-102]** Less copy-paste in Chart.js code - The debug page builds ~18 charts by hand; a small helper would shrink it. Only if you're editing charts anyway
- **[REFACTOR-073]** Simplify team competition data storage - The 9-parameter update method could be a simple upsert (now wrapped by `save_team_competition_data` in team.py)
- **[INFRA-088]** Trim tooling and docs - Makefile targets, quality-intelligence scripts and 60+ doc files are more than a hobby project needs. Delete what nobody uses when it gets in the way (was REFACTOR-049, DOC-032, REFACTOR-101, REFACTOR-028 changelog, REFACTOR-052..056) → [Details](tasks/INFRA-088.md)

---

**Testing**: Add a test when fixing a bug or changing behaviour. No coverage targets beyond what CI already enforces (50%).
