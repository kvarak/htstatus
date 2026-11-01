"""Series (league table + next round) page for one of the user's teams (FEAT-030)."""

from flask import Blueprint, request, session

from app import series
from app.auth_utils import require_authentication, track_activity
from app.utils import create_page

series_bp = Blueprint("series", __name__)


@series_bp.route("/series")
@require_authentication
@track_activity("series")
def series_page():
    """Show the stored series data (fetched at Update; no CHPP calls here)."""
    all_teams = session.get("all_teams", [])
    try:
        team_id = int(request.args.get("id", ""))
    except ValueError:
        team_id = all_teams[0] if all_teams else None
    if team_id not in all_teams:
        return create_page(
            template="series.html", title="Series", error="Unknown team.", view=None
        )

    team_name = session.get("all_team_names", [])[all_teams.index(team_id)]
    data = series.load(team_id)
    return create_page(
        template="series.html",
        title="Series",
        teamid=team_id,
        teamname=team_name,
        view=series.build_view(data, team_id) if data else None,
    )
