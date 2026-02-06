"""Player comparison routes and utilities."""

from flask import Blueprint, redirect, request, url_for

from app.auth_utils import get_team_info, get_user_teams, require_authentication
from app.error_handlers import ValidationError, validate_team_id
from app.utils import create_page, dprint

# Create Blueprint for player comparison
compare_bp = Blueprint("compare", __name__, url_prefix="/player")

# Global variable to be set by setup function
db = None

def setup_compare_blueprint(db_instance):
    """Initialize comparison blueprint with database instance."""
    global db
    db = db_instance

@compare_bp.route("/compare")
@require_authentication
def compare_players():
    """Display player comparison interface."""
    try:
        team_id = request.args.get("team_id")
        player_ids = request.args.getlist("player_ids")

        if not team_id:
            return redirect(url_for("player.player"))

        if not player_ids or len(player_ids) < 2 or len(player_ids) > 8:
            return redirect(url_for("player.player", id=team_id, error="Please select 2-8 players for comparison"))

        # Validate team access
        try:
            team_id = validate_team_id(team_id)
        except ValidationError as e:
            return redirect(url_for("player.player", error=str(e)))

        # Validate team access using consolidated function
        all_teams, all_team_names = get_user_teams()
        is_valid, teamname, error_msg = get_team_info(team_id, (all_teams, all_team_names))

        if not is_valid:
            return redirect(url_for("player.player", error=error_msg))

        # Import models
        try:
            from app.model_registry import get_players_model
            Players = get_players_model()
        except (ImportError, ValueError):
            from models import Players

        # Get player data
        players_data = []
        players_oldest_dict = {}

        # Get oldest player data for skill changes
        oldest_data = (
            db.session.query(Players)
            .filter_by(owner=team_id)
            .order_by(Players.data_date.asc())
            .all()
        )

        # Build dictionary of oldest data for each player
        for oldest_player in oldest_data:
            if oldest_player.ht_id not in players_oldest_dict:
                players_oldest_dict[oldest_player.ht_id] = {
                    'keeper': getattr(oldest_player, 'keeper', 0),
                    'defender': getattr(oldest_player, 'defender', 0),
                    'playmaker': getattr(oldest_player, 'playmaker', 0),
                    'winger': getattr(oldest_player, 'winger', 0),
                    'passing': getattr(oldest_player, 'passing', 0),
                    'scorer': getattr(oldest_player, 'scorer', 0),
                    'set_pieces': getattr(oldest_player, 'set_pieces', 0),
                }

        for player_id in player_ids:
            try:
                player_id = int(player_id)
                # Get latest player record
                player = (
                    db.session.query(Players)
                    .filter_by(ht_id=player_id, owner=team_id)
                    .order_by(Players.data_date.desc())
                    .first()
                )

                if player:
                    # Calculate best position using the same logic as player page
                    from app.constants import CALC_COLUMNS
                    from app.utils import calculateContribution

                    best_position = "-"
                    best_val = 0
                    for position in CALC_COLUMNS:
                        contribution = calculateContribution(position, player.__dict__)
                        if contribution > best_val:
                            best_position = position
                            best_val = contribution

                    # Get group information
                    group_name = 'No Group'
                    try:
                        from app.model_registry import (
                            get_group_model,
                            get_player_setting_model,
                        )
                        PlayerSetting = get_player_setting_model()
                        Group = get_group_model()
                    except (ImportError, ValueError):
                        from models import Group, PlayerSetting

                    # Check if player has a group assignment
                    from flask import session
                    player_setting = (
                        db.session.query(PlayerSetting)
                        .filter_by(player_id=player.ht_id, user_id=session["current_user_id"])
                        .first()
                    )

                    if player_setting and player_setting.group_id:
                        group = db.session.query(Group).filter_by(id=player_setting.group_id).first()
                        if group and group.name:
                            group_name = group.name

                    players_data.append({
                        'ht_id': player.ht_id,
                        'first_name': player.first_name,
                        'last_name': player.last_name,
                        'number': player.number,
                        'age': getattr(player, 'age', None),
                        'loyalty': getattr(player, 'loyalty', None),
                        'best_position': best_position,
                        'group_name': group_name,
                        'keeper': getattr(player, 'keeper', 0),
                        'defender': getattr(player, 'defender', 0),
                        'playmaker': getattr(player, 'playmaker', 0),
                        'winger': getattr(player, 'winger', 0),
                        'passing': getattr(player, 'passing', 0),
                        'scorer': getattr(player, 'scorer', 0),
                        'set_pieces': getattr(player, 'set_pieces', 0),
                        'form': getattr(player, 'form', None),
                        'stamina': getattr(player, 'stamina', None),
                        'tsi': getattr(player, 'tsi', None),
                        'salary': getattr(player, 'salary', None),
                        'specialty': getattr(player, 'specialty', None)
                    })

            except ValueError:
                continue

        if not players_data:
            return redirect(url_for("player.player", id=team_id, error="No valid players found for comparison"))

        # Prepare skill data for charts
        skill_names = ['keeper', 'defender', 'playmaker', 'winger', 'passing', 'scorer', 'set_pieces']
        chart_data = {
            'labels': skill_names,
            'datasets': []
        }

        colors = [
            'rgba(255, 99, 132, 0.6)',   # Red
            'rgba(54, 162, 235, 0.6)',   # Blue
            'rgba(255, 205, 86, 0.6)',   # Yellow
            'rgba(75, 192, 192, 0.6)',   # Teal
            'rgba(153, 102, 255, 0.6)',  # Purple
            'rgba(255, 159, 64, 0.6)'    # Orange
        ]

        for i, player in enumerate(players_data):
            player_name = f"{player['first_name']} {player['last_name']}"
            color = colors[i % len(colors)]

            chart_data['datasets'].append({
                'label': player_name,
                'data': [player[skill] for skill in skill_names],
                'backgroundColor': color,
                'borderColor': color.replace('0.6', '1.0'),
                'pointBackgroundColor': color.replace('0.6', '1.0'),
                'pointBorderColor': '#fff',
                'pointHoverBackgroundColor': '#fff',
                'pointHoverBorderColor': color.replace('0.6', '1.0')
            })

        return create_page(
            template="player-compare.html",
            title="Player Comparison",
            players_data=players_data,
            players_oldest=players_oldest_dict,
            chart_data=chart_data,
            skill_names=skill_names,
            team_id=team_id
        )

    except Exception as e:
        dprint(1, f"Player comparison error: {e}")
        return redirect(url_for("player.player", error="An error occurred during comparison"))
