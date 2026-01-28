"""Matches and stats routes blueprint for HT Status application."""
import traceback

from flask import Blueprint, request, session
from sqlalchemy import text

from app.auth_utils import require_authentication
from app.chpp_utilities import get_chpp_client
from app.hattrick_countries import get_country_display
from app.model_registry import get_match_model, get_match_play_model
from app.utils import create_page, dprint

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
        HTmatchrole=HTmatchrole,
        HTmatchbehaviour=HTmatchbehaviour,
        title="Matches",
    )


@matches_bp.route("/stats")
@require_authentication
def stats():
    """Display team statistics."""
    from app.model_registry import get_user_model

    # Track user activity (team-related page)
    User = get_user_model()
    current_user = db.session.query(User).filter_by(ht_id=session["current_user_id"]).first()
    if current_user:
        current_user.team()
        db.session.commit()

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
    top_scorers = get_top_scorers(current_players_list, limit=10, sort_by_ratio=True)
    top_performers = get_top_performers(current_players_list, limit=10)

    # Calculate skill averages for top 11 TSI players
    top_11_players = get_top_performers(current_players_list, limit=11)
    top_11_stats = calculate_team_statistics(top_11_players) if top_11_players else {}
    top_11_skill_averages = top_11_stats.get('skill_averages', {}) if top_11_stats else {}

    # Calculate age distribution for all players and top 11
    def calculate_age_distribution_unified(all_players, subset_players, min_age=16):
        """Calculate age distribution with unified age range for both datasets."""
        # Get all ages from all players to define the complete range
        all_ages = []
        for player in all_players:
            age = getattr(player, 'age_years', 0)
            if age >= min_age:
                all_ages.append(age)

        if not all_ages:
            return [], []

        # Define unified age range
        min_age_range = min(all_ages)
        max_age_range = max(all_ages)

        # Calculate distribution for all players
        all_age_counts = {}
        for player in all_players:
            age = getattr(player, 'age_years', 0)
            if age >= min_age:
                all_age_counts[age] = all_age_counts.get(age, 0) + 1

        # Calculate distribution for subset players
        subset_age_counts = {}
        for player in subset_players:
            age = getattr(player, 'age_years', 0)
            if age >= min_age:
                subset_age_counts[age] = subset_age_counts.get(age, 0) + 1

        # Create complete distributions with unified range
        all_distribution = []
        subset_distribution = []
        for age in range(min_age_range, max_age_range + 1):
            all_distribution.append((age, all_age_counts.get(age, 0)))
            subset_distribution.append((age, subset_age_counts.get(age, 0)))

        return all_distribution, subset_distribution

    age_distribution_all, age_distribution_top11 = calculate_age_distribution_unified(
        current_players_list,
        top_11_players if top_11_players else []
    )

    # Calculate country distribution for all players and top 11
    def calculate_country_distribution(all_players, subset_players):
        """Calculate country distribution for both datasets."""
        from app.hattrick_countries import get_country_info

        # Calculate distribution for all players
        all_country_data = {}
        for player in all_players:
            country_id = getattr(player, 'native_country_id', None)
            country_info = get_country_info(country_id)
            country_display = f"{country_info['flag']} {country_info['name']}"
            if country_display not in all_country_data:
                all_country_data[country_display] = {
                    'count': 0,
                    'color': country_info['color'],
                    'name': country_info['name']
                }
            all_country_data[country_display]['count'] += 1

        # Calculate distribution for subset players
        subset_country_data = {}
        for player in subset_players:
            country_id = getattr(player, 'native_country_id', None)
            country_info = get_country_info(country_id)
            country_display = f"{country_info['flag']} {country_info['name']}"
            if country_display not in subset_country_data:
                subset_country_data[country_display] = {
                    'count': 0,
                    'color': country_info['color'],
                    'name': country_info['name']
                }
            subset_country_data[country_display]['count'] += 1

        # Convert to list of tuples sorted by count, maintaining color info
        all_distribution = sorted(
            [(country, data['count'], data['color']) for country, data in all_country_data.items()],
            key=lambda x: x[1], reverse=True
        )
        subset_distribution = sorted(
            [(country, data['count'], data['color']) for country, data in subset_country_data.items()],
            key=lambda x: x[1], reverse=True
        )

        return all_distribution, subset_distribution

    country_distribution_all, country_distribution_top11 = calculate_country_distribution(
        current_players_list,
        top_11_players if top_11_players else []
    )

    # Find max count for scaling the bars (use all players max for both charts)
    max_count_all = max([count for age, count in age_distribution_all], default=1)
    match_stats = get_team_match_statistics(teamid)

    # Get competition data from CHPP (trophies not currently supported)
    trophies = []
    competition_info = {}
    try:
        print(f"\n=== FETCHING COMPETITION DATA FOR TEAM {teamid} ===")

        # Get CHPP client
        chpp = get_chpp_client(session)

        print("Using Custom CHPP client")

        team_details = chpp.team(ht_id=teamid)
        dprint(2, f"Team details fetched: {team_details.name}")

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

        dprint(2, f"Competition info extracted: {competition_info}")

    except Exception as e:
        dprint(1, f"Error fetching competition data: {e}")
        dprint(3, traceback.format_exc())
        competition_info = {}

    print("=== COMPETITION FETCH COMPLETE ===\n")

    return create_page(
        template="stats.html",
        teamname=teamname,
        teamid=teamid,
        team_stats=team_stats,
        top_scorers=top_scorers,
        top_performers=top_performers,
        current_players=current_players_list,
        match_stats=match_stats,
        trophies=trophies,
        competition_info=competition_info,
        top_11_skill_averages=top_11_skill_averages,
        age_distribution_all=age_distribution_all,
        age_distribution_top11=age_distribution_top11,
        country_distribution_all=country_distribution_all,
        country_distribution_top11=country_distribution_top11,
        max_count_all=max_count_all,
        title="Stats",
    )
