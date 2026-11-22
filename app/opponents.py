"""Scouting for upcoming matches: the opponent's recent results and setup, and our head-to-head.

The opponent's matches are fetched only during Update (CHPP is never called on a
page view). They are saved to the Match table, so the matches page reads them from
the database.
"""

from collections import Counter
from datetime import datetime

from app.utils import _process_matches_enhanced, dprint

RECENT_LIMIT = 10
# matchtype 1 = league, 3 = cup (same as matches.html); None = every match type
SETUP_FILTERS = {"league": (1,), "cup": (3,), "all": None}


def opponent_of(match, team_id):
    """Team id of the side that is not team_id."""
    return match.away_team_id if match.home_team_id == team_id else match.home_team_id


def refresh_opponent_matches(chpp, team_ids):
    """Save each upcoming opponent's matches. A failing opponent doesn't stop the others."""
    from app import db
    from models import Match

    now = datetime.now()
    for team_id in team_ids:
        upcoming = (
            db.session.query(Match)
            .filter(
                (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
                Match.datetime > now,
            )
            .all()
        )
        opponents = {opponent_of(m, team_id) for m in upcoming}
        for opponent_id in sorted(o for o in opponents if o and o > 0):
            try:
                matches = chpp.matches(id_=opponent_id, is_youth=False)
                _process_matches_enhanced(matches, chpp, fetch_enhanced=False)
            except Exception as e:
                dprint(1, f"Opponent match download failed for team {opponent_id}: {e}")
                continue
            _save_missing_setups(chpp, opponent_id, _past_matches(opponent_id, now))


def _past_matches(team_id, now):
    from app import db
    from models import Match

    return (
        db.session.query(Match)
        .filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id),
            Match.datetime < now,
        )
        .all()
    )


def _current_opponent_ids(ht_team_ids, now):
    """Opponent team ids in every upcoming match of a HattrickPlanner team."""
    from app import db
    from models import Match

    if not ht_team_ids:
        return set()
    ids = list(ht_team_ids)
    upcoming = (
        db.session.query(Match)
        .filter(
            Match.home_team_id.in_(ids) | Match.away_team_id.in_(ids),
            Match.datetime > now,
        )
        .all()
    )
    opponents = set()
    for match in upcoming:
        for team_id in (match.home_team_id, match.away_team_id):
            if team_id and team_id > 0 and team_id not in ht_team_ids:
                opponents.add(team_id)
    return opponents


def _scouting_keep_ids(opponent_id, now):
    """Match ids the scouting card needs for one opponent: its last RECENT_LIMIT
    finished matches in each setup filter (league, cup, all)."""
    past = [m for m in _past_matches(opponent_id, now) if m.is_finished]
    keep = set()
    for allowed in SETUP_FILTERS.values():
        picked = [m for m in past if allowed is None or m.matchtype in allowed]
        picked.sort(key=lambda m: m.datetime, reverse=True)
        keep.update(m.ht_id for m in picked[:RECENT_LIMIT])
    return keep


def prune_opponent_matches():
    """Delete scouting-only matches we no longer need (INFRA-094).

    Scouting saves opponents' matches to the Match table, and opponents change every
    week, so without pruning the table grows forever with matches no feature reads.

    Kept: every match involving a HattrickPlanner team (someone's own history and the
    head-to-head record), and, for teams that are a current upcoming opponent, the
    last RECENT_LIMIT finished matches the scouting card shows per filter. Every other
    match fetched purely for scouting is removed. Returns the number deleted.
    """
    from app import db
    from models import Match, MatchPlay, Team

    now = datetime.now()
    ht_team_ids = {t.ht_id for t in db.session.query(Team.ht_id)}

    keep_ids = set()
    for opponent_id in _current_opponent_ids(ht_team_ids, now):
        keep_ids |= _scouting_keep_ids(opponent_id, now)

    ht_ids = list(ht_team_ids)
    stale = (
        db.session.query(Match.ht_id)
        .filter(
            ~Match.home_team_id.in_(ht_ids),
            ~Match.away_team_id.in_(ht_ids),
            ~Match.ht_id.in_(keep_ids),
        )
        .all()
    )
    stale_ids = [row.ht_id for row in stale]
    if stale_ids:
        MatchPlay.query.filter(MatchPlay.match_id.in_(stale_ids)).delete(
            synchronize_session=False
        )
        Match.query.filter(Match.ht_id.in_(stale_ids)).delete(synchronize_session=False)
        db.session.commit()
    return len(stale_ids)


