"""Shared utility functions for HT Status application."""

import inspect
from datetime import datetime

from dateutil.relativedelta import relativedelta
from flask import current_app, render_template
from sqlalchemy import desc

from models import Match, Players

# Global variables - will be initialized by initialize_utils()
db = None
debug_level = None

def initialize_utils(app_instance, db_instance, debug_level_value):
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
        fname = inspect.stack()[1].filename.split('/')[-1]  # get calling file
        print(f"[{fname}]", *args)

def debug_print(route, function, *args):
    """Enhanced debug print for route tracing."""
    if debug_level is None or debug_level >= 2:
        fname = inspect.stack()[1].filename.split('/')[-1]  # get calling file
        print(f"[{fname}] {route}::{function}() -", *args)

# =============================================================================
# Date and Comparison Utilities
# =============================================================================

def diff_month(d1, d2):
    """Calculate month difference between two dates."""
    return (d1.year - d2.year) * 12 + d1.month - d2.month

def diff(first, second):
    """Calculate difference between two values with None handling."""
    if first is None or second is None:
        return None
    return first - second

# =============================================================================
# Template and Page Utilities
# =============================================================================

def create_page(template, title, **kwargs):
    """Create standardized page response with common template variables."""
    # Get variables from routes module
    import app.routes as routes_module

    # Standard template variables
    template_vars = {
        'bootstrap': getattr(routes_module, 'bootstrap', None),
        'title': title,
        'consumer_key': getattr(routes_module, 'consumer_key', ''),
        'consumer_secret': getattr(routes_module, 'consumer_secret', ''),
        'versionstr': getattr(routes_module, 'versionstr', ''),
        'fullversion': getattr(routes_module, 'fullversion', ''),
        'version': getattr(routes_module, 'version', ''),
        'timenow': getattr(routes_module, 'timenow', ''),
    }

    # Add any additional template variables
    template_vars.update(kwargs)

    return render_template(template, **template_vars)

# =============================================================================
# Player Data Processing Utilities
# =============================================================================

def get_training(players_data):
    """Process training data from player list."""
    if not players_data:
        return {}

    # Deduplicate players (same as in routes_bp.py implementation)
    seen_players = set()
    unique_players = []
    for player in players_data:
        player_key = (player.ht_id, player.data_date)
        if player_key not in seen_players:
            seen_players.add(player_key)
            unique_players.append(player)

    training_data = {}
    for player in unique_players:
        training_data[player.ht_id] = {
            'first_name': player.first_name,
            'last_name': player.last_name,
            'data_date': player.data_date.strftime('%Y-%m-%d') if player.data_date else 'N/A',
            'age': player.age,
            'skills': {
                'keeper': player.keeper,
                'defender': player.defender,
                'playmaker': player.playmaker,
                'winger': player.winger,
                'passing': player.passing,
                'scorer': player.scorer,
                'set_pieces': player.set_pieces,
            }
        }

    return training_data

def player_diff(playerid, daysago):
    """Get player skill differences over time (returns list format for template compatibility)."""
    try:
        # Query for player data from specified days ago
        cutoff_date = datetime.now() - relativedelta(days=daysago)

        old_player = db.session.query(Players).filter_by(ht_id=playerid)\
            .filter(Players.data_date <= cutoff_date)\
            .order_by(desc(Players.data_date)).first()

        current_player = db.session.query(Players).filter_by(ht_id=playerid)\
            .order_by(desc(Players.data_date)).first()

        if not old_player or not current_player:
            return []

        # Calculate differences for each skill
        skills = ['keeper', 'defender', 'playmaker', 'winger', 'passing', 'scorer', 'set_pieces']
        differences = []

        for skill in skills:
            old_val = getattr(old_player, skill, 0) or 0
            new_val = getattr(current_player, skill, 0) or 0

            if old_val != new_val:
                differences.append([
                    current_player.team_name or "Unknown Team",
                    current_player.first_name or "Unknown",
                    current_player.last_name or "Player",
                    skill.capitalize(),
                    old_val,
                    new_val
                ])

        return differences

    except Exception as e:
        dprint(1, f"Error in player_diff: {e}")
        return []

# =============================================================================
# Team Statistics and Analysis Functions
# =============================================================================

def calculateManmark(player):
    """Calculate manmark rating for a player."""
    try:
        experience = player.experience or 0

        # Convert experience to a 0-20 scale for calculations
        exp_rating = min(experience / 5.0, 20.0)  # Scale experience appropriately

        # Calculate man-mark as combination of defender skill and experience
        defender = player.defender or 0
        manmark = (defender + exp_rating * 0.3) * 0.95  # Slight reduction from pure defender

        return round(max(0, manmark), 2)
    except Exception as e:
        dprint(1, f"Error calculating manmark for player {player.ht_id}: {e}")
        return 0.0

