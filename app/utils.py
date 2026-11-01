"""Shared utility functions for HT Status application."""

from datetime import datetime
import inspect
import os

from flask import render_template, session

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
    """Version from the APP_VERSION env var (set in the Docker image) or git tags.

    Returns dict with version, fullversion, versionstr for consistent use across app.
    """
    import subprocess

    try:
        versionstr_raw = os.environ.get("APP_VERSION") or (
            subprocess.check_output(["git", "describe", "--tags"]).strip().decode()
        )

        # Parse the git describe output
        if "-" in versionstr_raw:
            # Format: "3.12-1-gedd7f4a" (commits ahead of tag)
            version = versionstr_raw.split("-")[0]
            # "3.15-8-g5015d35" -> "3.15.8-g5015d35" (replace first hyphen with dot)
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


def get_admin_feedback_counts(user=None):
    """Get feedback counts for admin indicators (hobby project scale).

    Takes the (already loaded) User; returns dict with no_replies and
    needs_followup counts, or None if not admin.
    Uses simple queries appropriate for <50 feedback items.
    """
    # Import here to avoid circular imports
    from sqlalchemy import and_, exists

    from models import Feedback, FeedbackComment, SUPERADMIN_HT_ID, User

    if not user or not user.is_admin():
        return None

    # Handle case where feedback tables don't exist (graceful degradation)
    try:
        # Get all admin user IDs for query optimization
        admin_users = User.query.filter(
            (User.role == "Admin") | (User.ht_id == SUPERADMIN_HT_ID)
        ).all()
        admin_user_ids = [admin.ht_id for admin in admin_users]

        # Count feedback with no admin replies (simple approach for hobby scale)
        no_replies_query = Feedback.query.filter(
            Feedback.status.in_(["open", "planned", "in-progress"]),
            ~Feedback.archived,
            ~exists().where(
                and_(
                    FeedbackComment.feedback_id == Feedback.id,
                    FeedbackComment.author_id.in_(admin_user_ids),
                )
            ),
        )
        no_replies = no_replies_query.count()

        # Count feedback needing admin follow-up (simplified approach)
        # For hobby scale: check if latest comment is from non-admin after admin reply exists
        needs_followup = 0
        feedback_with_admin_replies = Feedback.query.filter(
            Feedback.status.in_(["open", "planned", "in-progress"]),
            ~Feedback.archived,
            exists().where(
                and_(
                    FeedbackComment.feedback_id == Feedback.id,
                    FeedbackComment.author_id.in_(admin_user_ids),
                )
            ),
        ).all()

        for feedback in feedback_with_admin_replies:
            # Get latest comment for this feedback
            latest_comment = (
                FeedbackComment.query.filter_by(feedback_id=feedback.id)
                .order_by(FeedbackComment.created_at.desc())
                .first()
            )

            # If latest comment is from non-admin, needs follow-up
            if latest_comment and latest_comment.author_id not in admin_user_ids:
                needs_followup += 1

        return {"no_replies": no_replies, "needs_followup": needs_followup}
    except Exception:
        # Graceful degradation if feedback tables don't exist or other DB errors
        return {"no_replies": 0, "needs_followup": 0}


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

        from app.auth_utils import get_current_user

        user = get_current_user()
        if user and user.is_admin():
            template_vars["role"] = "Admin"

            # Add admin feedback counts for navigation indicators
            feedback_counts = get_admin_feedback_counts(user)
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


# Attributes shown in the skill-change timeline: attr -> change type
TIMELINE_ATTRIBUTES = {
    "keeper": "skill",
    "defender": "skill",
    "playmaker": "skill",
    "winger": "skill",
    "passing": "skill",
    "scorer": "skill",
    "set_pieces": "skill",
    "experience": "other",
    "age_years": "age",
    "cards": "cards",
    "injury_level": "injury",
}


def _record_changes(old_record, new_record, display_data):
    """List [display_data, attribute name, old, new, change_type, attribute key]."""
    changes = []
    for attr, change_type in TIMELINE_ATTRIBUTES.items():
        old_val = getattr(old_record, attr, None) or 0
        new_val = getattr(new_record, attr, None) or 0
        if old_val != new_val:
            changes.append(
                [
                    display_data,
                    _format_attribute_name(attr),
                    old_val,
                    new_val,
                    change_type,
                    attr,
                ]
            )
    return changes


