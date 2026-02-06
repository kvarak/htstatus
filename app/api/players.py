"""API routes for player operations including bulk assignment and filtering."""

from flask import Blueprint, jsonify, request, session

from app.auth_utils import get_team_info, get_user_teams, require_authentication
from app.error_handlers import ValidationError, validate_team_id
from app.utils import dprint

# Create Blueprint for API routes
api_bp = Blueprint("api", __name__, url_prefix="/api")

# These will be set by setup_api_blueprint()
db = None

def setup_api_blueprint(db_instance):
    """Initialize API blueprint with database instance."""
    global db
    db = db_instance

@api_bp.route("/players/bulk-assign", methods=["POST"])
@require_authentication
def bulk_assign_players():
    """Handle bulk player group assignment.

    Expected JSON payload:
    {
        "player_ids": ["123", "456", "789"],
        "group_id": "5" or null,
        "team_id": "12345"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        player_ids = data.get("player_ids", [])
        group_id = data.get("group_id")
        team_id = data.get("team_id")

        if not player_ids:
            return jsonify({"error": "No player IDs provided"}), 400

        if not team_id:
            return jsonify({"error": "Team ID is required"}), 400

        # Validate team access
        try:
            team_id = validate_team_id(team_id)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

        # Validate team access using consolidated function
        all_teams, all_team_names = get_user_teams()
        is_valid, teamname, error_msg = get_team_info(team_id, (all_teams, all_team_names))

        if not is_valid:
            return jsonify({"error": error_msg}), 403

        # Import models using registry pattern for consistency
        try:
            from app.model_registry import get_group_model, get_player_setting_model
            PlayerSetting = get_player_setting_model()
            Group = get_group_model()
        except (ImportError, ValueError):
            from models import Group, PlayerSetting

        current_user_id = session.get("current_user_id")
        if not current_user_id:
            return jsonify({"error": "User not authenticated"}), 401

        success_count = 0
        failed_players = []

        # Process bulk assignment in database transaction
        try:
            with db.session.begin():
                for player_id in player_ids:
                    try:
                        player_id = int(player_id)

                        # Check if player setting already exists
                        existing_setting = (
                            db.session.query(PlayerSetting)
                            .filter_by(player_id=player_id, user_id=current_user_id)
                            .first()
                        )

                        if group_id is None or group_id == "-1":
                            # Remove from group (delete setting)
                            if existing_setting:
                                db.session.delete(existing_setting)
                                success_count += 1
                        else:
                            # Assign to group
                            group_id = int(group_id)

                            # Verify group belongs to current user
                            group = db.session.query(Group).filter_by(id=group_id, user_id=current_user_id).first()
                            if not group:
                                failed_players.append({"player_id": player_id, "error": "Invalid group"})
                                continue

                            if existing_setting:
                                # Update existing setting
                                existing_setting.group_id = group_id
                            else:
                                # Create new setting
                                new_setting = PlayerSetting(
                                    player_id=player_id,
                                    user_id=current_user_id,
                                    group_id=group_id
                                )
                                db.session.add(new_setting)
                            success_count += 1

                    except ValueError:
                        failed_players.append({"player_id": player_id, "error": "Invalid player ID"})
                        continue
                    except Exception as e:
                        failed_players.append({"player_id": player_id, "error": str(e)})
                        continue

            dprint(2, f"Bulk assignment completed: {success_count} successful, {len(failed_players)} failed")

            result = {
                "success_count": success_count,
                "failed_count": len(failed_players),
                "message": f"Successfully updated {success_count} player{'s' if success_count != 1 else ''}"
            }

            if failed_players:
                result["failures"] = failed_players

            return jsonify(result)

        except Exception as e:
            db.session.rollback()
            dprint(1, f"Bulk assignment transaction failed: {e}")
            return jsonify({"error": "Database transaction failed", "details": str(e)}), 500

    except Exception as e:
        dprint(1, f"Bulk assignment error: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@api_bp.route("/players/filter", methods=["GET"])
@require_authentication
def filter_players():
    """Filter players based on criteria (for AJAX filtering).

    Query parameters:
    - team_id: Team ID
    - name: Player name filter
    - group_id: Group filter
    - position: Position filter
    - min_age: Minimum age
    - max_age: Maximum age
    """
    try:
        team_id = request.args.get("team_id")
        if not team_id:
            return jsonify({"error": "Team ID is required"}), 400

        # Validate team access
        try:
            team_id = validate_team_id(team_id)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400

        # Validate team access using consolidated function
        all_teams, all_team_names = get_user_teams()
        is_valid, teamname, error_msg = get_team_info(team_id, (all_teams, all_team_names))

        if not is_valid:
            return jsonify({"error": error_msg}), 403

        # Get filter parameters
        name_filter = request.args.get("name", "").lower()
        group_filter = request.args.get("group_id")
        # position_filter = request.args.get("position")  # TODO: Implement position filtering
        min_age = request.args.get("min_age", type=int)
        max_age = request.args.get("max_age", type=int)

        # Import models
        try:
            from app.model_registry import get_player_setting_model, get_players_model
            Players = get_players_model()
            PlayerSetting = get_player_setting_model()
        except (ImportError, ValueError):
            from models import Players, PlayerSetting

        current_user_id = session.get("current_user_id")

        # Query players for the team (get latest records)
        players_query = (
            db.session.query(Players)
            .filter_by(owner=team_id)
            .order_by(Players.data_date.desc(), Players.number)
        )

        # Apply filters (simplified for now - would need more sophisticated filtering)
        filtered_players = []
        for player in players_query.all():
            player_name = f"{player.first_name or ''} {player.last_name or ''}".strip().lower()

            # Name filter
            if name_filter and name_filter not in player_name:
                continue

            # Age filter (if age data available)
            if min_age is not None and hasattr(player, 'age') and player.age < min_age:
                continue
            if max_age is not None and hasattr(player, 'age') and player.age > max_age:
                continue

            # Group filter (check PlayerSetting)
            if group_filter:
                player_setting = (
                    db.session.query(PlayerSetting)
                    .filter_by(player_id=player.ht_id, user_id=current_user_id)
                    .first()
                )
                if group_filter == "unassigned":
                    if player_setting and player_setting.group_id:
                        continue
                else:
                    if not player_setting or str(player_setting.group_id) != group_filter:
                        continue

            filtered_players.append({
                "id": player.ht_id,
                "name": f"{player.first_name or ''} {player.last_name or ''}".strip(),
                "age": getattr(player, 'age', None),
                "number": player.number
            })

        return jsonify({
            "players": filtered_players,
            "count": len(filtered_players)
        })

    except Exception as e:
        dprint(1, f"Player filtering error: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
