"""Shared utility functions for HT Status application."""

import inspect
from datetime import datetime

from flask import current_app, render_template, session

from app.chpp import CHPP

# Global variables - will be initialized by initialize_utils()
db = None
debug_level = None


def initialize_utils(_app_instance, db_instance, debug_level_value):
    """Initialize utilities module with app and db instances."""
    # pylint: disable=unused-argument
    global db, debug_level
    db = db_instance
    debug_level = debug_level_value


# =============================================================================
# Debugging and Logging Utilities
# =============================================================================


def dprint(lvl, *args):
    """Debug print with level checking."""
    if debug_level is None or lvl <= debug_level:
        fname = inspect.stack()[1].filename.split("/")[-1]  # get calling file
        print(f"[{fname}]", *args)


def debug_print(route, function, *args):
    """Enhanced debug print for route tracing."""
    if debug_level is None or debug_level >= 2:
        fname = inspect.stack()[1].filename.split("/")[-1]  # get calling file
        print(f"[{fname}] {route}::{function}() -", *args)


# =============================================================================
# Date and Comparison Utilities
# =============================================================================


def diff_month(d1, d2):
    """Calculate month difference between two dates."""
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def diff(first, second):
    """Calculate difference between two values with None handling.

    For lists/iterables, returns items in first but not in second.
    For numeric values, returns arithmetic difference.
    """
    if first is None or second is None:
        return None

    # Handle list/set operations
    if isinstance(first, (list, tuple, set)) and isinstance(second, (list, tuple, set)):
        return list(set(first) - set(second))

    # Handle numeric operations
    return first - second


# =============================================================================
# Version Detection Utilities
# =============================================================================


def get_version_info():
    """Get version information with feature-based minor versioning.

    Returns dict with version, fullversion, versionstr for consistent use across app.
    - Major version from git tags (e.g., "3.0")
    - Minor version = count of features implemented since last major version
    - Patch version from git describe build number
    - Git hash for identification
    """
    import subprocess

    try:
        # Get git describe output
        versionstr_raw = subprocess.check_output(["git", "describe", "--tags"]).strip().decode()
        versionstr_parts = versionstr_raw.split("-")

        if len(versionstr_parts) >= 3:
            major_version_tag = versionstr_parts[0]  # e.g., "3.0"
            build_number = versionstr_parts[1]       # e.g., "16"
            git_hash = versionstr_parts[2]           # e.g., "gb9fb21c"

            # Extract major version number (3 from "3.0")
            major_number = major_version_tag.split('.')[0]  # "3"

            # Count features since last major version tag
            try:
                # Get commit messages since the last major version tag
                feature_commits = subprocess.check_output([
                    "git", "log", f"{major_version_tag}..HEAD", "--oneline", "--grep=FEAT-", "--grep=Add feature", "--grep=Implement"
                ]).strip().decode()

                # Count feature commits (non-empty lines)
                feature_count = len([line for line in feature_commits.split('\n') if line.strip()]) if feature_commits.strip() else 0

                # Count commits since last feature commit
                if feature_commits.strip():
                    # Get the hash of the most recent feature commit
                    recent_feature_lines = feature_commits.strip().split('\n')
                    most_recent_feature_hash = recent_feature_lines[0].split()[0]  # First word is the commit hash

                    # Count commits since that feature commit
                    commits_since_feature = subprocess.check_output([
                        "git", "rev-list", "--count", f"{most_recent_feature_hash}..HEAD"
                    ]).strip().decode()

                    patch_count = int(commits_since_feature) if commits_since_feature.isdigit() else 0
                else:
                    # No feature commits, count all commits since major version tag
                    commits_since_major = subprocess.check_output([
                        "git", "rev-list", "--count", f"{major_version_tag}..HEAD"
                    ]).strip().decode()
                    patch_count = int(commits_since_major) if commits_since_major.isdigit() else 0

            except subprocess.CalledProcessError:
                # Fallback: use build number if git log fails
                feature_count = int(build_number) if build_number.isdigit() else 0
                patch_count = 0

            # Semantic versioning format: major.minor.patch-ghash where minor = feature count, patch = commits since last feature
            version = f"{major_number}.{feature_count}"
            fullversion = f"{major_number}.{feature_count}.{patch_count}-{git_hash}"
            versionstr = fullversion
        else:
            # Simple tag without build info
            fullversion = versionstr_raw
            version = versionstr_raw
            versionstr = versionstr_raw
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        # Fallback for development environment
        fullversion = "2.0.0-dev"
        version = "2.0.0"
        versionstr = "2.0.0-dev"

    return {
        "version": version,
        "fullversion": fullversion,
        "versionstr": versionstr,
    }