def _player_group_info(player_ids):
    """Return {ht_id: Group} for the current user's group assignments (2 queries)."""
    from models import Group, PlayerSetting

    current_user_id = session.get("current_user_id") if session else None
    if not current_user_id or not player_ids:
        return {}
    try:
        settings = (
            db.session.query(PlayerSetting)
            .filter(PlayerSetting.user_id == current_user_id)
            .filter(PlayerSetting.player_id.in_(list(player_ids)))
            .all()
        )
        group_ids = {s.group_id for s in settings if s.group_id}
        groups = (
            {g.id: g for g in db.session.query(Group).filter(Group.id.in_(group_ids))}
            if group_ids
            else {}
        )
        return {
            s.player_id: groups[s.group_id]
            for s in settings
            if s.group_id in groups and groups[s.group_id].name
        }
    except Exception as e:
        dprint(2, f"Group lookup failed: {e}")
        return {}


def _player_display_data(record, group):
    """Display data for a timeline row: name (with group) and group colours."""
    base_name = f"{record.first_name or ''} {record.last_name or ''}".strip()
    if not group:
        return {
            "name": base_name,
            "group_name": None,
            "group_order": None,
            "text_color": None,
            "bg_color": None,
        }
    return {
        "name": f"{base_name} ({group.name})",
        "group_name": group.name,
        "group_order": group.order,
        "text_color": group.textcolor,
        "bg_color": group.bgcolor,
    }


def _format_attribute_name(attr):
    """Format attribute name for display."""
    attr_name = attr.replace("_", " ").title()
    if attr == "tsi":
        return "TSI"
    if attr == "set_pieces":
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
        # Scale experience appropriately
        exp_rating = min(experience / 5.0, 20.0)

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


# Skill weights per position code (the codes used as player-table columns).
# Tactical variants shift weight between skills; unknown codes fall back to passing.
POSITION_SKILL_WEIGHTS = {
    "GC": {"keeper": 1.0},
    "CD": {"defender": 0.8, "passing": 0.2},
    "CDO": {"defender": 0.6, "passing": 0.3, "playmaker": 0.1},
    "CDTW": {"defender": 0.8, "passing": 0.2},
    "WBD": {"defender": 0.8, "passing": 0.2},
    "WBN": {"defender": 0.7, "passing": 0.3},
    "WBO": {"defender": 0.5, "passing": 0.3, "winger": 0.2},
    "WBTM": {"defender": 0.6, "passing": 0.4},
    "WO": {"winger": 0.8, "passing": 0.2},
    "WTM": {"winger": 0.5, "playmaker": 0.3, "passing": 0.2},
    "WN": {"winger": 0.7, "passing": 0.3},
    "WD": {"winger": 0.6, "defender": 0.2, "passing": 0.2},
    "IMN": {"playmaker": 0.8, "passing": 0.2},
    "IMD": {"defender": 0.3, "playmaker": 0.5, "passing": 0.2},
    "IMO": {"playmaker": 0.6, "scorer": 0.2, "passing": 0.2},
    "IMTW": {"playmaker": 0.5, "winger": 0.3, "passing": 0.2},
    "FW": {"scorer": 0.8, "passing": 0.2},
    "FTW": {"scorer": 0.6, "winger": 0.2, "passing": 0.2},
    "DF": {"scorer": 0.6, "defender": 0.2, "passing": 0.2},
}
UNKNOWN_POSITION_WEIGHTS = {"passing": 1.0}

# Hattrick match role IDs (formation tester) -> position code
ROLE_ID_TO_POSITION = {
    100: "GC",
    101: "WBN",
    102: "CD",
    103: "CD",
    104: "CD",
    105: "WBN",
    106: "WN",
    107: "IMN",
    108: "IMN",
    109: "IMN",
    110: "WN",
    111: "FW",
    112: "FW",
    113: "FW",
}


def _player_value(player, field, default=0):
    """Read a field from a player model object or a player dict (None -> default)."""
    value = (
        player.get(field) if isinstance(player, dict) else getattr(player, field, None)
    )
    return default if value is None else value