def _save_missing_setups(chpp, team_id, matches):
    """Store formation and tactic of team_id for its last RECENT_LIMIT finished matches.

    matchdetails gives both sides, but only team_id's side is written. Matches that
    already have a formation are skipped, so each match is fetched once. A failed
    request is logged and retried at the next Update.
    """
    from app import db

    finished = [m for m in matches if m.is_finished and m.home_team_formation is None]
    finished.sort(key=lambda m: m.datetime, reverse=True)
    for match in finished[:RECENT_LIMIT]:
        try:
            details = chpp.matchdetails(id_=match.ht_id, match_events=False)
        except Exception as e:
            dprint(1, f"Opponent setup download failed for match {match.ht_id}: {e}")
            continue
        if match.home_team_id == team_id:
            match.home_team_formation = details.home_team_formation or ""
            match.home_team_tactic_type = details.home_team_tactic_type
        else:
            match.away_team_formation = details.away_team_formation or ""
            match.away_team_tactic_type = details.away_team_tactic_type
        db.session.commit()


def summarise(matches, team_id, limit=None):
    """Results of team_id in the finished matches, newest first.

    Returns {"matches": [row, ...], "record": {"W": n, "D": n, "L": n}}, where
    record is overall and "home"/"away" split the same way. limit keeps only
    the newest matches. Each row has the formation and tactic type of team_id
    (the template names the tactic with ``tactic_name``).
    """
    rows = []
    for m in sorted(matches, key=lambda m: m.datetime, reverse=True):
        if not m.is_finished or m.home_goals is None or m.away_goals is None:
            continue
        at_home = m.home_team_id == team_id
        goals_for, goals_against = (
            (m.home_goals, m.away_goals) if at_home else (m.away_goals, m.home_goals)
        )
        if goals_for > goals_against:
            result = "W"
        elif goals_for < goals_against:
            result = "L"
        else:
            result = "D"
        rows.append(
            {
                "date": m.datetime,
                "opponent": m.away_team_name if at_home else m.home_team_name,
                "home": at_home,
                "goals_for": goals_for,
                "goals_against": goals_against,
                "result": result,
                "formation": (
                    m.home_team_formation if at_home else m.away_team_formation
                ),
                "tactic": (
                    m.home_team_tactic_type if at_home else m.away_team_tactic_type
                ),
            }
        )
    if limit is not None:
        rows = rows[:limit]

    def tally(subset):
        counts = Counter(r["result"] for r in subset)
        return {key: counts.get(key, 0) for key in ("W", "D", "L")}

    return {
        "matches": rows,
        "record": {
            "all": tally(rows),
            "home": tally([r for r in rows if r["home"]]),
            "away": tally([r for r in rows if not r["home"]]),
        },
    }


def setup_summary(matches, team_id, kind):
    """Results, formations and tactics of team_id in its last RECENT_LIMIT matches of one type.

    kind is a key of SETUP_FILTERS. formations/tactics are shares for a
    stacked bar: (value, times, percent) most used first; unknown values (None or "")
    come last as None.
    """
    allowed = SETUP_FILTERS[kind]
    picked = [m for m in matches if allowed is None or m.matchtype in allowed]
    summary = summarise(picked, team_id, limit=RECENT_LIMIT)
    rows = summary["matches"]
    return {
        "matches": rows,
        "record": summary["record"],
        "formations": shares(r["formation"] for r in rows),
        "tactics": shares(r["tactic"] for r in rows),
    }


def shares(values):
    """(value, times, percent) per value, most used first, unknown (None or "") last."""
    values = [None if v == "" else v for v in values]
    if not values:
        return []
    counts = Counter(v for v in values if v is not None).most_common()
    unknown = values.count(None)
    if unknown:
        counts.append((None, unknown))
    return [(v, n, round(n * 100 / len(values))) for v, n in counts]


def scouting_for(match, team_id, now):
    """What the matches page shows for one upcoming match, from stored data only."""
    opponent_id = opponent_of(match, team_id)
    opponent_name = (
        match.away_team_name if match.home_team_id == team_id else match.home_team_name
    )
    opponent_matches = _past_matches(opponent_id, now)
    meetings = [
        m for m in opponent_matches if team_id in (m.home_team_id, m.away_team_id)
    ]
    return {
        "opponent_name": opponent_name,
        "head_to_head": summarise(meetings, team_id),
        "setup_default": "all",
        "setup": {
            kind: setup_summary(opponent_matches, opponent_id, kind)
            for kind in SETUP_FILTERS
        },
    }
