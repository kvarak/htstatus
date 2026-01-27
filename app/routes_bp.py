"""Flask routes converted to Blueprint pattern for HT Status application."""

# subprocess import removed - using shared version detection from app.utils
import time

from flask import Blueprint
from flask_bootstrap import Bootstrap

# Create Blueprint for routes (helper blueprint, not registered directly)
routes_bp = Blueprint("routes", __name__)

# Initialize these after app is created
bootstrap = None
consumer_key = None
consumer_secret = None
versionstr = None
fullversion = None
version = None
timenow = None
debug_level = None


def initialize_routes(app, _db_instance):
    """Initialize routes module with app and db instances."""
    global \
        bootstrap, \
        consumer_key, \
        consumer_secret, \
        versionstr, \
        fullversion, \
        version, \
        timenow, \
        debug_level

    # Get db from current app context
    from app.factory import db as factory_db

    global db
    db = factory_db

    # Initialize Flask-Bootstrap
    bootstrap = Bootstrap(app)

    # Set consumer_key and consumer_secret provided for your app by Hattrick
    consumer_key = app.config.get("CONSUMER_KEY", "dev_key")
    consumer_secret = app.config.get("CONSUMER_SECRETS", "dev_secret")

    # Handle version detection using shared utility
    print("DEBUG: initialize_routes - Detecting version")
    from app.utils import get_version_info
    version_info = get_version_info()

    # Extract version variables for module-level access
    versionstr = version_info["versionstr"]
    fullversion = version_info["fullversion"]
    version = version_info["version"]

    timenow = time.strftime("%Y-%m-%d %H:%M:%S")
    debug_level = app.config.get("DEBUG_LEVEL", 1)


# Module constants
default_group_order = 99
logfile = "htplanner.log"


# Add route function references for test compatibility
def index():
    """Index route function reference."""
    from app.blueprints.main import index as main_index

    return main_index()


def player():
    """Player route function reference."""
    from app.blueprints.player import player as player_func

    return player_func()


def team():
    """Team route function reference."""
    from app.blueprints.team import team as team_func

    return team_func()


def settings():
    """Settings route function reference."""
    from app.blueprints.main import settings as settings_func

    return settings_func()


def logout():
    """Logout route function reference."""
    from app.blueprints.auth import logout as logout_func

    return logout_func()


def matches():
    """Matches route function reference."""
    from app.blueprints.matches import matches as matches_func

    return matches_func()


def training():
    """Training route function reference."""
    from app.blueprints.training import training as training_func

    return training_func()


def update():
    """Update route function reference."""
    from app.blueprints.team import update as update_func

    return update_func()


def debug():
    """Debug/admin route function reference."""
    from app.blueprints.main import admin as admin_func

    return admin_func()


# Blueprint reference for test compatibility - use function to avoid circular dependency
def get_main_bp():
    """Get main blueprint reference."""
    from app.blueprints.main import main_bp

    return main_bp


# Create module-level variable for backward compatibility
def __getattr__(name):
    """Dynamic attribute access for main_bp."""
    if name == "main_bp":
        return get_main_bp()
    # This function provides backward compatibility for any remaining direct imports
    # All utility functions have been moved to app/utils.py
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Note: All utility functions (dprint, debug_print, diff_month, diff, get_training,
# player_diff, create_page) have been consolidated into app/utils.py
# Blueprints should import from app.utils instead of app.routes_bp

# --------------------------------------------------------------------------------
# Routes - Now handled by individual blueprint modules
# --------------------------------------------------------------------------------

# Note: All routes have been migrated to individual blueprint modules:
# - Main routes: app.blueprints.main
# - Auth routes: app.blueprints.auth
# - Player routes: app.blueprints.player
# - Team routes: app.blueprints.team
# - Match routes: app.blueprints.matches
# - Training routes: app.blueprints.training

# All routes migrated to blueprint modules - no direct route definitions needed here