def calculateContribution(position, player):
    """Calculate a player's contribution for a position.

    ``position`` is a position code (e.g. "IMN", see POSITION_SKILL_WEIGHTS) or a
    Hattrick match role ID (100-113), which is mapped to its code.
    ``player`` may be a Players object or a dict of its fields.
    """
    try:
        code = ROLE_ID_TO_POSITION.get(position, position)
        weights = POSITION_SKILL_WEIGHTS.get(code, UNKNOWN_POSITION_WEIGHTS)

        contribution = sum(
            (_player_value(player, skill) or 0) * weight
            for skill, weight in weights.items()
        )

        experience = _player_value(player, "experience") or 0
        form = _player_value(player, "form", 5) or 5
        loyalty = _player_value(player, "loyalty") or 0

        experience_mult = 1.0 + (min(experience, 20) / 100.0)  # Up to 20% bonus
        form_mult = 1.0 + (form - 5) / 20.0  # -25% to +25% based on form
        loyalty_mult = 1.0 + (min(loyalty, 20) / 200.0)  # Up to 10% bonus

        return round(
            max(0, contribution * experience_mult * form_mult * loyalty_mult), 2
        )

    except Exception as e:
        dprint(
            1,
            f"Error calculating contribution for player "
            f"{_player_value(player, 'ht_id', 'unknown')} at position {position}: {e}",
        )
        return 0.0


