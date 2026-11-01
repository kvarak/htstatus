# HattrickPlanner Feature Roadmap

> **Purpose**: Planned new user-facing features. Improvements, bug fixes, refactoring, tests and infrastructure live in [backlog.md](backlog.md).
> **Task IDs**: `./scripts/get-next-task-id.sh FEAT` (scans both files). Details go in [tasks/](tasks/) as `<ID>.md`.
> **Rule**: When a feature is started, mark it 🚀 ACTIVE; when done, delete it (and its task file); Git history is the archive.

## Next Up 🎯

- **[FEAT-008]** Next Game Analyser → [Details](tasks/FEAT-008.md)

## Cycle training 🔁

Built in this order; each step is useful on its own. Design notes: [tasks/cycle-training.md](tasks/cycle-training.md). Done: FEAT-035 training log (`app/training_log.py`), FEAT-036 who got trained (`app/trainees.py`)

- **[FEAT-037]** Measured training speed: from the existing player snapshots, each pop's interval as "level X → X+1 took N effective weeks" (sum of the player's weekly Training % for that skill), only when the whole interval is covered by the training log and minutes (else "incomplete"); shown in the Training History and the player card, plus "next level in about N weeks" once there are two measured intervals; old pops before FEAT-035 are not used; hint to update weekly
- **[FEAT-042]** Training speed overview (admin): a section at the top of `/debug` with what all users' measured pops (FEAT-037) say, per training type × age band (17-18, 19-20, 21-23, 24+), grouped by coach level and intensity (raw, not normalised): number of pops/players/teams, mean weeks per level with a 95% confidence interval, min/max, and the wiki baseline for comparison; every row shown, with rows based on few pops clearly marked; aggregates only, no names; database only
- **[FEAT-038]** Cycle plan: a saved plan per team with ordered phases (training type + weeks) and players marked full / half / not trained; timeline with dates, seasons and each player's age at every phase, and how many trainees each phase needs vs how many fit
- **[FEAT-039]** Projection: week by week, the expected skill levels per player and the week each target level is reached ("PM excellent around week 9 of season 97"), from a configurable `TrainingSpeedModel` (points per level by training type and age band, position effect, coach, assistants, intensity, stamina share) calibrated from the measured speeds (FEAT-037/FEAT-042), with the wiki values only as a fallback; shown as "around" because pops vary; all formulas in one module
- **[FEAT-040]** Targets and warnings: a target profile per player (e.g. playmaking 17, defending 13) and warnings like "target not reached before the plan ends", "trains slower from 21", "skill drops possible from 28", "too few trainees for this phase", "main skill so high that wages climb"; a cycle card on the player page
- **[FEAT-041]** Scenarios: templates (e.g. playmaking → defending → passing), clone a plan and compare two plans side by side, CSV export

## Later 🔮

- **[FEAT-019]** Player Skill Changes Timeline - 4-week timeline with better browser compatibility and simplified approach
- **[FEAT-016]** Alternative Leadership Indicators (30 min) - Replace complex charts with simple metrics
- **[FEAT-017]** User Preference System (60 min) - Store user chart/visualization preferences
