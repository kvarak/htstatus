"""Matches routes blueprint for HT Status application."""

from flask import Blueprint, request, session
from sqlalchemy import text

from app.auth_utils import require_authentication
from app.constants import HT_MATCH_ROLE
from app.hattrick_countries import get_country_display
from app.model_registry import get_match_model, get_match_play_model
from app.utils import (
    FORMATION_TEMPLATES,
    calculate_formation_effectiveness,
    create_page,
    get_formation_list,
)

# Create Blueprint for match routes
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


@matches_bp.app_template_filter('country_display')
def country_display_filter(country_id):
    """Template filter to display country with flag."""
    return get_country_display(country_id, include_flag=True)


@matches_bp.route("/matches", methods=["GET", "POST"])
@require_authentication
def matches():
    """Display team matches and match details."""
    # Get model classes from registry
    from app.model_registry import get_user_model
    Match = get_match_model()
    MatchPlay = get_match_play_model()

    # Track user activity
    User = get_user_model()
    current_user = db.session.query(User).filter_by(ht_id=session["current_user_id"]).first()
    if current_user:
        current_user.matches()
        db.session.commit()

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
        HTmatchrole=HT_MATCH_ROLE,
        HTmatchbehaviour=HTmatchbehaviour,
        title="Matches",
    )


@matches_bp.route("/formations")
@require_authentication
def formations():
    """Display formation tester and tactical analyzer."""
    from app.model_registry import get_user_model
    from models import Players

    # Track user activity (formation page)
    User = get_user_model()
    current_user = db.session.query(User).filter_by(ht_id=session["current_user_id"]).first()
    if current_user:
        current_user.formation()
        db.session.commit()

    teamid = request.values.get("id")
    teamid = int(teamid) if teamid else request.form.get("id")
    all_teams = session["all_teams"]

    if teamid not in all_teams:
        return create_page(template="formations.html", title="Formation Tester")

    all_team_names = session["all_team_names"]
    teamname = all_team_names[all_teams.index(teamid)]

    # Get all current players for the team
    current_players = (
        db.session.query(Players)
        .filter_by(owner=teamid)
        .order_by(Players.data_date.desc(), Players.tsi.desc())
        .all()
    )

    # Filter to get the most recent data for each player
    latest_players = {}
    for player in current_players:
        if player.ht_id not in latest_players:
            latest_players[player.ht_id] = player

    current_players_list = list(latest_players.values())

    # Sort players by number (players without numbers go to end)
    current_players_list.sort(key=lambda p: (p.number is None, p.number or 999))

    # Handle formation analysis if form was submitted
    formation_analysis = None
    # Get selected formation from either GET or POST request
    selected_formation = request.args.get("formation", request.form.get("formation", "4-4-2"))

    if request.method == "POST" and request.form.get("analyze"):
        player_assignments = {}
        formation_positions = FORMATION_TEMPLATES[selected_formation]["positions"]

        for position_id in formation_positions:
            player_ht_id = request.form.get(f"position_{position_id}")
            if player_ht_id:
                # Find the player object
                player = next((p for p in current_players_list if str(p.ht_id) == player_ht_id), None)
                if player:
                    player_assignments[position_id] = player

        formation_analysis = calculate_formation_effectiveness(selected_formation, player_assignments)

    return create_page(
        template="formations.html",
        teamname=teamname,
        teamid=teamid,
        current_players=current_players_list,
        formation_list=get_formation_list(),
        formation_templates=FORMATION_TEMPLATES,
        selected_formation=selected_formation,
        formation_analysis=formation_analysis,
        HTmatchrole=HT_MATCH_ROLE,
        title="Formation Tester",
    )
