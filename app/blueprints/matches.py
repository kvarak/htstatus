"""Matches routes blueprint for HT Status application."""

from datetime import datetime

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


@matches_bp.app_template_filter('has_enhanced_data')
def has_enhanced_data_filter(match):
    """Template filter to safely check if match has enhanced data."""
    try:
        if hasattr(match, 'has_enhanced_data'):
            return match.has_enhanced_data()
        # Fallback check for enhanced fields
        return (getattr(match, 'home_team_possession', None) is not None or
                getattr(match, 'home_team_shots', None) is not None or
                getattr(match, 'attendance', None) is not None)
    except Exception:
        # If any error occurs, assume no enhanced data
        return False


@matches_bp.route("/matches", methods=["GET", "POST"])
@require_authentication
def matches():
    """Display team matches and match details."""
    try:
        # Get model classes from registry
        from app.model_registry import get_user_model
        from app.utils import dprint
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

        # Safer conversion with error handling
        try:
            teamid = int(teamid) if teamid else request.form.get("id")
            if teamid:
                teamid = int(teamid)
        except (ValueError, TypeError):
            dprint(1, f"Invalid team ID provided: {teamid}")
            return create_page(template="matches.html", error="Invalid team ID provided.", title="Matches")

        try:
            matchid = int(matchid) if matchid else request.form.get("m")
            if matchid:
                matchid = int(matchid)
        except (ValueError, TypeError):
            dprint(1, f"Invalid match ID provided: {matchid}")
            matchid = None

        # Validate session data
        if "all_teams" not in session or not session["all_teams"]:
            dprint(1, "No teams in session, redirecting to update")
            return create_page(template="matches.html", error="No teams available. Please update your data first.", title="Matches")

        all_teams = session["all_teams"]

        # Handle archive download request - redirect to update route
        updatebutton = request.form.get("updatebutton")
        if updatebutton == "archive":
            # Redirect to update route with archive parameter and team ID
            from flask import redirect, url_for
            return redirect(url_for('team.update', archive=1, id=teamid))

        error = ""
        if not teamid or teamid not in all_teams:
            error = "Wrong teamid, try the links."
            return create_page(template="matches.html", error=error, title="Matches")

        if "all_team_names" not in session or not session["all_team_names"]:
            dprint(1, "No team names in session")
            return create_page(template="matches.html", error="Team data incomplete. Please update your data.", title="Matches")

        all_team_names = session["all_team_names"]
        try:
            teamname = all_team_names[all_teams.index(teamid)]
        except (IndexError, ValueError):
            dprint(1, f"Team ID {teamid} not found in team names list")
            return create_page(template="matches.html", error="Team not found in your teams.", title="Matches")

        # Get all registered matches with error handling
        try:
            dbmatches = (
                db.session.query(Match)
                .filter((Match.away_team_id == teamid) | (Match.home_team_id == teamid))
                .order_by(text("datetime desc"))
                .all()
            )
            dprint(2, f"Found {len(dbmatches)} matches for team {teamid}")
        except Exception as e:
            dprint(1, f"Database error fetching matches: {str(e)}")
            return create_page(template="matches.html", error="Error fetching matches from database.", title="Matches")

        # Split matches into upcoming and history for proper sorting
        current_time = datetime.now()
        upcoming_matches = []
        history_matches = []

        for m in dbmatches:
            try:
                if m.datetime and m.datetime > current_time:
                    upcoming_matches.append(m)
                elif m.datetime:
                    history_matches.append(m)
                # Skip matches with no datetime
            except Exception as e:
                dprint(2, f"Error processing match {getattr(m, 'ht_id', 'unknown')}: {str(e)}")
                continue

        # Sort upcoming matches chronologically (earliest first)
        upcoming_matches.sort(key=lambda x: x.datetime)

        # Combine back: upcoming first (chronological), then history (reverse chronological)
        dbmatches = upcoming_matches + history_matches

        # Get match plays with error handling
        dbmatchplays = {}
        for m in dbmatches:
            try:
                dbmatch = db.session.query(MatchPlay).filter_by(match_id=m.ht_id).all()
                dbmatchplays[m.ht_id] = dbmatch
            except Exception as e:
                dprint(2, f"Error fetching match plays for match {m.ht_id}: {str(e)}")
                dbmatchplays[m.ht_id] = []  # Empty list as fallback

        return create_page(
            template="matches.html",
            error=error,
            matches=dbmatches,
            upcoming_matches=upcoming_matches,
            history_matches=history_matches,
            has_upcoming=len(upcoming_matches) > 0,
            matchplays=dbmatchplays,
            matchidtoshow=matchid,
            teamname=teamname,
            teamid=teamid,
            HTmatchtype=HTmatchtype,
            HTmatchrole=HT_MATCH_ROLE,
            HTmatchbehaviour=HTmatchbehaviour,
            current_time=datetime.now(),
            title="Matches",
        )

    except Exception as e:
        # Log the full error for debugging
        import traceback

        from app.utils import dprint

        error_details = traceback.format_exc()
        dprint(1, f"CRITICAL ERROR in matches route: {str(e)}")
        dprint(1, f"Full traceback: {error_details}")

        # Try to log to database if error logging is available
        try:
            from app.error_handlers import log_error_to_database
            log_error_to_database(
                error_type="MatchesRouteError",
                error_message=str(e),
                stack_trace=error_details,
                user_id=session.get("current_user_id"),
                request_url=request.url
            )
        except Exception:  # noqa: S110
            pass  # Don't fail if error logging fails

        # Return a friendly error page instead of 500
        return create_page(
            template="matches.html",
            error="An error occurred loading matches. Please try again or contact support.",
            title="Matches"
        )
    dbmatchplays = {}
    for m in dbmatches:
        dbmatch = db.session.query(MatchPlay).filter_by(match_id=m.ht_id).all()
        dbmatchplays[m.ht_id] = dbmatch

    return create_page(
        template="matches.html",
        error=error,
        matches=dbmatches,
        upcoming_matches=upcoming_matches,
        history_matches=history_matches,
        has_upcoming=len(upcoming_matches) > 0,
        matchplays=dbmatchplays,
        matchidtoshow=matchid,
        teamname=teamname,
        teamid=teamid,
        HTmatchtype=HTmatchtype,
        HTmatchrole=HT_MATCH_ROLE,
        HTmatchbehaviour=HTmatchbehaviour,
        current_time=datetime.now(),
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
