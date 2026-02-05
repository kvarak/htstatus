"""Shared utility functions for HT Status application."""

import inspect
from datetime import datetime

from flask import current_app, render_template, session

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
    """Get version information using git tags.

    Returns dict with version, fullversion, versionstr for consistent use across app.
    Uses git describe --tags directly since we now tag all minor releases.
    """
    import subprocess

    try:
        # Get git describe output - this will show the current version
        versionstr_raw = subprocess.check_output(["git", "describe", "--tags"]).strip().decode()

        # Parse the git describe output
        if "-" in versionstr_raw:
            # Format: "3.12-1-gedd7f4a" (commits ahead of tag)
            parts = versionstr_raw.split("-")
            tag_version = parts[0]  # "3.12"
            # Skip commits_ahead and git_hash as they're not needed

            version = tag_version
            # Convert format from "3.15-8-g5015d35" to "3.15.8-g5015d35" (replace first hyphen with dot)
            fullversion = versionstr_raw.replace("-", ".", 1)
            versionstr = fullversion
        else:
            # Exact tag match (no commits ahead)
            version = versionstr_raw
            fullversion = versionstr_raw
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
# Admin Feedback Utilities
# =============================================================================


def get_admin_feedback_counts(user_id=None):
    """Get feedback counts for admin indicators (hobby project scale).

    Returns dict with no_replies and needs_followup counts, or None if not admin.
    Uses simple queries appropriate for <50 feedback items.
    """
    # Import here to avoid circular imports
    from sqlalchemy import and_, exists

    from models import Feedback, FeedbackComment, User

    # Check admin status
    user = None
    if user_id:
        user = User.query.filter_by(ht_id=user_id).first()

    if not user or not (user.role == "Admin" or user.ht_id == 182085):
        return None

    # Handle case where feedback tables don't exist (graceful degradation)
    try:
        # Get all admin user IDs for query optimization
        admin_users = User.query.filter(
            (User.role == "Admin") | (User.ht_id == 182085)
        ).all()
        admin_user_ids = [admin.ht_id for admin in admin_users]

        # Count feedback with no admin replies (simple approach for hobby scale)
        no_replies_query = Feedback.query.filter(
            Feedback.status.in_(['open', 'planned', 'in-progress']),
            ~Feedback.archived,
            ~exists().where(
                and_(
                    FeedbackComment.feedback_id == Feedback.id,
                    FeedbackComment.author_id.in_(admin_user_ids)
                )
            )
        )
        no_replies = no_replies_query.count()

        # Count feedback needing admin follow-up (simplified approach)
        # For hobby scale: check if latest comment is from non-admin after admin reply exists
        needs_followup = 0
        feedback_with_admin_replies = Feedback.query.filter(
            Feedback.status.in_(['open', 'planned', 'in-progress']),
            ~Feedback.archived,
            exists().where(
                and_(
                    FeedbackComment.feedback_id == Feedback.id,
                    FeedbackComment.author_id.in_(admin_user_ids)
                )
            )
        ).all()

        for feedback in feedback_with_admin_replies:
            # Get latest comment for this feedback
            latest_comment = FeedbackComment.query.filter_by(
                feedback_id=feedback.id
            ).order_by(FeedbackComment.created_at.desc()).first()

            # If latest comment is from non-admin, needs follow-up
            if latest_comment and latest_comment.author_id not in admin_user_ids:
                needs_followup += 1

        return {
            "no_replies": no_replies,
            "needs_followup": needs_followup
        }
    except Exception:
        # Graceful degradation if feedback tables don't exist or other DB errors
        return {
            "no_replies": 0,
            "needs_followup": 0
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
        if user and (user.role == "Admin" or user.ht_id == 182085):
            template_vars["role"] = "Admin"

            # Add admin feedback counts for navigation indicators
            feedback_counts = get_admin_feedback_counts(user.ht_id)
            if feedback_counts:
                template_vars["admin_feedback_counts"] = feedback_counts

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
        player_name includes group name if player belongs to a group: "Player Name (Group Name)"
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
        player_display_data = _get_player_display_data(player_id, new_record)

        for attr, change_type in check_attrs.items():
            old_val = getattr(old_record, attr, None) or 0
            new_val = getattr(new_record, attr, None) or 0

            if old_val != new_val:
                attr_name = _format_attribute_name(attr)
                changes.append([player_display_data, attr_name, old_val, new_val, change_type])

        return changes

    except Exception as e:
        dprint(1, f"Error in get_player_changes: {e}")
        return []


def _get_player_display_name(player_id, player_record):
    """Get player display name with optional group name (legacy function).

    Args:
        player_id: Hattrick player ID
        player_record: Player database record

    Returns:
        str: "Player Name" or "Player Name (Group Name)" if group exists
    """
    display_data = _get_player_display_data(player_id, player_record)
    return display_data['name']


def _get_player_display_data(player_id, player_record):
    """Get player display data including name and group colors.

    Args:
        player_id: Hattrick player ID
        player_record: Player database record

    Returns:
        dict: {
            'name': str,           # "Player Name" or "Player Name (Group Name)"
            'group_name': str,     # Group name or None
            'group_order': int,    # Group order number or None
            'text_color': str,     # Group text color or None
            'bg_color': str        # Group background color or None
        }
    """
    base_name = f"{player_record.first_name or ''} {player_record.last_name or ''}".strip()

    result = {
        'name': base_name,
        'group_name': None,
        'group_order': None,
        'text_color': None,
        'bg_color': None
    }

    try:
        # Use module-level session import to work with test mocking
        current_user_id = session.get("current_user_id") if session else None

        if not current_user_id:
            return result

        # Import models using registry pattern with fallback
        try:
            from app.model_registry import get_group_model, get_player_setting_model
            PlayerSetting = get_player_setting_model()
            Group = get_group_model()
        except (ImportError, ValueError):
            from models import Group, PlayerSetting

        # Query for player's group
        player_setting = (
            db.session.query(PlayerSetting)
            .filter_by(player_id=player_id, user_id=current_user_id)
            .first()
        )

        if player_setting and player_setting.group_id:
            group = db.session.query(Group).filter_by(id=player_setting.group_id).first()
            if group and group.name:
                result['name'] = f"{base_name} ({group.name})"
                result['group_name'] = group.name
                result['group_order'] = group.order
                result['text_color'] = group.textcolor
                result['bg_color'] = group.bgcolor

    except Exception as e:
        dprint(2, f"Group lookup failed for player {player_id}: {e}")

    return result


def _format_attribute_name(attr):
    """Format attribute name for display."""
    attr_name = attr.replace("_", " ").title()
    if attr == "tsi":
        return "TSI"
    elif attr == "set_pieces":
        return "Set Pieces"
    return attr_name


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
        # Map position codes to position IDs if needed
        position_code_to_id = {
            "GC": 100,    # Goalkeeper contribution
            "CD": 103,    # Central Defender Normal - using middle central defender
            "CDO": 103,   # Central Defender Offensive - using middle central defender with offensive weighting
            "CDTW": 102,  # Side Central Defender Towards Wing - using right central defender
            "WBD": 101,   # Wing Back Defensive - using right back
            "WBN": 101,   # Wingback Normal - using right back
            "WBO": 101,   # Wing Back Offensive - using right back with offensive weighting
            "WBTM": 101,  # Wingback Towards Middle - using right back
            "WO": 106,    # Winger Offensive - using right winger
            "WTM": 106,   # Winger Towards Middle - using right winger
            "WN": 106,    # Winger Normal - using right winger
            "WD": 106,    # Winger Defensive - using right winger with defensive weighting
            "IMN": 108,   # Inner Midfielder Normal - using central inner midfield
            "IMD": 108,   # Inner Midfielder Defensive - using central inner midfield
            "IMO": 108,   # Inner Midfielder Offensive - using central inner midfield
            "IMTW": 107,  # Inner Midfielder Towards Wing - using right inner midfield
            "FW": 112,    # Forward Normal - using middle forward
            "FTW": 111,   # Forward Towards Wing - using right forward
            "DF": 112,    # Defensive Forward - using middle forward
        }

        # Convert position code to ID if it's a string
        if isinstance(position, str):
            position = position_code_to_id.get(position, 108)  # Default to central midfield if not found

        # Position skill mappings based on Hattrick position requirements and tactical variations
        position_skills = {
            100: {"keeper": 1.0},  # Goalkeeper
            101: {"defender": 0.7, "passing": 0.3},  # Right Back / Wing Back base
            102: {"defender": 0.8, "passing": 0.2},  # Right Centre Back
            103: {"defender": 0.8, "passing": 0.2},  # Centre Back / Central Defender base
            104: {"defender": 0.8, "passing": 0.2},  # Left Centre Back
            105: {"defender": 0.7, "passing": 0.3},  # Left Back
            106: {"winger": 0.7, "passing": 0.3},  # Right Winger / Winger base
            107: {"playmaker": 0.6, "passing": 0.4},  # Right Inner Midfield
            108: {"playmaker": 0.8, "passing": 0.2},  # Central Inner Midfield / Inner Midfielder base
            109: {"playmaker": 0.6, "passing": 0.4},  # Left Inner Midfield
            110: {"winger": 0.7, "passing": 0.3},  # Left Winger
            111: {"scorer": 0.6, "passing": 0.4},  # Right Forward
            112: {"scorer": 0.8, "passing": 0.2},  # Central Forward / Forward base
            113: {"scorer": 0.6, "passing": 0.4},  # Left Forward
        }

        # Handle tactical variations with custom skill weightings
        if isinstance(position, str):
            if position == "CDO":  # Central Defender Offensive
                skills_weights = {"defender": 0.6, "passing": 0.3, "playmaker": 0.1}
            elif position == "WBD":  # Wing Back Defensive
                skills_weights = {"defender": 0.8, "passing": 0.2}
            elif position == "WBO":  # Wing Back Offensive
                skills_weights = {"defender": 0.5, "passing": 0.3, "winger": 0.2}
            elif position == "WBTM":  # Wingback Towards Middle
                skills_weights = {"defender": 0.6, "passing": 0.4}
            elif position == "WO":  # Winger Offensive
                skills_weights = {"winger": 0.8, "passing": 0.2}
            elif position == "WTM":  # Winger Towards Middle
                skills_weights = {"winger": 0.5, "playmaker": 0.3, "passing": 0.2}
            elif position == "WD":  # Winger Defensive
                skills_weights = {"winger": 0.6, "defender": 0.2, "passing": 0.2}
            elif position == "IMD":  # Inner Midfielder Defensive
                skills_weights = {"defender": 0.3, "playmaker": 0.5, "passing": 0.2}
            elif position == "IMO":  # Inner Midfielder Offensive
                skills_weights = {"playmaker": 0.6, "scorer": 0.2, "passing": 0.2}
            elif position == "IMTW":  # Inner Midfielder Towards Wing
                skills_weights = {"playmaker": 0.5, "winger": 0.3, "passing": 0.2}
            elif position == "FTW":  # Forward Towards Wing
                skills_weights = {"scorer": 0.6, "winger": 0.2, "passing": 0.2}
            elif position == "DF":  # Defensive Forward
                skills_weights = {"scorer": 0.6, "defender": 0.2, "passing": 0.2}
            else:
                # Use standard position mapping
                skills_weights = position_skills.get(position, {"passing": 1.0})
        else:
            # Numeric position ID
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
        "leadership",
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


def downloadRecentMatches(teamid, chpp=None):
    """Download recent and upcoming matches for a team.

    Downloads recent and upcoming matches using CHPP matches endpoint.
    This is different from downloadMatches which handles historical archive.

    Args:
        teamid: Hattrick team ID
        chpp: CHPP client (optional, will create if not provided)

    Returns:
        dict with 'success', 'recent_count', 'upcoming_count', 'count', 'message' keys
    """
    from datetime import datetime

    from flask import current_app, session

    try:
        # Use provided CHPP client or create one
        if chpp is None:
            from app.chpp import CHPP
            consumer_key = current_app.config.get("CONSUMER_KEY")
            consumer_secret = current_app.config.get("CONSUMER_SECRETS")

            if not consumer_key or not consumer_secret:
                return {
                    "success": False,
                    "error": "CHPP configuration missing",
                    "recent_count": 0,
                    "upcoming_count": 0,
                    "count": 0,
                    "message": "CHPP configuration missing"
                }

            chpp = CHPP(
                consumer_key, consumer_secret,
                session["access_key"], session["access_secret"]
            )

        dprint(2, f"Fetching recent/upcoming matches for team {teamid}")

        # Fetch recent and upcoming matches
        matches = chpp.matches(id_=teamid, is_youth=False)

        # Process matches and separate recent vs upcoming
        recent_count = 0
        upcoming_count = 0
        total_added = 0
        total_enhanced = 0
        current_time = datetime.now()

        for match in matches:
            try:
                # Parse match datetime - handle both string and datetime objects
                if hasattr(match.datetime, 'year'):
                    # Already a datetime object
                    match_datetime = match.datetime
                elif match.datetime:
                    # String datetime - try multiple formats
                    try:
                        match_datetime = datetime.strptime(match.datetime, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        from dateutil import parser
                        match_datetime = parser.parse(match.datetime)
                else:
                    # No datetime available - skip this match
                    dprint(3, f"Skipping match {match.ht_id} - no datetime")
                    continue

                # Check if match has been played (recent) or is upcoming
                if match_datetime < current_time and match.home_goals is not None:
                    recent_count += 1
                elif match_datetime > current_time:
                    upcoming_count += 1

                # Save match to database (use enhanced processing)
                added, updated, enhanced = _process_matches_enhanced([match], chpp, fetch_enhanced=True)
                total_added += added
                total_enhanced += enhanced

            except Exception as e:
                dprint(2, f"Warning: Could not process match {match.ht_id}: {str(e)}")
                import traceback
                dprint(3, f"Match processing error details: {traceback.format_exc()}")
                continue

        message = f"Recent matches download complete: {recent_count} recent, {upcoming_count} upcoming, {total_added} new matches saved"
        if total_enhanced > 0:
            message += f", {total_enhanced} enhanced with analytics"
        dprint(2, message)

        return {
            "success": True,
            "recent_count": recent_count,
            "upcoming_count": upcoming_count,
            "count": total_added,
            "enhanced_count": total_enhanced,
            "message": message
        }

    except Exception as e:
        error_msg = f"Error downloading recent matches for team {teamid}: {str(e)}"
        dprint(1, error_msg)
        return {
            "success": False,
            "error": str(e),
            "recent_count": 0,
            "upcoming_count": 0,
            "count": 0,
            "message": error_msg
        }


def downloadMatches(teamid, chpp=None):
    """Download match archive for a team (recent matches only).

    Downloads recent matches using CHPP matchesarchive endpoint.
    Filters out matches older than 1 year to avoid historical data contamination
    from team ID reuse or inactive periods.

    Args:
        teamid: Hattrick team ID
        chpp: CHPP client (optional, will create if not provided)

    Returns:
        dict with 'success', 'count', 'updated', 'message' keys
    """
    from flask import current_app, session

    try:
        # Use provided CHPP client or create one
        if chpp is None:
            from app.chpp import CHPP
            consumer_key = current_app.config.get("CONSUMER_KEY")
            consumer_secret = current_app.config.get("CONSUMER_SECRETS")

            chpp = CHPP(
                consumer_key, consumer_secret,
                session["access_key"], session["access_secret"]
            )

        dprint(1, f"Downloading recent match archive for team {teamid}")

        # Get matches using default CHPP behavior (recent matches)
        # This is simpler and more reliable than season-based detection
        try:
            matches_data = chpp.matches_archive(id_=teamid)

            # Filter out matches older than 1 year to avoid historical contamination
            if matches_data:
                from datetime import timedelta
                cutoff_date = datetime.now() - timedelta(days=365)
                recent_matches = []

                for match in matches_data:
                    try:
                        if hasattr(match.datetime, 'year'):
                            match_date = match.datetime
                        elif match.datetime:
                            from dateutil import parser
                            match_date = parser.parse(str(match.datetime))
                        else:
                            continue

                        if match_date >= cutoff_date:
                            recent_matches.append(match)

                    except Exception:
                        # Skip matches with invalid dates
                        continue

                matches_data = recent_matches
                dprint(2, f"Filtered to {len(matches_data)} recent matches (last 1 year)")

        except Exception as e:
            dprint(1, f"Warning: Could not fetch matches: {str(e)}")
            matches_data = []

        # Process matches
        added, updated, enhanced = _process_matches_enhanced(matches_data, chpp, fetch_enhanced=True)

        message = f"Archive download complete: {added} new, {updated} updated"
        if enhanced > 0:
            message += f", {enhanced} enhanced with analytics"
        dprint(1, message)

        return {
            "success": True,
            "count": added,
            "updated": updated,
            "enhanced_count": enhanced,
            "message": message
        }

    except Exception as e:
        dprint(1, f"Error downloading match archive for team {teamid}: {str(e)}")
        if 'db' in locals():
            db.session.rollback()
        return {
            "success": False,
            "error": str(e),
            "count": 0,
            "message": f"Archive download failed: {str(e)}"
        }


def _process_matches(matches):
    """Process a list of matches and add/update them in the database.

    Args:
        matches: List of CHPPMatch objects

    Returns:
        tuple: (added_count, updated_count)
    """
    from models import Match

    added = 0
    updated = 0

    for match in matches:
        try:
            # Parse match datetime
            if hasattr(match.datetime, 'year'):
                thedate = datetime(
                    match.datetime.year, match.datetime.month, match.datetime.day,
                    match.datetime.hour, match.datetime.minute,
                )
            elif match.datetime:
                try:
                    from dateutil import parser
                    thedate = parser.parse(match.datetime)
                except Exception:
                    thedate = datetime.strptime(match.datetime, "%Y-%m-%d %H:%M:%S")
            else:
                dprint(2, f"No datetime for match {match.ht_id}, skipping")
                continue

            dprint(3, f"Processing match {match.ht_id}: {match.home_team_name} vs {match.away_team_name}")

            # Check if match already exists
            dbmatch = db.session.query(Match).filter_by(ht_id=match.ht_id).first()

            if dbmatch:
                # Update existing match
                dbmatch.home_goals = match.home_goals
                dbmatch.away_goals = match.away_goals
                dbmatch.home_team_name = match.home_team_name
                dbmatch.away_team_name = match.away_team_name
                updated += 1
            else:
                # Create new match record
                thismatch = {
                    "ht_id": match.ht_id,
                    "home_team_id": match.home_team_id,
                    "home_team_name": match.home_team_name,
                    "away_team_id": match.away_team_id,
                    "away_team_name": match.away_team_name,
                    "datetime": thedate,
                    "matchtype": match.matchtype,
                    "context_id": match.context_id,
                    "rule_id": match.rule_id,
                    "cup_level": match.cup_level,
                    "cup_level_index": match.cup_level_index,
                    "home_goals": match.home_goals,
                    "away_goals": match.away_goals,
                }

                newmatch = Match(thismatch)
                db.session.add(newmatch)
                added += 1

            db.session.commit()

        except Exception as e:
            dprint(2, f"Error processing match {match.ht_id}: {str(e)}")
            db.session.rollback()
            continue

    return added, updated


def fetch_enhanced_match_data(match_id, chpp=None):
    """Fetch enhanced match data (statistics, lineup, events) for a finished match.

    Args:
        match_id: Hattrick match ID
        chpp: CHPP client (optional, will create if not provided)

    Returns:
        dict: Enhanced match data or empty dict if unavailable
    """

    from flask import current_app, session

    if chpp is None:
        from app.chpp import CHPP
        consumer_key = current_app.config.get("CONSUMER_KEY")
        consumer_secret = current_app.config.get("CONSUMER_SECRETS")

        if not consumer_key or not consumer_secret:
            return {}

        chpp = CHPP(
            consumer_key, consumer_secret,
            session["access_key"], session["access_secret"]
        )

    enhanced_data = {}

    try:
        # Fetch match details for comprehensive statistics
        dprint(3, f"Fetching match details for match {match_id}")
        details = chpp.matchdetails(id_=match_id, match_events=True)

        # Calculate average possession for debug output
        home_poss_avg = None
        away_poss_avg = None
        if (details.possession_first_half_home is not None and
            details.possession_second_half_home is not None):
            home_poss_avg = (details.possession_first_half_home + details.possession_second_half_home) / 2
        if (details.possession_first_half_away is not None and
            details.possession_second_half_away is not None):
            away_poss_avg = (details.possession_first_half_away + details.possession_second_half_away) / 2

        # Calculate total chances for debug output
        home_total = sum(filter(None, [
            details.home_team_chances_left,
            details.home_team_chances_center,
            details.home_team_chances_right,
            details.home_team_chances_special,
            details.home_team_chances_other
        ]))
        away_total = sum(filter(None, [
            details.away_team_chances_left,
            details.away_team_chances_center,
            details.away_team_chances_right,
            details.away_team_chances_special,
            details.away_team_chances_other
        ]))

        # Debug: Check what we actually got from CHPP
        dprint(3, f"  CHPP returned - possession: {home_poss_avg}/{away_poss_avg}, "
               f"chances: {home_total}/{away_total}, "
               f"attendance: {details.attendance}")

        enhanced_data.update({
            "possession_first_half_home": details.possession_first_half_home,
            "possession_first_half_away": details.possession_first_half_away,
            "possession_second_half_home": details.possession_second_half_home,
            "possession_second_half_away": details.possession_second_half_away,
            "home_team_chances_left": details.home_team_chances_left,
            "home_team_chances_center": details.home_team_chances_center,
            "home_team_chances_right": details.home_team_chances_right,
            "home_team_chances_special": details.home_team_chances_special,
            "home_team_chances_other": details.home_team_chances_other,
            "away_team_chances_left": details.away_team_chances_left,
            "away_team_chances_center": details.away_team_chances_center,
            "away_team_chances_right": details.away_team_chances_right,
            "away_team_chances_special": details.away_team_chances_special,
            "away_team_chances_other": details.away_team_chances_other,
            "home_team_rating": details.home_team_rating,
            "away_team_rating": details.away_team_rating,
            "home_team_rating_right_def": details.home_team_rating_right_def,
            "home_team_rating_mid_def": details.home_team_rating_mid_def,
            "home_team_rating_left_def": details.home_team_rating_left_def,
            "away_team_rating_right_def": details.away_team_rating_right_def,
            "away_team_rating_mid_def": details.away_team_rating_mid_def,
            "away_team_rating_left_def": details.away_team_rating_left_def,
            "home_team_rating_right_att": details.home_team_rating_right_att,
            "home_team_rating_mid_att": details.home_team_rating_mid_att,
            "home_team_rating_left_att": details.home_team_rating_left_att,
            "away_team_rating_right_att": details.away_team_rating_right_att,
            "away_team_rating_mid_att": details.away_team_rating_mid_att,
            "away_team_rating_left_att": details.away_team_rating_left_att,
            "home_team_rating_set_pieces_def": details.home_team_rating_set_pieces_def,
            "home_team_rating_set_pieces_att": details.home_team_rating_set_pieces_att,
            "away_team_rating_set_pieces_def": details.away_team_rating_set_pieces_def,
            "away_team_rating_set_pieces_att": details.away_team_rating_set_pieces_att,
            "attendance": details.attendance,
            "arena_capacity_terraces": details.arena_capacity_terraces,
            "arena_capacity_basic": details.arena_capacity_basic,
            "arena_capacity_roof": details.arena_capacity_roof,
            "arena_capacity_vip": details.arena_capacity_vip,
            "weather_id": details.weather_id,
            "added_minutes": details.added_minutes,
            "referee_id": details.referee_id,
            "referee_name": details.referee_name,
            "referee_country_id": details.referee_country_id,
            "referee_country": details.referee_country,
            "referee_team_id": details.referee_team_id,
            "referee_team_name": details.referee_team_name,
            "home_team_dress_uri": details.home_team_dress_uri,
            "away_team_dress_uri": details.away_team_dress_uri,
            "home_team_attitude": details.home_team_attitude,
            "away_team_attitude": details.away_team_attitude,
            "home_team_tactic_type": details.home_team_tactic_type,
            "home_team_tactic_skill": details.home_team_tactic_skill,
            "away_team_tactic_type": details.away_team_tactic_type,
            "away_team_tactic_skill": details.away_team_tactic_skill,
        })

        # Fetch match lineup for formation and tactical data
        dprint(3, f"Fetching match lineup for match {match_id}")
        lineup = chpp.matchlineup(id_=match_id)

        enhanced_data.update({
            "home_team_formation": lineup.home_team_formation,
            "away_team_formation": lineup.away_team_formation,
            "home_team_tactic": lineup.home_team_tactic,
            "away_team_tactic": lineup.away_team_tactic,
        })

        # Filter out None values - only save fields that have actual data
        enhanced_data = {k: v for k, v in enhanced_data.items() if v is not None}

        if enhanced_data:
            dprint(2, f"Successfully fetched enhanced data for match {match_id}: {len(enhanced_data)} fields")
        else:
            dprint(2, f"No enhanced data available for match {match_id}")

    except Exception as e:
        dprint(2, f"Could not fetch enhanced data for match {match_id}: {str(e)}")
        # Return partial data if available
        enhanced_data = {k: v for k, v in enhanced_data.items() if v is not None}

    return enhanced_data


def update_match_with_enhanced_data(match_id, enhanced_data):
    """Update existing match record with enhanced analytics data.

    Args:
        match_id: Hattrick match ID
        enhanced_data: Dictionary of enhanced match data

    Returns:
        bool: True if successfully updated, False otherwise
    """
    from models import Match

    try:
        dbmatch = db.session.query(Match).filter_by(ht_id=match_id).first()

        if not dbmatch:
            dprint(2, f"Match {match_id} not found in database for enhanced data update")
            return False

        # Update with enhanced data
        for field, value in enhanced_data.items():
            if hasattr(dbmatch, field) and value is not None:
                setattr(dbmatch, field, value)

        db.session.commit()
        dprint(3, f"Updated match {match_id} with enhanced data")
        return True

    except Exception as e:
        dprint(2, f"Error updating match {match_id} with enhanced data: {str(e)}")
        db.session.rollback()
        return False


def _process_matches_enhanced(matches, chpp=None, fetch_enhanced=True):
    """Process matches and optionally fetch enhanced analytics data.

    Args:
        matches: List of CHPPMatch objects
        chpp: CHPP client for enhanced data fetching
        fetch_enhanced: Whether to fetch enhanced data for finished matches

    Returns:
        tuple: (added_count, updated_count, enhanced_count)
    """
    from datetime import datetime

    from models import Match

    added = 0
    updated = 0
    enhanced = 0

    for match in matches:
        try:
            # Parse match datetime
            if hasattr(match.datetime, 'year'):
                thedate = datetime(
                    match.datetime.year, match.datetime.month, match.datetime.day,
                    match.datetime.hour, match.datetime.minute,
                )
            elif match.datetime:
                try:
                    from dateutil import parser
                    thedate = parser.parse(match.datetime)
                except Exception:
                    thedate = datetime.strptime(match.datetime, "%Y-%m-%d %H:%M:%S")
            else:
                dprint(2, f"No datetime for match {match.ht_id}, skipping")
                continue

            dprint(3, f"Processing match {match.ht_id}: {match.home_team_name} vs {match.away_team_name}")

            # Check if match already exists
            dbmatch = db.session.query(Match).filter_by(ht_id=match.ht_id).first()

            # Determine if match is finished (has goals scored)
            is_finished = (match.home_goals is not None and match.away_goals is not None)

            if dbmatch:
                # Update existing match
                dbmatch.home_goals = match.home_goals
                dbmatch.away_goals = match.away_goals
                dbmatch.home_team_name = match.home_team_name
                dbmatch.away_team_name = match.away_team_name
                updated += 1

                # Fetch enhanced data if match is finished
                # Always fetch to ensure we have the most complete data available
                if fetch_enhanced and is_finished and chpp:
                    enhanced_data = fetch_enhanced_match_data(match.ht_id, chpp)
                    if enhanced_data:
                        for field, value in enhanced_data.items():
                            if hasattr(dbmatch, field):
                                setattr(dbmatch, field, value)
                        enhanced += 1

            else:
                # Create new match record
                thismatch = {
                    "ht_id": match.ht_id,
                    "home_team_id": match.home_team_id,
                    "home_team_name": match.home_team_name,
                    "away_team_id": match.away_team_id,
                    "away_team_name": match.away_team_name,
                    "datetime": thedate,
                    "matchtype": match.matchtype,
                    "context_id": match.context_id,
                    "rule_id": match.rule_id,
                    "cup_level": match.cup_level,
                    "cup_level_index": match.cup_level_index,
                    "home_goals": match.home_goals,
                    "away_goals": match.away_goals,
                }

                # Add enhanced data if available and match is finished
                if fetch_enhanced and is_finished and chpp:
                    enhanced_data = fetch_enhanced_match_data(match.ht_id, chpp)
                    thismatch.update(enhanced_data)
                    if enhanced_data:
                        enhanced += 1

                newmatch = Match(thismatch)
                db.session.add(newmatch)
                added += 1

            db.session.commit()

        except Exception as e:
            dprint(2, f"Error processing match {match.ht_id}: {str(e)}")
            db.session.rollback()
            continue

    return added, updated, enhanced


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


# =============================================================================
# Default Group Management
# =============================================================================


def create_default_groups(user_id):
    """Create default player groups for a new user.

    Args:
        user_id: Hattrick user ID to create groups for

    Returns:
        list: List of created Group objects, empty list if user already has groups

    Raises:
        Exception: If database transaction fails
    """
    from models import Group, User

    dprint(2, f"Creating default groups for user {user_id}")

    # Verify user exists in database first
    user = User.query.filter_by(ht_id=user_id).first()
    if not user:
        dprint(1, f"Cannot create groups: user {user_id} not found in database")
        return []

    # Check if user already has groups
    existing_groups = Group.query.filter_by(user_id=user_id).count()
    if existing_groups > 0:
        dprint(2, f"User {user_id} already has {existing_groups} groups, skipping default creation")
        return []

    # Default groups with football theme colors and spacing for customization
    default_groups = [
        {
            "name": "Goalkeepers",
            "order": 10,
            "textcolor": "#FFFFFF",
            "bgcolor": "#001f3f"  # Navy blue
        },
        {
            "name": "Defenders",
            "order": 20,
            "textcolor": "#FFFFFF",
            "bgcolor": "#0074D9"  # Blue
        },
        {
            "name": "Wing Defenders",
            "order": 30,
            "textcolor": "#FFFFFF",
            "bgcolor": "#2ECC40"  # Green
        },
        {
            "name": "Midfielders",
            "order": 40,
            "textcolor": "#000000",
            "bgcolor": "#FFFFFF"  # White
        },
        {
            "name": "Wingers",
            "order": 50,
            "textcolor": "#FFFFFF",
            "bgcolor": "#B10DC9"  # Purple
        },
        {
            "name": "Forwards",
            "order": 60,
            "textcolor": "#FFFFFF",
            "bgcolor": "#FF4136"  # Red
        }
    ]

    created_groups = []

    try:
        for group_data in default_groups:
            group = Group(
                user_id=user_id,
                name=group_data["name"],
                order=group_data["order"],
                textcolor=group_data["textcolor"],
                bgcolor=group_data["bgcolor"]
            )
            db.session.add(group)
            created_groups.append(group)

        db.session.commit()
        dprint(1, f"Created {len(created_groups)} default groups for user {user_id}")
        return created_groups

    except Exception as e:
        dprint(1, f"Error creating default groups for user {user_id}: {e}")
        db.session.rollback()
        raise


# =============================================================================
# Formation Testing Utilities
# =============================================================================

# Standard Hattrick formations with position mappings
FORMATION_TEMPLATES = {
    "5-5-0": {
        "name": "5-5-0 (Defensive)",
        "description": "5 defenders, 5 midfielders, 0 forwards",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},  # GK
            101: {"row": 2, "col": 5, "name": "Right Back"},  # RB
            102: {"row": 2, "col": 4, "name": "Right Centre Back"},  # RCB
            103: {"row": 2, "col": 3, "name": "Centre Back"},  # CB
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},  # LCB
            105: {"row": 2, "col": 1, "name": "Left Back"},  # LB
            106: {"row": 3, "col": 5, "name": "Right Midfielder"},  # RM
            107: {"row": 3, "col": 4, "name": "Right Inner Midfield"},  # RIM
            108: {"row": 3, "col": 3, "name": "Central Midfield"},  # CM
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},  # LIM
            110: {"row": 3, "col": 1, "name": "Left Midfielder"},  # LM
        }
    },
    "5-4-1": {
        "name": "5-4-1 (Defensive Counter)",
        "description": "5 defenders, 4 midfielders, 1 forward",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},
            101: {"row": 2, "col": 5, "name": "Right Back"},
            102: {"row": 2, "col": 4, "name": "Right Centre Back"},
            103: {"row": 2, "col": 3, "name": "Centre Back"},
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},
            105: {"row": 2, "col": 1, "name": "Left Back"},
            107: {"row": 3, "col": 4, "name": "Right Inner Midfield"},
            108: {"row": 3, "col": 3, "name": "Central Midfield"},
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},
            110: {"row": 3, "col": 1, "name": "Left Midfielder"},
            112: {"row": 4, "col": 3, "name": "Centre Forward"},
        }
    },
    "5-3-2": {
        "name": "5-3-2 (Wing Backs)",
        "description": "5 defenders, 3 midfielders, 2 forwards",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},
            101: {"row": 2, "col": 5, "name": "Right Back"},
            102: {"row": 2, "col": 4, "name": "Right Centre Back"},
            103: {"row": 2, "col": 3, "name": "Centre Back"},
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},
            105: {"row": 2, "col": 1, "name": "Left Back"},
            107: {"row": 3, "col": 4, "name": "Right Inner Midfield"},
            108: {"row": 3, "col": 3, "name": "Central Midfield"},
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},
            111: {"row": 4, "col": 4, "name": "Right Forward"},
            113: {"row": 4, "col": 2, "name": "Left Forward"},
        }
    },
    "5-2-3": {
        "name": "5-2-3 (Attack)",
        "description": "5 defenders, 2 midfielders, 3 forwards",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},
            101: {"row": 2, "col": 5, "name": "Right Back"},
            102: {"row": 2, "col": 4, "name": "Right Centre Back"},
            103: {"row": 2, "col": 3, "name": "Centre Back"},
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},
            105: {"row": 2, "col": 1, "name": "Left Back"},
            108: {"row": 3, "col": 3, "name": "Central Midfield"},
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},
            111: {"row": 4, "col": 4, "name": "Right Forward"},
            112: {"row": 4, "col": 3, "name": "Centre Forward"},
            113: {"row": 4, "col": 2, "name": "Left Forward"},
        }
    },
    "4-5-1": {
        "name": "4-5-1 (Control)",
        "description": "4 defenders, 5 midfielders, 1 forward",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},
            101: {"row": 2, "col": 5, "name": "Right Back"},
            102: {"row": 2, "col": 4, "name": "Right Centre Back"},
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},
            105: {"row": 2, "col": 1, "name": "Left Back"},
            106: {"row": 3, "col": 5, "name": "Right Midfielder"},
            107: {"row": 3, "col": 4, "name": "Right Inner Midfield"},
            108: {"row": 3, "col": 3, "name": "Central Midfield"},
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},
            110: {"row": 3, "col": 1, "name": "Left Midfielder"},
            112: {"row": 4, "col": 3, "name": "Centre Forward"},
        }
    },
    "4-4-2": {
        "name": "4-4-2 (Classic)",
        "description": "4 defenders, 4 midfielders, 2 forwards",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},
            101: {"row": 2, "col": 5, "name": "Right Back"},
            102: {"row": 2, "col": 4, "name": "Right Centre Back"},
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},
            105: {"row": 2, "col": 1, "name": "Left Back"},
            107: {"row": 3, "col": 4, "name": "Right Inner Midfield"},
            108: {"row": 3, "col": 3, "name": "Central Midfield"},
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},
            110: {"row": 3, "col": 1, "name": "Left Midfielder"},
            111: {"row": 4, "col": 4, "name": "Right Forward"},
            113: {"row": 4, "col": 2, "name": "Left Forward"},
        }
    },
    "4-3-3": {
        "name": "4-3-3 (Attacking)",
        "description": "4 defenders, 3 midfielders, 3 forwards",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},
            101: {"row": 2, "col": 5, "name": "Right Back"},
            102: {"row": 2, "col": 4, "name": "Right Centre Back"},
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},
            105: {"row": 2, "col": 1, "name": "Left Back"},
            107: {"row": 3, "col": 4, "name": "Right Inner Midfield"},
            108: {"row": 3, "col": 3, "name": "Central Midfield"},
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},
            111: {"row": 4, "col": 4, "name": "Right Forward"},
            112: {"row": 4, "col": 3, "name": "Centre Forward"},
            113: {"row": 4, "col": 2, "name": "Left Forward"},
        }
    },
    "3-5-2": {
        "name": "3-5-2 (Midfield)",
        "description": "3 defenders, 5 midfielders, 2 forwards",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},
            102: {"row": 2, "col": 4, "name": "Right Centre Back"},
            103: {"row": 2, "col": 3, "name": "Centre Back"},
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},
            106: {"row": 3, "col": 5, "name": "Right Midfielder"},
            107: {"row": 3, "col": 4, "name": "Right Inner Midfield"},
            108: {"row": 3, "col": 3, "name": "Central Midfield"},
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},
            110: {"row": 3, "col": 1, "name": "Left Midfielder"},
            111: {"row": 4, "col": 4, "name": "Right Forward"},
            113: {"row": 4, "col": 2, "name": "Left Forward"},
        }
    },
    "3-4-3": {
        "name": "3-4-3 (All-out Attack)",
        "description": "3 defenders, 4 midfielders, 3 forwards",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},
            102: {"row": 2, "col": 4, "name": "Right Centre Back"},
            103: {"row": 2, "col": 3, "name": "Centre Back"},
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},
            107: {"row": 3, "col": 4, "name": "Right Inner Midfield"},
            108: {"row": 3, "col": 3, "name": "Central Midfield"},
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},
            110: {"row": 3, "col": 1, "name": "Left Midfielder"},
            111: {"row": 4, "col": 4, "name": "Right Forward"},
            112: {"row": 4, "col": 3, "name": "Centre Forward"},
            113: {"row": 4, "col": 2, "name": "Left Forward"},
        }
    },
    "2-5-3": {
        "name": "2-5-3 (Ultra Attack)",
        "description": "2 defenders, 5 midfielders, 3 forwards",
        "positions": {
            100: {"row": 1, "col": 3, "name": "Goalkeeper"},
            103: {"row": 2, "col": 3, "name": "Centre Back"},
            104: {"row": 2, "col": 2, "name": "Left Centre Back"},
            106: {"row": 3, "col": 5, "name": "Right Midfielder"},
            107: {"row": 3, "col": 4, "name": "Right Inner Midfield"},
            108: {"row": 3, "col": 3, "name": "Central Midfield"},
            109: {"row": 3, "col": 2, "name": "Left Inner Midfield"},
            110: {"row": 3, "col": 1, "name": "Left Midfielder"},
            111: {"row": 4, "col": 4, "name": "Right Forward"},
            112: {"row": 4, "col": 3, "name": "Centre Forward"},
            113: {"row": 4, "col": 2, "name": "Left Forward"},
        }
    }
}


