"""Blueprint modules for HT Status application."""

from app.blueprints.auth import auth_bp
from app.blueprints.main import main_bp
from app.blueprints.player import player_bp
from app.blueprints.team import team_bp

__all__ = ["auth_bp", "main_bp", "player_bp", "team_bp"]
