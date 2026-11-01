"""Series (league table + next round) page for one of the user's teams (FEAT-030)."""

from flask import Blueprint

from app import series
from app.auth_utils import (
    current_team,
    require_authentication,
    track_activity,
    WRONG_TEAM,
)
from app.utils import create_page

series_bp = Blueprint("series", __name__)


@series_bp.route("/series")
@require_authentication
@track_activity("series")
def series_page():
    """Show the stored series data (fetched at Update; no CHPP calls here)."""
    team_id, team_name = current_team()
    if team_id is None:
        return create_page(
            template="series.html", title="Series", error=WRONG_TEAM, view=None
        )
    data = series.load(team_id)
    return create_page(
        template="series.html",
        title="Series",
        teamid=team_id,
        teamname=team_name,
        view=series.build_view(data, team_id) if data else None,
    )
