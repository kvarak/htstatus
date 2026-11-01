"""Team statistics routes blueprint for HT Status application."""

from flask import Blueprint

from app.auth_utils import (
    current_team,
    require_authentication,
    track_activity,
    WRONG_TEAM,
)
from app.utils import create_page

stats_bp = Blueprint("stats", __name__)


def _competition_info(team_record):
    if team_record is None:
        return {}
    return {
        "league_name": team_record.league_name,
        "league_level": team_record.league_level,
        "cup_name": team_record.cup_cup_name,
        "still_in_cup": team_record.cup_still_in_cup,
        "cup_match_rounds_left": team_record.cup_cup_round_index,
        "power_rating": team_record.power_rating,
        "dress_uri": team_record.dress_uri,
        "logo_url": team_record.logo_url,
    }


@stats_bp.route("/stats")
@require_authentication
@track_activity("stats")
def stats():
    """Display team statistics."""
    teamid, teamname = current_team()
    if teamid is None:
        return create_page(template="stats.html", title="Stats", error=WRONG_TEAM)

    from app import team_stats as ts
    from app.roster import latest_player_records
    from app.translations import ht_term
    from models import Players, Team

    players = latest_player_records(Players, teamid)
    top_11 = ts.top_by_tsi(players, limit=11)
    ages_all, ages_top11 = ts.age_distributions(players, top_11)

    charts = {
        "composition": [
            (ht_term("MatchPositions", term, english), count)
            for term, english, count in ts.squad_composition(players)
        ],
        "age_groups": ts.age_groups(players),
        "ages_all": ages_all,
        "ages_top11": ages_top11,
        "max_age_count": max((count for _, count in ages_all), default=1),
        "countries_all": ts.country_distribution(players),
        "countries_top11": ts.country_distribution(top_11),
    }

    return create_page(
        template="stats.html",
        title="Stats",
        teamname=teamname,
        teamid=teamid,
        team_stats=ts.team_statistics(players),
        top_11_skill_averages=ts.team_statistics(top_11).get("skill_averages", {}),
        top_scorers=ts.top_scorers(players),
        top_performers=ts.top_by_tsi(players),
        competition_info=_competition_info(Team.get_by_ht_id(teamid)),
        charts=charts,
    )
