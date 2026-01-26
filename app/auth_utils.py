"""Authentication decorators and utilities for HTStatus application."""

from functools import wraps

from flask import render_template, session


def require_authentication(f):
    """Decorator to require authentication for route access.

    Replaces the repeated pattern:
        if session.get('current_user') is None:
            return render_template('_forward.html', url='/login')

    Usage:
        @blueprint.route('/protected')
        @require_authentication
        def protected_route():
            # Route logic here
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("current_user") is None:
            return render_template("_forward.html", url="/login")
        return f(*args, **kwargs)

    return decorated_function


def get_current_user_id():
    """Get current user ID from session.

    Standardized access to current user ID to replace direct session access.
    """
    return session.get("current_user_id")


def get_user_teams():
    """Get current user's teams from session.

    Returns tuple of (team_ids, team_names) for consistent access.
    """
    return session.get("all_teams", []), session.get("all_team_names", [])


def is_authenticated():
    """Check if user is currently authenticated."""
    return session.get("current_user") is not None


def get_team_info(teamid, user_teams=None):
    """Get team name for given team ID with validation.

    Args:
        teamid: Team ID to look up
        user_teams: Optional tuple of (team_ids, team_names)

    Returns:
        tuple: (is_valid, team_name, error_message)
    """
    if user_teams is None:
        all_teams, all_team_names = get_user_teams()
    else:
        all_teams, all_team_names = user_teams

    if teamid not in all_teams:
        return False, None, "Wrong teamid, try the links."

    team_name = all_team_names[all_teams.index(teamid)]
    return True, team_name, None
