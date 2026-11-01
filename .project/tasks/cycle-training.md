# Cycle training (FEAT-038 to FEAT-041; FEAT-035 to FEAT-037 and FEAT-042 done)

Cycle training: a core group of trainees is trained in several skills in turn (often playmaking, defending, passing, sometimes scoring) over a few seasons, to end up with multi-skilled, valuable players. It's the reason this site exists.

## Order and why

1. **FEAT-035 Training log (done).** `app/training_log.py` and the `training_week` table: each Update saves the last training (final) and the coming one (planned). The CHPP `training` file, version 2.1. The history only starts from the first Update after deploy.
2. **FEAT-036 Who got trained (done).** `app/training_rules.py` (`TRAINING_POSITION_EFFECTS`: full/partial/osmosis per sector, following HO where it differs from the wiki), `app/match_minutes.py` (minutes from matchlineup 2.0 orders, red cards and injuries, like HO), `match_position_minutes` table, `app/trainees.py` (best 90 minutes per week, shown as one training % per player: full minutes + half minutes at 50% + osmosis minutes at 1/6, 1/8 for playmaking/crossing, 5/39 for wing attacks, as HO's `calcSkillIncrement`; FEAT-039 should reuse `training_share`). Lineups are fetched with the team id for finished matches during Update; only matches downloaded after this release have minutes.
3. **FEAT-037 Measured speed (done).** `app/training_speed.py`: pops from the player snapshots (one level up; the pop's week is known only with exactly one training Thursday between the two snapshots), effective weeks between two known pops = sum of `training_share` in weeks whose training type trains that skill (`SKILL_TRAINING_TYPES`), counted only when every week is logged and its matches have lineups (`trainees.week_minutes`). Status per pop: measured, incomplete, unknown start, unknown week. Shown in the Training History ("3.0 wk") and Current Skills ("≈3.0 wk/level · next ≈2.0" after two measured intervals). Computed on page view, nothing stored. Assumes a Thursday snapshot is from before that night's training (as the training log does); worth checking against real data.
3b. **FEAT-042 Training speed overview (admin, done).** `app/training_speed_stats.py`, top of `/debug`: measured single-type pops of all teams per training type × age band × intensity band: n (players, teams), mean weeks/level, 95% CI (t), min-max, Schum's expected weeks for the same pops and the measured/Schum ratio. Rows with < 5 pops are marked "few". Schum's formula (`training_rules.schum_weeks_per_level`, from HO) assumes a solid coach and no assistants until StaffList is fetched; then group by coach level too and pass the real values. Computed on page view.
4. **FEAT-038 Cycle plan.** The first planner, without projections: phases, trainees, a timeline with ages and dates, and squad needs per phase. New tables via a reviewed Alembic migration (additive only).
5. **FEAT-039 Projection.** Adds expected skills per phase. Use the measured speed when there is enough history, otherwise defaults.
6. **FEAT-040 Targets and warnings.** Needs 039. Advisory only, never blocking.
7. **FEAT-041 Scenarios.** Templates, cloning, side-by-side comparison, export.

Skipped on purpose (maybe later): market value, sale timing, purchase suggestions and wage modelling, automatic "best order" optimisation.

## What the sources say

Sources: the Hattrick wiki pages [Training](https://wiki.hattrick.org/wiki/Training) and [Trainee](https://wiki.hattrick.org/wiki/Trainee), [ht-cycle-planner.vercel.app](https://ht-cycle-planner.vercel.app/) (an existing planner), the Aristo Curious video "Training Cycle: A Hattrick Secret to Making Money" and two r/hattrick threads (the Reddit threads were not readable from here).

- **Training timing:** weekly, at the Thursday-night update, and minute-based. A player gets at most 90 minutes per week. If he played in two positions, the better one counts. Friendlies are used to give trainees who missed the league match their minutes, hence the "still needs minutes" hint in FEAT-036.
- **Which positions train:** this depends on the training type (e.g. scoring: forwards; playmaking: inner midfielders, partly wingers; defending: defenders and wing backs). That limits the trainees per type, so it drives the "squad needs per phase" view in FEAT-038.
- **Speed factors** (FEAT-039 inputs):
  - the training type: the wiki has a weeks-per-level table for a 17-year-old at 100% intensity, 15% stamina, a solid coach and 2 top assistants
  - age: about 4% slower per year over 17
  - coach: about 1 week extra per level below solid
  - assistants, intensity and stamina share
  - set pieces training gives the goalkeeper and the set-pieces taker a 25% bonus
- **Pops vary:** after a pop the player carries some progress into the new level, so individual players are ±1 week from the average. Show projections as "around week N", never as an exact date.
- **Age:**
  - trainees are typically 17-21, and trainees are often sold at 21
  - from 21 training is noticeably slower
  - skill drops can start at 27-28, small around 30 and larger around 35
  - scoring drops fastest and goalkeeping slowest
- **Wages:** very high main skills push wages up, and you can "overtrain" a player into an unsustainable salary. Warn about it, but don't model wages exactly.
- **The existing planner:** its core is a weekly progress table (skills and stamina, highlighting increases and drops), a wages table and "when will each player reach the target". That's the bar for FEAT-039 and FEAT-040.

## Confirmed facts

Sources:
- [Beginners' Guide](https://www.hattrick.org/en-us/Help/BeginnersGuide.aspx)
- [Hattrick history](https://www.hattrick.org/en-us/Help/History.aspx)
- [Wiki: Training](https://wiki.hattrick.org/wiki/Training)
- [YouthClub training speed](https://www.hattrick-youthclub.org/site/trainingsspeed)

Facts:
- **Season:** 16 weeks (14 league rounds, a qualifier week and a week without league). Model time as season plus week 0-15.
- **Ages:** take them from each player's own age data (years and days); don't assume one year per season.
- **Weekly training:** once a week at the Thursday update, at most 90 minutes per player. If a player played more than 90 minutes in trainable positions, the best 90 count.
- **Positions:** the `TRAINING_POSITION_EFFECTS` mapping below, with three levels: FULL, PARTIAL (the wiki's brackets) and MINOR (double brackets). "Others" are not zero.

| Training | Skill | FULL positions | Others |
|---|---|---|---|
| Goalkeeping | Keeper | Goalkeeper | – |
| Crossing (winger) | Winger | Wingers | Wing backs partial, others minor |
| Scoring | Scoring | Forwards | minor |
| Playmaking | Playmaking | Inner midfielders | Wingers partial, others minor |
| Wing attacks | Winger | Forwards, wingers | minor |
| Defending | Defending | Defenders, wing backs | minor |
| Short passes | Passing | Midfielders, wingers, forwards | minor |
| Through passes | Passing | Defenders, midfielders, wingers | minor |
| Defensive positions | Defending | Goalkeeper, defenders, inner midfielders, wingers | minor |
| Shooting | Scoring | All outfield players | minor |
| Set pieces | Set pieces | Everyone who played | the taker and the goalkeeper get +25% |

Check these levels against the wiki once more when building FEAT-036; the wiki table rendering is partly garbled.

**Speed** (no single current, complete public table exists):
- The wiki numbers are averages for one baseline: 17 years old, Solid to Excellent, 100% intensity, 15% stamina, a Solid coach and 2 top assistants.
- Season 43 made training faster at many levels and slower at high ones, so older tables don't fit. That change also made skill drops depend more on skill level and less on age.
- About 4% slower per year over 17.
- About 1 week extra per coach level below Solid; Excellent is slightly faster than Solid.
- Assistants and intensity matter. Stamina share (usually 10-15%) takes time away from skill training.

**Speed model rules** (FEAT-037 and FEAT-039):
- **`TrainingSpeedModel`:** one service with these inputs:
  - training type, current skill level and age
  - position effect (FULL, PARTIAL or MINOR) and minutes
  - coach level, assistants, intensity and stamina share
- **Data shape:** a matrix of "training points from level X to X+1" per training type and age band, in config or the database, plus correction factors per training type and level.
- **Seed values:** the wiki baseline, used only as a fallback.
- **YouthClub tables:** for checking the shape of the curves only. They count matches, are youth-oriented and depend on factors the user sets.
- **Calibration:** FEAT-037 fits the correction factors from the skill-ups we actually observe. It could use all HattrickPlanner users, as anonymous aggregates only and never another team's data. Without enough data, use the seed.

## Rules

- **Game rules:** don't guess them. Which positions count for each training type, partial-minute effects, training speed by age, skill level, coach and intensity, and age decline must come from the Hattrick manual or a source the user picks. Ask when unsure. Keep them in one module (e.g. `app/training_rules.py`) with named constants, so they can be checked and tuned.
- **Simulation:** a pure, deterministic function from current squad and plan to weekly projections, unit-tested without Flask. Compute projections on page view; don't store them unless that gets slow.
- **Weeks:** model weeks, not seasons, because training happens weekly.
- **CHPP:** only during login and Update, as everywhere else (`make check-chpp`).
- **Phases:** the user chooses the order; don't hard-code one "right" cycle.
