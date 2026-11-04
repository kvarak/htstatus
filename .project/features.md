# HattrickPlanner Feature Roadmap

> **Purpose**: Planned new user-facing features. Improvements, bug fixes, refactoring, tests and infrastructure live in [backlog.md](backlog.md).
> **Task IDs**: `./scripts/get-next-task-id.sh FEAT` (scans both files). Details go in [tasks/](tasks/) as `<ID>.md`.
> **Rule**: When a feature is started, mark it 🚀 ACTIVE; when done, delete it (and its task file); Git history is the archive.

## Next up

*Nothing right now*

## Cycle training 🔁

Built in this order; each step is useful on its own. Design notes: [tasks/cycle-training.md](tasks/cycle-training.md). Done: FEAT-035 training log (`app/training_log.py`), FEAT-036 who got trained (`app/trainees.py`), FEAT-037 measured training speed (`app/training_speed.py`), FEAT-042 admin speed overview (`app/training_speed_stats.py`)

- **[FEAT-044]** Coaching staff: fetch StaffList during Update (coach level, assistant coach levels) into the training log per week; the speed overview then groups by coach level and Schum uses the real coach and assistants instead of "solid, none"
- **[FEAT-038]** Cycle plan: a saved plan per team with ordered phases (training type + weeks) and players marked full / half / not trained; timeline with dates, seasons and each player's age at every phase, and how many trainees each phase needs vs how many fit
- **[FEAT-039]** Projection: week by week, the expected skill levels per player and the week each target level is reached ("PM excellent around week 9 of season 97"), from a configurable `TrainingSpeedModel` (points per level by training type and age band, position effect, coach, assistants, intensity, stamina share) calibrated from the measured speeds (FEAT-037/FEAT-042, e.g. per-type correction of the Schum ratio), with Schum's formula (`schum_weeks_per_level`) as the fallback; shown as "around" because pops vary; all formulas in one module
- **[FEAT-040]** Targets and warnings: a target profile per player (e.g. playmaking 17, defending 13) and warnings like "target not reached before the plan ends", "trains slower from 21", "skill drops possible from 28", "too few trainees for this phase", "main skill so high that wages climb"; a cycle card on the player page
- **[FEAT-041]** Scenarios: templates (e.g. playmaking → defending → passing), clone a plan and compare two plans side by side, CSV export

## Later 🔮

- **[FEAT-045]** Team mood: team spirit, self-confidence, fan mood, fan expectations (season and each upcoming match) and sponsor popularity for the own team, in Hattrick's words with the change since the last Update. Needs Fans and Economy approved in the functional description first. Record: [tasks/FEAT-045.md](tasks/FEAT-045.md)
- **[FEAT-019]** Player Skill Changes Timeline - 4-week timeline with better browser compatibility and simplified approach
- **[FEAT-016]** Alternative Leadership Indicators (30 min) - Replace complex charts with simple metrics
- **[FEAT-017]** User Preference System (60 min) - Store user chart/visualization preferences
