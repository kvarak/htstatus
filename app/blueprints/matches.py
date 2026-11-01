"""Matches routes blueprint for HT Status application."""

from datetime import datetime

from flask import Blueprint, redirect, request, url_for

from app.auth_utils import (
    current_team,
    require_authentication,
    track_activity,
    WRONG_TEAM,
)
from app.hattrick_countries import get_country_display
from app.utils import (
    calculate_formation_effectiveness,
    create_page,
    FORMATION_TEMPLATES,
    get_formation_list,
)

# Create Blueprint for match routes
matches_bp = Blueprint("matches", __name__)

db = None


def setup_matches_blueprint(db_instance):
    """Initialize matches blueprint with db instance."""
    global db
    db = db_instance


@matches_bp.app_template_filter("country_display")
def country_display_filter(country_id):
    """Template filter to display country with flag."""
    return get_country_display(country_id, include_flag=True)


@matches_bp.route("/matches", methods=["GET", "POST"])
@require_authentication
@track_activity("matches")
def matches():
    """Upcoming matches (soonest first) and played matches (latest first)."""
    from models import Match

    teamid, teamname = current_team()
    if teamid is None:
        return create_page(template="matches.html", error=WRONG_TEAM, title="Matches")

    if request.form.get("updatebutton") == "archive":
        return redirect(url_for("team.update", archive=1, id=teamid))

    team_matches = (
        db.session.query(Match)
        .filter((Match.away_team_id == teamid) | (Match.home_team_id == teamid))
        .filter(Match.datetime.isnot(None))
        .order_by(Match.datetime.desc())
        .all()
    )
    now = datetime.now()
    upcoming = sorted(
        (m for m in team_matches if m.datetime > now), key=lambda m: m.datetime
    )
    history = [m for m in team_matches if m.datetime <= now]

    return create_page(
        template="matches.html",
        matches=upcoming + history,
        upcoming_matches=upcoming,
        history_matches=history,
        has_upcoming=bool(upcoming),
        teamname=teamname,
        teamid=teamid,
        title="Matches",
    )


@matches_bp.route("/formations")
@require_authentication
@track_activity("formation")
def formations():
    """Display formation tester and tactical analyzer."""
    from app.roster import latest_player_records
    from models import Players

    teamid, teamname = current_team()
    if teamid is None:
        return create_page(
            template="formations.html", title="Formation Tester", error=WRONG_TEAM
        )

    # Get all current players for the team
    current_players_list = latest_player_records(Players, teamid)

    # Sort players by number (players without numbers go to end)
    current_players_list.sort(key=lambda p: (p.number is None, p.number or 999))

    # Handle formation analysis if form was submitted
    formation_analysis = None
    # Get selected formation from either GET or POST request
    selected_formation = request.args.get(
        "formation", request.form.get("formation", "4-4-2")
    )
    if selected_formation not in FORMATION_TEMPLATES:
        selected_formation = "4-4-2"

    if request.method == "POST" and request.form.get("analyze"):
        player_assignments = {}
        formation_positions = FORMATION_TEMPLATES[selected_formation]["positions"]

        for position_id in formation_positions:
            player_ht_id = request.form.get(f"position_{position_id}")
            if player_ht_id:
                # Find the player object
                player = next(
                    (p for p in current_players_list if str(p.ht_id) == player_ht_id),
                    None,
                )
                if player:
                    player_assignments[position_id] = player

        formation_analysis = calculate_formation_effectiveness(
            selected_formation, player_assignments
        )

    return create_page(
        template="formations.html",
        teamname=teamname,
        teamid=teamid,
        current_players=current_players_list,
        formation_list=get_formation_list(),
        formation_templates=FORMATION_TEMPLATES,
        selected_formation=selected_formation,
        formation_analysis=formation_analysis,
        title="Formation Tester",
    )
