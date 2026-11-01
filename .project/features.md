# HattrickPlanner Feature Roadmap

> **Purpose**: Planned new user-facing features. Improvements, bug fixes, refactoring, tests and infrastructure live in [backlog.md](backlog.md).
> **Task IDs**: `./scripts/get-next-task-id.sh FEAT` (scans both files). Details go in [tasks/](tasks/) as `<ID>.md`.
> **Rule**: When a feature is started, mark it 🚀 ACTIVE; when done, delete it (and its task file); Git history is the archive.

## Next Up 🎯

- **[FEAT-008]** Next Game Analyser → [Details](tasks/FEAT-008.md)

## Cycle training 🔁

Built in this order; each step is useful on its own. Design notes: [tasks/FEAT-035.md](tasks/FEAT-035.md)

- **[FEAT-035]** Training log: fetch the team's training (type, intensity, stamina share, coach) during Update and show this week's and past weeks' training on the Training page
- **[FEAT-036]** Who got trained: per player and week, the minutes (max 90) played in a position that counts for that week's training (from MatchLineup), shown as full / partial / none on the Training page, plus "still needs minutes this week" so you know whom to play in a friendly
- **[FEAT-037]** Measured training speed: from the history, how many trained weeks each player needed per skill level, and "next level expected in about N weeks"; also calibrates the speed model (anonymous aggregates across users); no formulas, only what we observed
- **[FEAT-038]** Cycle plan: a saved plan per team with ordered phases (training type + weeks) and players marked full / half / not trained; timeline with dates, seasons and each player's age at every phase, and how many trainees each phase needs vs how many fit
- **[FEAT-039]** Projection: week by week, the expected skill levels per player and the week each target level is reached ("PM excellent around week 9 of season 97"), from a configurable `TrainingSpeedModel` (points per level by training type and age band, position effect, coach, assistants, intensity, stamina share) calibrated by FEAT-037, with the wiki values only as a fallback; shown as "around" because pops vary; all formulas in one module
- **[FEAT-040]** Targets and warnings: a target profile per player (e.g. playmaking 17, defending 13) and warnings like "target not reached before the plan ends", "trains slower from 21", "skill drops possible from 28", "too few trainees for this phase", "main skill so high that wages climb"; a cycle card on the player page
- **[FEAT-041]** Scenarios: templates (e.g. playmaking → defending → passing), clone a plan and compare two plans side by side, CSV export

## Later 🔮

- **[FEAT-019]** Player Skill Changes Timeline - 4-week timeline with better browser compatibility and simplified approach
- **[FEAT-016]** Alternative Leadership Indicators (30 min) - Replace complex charts with simple metrics
- **[FEAT-017]** User Preference System (60 min) - Store user chart/visualization preferences