# =============================================================================
# Template and Page Utilities
# =============================================================================


def create_page(template, title, **kwargs):
    """Create standardized page response with common template variables."""
    import time

    from flask import current_app, session

    # Get version info using shared function
    version_info = get_version_info()

    # Standard template variables
    template_vars = {
        "bootstrap": None,  # Bootstrap handled by template
        "title": title,
        "apptitle": current_app.config.get("APP_NAME", "HT Status"),
        "consumer_key": current_app.config.get("CONSUMER_KEY", ""),
        "consumer_secret": current_app.config.get("CONSUMER_SECRETS", ""),
        "versionstr": version_info["versionstr"],
        "fullversion": version_info["fullversion"],
        "version": version_info["version"],
        "timenow": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Add session variables for logged-in users
    if session.get("current_user"):
        template_vars.update(
            {
                "current_user": session.get("current_user"),
                "current_user_id": session.get("current_user_id"),
                "all_teams": session.get("all_teams", []),
                "all_team_names": session.get("all_team_names", []),
                "team_id": session.get("team_id"),
                "password_migration_needed": session.get(
                    "password_migration_needed", False
                ),
            }
        )

        # Check if user has admin role
        from models import User

        user = User.query.filter_by(ht_id=session.get("current_user_id")).first()
        if user and user.role == "Admin":
            template_vars["role"] = "Admin"

    # Add any additional template variables
    template_vars.update(kwargs)

    return render_template(template, **template_vars)


# =============================================================================
# Player Data Processing Utilities
# =============================================================================


def get_training(players_data):
    """Process training data from player list."""
    if not players_data:
        return [], {}, {}

    # Group players by ht_id and sort by date
    player_timelines = {}
    playernames = {}

    for player in players_data:
        ht_id = player.ht_id
        if ht_id not in player_timelines:
            player_timelines[ht_id] = []
            playernames[ht_id] = f"{player.first_name} {player.last_name}"

        # Create skills array in the order expected by templates
        skills = [
            player.keeper or 0,
            player.defender or 0,
            player.playmaker or 0,
            player.winger or 0,
            player.passing or 0,
            player.scorer or 0,
            player.set_pieces or 0,
        ]

        date_str = player.data_date.strftime("%Y-%m-%d") if player.data_date else "N/A"
        player_timelines[ht_id].append((date_str, skills))

    # Sort each player's timeline by date
    for ht_id in player_timelines:
        player_timelines[ht_id].sort(key=lambda x: x[0])

    # Get list of all player IDs
    allplayerids = list(player_timelines.keys())

    # allplayers should contain the timeline data for each player
    allplayers = player_timelines

    return allplayerids, allplayers, playernames


def player_diff(playerid, daysago, team_name="Unknown Team"):
    """Get player skill differences over time.

    Args:
        playerid: Hattrick player ID
        daysago: Number of days back to compare
        team_name: Team name for display (default: "Unknown Team")

    Returns:
        List of changes, each as: [team_name, first_name, last_name, skill, old_val, new_val]
        Returns empty list if no changes found.
    """
    try:
        from datetime import datetime

        from dateutil.relativedelta import relativedelta
        from sqlalchemy import desc

        from models import Players

        # Query for player data from specified days ago
        cutoff_date = datetime.now() - relativedelta(days=daysago)

        # Get the most recent record before or on the cutoff date
        old_player = (
            db.session.query(Players)
            .filter_by(ht_id=playerid)
            .filter(Players.data_date <= cutoff_date)
            .order_by(desc(Players.data_date))
            .first()
        )

        # Get the most recent record overall
        current_player = (
            db.session.query(Players)
            .filter_by(ht_id=playerid)
            .order_by(desc(Players.data_date))
            .first()
        )

        if not old_player or not current_player:
            return []

        # Calculate differences for each skill
        skills = [
            "keeper",
            "defender",
            "playmaker",
            "winger",
            "passing",
            "scorer",
            "set_pieces",
        ]
        differences = []

        for skill in skills:
            old_val = getattr(old_player, skill, 0) or 0
            new_val = getattr(current_player, skill, 0) or 0

            if old_val != new_val:
                differences.append(
                    [
                        team_name,
                        current_player.first_name or "Unknown",
                        current_player.last_name or "Player",
                        skill.capitalize(),
                        old_val,
                        new_val,
                    ]
                )

        # If no differences found, return empty list
        if not differences:
            return []

        # Return flat list of changes (simplified API)
        return differences

    except Exception as e:
        dprint(1, f"Error in player_diff: {e}")
        return []


def player_daily_changes(playerid, days_ago, team_name="Unknown Team"):
    """Get player skill changes between two consecutive days (for timeline view).

    This function compares skills between today-days_ago and today-(days_ago+1)
    to show only changes that occurred on that specific day.

    Args:
        playerid: Hattrick player ID
        days_ago: Number of days back to check (0 = today vs yesterday)
        team_name: Team name for display

    Returns: List with same format as player_diff, but only for day-specific changes
    """
    try:
        from datetime import datetime, timedelta

        from sqlalchemy import Date, cast, desc

        from models import Players

        # Calculate target dates
        target_date = (datetime.now() - timedelta(days=days_ago)).date()

        # Get the most recent record for target date
        target_player = (
            db.session.query(Players)
            .filter_by(ht_id=playerid)
            .filter(cast(Players.data_date, Date) == target_date)
            .order_by(desc(Players.data_date))
            .first()
        )

        # Get the most recent record BEFORE target date (not necessarily previous day)
        prev_player = (
            db.session.query(Players)
            .filter_by(ht_id=playerid)
            .filter(cast(Players.data_date, Date) < target_date)
            .order_by(desc(Players.data_date))
            .first()
        )

        if not target_player or not prev_player:
            return []

        # Calculate differences for each skill
        skills = [
            "keeper",
            "defender",
            "playmaker",
            "winger",
            "passing",
            "scorer",
            "set_pieces",
        ]
        differences = []

        for skill in skills:
            old_val = getattr(prev_player, skill, 0) or 0
            new_val = getattr(target_player, skill, 0) or 0

            if old_val != new_val:
                differences.append(
                    [
                        team_name,
                        target_player.first_name or "Unknown",
                        target_player.last_name or "Player",
                        skill.capitalize(),
                        old_val,
                        new_val,
                    ]
                )

        # If no differences found, return empty list
        if not differences:
            return []

        # Return nested structure: [[player_info], [changes...]]
        return [
            [
                team_name,
                target_player.first_name or "Unknown",
                target_player.last_name or "Player",
            ]
        ] + differences

    except Exception as e:
        dprint(1, f"Error in player_daily_changes: {e}")
        return []


def get_player_changes(player_id, start_days_ago, end_days_ago):
    """Universal function to get ANY player changes between two time periods.

    Args:
        player_id: Hattrick player ID
        start_days_ago: Start of period (older date, higher number)
        end_days_ago: End of period (newer date, lower number)
        team_name: Team name for display

    Returns:
        List of changes: [player_name, attribute, old_value, new_value, change_type]
    """
    try:
        from datetime import datetime, timedelta

        from sqlalchemy import Date, cast, desc

        from models import Players

        # Calculate dates
        start_date = (datetime.now() - timedelta(days=start_days_ago)).date()
        end_date = (datetime.now() - timedelta(days=end_days_ago)).date()

        # Get records at start and end of period
        old_record = (
            db.session.query(Players)
            .filter_by(ht_id=player_id)
            .filter(cast(Players.data_date, Date) <= start_date)
            .order_by(desc(Players.data_date))
            .first()
        )

        new_record = (
            db.session.query(Players)
            .filter_by(ht_id=player_id)
            .filter(cast(Players.data_date, Date) <= end_date)
            .order_by(desc(Players.data_date))
            .first()
        )

        if (
            not old_record
            or not new_record
            or old_record.data_date == new_record.data_date
        ):
            return []

        # Attributes to check for changes
        check_attrs = {
            # Skills
            "keeper": "skill",
            "defender": "skill",
            "playmaker": "skill",
            "winger": "skill",
            "passing": "skill",
            "scorer": "skill",
            "set_pieces": "skill",
            # Other important attributes
            "experience": "other",
            "age_years": "age",
            # Cards and injuries - critical player status changes
            "cards": "cards",
            "injury_level": "injury",
        }

        # List not to check for, as reference:
        # 'id', 'data_date', 'ht_id', 'first_name', 'last_name',
        # 'owner', 'age_days', 'age', 'next_birthday', 'loyalty': 'other',
        # 'stamina': 'other', 'form': 'other', 'tsi': 'money', 'salary': 'money',

        changes = []
        player_name = (
            f"{new_record.first_name or ''} {new_record.last_name or ''}".strip()
        )

        for attr, change_type in check_attrs.items():
            old_val = getattr(old_record, attr, None) or 0
            new_val = getattr(new_record, attr, None) or 0

            if old_val != new_val:
                # Clean up attribute name
                attr_name = attr.replace("_", " ").title()
                if attr == "tsi":
                    attr_name = "TSI"
                elif attr == "set_pieces":
                    attr_name = "Set Pieces"

                changes.append([player_name, attr_name, old_val, new_val, change_type])

        return changes

    except Exception as e:
        dprint(1, f"Error in get_player_changes: {e}")
        return []


# =============================================================================
# Team Statistics and Analysis Functions
# =============================================================================


def calculateManmark(player):
    """Calculate manmark rating for a player."""
    try:
        # Handle both object attributes and dictionary keys
        if hasattr(player, "experience"):
            experience = player.experience or 0
            defender = player.defender or 0
        else:
            experience = player.get("experience", 0) or 0
            defender = player.get("defender", 0) or 0

        # Convert experience to a 0-20 scale for calculations
        exp_rating = min(experience / 5.0, 20.0)  # Scale experience appropriately

        # Calculate man-mark as combination of defender skill and experience
        manmark = (
            defender + exp_rating * 0.3
        ) * 0.95  # Slight reduction from pure defender

        return round(max(0, manmark), 2)
    except Exception as e:
        # Handle both object attributes and dictionary keys for error logging
        if hasattr(player, "ht_id"):
            player_id = player.ht_id
        else:
            player_id = player.get("ht_id", "unknown")
        dprint(1, f"Error calculating manmark for player {player_id}: {e}")
        return 0.0


def calculateContribution(position, player):
    """Calculate player contribution to team based on position and skills."""
    try:
        # Position skill mappings based on Hattrick position requirements
        position_skills = {
            100: {"keeper": 1.0},  # Goalkeeper
            101: {"defender": 0.7, "passing": 0.3},  # Right Back
            102: {"defender": 0.8, "passing": 0.2},  # Right Centre Back
            103: {"defender": 0.8, "passing": 0.2},  # Centre Back
            104: {"defender": 0.8, "passing": 0.2},  # Left Centre Back
            105: {"defender": 0.7, "passing": 0.3},  # Left Back
            106: {"winger": 0.7, "passing": 0.3},  # Right Winger
            107: {"playmaker": 0.6, "passing": 0.4},  # Right Inner Midfield
            108: {"playmaker": 0.8, "passing": 0.2},  # Central Inner Midfield
            109: {"playmaker": 0.6, "passing": 0.4},  # Left Inner Midfield
            110: {"winger": 0.7, "passing": 0.3},  # Left Winger
            111: {"scorer": 0.6, "passing": 0.4},  # Right Forward
            112: {"scorer": 0.8, "passing": 0.2},  # Central Forward
            113: {"scorer": 0.6, "passing": 0.4},  # Left Forward
        }

        skills_weights = position_skills.get(position, {"passing": 1.0})

        contribution = 0.0
        for skill, weight in skills_weights.items():
            # Handle both object attributes and dictionary keys
            if hasattr(player, skill):
                skill_value = getattr(player, skill, 0) or 0
            else:
                skill_value = player.get(skill, 0) or 0
            contribution += skill_value * weight

        # Apply experience and form multipliers
        # Handle both object attributes and dictionary keys
        if hasattr(player, "experience"):
            experience = player.experience or 0
            form = player.form or 5
            loyalty = player.loyalty or 0
        else:
            experience = player.get("experience", 0) or 0
            form = player.get("form", 5) or 5
            loyalty = player.get("loyalty", 0) or 0

        experience_mult = 1.0 + (min(experience, 20) / 100.0)  # Up to 20% bonus
        form_mult = 1.0 + (form - 5) / 20.0  # -25% to +25% based on form
        loyalty_mult = 1.0 + (min(loyalty, 20) / 200.0)  # Up to 10% bonus

        final_contribution = contribution * experience_mult * form_mult * loyalty_mult

        return round(max(0, final_contribution), 2)

    except Exception as e:
        # Handle both object attributes and dictionary keys for error logging
        if hasattr(player, "ht_id"):
            player_id = player.ht_id
        else:
            player_id = player.get("ht_id", "unknown")
        dprint(
            1,
            f"Error calculating contribution for player {player_id} at position {position}: {e}",
        )
        return 0.0


def calculate_team_statistics(players):
    """Calculate comprehensive team statistics from player list."""
    if not players:
        return {}

    stats = {
        "total_players": len(players),
        "avg_age": 0,
        "avg_tsi": 0,
        "total_salary": 0,
        "skill_averages": {},
    }

    # Helper function to get player attribute value as numeric
    def get_player_attr(player, attr):
        # For SQLAlchemy objects, always use getattr
        # For dictionaries, use .get() method
        if hasattr(player, attr):
            value = getattr(player, attr, 0)
        elif hasattr(player, "get"):
            value = player.get(attr, 0)
        else:
            value = 0

        # Convert to numeric, handling None, string, and other types
        if value is None:
            return 0
        try:
            # Try to convert to int first, then float if that fails
            if isinstance(value, str):
                # Handle empty strings
                if not value.strip():
                    return 0
                # Try int first, then float
                try:
                    return int(value)
                except ValueError:
                    return float(value)
            elif isinstance(value, (int, float)):
                return value
            else:
                return 0
        except (ValueError, TypeError):
            return 0

    # Calculate averages - handle age as years from age_years field
    total_age = sum(
        get_player_attr(player, "age_years") for player in players
    )  # Use age_years instead of age string
    total_tsi = sum(get_player_attr(player, "tsi") for player in players)
    total_salary = sum(get_player_attr(player, "salary") for player in players)
    total_goals = sum(
        get_player_attr(player, "current_team_goals") for player in players
    )

    # Additional career statistics
    total_career_goals = sum(
        get_player_attr(player, "career_goals") for player in players
    )
    total_matches = sum(
        get_player_attr(player, "current_team_matches") for player in players
    )

    # Breakdown by competition type
    total_league_goals = sum(
        get_player_attr(player, "league_goals") for player in players
    )
    total_cup_goals = sum(
        get_player_attr(player, "cup_goals") for player in players
    )
    total_friendlies_goals = sum(
        get_player_attr(player, "friendlies_goals") for player in players
    )

    stats["avg_age"] = round(total_age / len(players), 1) if len(players) > 0 else 0
    stats["avg_tsi"] = round(total_tsi / len(players), 0) if len(players) > 0 else 0
    stats["total_salary"] = total_salary
    stats["total_team_goals"] = total_goals
    stats["total_career_goals"] = total_career_goals
    stats["total_league_goals"] = total_league_goals
    stats["total_cup_goals"] = total_cup_goals
    stats["total_friendlies_goals"] = total_friendlies_goals
    stats["total_matches"] = total_matches
    stats["goals_per_match"] = (
        round(total_goals / total_matches, 1) if total_matches > 0 else 0
    )
    stats["avg_wage"] = round(total_salary / len(players), 0) if len(players) > 0 else 0

    # Calculate skill averages
    skills = [
        "keeper",
        "defender",
        "playmaker",
        "winger",
        "passing",
        "scorer",
        "set_pieces",
    ]
    for skill in skills:
        skill_sum = sum(get_player_attr(player, skill) for player in players)
        avg_skill = round(skill_sum / len(players), 1)
        stats["skill_averages"][skill] = avg_skill

    return stats


def get_top_scorers(players, limit=5, sort_by_ratio=False):
    """Get top scoring players from the list.

    Enhanced for INFRA-028 to work correctly with both SQLAlchemy and CHPPPlayer data.
    Returns all players sorted by goals (including 0-goal players) for consistent display.

    Args:
        players: List of player objects
        limit: Maximum number of players to return
        sort_by_ratio: If True, sort by goals/match ratio instead of total goals
    """
    # Use the same helper function as calculate_team_statistics
    def get_player_attr(player, attr):
        # For SQLAlchemy objects, always use getattr
        # For dictionaries, use .get() method
        if hasattr(player, attr):
            value = getattr(player, attr, 0)
        elif hasattr(player, "get"):
            value = player.get(attr, 0)
        else:
            value = 0

        # Convert to numeric, handling None, string, and other types
        if value is None:
            return 0
        try:
            return float(value) if value != "" else 0
        except (ValueError, TypeError):
            return 0

    # Helper function to get goal count from various goal fields
    def get_player_goals(player):
        # Try multiple goal fields for broader compatibility
        current_team_goals = get_player_attr(player, "current_team_goals") or 0
        goals_current_team = get_player_attr(player, "goals_current_team") or 0
        career_goals = get_player_attr(player, "career_goals") or 0

        # Prefer current team goals, fall back to career goals
        return current_team_goals or goals_current_team or career_goals

    # Helper function to get matches played
    def get_player_matches(player):
        current_team_matches = get_player_attr(player, "current_team_matches") or 0
        matches_current_team = get_player_attr(player, "matches_current_team") or 0
        return current_team_matches or matches_current_team or 0

    # Helper function to calculate goals per match ratio
    def get_goals_per_match(player):
        goals = get_player_goals(player)
        matches = get_player_matches(player)
        return goals / matches if matches > 0 else 0

    # Return all players sorted by goals or goals/match ratio
    all_players = list(players)

    if sort_by_ratio:
        # Sort by goals/match ratio (for players with at least 1 match)
        all_players.sort(key=lambda p: (get_player_matches(p) > 0, get_goals_per_match(p)), reverse=True)
    else:
        # Sort by total goals
        all_players.sort(key=get_player_goals, reverse=True)

    return all_players[:limit]


def get_top_performers(players, limit=5):
    """Get top performing players based on TSI (since rating data may not be available)."""
    # Filter players with TSI data and sort by TSI
    performers = [p for p in players if getattr(p, "tsi", 0) and p.tsi > 0]
    performers.sort(key=lambda x: getattr(x, "tsi", 0) or 0, reverse=True)

    return performers[:limit]


def get_team_match_statistics(teamid):
    """Get comprehensive match statistics for a team."""
    from models import Match

    try:
        # Query match data for the team (check both home and away)
        from sqlalchemy import or_

        matches = (
            db.session.query(Match)
            .filter(or_(Match.home_team_id == teamid, Match.away_team_id == teamid))
            .all()
        )

        if not matches:
            # Return empty stats object
            class EmptyStats:
                def __init__(self):
                    self.total_matches = 0
                    self.wins = 0
                    self.draws = 0
                    self.losses = 0
                    self.goals_for = 0
                    self.goals_against = 0
                    self.goal_difference = 0
                    self.win_percentage = 0

            return EmptyStats()

        stats = {
            "total_matches": len(matches),
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for": 0,
            "goals_against": 0,
        }

        for match in matches:
            # Determine if team was playing at home or away
            is_home_match = match.home_team_id == teamid

            if is_home_match:
                stats["goals_for"] += match.home_goals or 0
                stats["goals_against"] += match.away_goals or 0

                # Determine result for home team
                if (match.home_goals or 0) > (match.away_goals or 0):
                    stats["wins"] += 1
                elif (match.home_goals or 0) == (match.away_goals or 0):
                    stats["draws"] += 1
                else:
                    stats["losses"] += 1
            else:
                stats["goals_for"] += match.away_goals or 0
                stats["goals_against"] += match.home_goals or 0

                # Determine result for away team
                if (match.away_goals or 0) > (match.home_goals or 0):
                    stats["wins"] += 1
                elif (match.away_goals or 0) == (match.home_goals or 0):
                    stats["draws"] += 1
                else:
                    stats["losses"] += 1

        # Calculate derived stats
        stats["goal_difference"] = stats["goals_for"] - stats["goals_against"]
        stats["win_percentage"] = (
            round((stats["wins"] / stats["total_matches"]) * 100, 1)
            if stats["total_matches"] > 0
            else 0
        )

        # Convert to object with dot notation support
        class MatchStats:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)

        return MatchStats(stats)

    except Exception as e:
        dprint(1, f"Error getting match statistics for team {teamid}: {e}")

        # Return empty stats on error
        class EmptyStats:
            def __init__(self):
                self.total_matches = 0
                self.wins = 0
                self.draws = 0
                self.losses = 0
                self.goals_for = 0
                self.goals_against = 0
                self.goal_difference = 0
                self.win_percentage = 0

        return EmptyStats()