def calculate_formation_effectiveness(formation_key, player_assignments):
    """Calculate total team effectiveness for a given formation and player assignments.

    Args:
        formation_key: String key for the formation (e.g., "4-4-2")
        player_assignments: Dict mapping position_id to player object

    Returns:
        Dict with effectiveness score and position breakdowns
    """
    if formation_key not in FORMATION_TEMPLATES:
        return {"total_score": 0, "position_scores": {}, "error": "Invalid formation"}

    formation = FORMATION_TEMPLATES[formation_key]
    total_score = 0.0
    position_scores = {}

    for position_id in formation["positions"]:
        player = player_assignments.get(position_id)
        if player:
            contribution = calculateContribution(position_id, player)
            position_scores[position_id] = {
                "contribution": contribution,
                "position_name": formation["positions"][position_id]["name"],
                "player_name": f"{getattr(player, 'first_name', '')} {getattr(player, 'last_name', '')}"
            }
            total_score += contribution
        else:
            position_scores[position_id] = {
                "contribution": 0,
                "position_name": formation["positions"][position_id]["name"],
                "player_name": "No player assigned"
            }

    return {
        "total_score": round(total_score, 2),
        "average_score": round(total_score / len(formation["positions"]), 2),
        "position_scores": position_scores,
        "formation_name": formation["name"]
    }