def calculateContribution(position, player):
    """Calculate player contribution to team based on position and skills."""
    try:
        # Position skill mappings based on Hattrick position requirements
        position_skills = {
            100: {'keeper': 1.0},  # Goalkeeper
            101: {'defender': 0.7, 'passing': 0.3},  # Right Back
            102: {'defender': 0.8, 'passing': 0.2},  # Right Centre Back
            103: {'defender': 0.8, 'passing': 0.2},  # Centre Back
            104: {'defender': 0.8, 'passing': 0.2},  # Left Centre Back
            105: {'defender': 0.7, 'passing': 0.3},  # Left Back
            106: {'winger': 0.7, 'passing': 0.3},    # Right Winger
            107: {'playmaker': 0.6, 'passing': 0.4},  # Right Inner Midfield
            108: {'playmaker': 0.8, 'passing': 0.2},  # Central Inner Midfield
            109: {'playmaker': 0.6, 'passing': 0.4},  # Left Inner Midfield
            110: {'winger': 0.7, 'passing': 0.3},    # Left Winger
            111: {'scorer': 0.6, 'passing': 0.4},    # Right Forward
            112: {'scorer': 0.8, 'passing': 0.2},    # Central Forward
            113: {'scorer': 0.6, 'passing': 0.4},    # Left Forward
        }

        skills_weights = position_skills.get(position, {'passing': 1.0})

        contribution = 0.0
        for skill, weight in skills_weights.items():
            skill_value = getattr(player, skill, 0) or 0
            contribution += skill_value * weight

        # Apply experience and form multipliers
        experience_mult = 1.0 + (min(player.experience or 0, 20) / 100.0)  # Up to 20% bonus
        form_mult = 1.0 + ((player.form or 5) - 5) / 20.0  # -25% to +25% based on form
        loyalty_mult = 1.0 + (min(player.loyalty or 0, 20) / 200.0)  # Up to 10% bonus

        final_contribution = contribution * experience_mult * form_mult * loyalty_mult

        return round(max(0, final_contribution), 2)

    except Exception as e:
        dprint(1, f"Error calculating contribution for player {player.ht_id} at position {position}: {e}")
        return 0.0

def calculate_team_statistics(players):
    """Calculate comprehensive team statistics from player list."""
    if not players:
        return {}

    stats = {
        'total_players': len(players),
        'avg_age': 0,
        'avg_tsi': 0,
        'total_salary': 0,
        'skill_averages': {}
    }

    # Calculate averages
    total_age = sum(player.age or 0 for player in players)
    total_tsi = sum(player.tsi or 0 for player in players)
    total_salary = sum(player.salary or 0 for player in players)

    stats['avg_age'] = round(total_age / len(players), 1)
    stats['avg_tsi'] = round(total_tsi / len(players), 0)
    stats['total_salary'] = total_salary

    # Calculate skill averages
    skills = ['keeper', 'defender', 'playmaker', 'winger', 'passing', 'scorer', 'set_pieces']
    for skill in skills:
        skill_sum = sum(getattr(player, skill, 0) or 0 for player in players)
        stats['skill_averages'][skill] = round(skill_sum / len(players), 1)

    return stats

def get_top_scorers(players, limit=5):
    """Get top scoring players from the list."""
    # Filter players with goals and sort by goals scored
    scorers = [p for p in players if getattr(p, 'goals', 0) and p.goals > 0]
    scorers.sort(key=lambda x: x.goals or 0, reverse=True)

    return scorers[:limit]

def get_top_performers(players, limit=5):
    """Get top performing players based on average rating."""
    # Filter players with rating data and sort by average rating
    performers = [p for p in players if getattr(p, 'rating_average', 0) and p.rating_average > 0]
    performers.sort(key=lambda x: x.rating_average or 0, reverse=True)

    return performers[:limit]

def get_team_match_statistics(teamid):
    """Get comprehensive match statistics for a team."""
    try:
        # Query match data for the team
        matches = db.session.query(Match).filter_by(team_id=teamid).all()

        if not matches:
            return {}

        stats = {
            'total_matches': len(matches),
            'wins': 0,
            'draws': 0,
            'losses': 0,
            'goals_for': 0,
            'goals_against': 0
        }

        for match in matches:
            stats['goals_for'] += match.home_goals if match.is_home_match else match.away_goals
            stats['goals_against'] += match.away_goals if match.is_home_match else match.home_goals

            # Determine result
            if match.is_home_match:
                if match.home_goals > match.away_goals:
                    stats['wins'] += 1
                elif match.home_goals == match.away_goals:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1
            else:
                if match.away_goals > match.home_goals:
                    stats['wins'] += 1
                elif match.away_goals == match.home_goals:
                    stats['draws'] += 1
                else:
                    stats['losses'] += 1

        return stats

    except Exception as e:
        dprint(1, f"Error getting match statistics for team {teamid}: {e}")
        return {}

# =============================================================================
# Data Processing and Download Utilities
# =============================================================================

def downloadMatches(teamid):
    """Download and process match data for a team."""
    try:
        # This is a complex function from routes.py - keeping the original implementation
        # but importing it here for consolidation
        from app.routes import downloadMatches as original_downloadMatches
        return original_downloadMatches(teamid)
    except ImportError:
        dprint(1, "Warning: downloadMatches function needs to be migrated")
        return []

def count_clicks(page):
    """Count page clicks for analytics."""
    try:
        # Simple click counting - could be enhanced with proper analytics
        if hasattr(current_app, 'click_counter'):
            current_app.click_counter[page] = current_app.click_counter.get(page, 0) + 1
        else:
            current_app.click_counter = {page: 1}

        return current_app.click_counter.get(page, 0)
    except Exception as e:
        dprint(1, f"Error counting clicks for page {page}: {e}")
        return 0