# =============================================================================
# Data Processing and Download Utilities
# =============================================================================


def downloadMatches(teamid):
    """Download and process match data for a team."""

    from flask import current_app

    from models import Match

    # Get CHPP credentials from app config
    consumer_key = current_app.config.get("CONSUMER_KEY")
    consumer_secret = current_app.config.get("CONSUMER_SECRETS")

    chpp = CHPP(
        consumer_key, consumer_secret, session["access_key"], session["access_secret"]
    )

    the_matches = chpp.matches_archive(id_=teamid, is_youth=False)

    for match in the_matches:
        dprint(2, "---------------")

        # TODO: get more details about the match like below
        # the_match = chpp.match(ht_id=match.ht_id)

        thedate = datetime(
            match.datetime.year,
            match.datetime.month,
            match.datetime.day,
            match.datetime.hour,
            match.datetime.minute,
        )

        dprint(2, "Adding match ", match.ht_id, " to database.")

        dbmatch = db.session.query(Match).filter_by(ht_id=match.ht_id).first()

        if dbmatch:
            dprint(1, "WARNING: This match already exists.")
        else:
            thismatch = {}
            thismatch["ht_id"] = match.ht_id
            thismatch["home_team_id"] = match.home_team_id
            thismatch["home_team_name"] = match.home_team_name
            thismatch["away_team_id"] = match.away_team_id
            thismatch["away_team_name"] = match.away_team_name
            thismatch["datetime"] = thedate
            thismatch["matchtype"] = match.type
            thismatch["context_id"] = match.context_id
            thismatch["rule_id"] = match.rule_id
            thismatch["cup_level"] = match.cup_level
            thismatch["cup_level_index"] = match.cup_level_index
            thismatch["home_goals"] = match.home_goals
            thismatch["away_goals"] = match.away_goals

            newmatch = Match(thismatch)
            db.session.add(newmatch)
            db.session.commit()

            matchlineup = chpp.match_lineup(match_id=match.ht_id, team_id=teamid)
            for p in matchlineup.lineup_players:
                dprint(2, " - Adding ", p.first_name, " ", p.last_name, " to database")
                thismatchlineup = {}
                thismatchlineup["match_id"] = match.ht_id
                thismatchlineup["player_id"] = p.id
                thismatchlineup["datetime"] = thedate
                thismatchlineup["role_id"] = p.role_id
                thismatchlineup["first_name"] = p.first_name
                thismatchlineup["nick_name"] = p.nick_name
                thismatchlineup["last_name"] = p.last_name
                thismatchlineup["rating_stars"] = p.rating_stars
                thismatchlineup["rating_stars_eom"] = p.rating_stars_eom
                thismatchlineup["behaviour"] = p.behaviour

                from models import MatchPlay

                newmatchlineup = MatchPlay(thismatchlineup)
                db.session.add(newmatchlineup)
                db.session.commit()


def count_clicks(page):
    """Count page clicks for analytics."""
    try:
        # Simple click counting - could be enhanced with proper analytics
        if hasattr(current_app, "click_counter"):
            current_app.click_counter[page] = current_app.click_counter.get(page, 0) + 1
        else:
            current_app.click_counter = {page: 1}

        return current_app.click_counter.get(page, 0)
    except Exception as e:
        dprint(1, f"Error counting clicks for page {page}: {e}")
        return 0