def best_position(player):
    """The position (CALC_COLUMNS key) where the player contributes most, or "-"."""
    from app.constants import CALC_COLUMNS

    best, best_value = "-", 0
    for position in CALC_COLUMNS:
        value = calculateContribution(position, player)
        if value > best_value:
            best, best_value = position, value
    return best


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
                    "message": "CHPP configuration missing",
                }

            chpp = CHPP(
                consumer_key,
                consumer_secret,
                session["access_key"],
                session["access_secret"],
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
                if hasattr(match.datetime, "year"):
                    # Already a datetime object
                    match_datetime = match.datetime
                elif match.datetime:
                    # String datetime - try multiple formats
                    try:
                        match_datetime = datetime.strptime(
                            match.datetime, "%Y-%m-%d %H:%M:%S"
                        )
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
                added, updated, enhanced = _process_matches_enhanced(
                    [match], chpp, fetch_enhanced=True
                )
                total_added += added
                total_enhanced += enhanced

            except Exception as e:
                dprint(2, f"Warning: Could not process match {match.ht_id}: {e!s}")
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
            "message": message,
        }

    except Exception as e:
        error_msg = f"Error downloading recent matches for team {teamid}: {e!s}"
        dprint(1, error_msg)
        return {
            "success": False,
            "error": str(e),
            "recent_count": 0,
            "upcoming_count": 0,
            "count": 0,
            "message": error_msg,
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
                consumer_key,
                consumer_secret,
                session["access_key"],
                session["access_secret"],
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
                        if hasattr(match.datetime, "year"):
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
                dprint(
                    2, f"Filtered to {len(matches_data)} recent matches (last 1 year)"
                )

        except Exception as e:
            dprint(1, f"Warning: Could not fetch matches: {e!s}")
            matches_data = []

        # Process matches
        added, updated, enhanced = _process_matches_enhanced(
            matches_data, chpp, fetch_enhanced=True
        )

        message = f"Archive download complete: {added} new, {updated} updated"
        if enhanced > 0:
            message += f", {enhanced} enhanced with analytics"
        dprint(1, message)

        return {
            "success": True,
            "count": added,
            "updated": updated,
            "enhanced_count": enhanced,
            "message": message,
        }

    except Exception as e:
        dprint(1, f"Error downloading match archive for team {teamid}: {e!s}")
        if "db" in locals():
            db.session.rollback()
        return {
            "success": False,
            "error": str(e),
            "count": 0,
            "message": f"Archive download failed: {e!s}",
        }


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
            consumer_key,
            consumer_secret,
            session["access_key"],
            session["access_secret"],
        )

    enhanced_data = {}

    try:
        # Fetch match details for comprehensive statistics
        dprint(3, f"Fetching match details for match {match_id}")
        details = chpp.matchdetails(id_=match_id, match_events=True)

        # Calculate average possession for debug output
        home_poss_avg = None
        away_poss_avg = None
        if (
            details.possession_first_half_home is not None
            and details.possession_second_half_home is not None
        ):
            home_poss_avg = (
                details.possession_first_half_home + details.possession_second_half_home
            ) / 2
        if (
            details.possession_first_half_away is not None
            and details.possession_second_half_away is not None
        ):
            away_poss_avg = (
                details.possession_first_half_away + details.possession_second_half_away
            ) / 2

        # Calculate total chances for debug output
        home_total = sum(
            filter(
                None,
                [
                    details.home_team_chances_left,
                    details.home_team_chances_center,
                    details.home_team_chances_right,
                    details.home_team_chances_special,
                    details.home_team_chances_other,
                ],
            )
        )
        away_total = sum(
            filter(
                None,
                [
                    details.away_team_chances_left,
                    details.away_team_chances_center,
                    details.away_team_chances_right,
                    details.away_team_chances_special,
                    details.away_team_chances_other,
                ],
            )
        )

        # Debug: Check what we actually got from CHPP
        dprint(
            3,
            f"  CHPP returned - possession: {home_poss_avg}/{away_poss_avg}, "
            f"chances: {home_total}/{away_total}, "
            f"attendance: {details.attendance}",
        )

        enhanced_data.update(
            {
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
            }
        )

        # Fetch match lineup for formation and tactical data
        dprint(3, f"Fetching match lineup for match {match_id}")
        lineup = chpp.matchlineup(id_=match_id)

        enhanced_data.update(
            {
                "home_team_formation": lineup.home_team_formation,
                "away_team_formation": lineup.away_team_formation,
                "home_team_tactic": lineup.home_team_tactic,
                "away_team_tactic": lineup.away_team_tactic,
            }
        )

        # Filter out None values - only save fields that have actual data
        enhanced_data = {k: v for k, v in enhanced_data.items() if v is not None}

        if enhanced_data:
            dprint(
                2,
                f"Successfully fetched enhanced data for match {match_id}: {len(enhanced_data)} fields",
            )
        else:
            dprint(2, f"No enhanced data available for match {match_id}")

    except Exception as e:
        dprint(2, f"Could not fetch enhanced data for match {match_id}: {e!s}")
        # Return partial data if available
        enhanced_data = {k: v for k, v in enhanced_data.items() if v is not None}

    return enhanced_data


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
            if hasattr(match.datetime, "year"):
                thedate = datetime(
                    match.datetime.year,
                    match.datetime.month,
                    match.datetime.day,
                    match.datetime.hour,
                    match.datetime.minute,
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

            dprint(
                3,
                f"Processing match {match.ht_id}: {match.home_team_name} vs {match.away_team_name}",
            )

            # Check if match already exists
            dbmatch = db.session.query(Match).filter_by(ht_id=match.ht_id).first()

            # Determine if match is finished (has goals scored)
            is_finished = match.home_goals is not None and match.away_goals is not None

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
            dprint(2, f"Error processing match {match.ht_id}: {e!s}")
            db.session.rollback()
            continue

    return added, updated, enhanced


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
        dprint(
            2,
            f"User {user_id} already has {existing_groups} groups, skipping default creation",
        )
        return []

    # Default groups with football theme colors and spacing for customization
    default_groups = [
        {
            "name": "Goalkeepers",
            "order": 10,
            "textcolor": "#FFFFFF",
            "bgcolor": "#001f3f",  # Navy blue
        },
        {
            "name": "Defenders",
            "order": 20,
            "textcolor": "#FFFFFF",
            "bgcolor": "#0074D9",  # Blue
        },
        {
            "name": "Wing Defenders",
            "order": 30,
            "textcolor": "#FFFFFF",
            "bgcolor": "#2ECC40",  # Green
        },
        {
            "name": "Midfielders",
            "order": 40,
            "textcolor": "#000000",
            "bgcolor": "#FFFFFF",  # White
        },
        {
            "name": "Wingers",
            "order": 50,
            "textcolor": "#FFFFFF",
            "bgcolor": "#B10DC9",  # Purple
        },
        {
            "name": "Forwards",
            "order": 60,
            "textcolor": "#FFFFFF",
            "bgcolor": "#FF4136",  # Red
        },
    ]

    created_groups = []

    try:
        for group_data in default_groups:
            group = Group(
                user_id=user_id,
                name=group_data["name"],
                order=group_data["order"],
                textcolor=group_data["textcolor"],
                bgcolor=group_data["bgcolor"],
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
        },
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
        },
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
        },
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
        },
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
        },
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
        },
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
        },
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
        },
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
        },
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
        },
    },
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
                "player_name": f"{getattr(player, 'first_name', '')} {getattr(player, 'last_name', '')}",
            }
            total_score += contribution
        else:
            position_scores[position_id] = {
                "contribution": 0,
                "position_name": formation["positions"][position_id]["name"],
                "player_name": "No player assigned",
            }

    return {
        "total_score": round(total_score, 2),
        "average_score": round(total_score / len(formation["positions"]), 2),
        "position_scores": position_scores,
        "formation_name": formation["name"],
    }


