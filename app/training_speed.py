"""Measured training speed (FEAT-037): how many effective weeks each skill-up took.

A "pop" is a skill going up one level between two player snapshots. It belongs
to the training update (Thursday) between them; when there's more than one
Thursday in between we can't tell which, so the pop's week is unknown.

Between two pops of the same skill whose weeks are known, the effective weeks
are the sum of the player's weekly training share (``training_share``: full
minutes 100%, half 50%, osmosis a little) in the weeks whose training type
trains that skill; other training types add 0. The interval only counts when
every week in it is in the training log and its matches have lineups.

Assumption (as in the training log): a snapshot taken on a Thursday is from
before that night's training. Database only; no CHPP calls.
"""

from datetime import timedelta
from statistics import mean

from app.trainees import training_date_of, week_minutes
from app.training_rules import trained_minutes, training_share

SKILLS = (
    "keeper",
    "defender",
    "playmaker",
    "winger",
    "passing",
    "scorer",
    "set_pieces",
)
# Which CHPP training types train each skill (Hattrick wiki / HO training types)
SKILL_TRAINING_TYPES = {
    "keeper": (9,),
    "defender": (3, 11),  # defending, defensive positions
    "playmaker": (8,),
    "winger": (5, 12),  # crossing, wing attacks
    "passing": (7, 10),  # short passes, through passes
    "scorer": (4, 6),  # scoring, shooting
    "set_pieces": (2,),
}
MIN_INTERVALS_FOR_ESTIMATE = 2

MEASURED = "measured"
INCOMPLETE = "incomplete"  # a week in between has no training log or lineups
UNKNOWN_START = (
    "unknown start"  # first pop we saw, or the previous pop's week is unknown
)
UNKNOWN_WEEK = "unknown week"  # more than one training update between the snapshots


def _thursdays(start, end):
    """Training dates T with start <= T < end."""
    first = training_date_of(start)
    weeks = []
    while first < end:
        weeks.append(first)
        first += timedelta(days=7)
    return weeks


def find_pops(snapshots, skill):
    """Skill-ups of one level, oldest first.

    ``snapshots``: the player's records (``data_date``, skill attributes, age),
    oldest first. A drop or a jump of more than one level resets the chain, so
    the next pop has an unknown start.
    """
    pops = []
    previous = None
    reset = True
    for snap in snapshots:
        value = getattr(snap, skill)
        if previous is not None and value is not None:
            before = getattr(previous, skill)
            if before is not None and value != before:
                if value == before + 1:
                    weeks = _thursdays(previous.data_date.date(), snap.data_date.date())
                    pops.append(
                        {
                            "skill": skill,
                            "from": before,
                            "to": value,
                            "seen": snap.data_date.date(),
                            "week": weeks[0] if len(weeks) == 1 else None,
                            "age_years": snap.age_years,
                            "age_days": snap.age_days,
                            "after_reset": reset,
                        }
                    )
                    reset = False
                else:
                    reset = True
        previous = snap
    return pops


def _mean_of(values):
    values = [v for v in values if v is not None]
    return round(mean(values)) if values else None


class WeekData:
    """The team's training log and per-player training shares, loaded once."""

    def __init__(self, team_id):
        from models import TrainingWeek

        self.log = {
            w.training_date: w
            for w in TrainingWeek.query.filter_by(team_id=team_id, planned=False)
        }
        minutes, self.missing = week_minutes(team_id, self.log)
        self.shares = {
            date: {
                player: training_share(
                    week.training_type, trained_minutes(week.training_type, per_role)
                )
                for player, per_role in minutes.get(date, {}).items()
            }
            for date, week in self.log.items()
        }

    def interval(self, player_id, skill, after, until):
        """Effective weeks for ``skill`` in training weeks after ``after`` up to
        ``until`` (inclusive), or None if a week is missing. Also returns the
        training types and the intensity/stamina of the weeks that counted."""
        types = SKILL_TRAINING_TYPES[skill]
        total, used = 0.0, []
        week = after + timedelta(days=7)
        while week <= until:
            log = self.log.get(week)
            if log is None:
                return None
            if log.training_type in types:
                if week in self.missing:
                    return None
                total += self.shares[week].get(player_id, 0.0)
                used.append(log)
            week += timedelta(days=7)
        return {
            "weeks": total,
            "training_types": sorted({w.training_type for w in used}),
            "intensity": _mean_of(w.intensity for w in used),
            "stamina_share": _mean_of(w.stamina_share for w in used),
        }

    def last_week(self):
        return max(self.log) if self.log else None


def measure_player(snapshots, data, player_id):
    """Per skill: the pops with their status and effective weeks, plus an estimate.

    Returns ``{skill: {"pops": [...], "per_level": weeks or None,
    "next_in": weeks or None}}`` for the skills with at least one pop.
    """
    result = {}
    for skill in SKILLS:
        pops = find_pops(snapshots, skill)
        if not pops:
            continue
        previous = None
        for pop in pops:
            pop["weeks"] = None
            if pop["week"] is None:
                pop["status"] = UNKNOWN_WEEK
            elif pop["after_reset"] or previous is None or previous["week"] is None:
                pop["status"] = UNKNOWN_START
            else:
                measured = data.interval(
                    player_id, skill, previous["week"], pop["week"]
                )
                if measured is None:
                    pop["status"] = INCOMPLETE
                else:
                    pop.update(measured)
                    pop["status"] = MEASURED
            previous = pop
        measured = [p["weeks"] for p in pops if p["status"] == MEASURED]
        per_level = (
            mean(measured) if len(measured) >= MIN_INTERVALS_FOR_ESTIMATE else None
        )
        next_in = None
        last = pops[-1]
        if per_level is not None and last["week"] is not None and data.last_week():
            progress = data.interval(player_id, skill, last["week"], data.last_week())
            if progress is not None:
                next_in = max(per_level - progress["weeks"], 0.0)
        result[skill] = {"pops": pops, "per_level": per_level, "next_in": next_in}
    return result


def measure_team(team_id, snapshots_by_player):
    """``{player_id: measure_player(...)}`` for the team's players."""
    data = WeekData(team_id)
    return {
        player_id: measure_player(snapshots, data, player_id)
        for player_id, snapshots in snapshots_by_player.items()
    }


def history_marks(skill_changes, speed):
    """Which Training History cells show a measured pop.

    ``skill_changes``: the page's rows ``(date, skills, changes)``, newest first.
    Returns ``{(row_date, skill_index): pop}`` for skill-ups whose pop was seen
    after the previous (older) row and up to this row.
    """
    marks = {}
    for index, (row_date, _skills, changes) in enumerate(skill_changes):
        older = skill_changes[index + 1][0] if index + 1 < len(skill_changes) else None
        for i, skill in enumerate(SKILLS):
            if changes[i] <= 0 or skill not in speed:
                continue
            for pop in speed[skill]["pops"]:
                if (older is None or older < pop["seen"]) and pop["seen"] <= row_date:
                    marks[(row_date, i)] = pop
    return marks
