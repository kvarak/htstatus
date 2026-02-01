"""Team statistics routes blueprint for HT Status application."""
import traceback

from flask import Blueprint, request, session

from app.auth_utils import require_authentication
from app.utils import create_page, dprint

# Create Blueprint for stats routes
stats_bp = Blueprint("stats", __name__)

# This will be set by setup_stats_blueprint()
db = None


def setup_stats_blueprint(db_instance):
    """Initialize stats blueprint with db instance."""
    global db
    db = db_instance


@stats_bp.route("/stats")
@require_authentication
def stats():
    """Display team statistics."""
    from app.model_registry import get_user_model

    # Track user activity (stats page)
    User = get_user_model()
    current_user = db.session.query(User).filter_by(ht_id=session["current_user_id"]).first()
    if current_user:
        current_user.stats()
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
    # REFACTOR-064: Get competition data from database instead of CHPP API
    competition_info = {}
    try:
        dprint(2, f"Fetching competition data from database for team {teamid}")

        # Import Team model here to avoid circular imports
        from models import Team

        # Get team competition data from database
        team_record = Team.get_by_ht_id(teamid)
        if team_record:
            competition_info = {
                "league_name": team_record.league_name,
                "league_level": team_record.league_level,
                "league_level_unit_name": None,  # Not stored in current model
                "cup_name": team_record.cup_cup_name,
                "cup_level": team_record.cup_cup_round,
                "still_in_cup": team_record.cup_still_in_cup,
                "cup_match_rounds_left": team_record.cup_cup_round_index,
                "power_rating": team_record.power_rating,
                "power_rating_global_ranking": None,  # Not stored in current model
                "power_rating_league_ranking": None,  # Not stored in current model
                "dress_uri": team_record.dress_uri,
                "dress_alternate_uri": None,  # Not stored in current model
                "logo_url": team_record.logo_url,
            }
            dprint(2, f"Competition info loaded from database: {competition_info}")
        else:
            dprint(1, f"No team record found in database for team {teamid}")
            competition_info = {}

    except Exception as e:
        dprint(1, f"Error fetching competition data from database: {e}")
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
