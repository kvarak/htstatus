"""Series (league) table and next round for a team (FEAT-030).

Shows only what Hattrick's data says: no guessed promotion/relegation rules.

Standings (leaguedetails) and the season's matches (leaguefixtures) are fetched
at Update only (CHPP policy) and stored per team as JSON in the instance folder,
so the /series page never calls CHPP and needs no database change.
"""

from datetime import datetime

from app import instance_cache
from app.utils import dprint

FOLDER = "series"
FORM_LENGTH = 5
RIVAL_POINTS = 3  # next-round matches with a team this close to us get a tag


def refresh(chpp, team_id, unit_id):
    """Fetch and store the team's series; failures are logged, never raised."""
    if not unit_id:
        return
    try:
        data = {
            "details": chpp.league_details(unit_id),
            "fixtures": chpp.league_fixtures(unit_id),
            "fetched": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        instance_cache.write_json(FOLDER, team_id, data)
    except Exception as e:
        dprint(1, f"Could not refresh series for team {team_id}: {e}")


def load(team_id):
    """The stored series data for a team, or None before the first Update."""
    return instance_cache.read_json(FOLDER, team_id)


def _played(match):
    return match["home_goals"] is not None and match["away_goals"] is not None


def result_for(match, team_id):
    """ "W", "D" or "L" from the team's point of view (None if unplayed)."""
    if not _played(match):
        return None
    ours, theirs = match["home_goals"], match["away_goals"]
    if match["away_id"] == team_id:
        ours, theirs = theirs, ours
    return "W" if ours > theirs else "L" if ours < theirs else "D"


def form(matches, team_id):
    """The team's last FORM_LENGTH results, oldest first."""
    results = [
        result_for(m, team_id)
        for m in matches
        if _played(m) and team_id in (m["home_id"], m["away_id"])
    ]
    return results[-FORM_LENGTH:]


def _opponent(match, team_id):
    if match["home_id"] == team_id:
        return match["away_id"], match["away_name"], "home"
    return match["home_id"], match["home_name"], "away"


def build_view(data, team_id):
    """Everything the series page shows, computed from the stored CHPP data."""
    details, matches = data["details"], data["fixtures"]["matches"]

    table = []
    for row in details["teams"]:
        table.append(
            {
                **row,
                "goal_difference": (row["goals_for"] or 0)
                - (row["goals_against"] or 0),
                "form": form(matches, row["team_id"]),
                "is_us": row["team_id"] == team_id,
            }
        )
    by_id = {row["team_id"]: row for row in table}
    us = by_id.get(team_id)

    unplayed = [m for m in matches if not _played(m)]
    next_round = min((m["round"] for m in unplayed), default=None)
    next_matches = [m for m in unplayed if m["round"] == next_round]
    rivals = {
        row["team_id"]
        for row in table
        if us and not row["is_us"] and abs(row["points"] - us["points"]) <= RIVAL_POINTS
    }
    next_round_view = [
        {
            **m,
            "home_position": by_id.get(m["home_id"], {}).get("position"),
            "away_position": by_id.get(m["away_id"], {}).get("position"),
            "is_ours": team_id in (m["home_id"], m["away_id"]),
            "is_key": bool(rivals & {m["home_id"], m["away_id"]}),
        }
        for m in next_matches
    ]

    our_remaining = []
    for m in unplayed:
        if team_id not in (m["home_id"], m["away_id"]):
            continue
        opp_id, opp_name, venue = _opponent(m, team_id)
        our_remaining.append(
            {
                "round": m["round"],
                "date": m["date"],
                "opponent_id": opp_id,
                "opponent_name": opp_name,
                "venue": venue,
                "opponent_position": by_id.get(opp_id, {}).get("position"),
            }
        )

    next_opponent = None
    if our_remaining:
        first = our_remaining[0]
        opp_row = by_id.get(first["opponent_id"])
        earlier = [
            m
            for m in matches
            if _played(m)
            and {m["home_id"], m["away_id"]} == {team_id, first["opponent_id"]}
        ]
        next_opponent = {
            **first,
            "row": opp_row,
            "earlier_results": [
                {"match": m, "result": result_for(m, team_id)} for m in earlier
            ],
        }

    leader = table[0] if table else None
    behind_leader = leader["points"] - us["points"] if us and leader else None

    return {
        "details": details,
        "season": data["fixtures"].get("season"),
        "fetched": data.get("fetched"),
        "table": table,
        "us": us,
        "next_round": next_round,
        "next_round_matches": next_round_view,
        "our_remaining": our_remaining,
        "next_opponent": next_opponent,
        "behind_leader": behind_leader,
    }
