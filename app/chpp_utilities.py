"""CHPP Client Utilities

Centralized utilities for CHPP (Community Hattrick Public Platform) client initialization
and common operations. Provides single source of truth for CHPP integration patterns.

This module consolidates CHPP initialization logic previously duplicated across:
- app/blueprints/auth.py (OAuth flows)
- app/blueprints/team.py (team data fetching)
- app/blueprints/matches.py (match data retrieval)

Usage:
    from app.chpp_utilities import get_chpp_client, fetch_user_teams

    chpp = get_chpp_client(session)
    teams = fetch_user_teams(chpp)
"""

from typing import Optional

from flask import current_app

from app.chpp import CHPP


def get_chpp_client(
    flask_session: dict,
    consumer_key: Optional[str] = None,
    consumer_secret: Optional[str] = None,
) -> CHPP:
    """Initialize CHPP client with session credentials.

    Args:
        flask_session: Flask session containing access_key and access_secret
        consumer_key: Optional CHPP consumer key (uses app config if not provided)
        consumer_secret: Optional CHPP consumer secret (uses app config if not provided)

    Returns:
        CHPP: Initialized CHPP client instance

    Raises:
        KeyError: If required session keys or config values are missing

    Example:
        >>> chpp = get_chpp_client(session)
        >>> user = chpp.user()
    """
    # Use provided credentials or fall back to app config
    if consumer_key is None:
        consumer_key = current_app.config["CONSUMER_KEY"]
    if consumer_secret is None:
        consumer_secret = current_app.config["CONSUMER_SECRETS"]

    # Initialize with session OAuth tokens
    return CHPP(
        consumer_key,
        consumer_secret,
        flask_session["access_key"],
        flask_session["access_secret"],
    )


def get_chpp_client_no_auth(
    consumer_key: Optional[str] = None,
    consumer_secret: Optional[str] = None,
) -> CHPP:
    """Initialize CHPP client without OAuth tokens (for OAuth flow initiation).

    Args:
        consumer_key: Optional CHPP consumer key (uses app config if not provided)
        consumer_secret: Optional CHPP consumer secret (uses app config if not provided)

    Returns:
        CHPP: Initialized CHPP client instance without user tokens

    Example:
        >>> chpp = get_chpp_client_no_auth()
        >>> auth_url = chpp.authorize()
    """
    # Use provided credentials or fall back to app config
    if consumer_key is None:
        consumer_key = current_app.config["CONSUMER_KEY"]
    if consumer_secret is None:
        consumer_secret = current_app.config["CONSUMER_SECRETS"]

    return CHPP(consumer_key, consumer_secret)


def fetch_user_teams(chpp: CHPP, user=None) -> tuple[list[int], list[str]]:
    """Fetch the IDs and names of all teams owned by the current CHPP user.

    Works around the known CHPP "YouthTeamId" parse error on ``user()`` (users
    without a youth team) by reading team IDs from managercompendium directly.
    A team whose name can't be fetched is called "Team <id>".

    Args:
        chpp: Initialized CHPP client with user authentication
        user: Optional already-fetched ``chpp.user()`` result
    """
    try:
        team_ids = (user or chpp.user())._teams_ht_id
    except Exception as e:
        if "YouthTeamId" not in str(e):
            raise
        root = chpp.request(file="managercompendium", version="1.6")
        team_ids = [
            int(node.text) for node in root.findall(".//Team/TeamId") if node.text
        ]

    team_names = []
    for team_id in team_ids:
        try:
            team_names.append(chpp.team(ht_id=team_id).name)
        except Exception:
            team_names.append(f"Team {team_id}")
    return team_ids, team_names


def get_current_user_context(chpp: CHPP) -> dict:
    """Fetch current user context including user details and owned teams.

    Args:
        chpp: Initialized CHPP client with user authentication

    Returns:
        dict: User context containing user object, team IDs, and team names

    Example:
        >>> chpp = get_chpp_client(session)
        >>> context = get_current_user_context(chpp)
        >>> print(f"User: {context['user'].username}")
        >>> print(f"Teams: {context['team_names']}")
    """
    user = chpp.user()
    team_ids, team_names = fetch_user_teams(chpp, user)

    return {
        "user": user,
        "team_ids": team_ids,
        "team_names": team_names,
        "ht_user": user.username,
        "ht_id": user.ht_id,
    }
