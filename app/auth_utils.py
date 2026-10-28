"""Authentication decorators and utilities for HTStatus application."""

from functools import wraps

from flask import g, render_template, session


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


def get_current_user():
    """Return the logged-in User from the database, or None.

    Cached on ``flask.g`` so a request queries the user at most once, however
    many helpers ask for it. Uses only session + database (never CHPP).
    """
    user_id = get_current_user_id()
    if user_id is None:
        return None
    cached = g.get("current_user_obj")
    if cached is not None and cached.ht_id == user_id:
        return cached

    from app import db
    from app.model_registry import get_user_model

    user = db.session.query(get_user_model()).filter_by(ht_id=user_id).first()
    g.current_user_obj = user
    return user


def track_activity(activity):
    """Decorator recording a page visit via ``User.<activity>()`` before the view.

    Usage (below the route/auth decorators)::

        @bp.route("/training")
        @require_authentication
        @track_activity("training")
        def training(): ...

    Anonymous visitors (no session user) are not tracked.
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if user:
                getattr(user, activity)()
                from app import db

                db.session.commit()
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_user_teams():
    """Get current user's teams from session.

    Returns tuple of (team_ids, team_names) for consistent access.
    """
    return session.get("all_teams", []), session.get("all_team_names", [])


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