def get_formation_list():
    """Get list of available formations for dropdown selection."""
    return [
        {"key": key, "name": template["name"], "description": template["description"]}
        for key, template in FORMATION_TEMPLATES.items()
    ]


def _player_history(player_ids, since):
    """{ht_id: [records oldest first]} with all rows from ``since`` on plus the
    last row before it (the baseline for the oldest week). Two queries."""
    from sqlalchemy import cast, Date

    from models import Players

    window = (
        db.session.query(Players)
        .filter(Players.ht_id.in_(player_ids))
        .filter(cast(Players.data_date, Date) >= since)
        .all()
    )
    baseline = (
        db.session.query(Players)
        .filter(Players.ht_id.in_(player_ids))
        .filter(cast(Players.data_date, Date) < since)
        .distinct(Players.ht_id)
        .order_by(Players.ht_id, Players.data_date.desc())
        .all()
    )
    history = {}
    for record in sorted(baseline + window, key=lambda r: r.data_date):
        history.setdefault(record.ht_id, []).append(record)
    return history


def _record_on(records, day):
    """Latest record (oldest-first list) whose data_date falls on or before ``day``."""
    found = None
    for record in records:
        if record.data_date.date() > day:
            break
        found = record
    return found


def get_team_timeline(team_id, weeks=4):
    """Get 4-week timeline of skill changes for a specific team.

    Loads the needed player history once (instead of querying per player and
    week) and compares the latest snapshot at each week boundary.

    Returns:
        dict: {"week_1": {"week_label", "is_current", "days_ago_start",
        "days_ago_end", "changes": [[display_data, name, old, new, type, attr], ...]}, ...}
    """
    try:
        from datetime import timedelta

        from models import Players

        player_ids = [
            row.ht_id
            for row in db.session.query(Players.ht_id)
            .filter_by(owner=team_id)
            .distinct()
        ]
        if not player_ids:
            return {}

        today = datetime.now().date()
        history = _player_history(player_ids, today - timedelta(days=weeks * 7))
        groups = _player_group_info(player_ids)

        def sort_key(change):
            data = change[0]
            order = data.get("group_order")
            return (9999 if order is None else order, data.get("name", ""))

        timeline = {}
        for week_num in range(1, weeks + 1):
            start_days, end_days = week_num * 7, (week_num - 1) * 7
            start_day = today - timedelta(days=start_days)
            end_day = today - timedelta(days=end_days)

            changes = []
            for player_id, records in history.items():
                old = _record_on(records, start_day)
                new = _record_on(records, end_day)
                if not old or not new or old.data_date == new.data_date:
                    continue
                display = _player_display_data(new, groups.get(player_id))
                changes.extend(_record_changes(old, new, display))

            timeline[f"week_{week_num}"] = {
                "week_label": f"Week {week_num}",
                "is_current": week_num == 1,
                "days_ago_start": start_days,
                "days_ago_end": end_days,
                "changes": sorted(changes, key=sort_key),
            }
        return timeline

    except Exception as e:
        dprint(1, f"Error in get_team_timeline: {e}")
        return {}
