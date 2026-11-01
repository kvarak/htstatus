"""Who got trained each week (FEAT-036).

Combines the training log (``TrainingWeek``) with the minutes per position saved
from match lineups (``MatchPositionMinutes``). Database only, no CHPP calls.
"""

from datetime import datetime, time, timedelta

from app.training_log import TRAINING_WEEKDAY
from app.training_rules import (
    effect_factors,
    FULL,
    MINUTES_PER_WEEK,
    OSMOSIS,
    PARTIAL,
    ROLE_SHORT,
    trained_minutes,
    TRAINING_POSITION_EFFECTS,
    training_share,
)

# Match types that give training (as in Hattrick Organizer's "official" matches):
# league, qualification, cup, friendlies and Masters; not tournaments or ladders
TRAINING_MATCH_TYPES = (1, 2, 3, 4, 5, 7, 8, 9)

FULLY_TRAINED = "full"
PARTLY_TRAINED = "partly"
MINIMALLY_TRAINED = "minimal"  # osmosis only: too small to plan with
NOT_TRAINED = "none"


def training_date_of(day):
    """The training Thursday a match on ``day`` counts for (the same day on Thursdays)."""
    return day + timedelta(days=(TRAINING_WEEKDAY - day.weekday()) % 7)


def _week_minutes(team_id, weeks):
    """{training_date: {player_id: {role_id: minutes}}} for the given weeks."""
    from sqlalchemy import or_

    from models import Match, MatchPositionMinutes

    dates = {w.training_date for w in weeks}
    if not dates:
        return {}
    start = datetime.combine(min(dates) - timedelta(days=6), time.min)
    end = datetime.combine(max(dates), time.max)
    matches = Match.query.filter(
        or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
        Match.matchtype.in_(TRAINING_MATCH_TYPES),
        Match.datetime >= start,
        Match.datetime <= end,
    ).all()
    match_week = {m.ht_id: training_date_of(m.datetime.date()) for m in matches}
    result = {d: {} for d in dates}
    if not match_week:
        return result
    rows = MatchPositionMinutes.query.filter(
        MatchPositionMinutes.team_id == team_id,
        MatchPositionMinutes.match_id.in_(match_week),
    ).all()
    for row in rows:
        week = result.get(match_week[row.match_id])
        if week is None:
            continue
        per_role = week.setdefault(row.player_id, {})
        per_role[row.role_id] = per_role.get(row.role_id, 0) + row.minutes
    return result


def _status(counted):
    if counted[FULL] >= MINUTES_PER_WEEK:
        return FULLY_TRAINED
    if counted[FULL] or counted[PARTIAL]:
        return PARTLY_TRAINED
    if counted[OSMOSIS]:
        return MINIMALLY_TRAINED
    return NOT_TRAINED


def weekly_reports(team_id, weeks, squad):
    """Per training week: who got how many training minutes.

    ``squad`` is ``{player_id: name}`` (current players). Returns
    ``{training_date: report}``; a report has ``rows`` (one per squad player,
    best trained first) and the counts ``full``/``partly``. Weeks whose training
    doesn't depend on positions (stamina, general) are left out.
    """
    weeks = [w for w in weeks if w.training_type in TRAINING_POSITION_EFFECTS]
    minutes = _week_minutes(team_id, weeks)
    reports = {}
    for week in weeks:
        played = minutes.get(week.training_date, {})
        rows = []
        for player_id, name in squad.items():
            per_role = played.get(player_id, {})
            counted = trained_minutes(week.training_type, per_role)
            rows.append(
                {
                    "player_id": player_id,
                    "name": name,
                    "positions": ", ".join(
                        f"{ROLE_SHORT[r]} {m}'"
                        for r, m in sorted(per_role.items(), key=lambda rm: -rm[1])
                        if r in ROLE_SHORT
                    ),
                    FULL: counted[FULL],
                    PARTIAL: counted[PARTIAL],
                    OSMOSIS: counted[OSMOSIS],
                    "share": round(100 * training_share(week.training_type, counted)),
                    "status": _status(counted),
                    "needs": MINUTES_PER_WEEK - counted[FULL],
                }
            )
        rows.sort(key=lambda r: (-r["share"], -r[FULL], r["name"]))
        reports[week.training_date] = {
            "rows": rows,
            "full": sum(r["status"] == FULLY_TRAINED for r in rows),
            "partly": sum(r["status"] == PARTLY_TRAINED for r in rows),
            "minimal": sum(r["status"] == MINIMALLY_TRAINED for r in rows),
            "factors": {
                k: round(100 * v) for k, v in effect_factors(week.training_type).items()
            },
        }
    return reports
