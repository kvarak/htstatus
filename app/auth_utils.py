"""Authentication decorators and utilities for HTStatus application."""

from functools import wraps

from flask import g, render_template, request, session


def require_authentication(f):
    """Decorator to require authentication for route access.

    Replaces the repeated pattern:
        if session.get('current_user') is None:
            return render_template('_forward.html', url='/login')

    Also logs the user out when the session points to a user that no longer
    exists in the database.

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
        if get_current_user() is None:
            # Session outlived its User row (e.g. DB reset); logging in recreates it
            session.clear()
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
    from models import User

    user = db.session.query(User).filter_by(ht_id=user_id).first()
    g.current_user_obj = user
    return user


def track_activity(activity):
    """Decorator recording a page visit via ``User.record_visit(activity)`` before the view.

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
                user.record_visit(activity)
                from app import db

                db.session.commit()
            return f(*args, **kwargs)

        return decorated_function

    return decorator


WRONG_TEAM = "Wrong teamid, try the links."


def current_team(raw_id=None):
    """The requested team if it is one of the user's teams.

    Reads ``id`` from the query string/form unless ``raw_id`` is given.
    Returns ``(team_id, team_name)``, or ``(None, None)`` for a missing,
    malformed or foreign team id.
    """
    if raw_id is None:
        raw_id = request.values.get("id")
    try:
        team_id = int(raw_id)
    except (TypeError, ValueError):
        return None, None
    teams = session.get("all_teams", [])
    if team_id not in teams:
        return None, None
    return team_id, session.get("all_team_names", [])[teams.index(team_id)]
