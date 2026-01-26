"""Matches and stats routes blueprint for HT Status application."""

from flask import Blueprint, request, session
from sqlalchemy import text

from app.auth_utils import require_authentication
from app.model_registry import get_match_model, get_match_play_model
from app.utils import create_page

# Create Blueprint for match and stats routes
matches_bp = Blueprint("matches", __name__)

# These will be set by setup_matches_blueprint()
db = None
HTmatchtype = {}
HTmatchrole = {}
HTmatchbehaviour = {}


def setup_matches_blueprint(db_instance, match_types, match_roles, match_behaviours):
    """Initialize matches blueprint with db instance and Hattrick constants."""
    global db, HTmatchtype, HTmatchrole, HTmatchbehaviour
    db = db_instance
    HTmatchtype = match_types
    HTmatchrole = match_roles
    HTmatchbehaviour = match_behaviours


@matches_bp.route("/matches", methods=["GET", "POST"])
@require_authentication
def matches():
    """Display team matches and match details."""
    # Get model classes from registry
    Match = get_match_model()
    MatchPlay = get_match_play_model()

    teamid = request.values.get("id")
    matchid = request.values.get("m")

    teamid = int(teamid) if teamid else request.form.get("id")
    matchid = int(matchid) if matchid else request.form.get("m")
    all_teams = session["all_teams"]

    error = ""
    if teamid not in all_teams:
        error = "Wrong teamid, try the links."
        return create_page(template="matches.html", error=error, title="Matches")

    all_team_names = session["all_team_names"]
    teamname = all_team_names[all_teams.index(teamid)]

    # Get all registered matches
    dbmatches = (
        db.session.query(Match)
        .filter((Match.away_team_id == teamid) | (Match.home_team_id == teamid))
        .order_by(text("datetime desc"))
        .all()
    )
    dbmatchplays = {}
    for m in dbmatches:
        dbmatch = db.session.query(MatchPlay).filter_by(match_id=m.ht_id).all()
        dbmatchplays[m.ht_id] = dbmatch

    return create_page(
        template="matches.html",
        error=error,
        matches=dbmatches,
        matchplays=dbmatchplays,
        matchidtoshow=matchid,
        teamname=teamname,
        teamid=teamid,
        HTmatchtype=HTmatchtype,
        HTmatchrole=HTmatchrole,
        HTmatchbehaviour=HTmatchbehaviour,
        title="Matches",
    )


@matches_bp.route("/stats")
@require_authentication
def stats():
    """Display team statistics."""

    teamid = request.values.get("id")

    teamid = int(teamid) if teamid else request.form.get("id")
    all_teams = session["all_teams"]

    if teamid not in all_teams:
        return create_page(template="stats.html", title="Stats")

    all_team_names = session["all_team_names"]
    teamname = all_team_names[all_teams.index(teamid)]

    # Get all current players for the team
    from models import Players

    current_players = (
        db.session.query(Players)
        .filter_by(owner=teamid)
        .order_by(Players.data_date.desc())
        .all()
    )

    # Filter to get the most recent data for each player
    latest_players = {}
    for player in current_players:
        if player.ht_id not in latest_players:
            latest_players[player.ht_id] = player

    current_players_list = list(latest_players.values())

    # Calculate team statistics
    from app.utils import (
        calculate_team_statistics,
        get_team_match_statistics,
        get_top_performers,
        get_top_scorers,
    )

    team_stats = calculate_team_statistics(current_players_list)

    # Get top performers
    top_scorers = get_top_scorers(current_players_list)
    top_performers = get_top_performers(current_players_list)

    # Get match statistics for the team
    match_stats = get_team_match_statistics(teamid)

    # Get competition data from CHPP (trophies not supported in this pyCHPP version)
    trophies = []
    competition_info = {}
    try:
        print(f"\n=== FETCHING COMPETITION DATA FOR TEAM {teamid} ===")
        from flask import current_app as app

        from pychpp import CHPP

        chpp = CHPP(
            app.config["CONSUMER_KEY"],
            app.config["CONSUMER_SECRETS"],
            session["access_key"],
            session["access_secret"],
        )

        # Check pyCHPP version
        import pychpp

        print(f"pyCHPP version: {getattr(pychpp, '__version__', 'Unknown')}")

        team_details = chpp.team(ht_id=teamid)
        print(f"Team details fetched: {team_details.name}")

        # Extract available competition information
        competition_info = {
            "league_name": getattr(team_details, "league_name", None),
            "league_level": getattr(team_details, "league_level", None),
            "league_level_unit_name": getattr(
                team_details, "league_level_unit_name", None
            ),
            "cup_name": getattr(team_details, "cup_name", None),
            "cup_level": getattr(team_details, "cup_level", None),
            "still_in_cup": getattr(team_details, "still_in_cup", False),
            "cup_match_rounds_left": getattr(team_details, "cup_match_rounds_left", 0),
            "power_rating": getattr(team_details, "power_rating", None),
            "power_rating_global_ranking": getattr(
                team_details, "power_rating_global_ranking", None
            ),
            "power_rating_league_ranking": getattr(
                team_details, "power_rating_league_ranking", None
            ),
            "dress_uri": getattr(team_details, "dress_uri", None),
            "dress_alternate_uri": getattr(team_details, "dress_alternate_uri", None),
            "logo_url": getattr(team_details, "logo_url", None),
        }

        print(f"Competition info extracted: {competition_info}")
        print("Note: Trophy data not supported in this pyCHPP version")

    except Exception as e:
        print(f"Error fetching competition data: {e}")
        import traceback

        print(traceback.format_exc())
        competition_info = {}

    print("=== COMPETITION FETCH COMPLETE ===\n")

    return create_page(
        template="stats.html",
        teamname=teamname,
        teamid=teamid,
        team_stats=team_stats,
        top_scorers=top_scorers,
        top_performers=top_performers,
        match_stats=match_stats,
        trophies=trophies,
        competition_info=competition_info,
        title="Stats",
    )