def get_formation_list():
    """Get list of available formations for dropdown selection."""
    return [
        {"key": key, "name": template["name"], "description": template["description"]}
        for key, template in FORMATION_TEMPLATES.items()
    ]


def get_team_timeline(team_id):
    """Get 4-week timeline of skill changes for a specific team.

    Extracted from team.py update route for reuse in player pages.

    Args:
        team_id: Hattrick team ID to filter players by

    Returns:
        dict: Timeline changes structured by week with format:
        {
            "week_1": {
                "week_label": "Week 1",
                "is_current": True,
                "days_ago_start": 7,
                "days_ago_end": 0,
                "changes": [player_changes...]
            },
            ...
        }
    """
    try:
        from flask import current_app

        from models import Players

        # Get db from current Flask app context if not set globally
        current_db = db if db is not None else current_app.extensions['sqlalchemy'].db

        # Get all players for this team from current roster
        latest_players = (
            current_db.session.query(Players.ht_id)
            .filter_by(owner=team_id)
            .distinct()
            .all()
        )

        players_fromht = [p.ht_id for p in latest_players]

        if not players_fromht:
            return {}

        # Collect changes for 4-week timeline - simplified
        timeline_changes = {}

        for week_num in range(1, 5):  # Weeks 1-4
            week_start_days = week_num * 7  # Start of week (older)
            week_end_days = (week_num - 1) * 7  # End of week (newer)

            timeline_changes[f"week_{week_num}"] = {
                "week_label": f"Week {week_num}",
                "is_current": week_num == 1,
                "days_ago_start": week_start_days,
                "days_ago_end": week_end_days,
                "changes": [],
            }

            # Get all changes for all players in this week period
            for player_id in players_fromht:
                player_changes = get_player_changes(
                    player_id, week_start_days, week_end_days
                )

                for change in player_changes:
                    timeline_changes[f"week_{week_num}"]["changes"].append(change)

            # Sort changes by group order (None last), then by player name
            def sort_changes_key(change):
                player_data = change[0]  # First element is player display data
                if isinstance(player_data, dict):
                    # Sort by group order (None values last), then by player name
                    group_order = player_data.get('group_order')
                    if group_order is None:
                        group_order = 9999  # Put players without groups at the end
                    player_name = player_data.get('name', '')
                    return (group_order, player_name)
                else:
                    # Legacy string format - use as is
                    return (9999, str(player_data))

            timeline_changes[f"week_{week_num}"]["changes"].sort(key=sort_changes_key)

        return timeline_changes

    except Exception as e:
        dprint(1, f"Error in get_team_timeline: {e}")
        return {}

