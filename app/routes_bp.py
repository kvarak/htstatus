"""Flask routes converted to Blueprint pattern for HT Status application."""

import inspect
import subprocess  # noqa: B404 - Used only for git version detection (static commands)
import time

from flask import Blueprint, current_app, render_template, session
from flask_bootstrap import Bootstrap
from sqlalchemy import desc

from models import User

# Create Blueprint for routes (helper blueprint, not registered directly)
routes_bp = Blueprint('routes', __name__)

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
    print("DEBUG: initialize_routes - Start")
    global bootstrap, consumer_key, consumer_secret, versionstr, fullversion, version, timenow, debug_level

    # Get db from current app context
    print("DEBUG: initialize_routes - Getting db")
    from app.factory import db as factory_db
    global db
    db = factory_db

    # Initialize Flask-Bootstrap
    print("DEBUG: initialize_routes - Initializing Bootstrap")
    bootstrap = Bootstrap(app)

    # Set consumer_key and consumer_secret provided for your app by Hattrick
    print("DEBUG: initialize_routes - Setting CHPP credentials")
    consumer_key = app.config.get('CONSUMER_KEY', 'dev_key')
    consumer_secret = app.config.get('CONSUMER_SECRETS', 'dev_secret')

    # Handle version detection safely
    print("DEBUG: initialize_routes - Detecting version")
    # Security Note: Git version detection for UI display only
    # - Static command with no user input injection vectors
    # - Development/operations utility with fallback for missing git
    # - Risk is theoretical (partial path warning) rather than practical
    # - Acceptable for development tooling purposes
    try:
        versionstr = subprocess.check_output(["git", "describe", "--tags"]).strip()  # noqa: B607,B603
        versionstr = versionstr.decode("utf-8").split('-')
        fullversion = versionstr[0] + "." + versionstr[1] + "-" + versionstr[2]
        version = versionstr[0] + "." + versionstr[1]
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        # Fallback for development environment
        fullversion = "2.0.0-dev"
        version = "2.0.0"

    timenow = time.strftime('%Y-%m-%d %H:%M:%S')
    print("DEBUG: initialize_routes - Complete")
    debug_level = app.config.get('DEBUG_LEVEL', 1)


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
    if name == 'main_bp':
        return get_main_bp()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# --------------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------------

def dprint(lvl, *args):
    """Debug print function."""
    if debug_level and lvl <= debug_level:
        # 0 represents this line, 1 represents line at caller
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        pstr = ""
        for a in args:
            pstr = pstr + str(a)
        print(now + " " + info.function + ":" + str(info.lineno) + " " + pstr)


def debug_print(route, function, *args):
    """Debug print function for route tracking."""
    if debug_level and debug_level >= 2:
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        pstr = ""
        for a in args:
            pstr = pstr + str(a)
        print(now + " [" + route + "] " + function + " " + pstr)


def diff_month(d1, d2):
    """Calculate months between two dates."""
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def diff(first, second):
    """Find elements in first list that are not in second list."""
    return [item for item in first if item not in second]


def get_training(players_data):
    """Extract training and player name data from player records."""
    allplayerids = []
    allplayers = {}
    playernames = {}
    for entry in players_data:
        allplayers[entry.ht_id] = []
        if entry.number == 100:
            playernames[entry.ht_id] = entry.first_name + " " + entry.last_name
        else:
            playernames[entry.ht_id] = str(entry.number) + ". " + \
                entry.first_name + " " + entry.last_name
        if entry.ht_id not in allplayerids:
            allplayerids.append(entry.ht_id)

    return (allplayerids, allplayers, playernames)


def player_diff(playerid, daysago):
    """Calculate player skill changes over a period of days."""
    from datetime import datetime, timedelta

    from models import Players

    # Get current player data
    now = datetime.now()
    targetdate = now - timedelta(days=daysago)

    playerdata_now = (db.session.query(Players)
                      .filter_by(ht_id=playerid)
                      .order_by(desc("data_date"))
                      .first())

    playerdata_then = (db.session.query(Players)
                       .filter_by(ht_id=playerid)
                       .filter(Players.data_date <= targetdate)
                       .order_by(desc("data_date"))
                       .first())

    if not playerdata_now or not playerdata_then:
        return None

    playername = playerdata_now.first_name + " " + playerdata_now.last_name

    changes = {
        'id': playerid,
        'name': playername,
        'keeper': playerdata_now.keeper - playerdata_then.keeper,
        'defender': playerdata_now.defender - playerdata_then.defender,
        'playmaker': playerdata_now.playmaker - playerdata_then.playmaker,
        'winger': playerdata_now.winger - playerdata_then.winger,
        'passing': playerdata_now.passing - playerdata_then.passing,
        'scorer': playerdata_now.scorer - playerdata_then.scorer,
        'set_pieces': playerdata_now.set_pieces - playerdata_then.set_pieces,
    }

    # Return None if no changes
    total_change = sum([v for k, v in changes.items() if k != 'id' and k != 'name'])
    if total_change == 0:
        return None

    return changes


def create_page(template, title, **kwargs):
    """Create page with standard template context."""
    last_update = ""

    # Get current app for config access
    app = current_app

    if 'current_user' in session:
        current_user = session['current_user']
        all_teams = session.get('all_teams', [])
        all_team_names = session.get('all_team_names', [])
        try:
            user = (db.session.query(User)
                    .filter_by(ht_id=session['current_user_id'])
                    .first())
            if user:
                last_update = getattr(user, 'last_update', '')
            role = False
        except Exception:
            role = False
    else:
        current_user = False
        all_teams = False
        all_team_names = False
        role = False

    # Handle changelog files safely
    try:
        with open('app/static/changelog.txt') as f:
            changelog = f.readlines()
        with open('app/static/changelog-full.txt') as f:
            changelogfull = f.readlines()
    except FileNotFoundError:
        changelog = ["No changelog available"]
        changelogfull = ["No changelog available"]

    return render_template(
        template,
        title=title,
        version=version or "2.0.0",
        timenow=timenow or time.strftime('%Y-%m-%d %H:%M:%S'),
        fullversion=fullversion or "2.0.0-dev",
        apptitle=app.config.get('APP_NAME', 'HT Status'),
        current_user=current_user,
        all_teams=all_teams,
        all_team_names=all_team_names,
        role=role,
        changelog=changelog,
        changelogfull=changelogfull,
        last_update=last_update,
        **kwargs)

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
