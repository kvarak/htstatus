"""Flask routes converted to Blueprint pattern for HT Status application."""

import inspect
import math
import re
import subprocess
import time
import traceback
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from flask import render_template, request, session, Blueprint, current_app
from flask_bootstrap import Bootstrap
from pychpp import CHPP
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from models import Group, Match, MatchPlay, Players, PlayerSetting, User

# Create Blueprint for routes
main_bp = Blueprint('main', __name__)

# Initialize these after app is created
bootstrap = None
consumer_key = None
consumer_secret = None
versionstr = None
fullversion = None
version = None
timenow = None
debug_level = None

def initialize_routes(app, db_instance):
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
    try:
        versionstr = subprocess.check_output(["git", "describe", "--tags"]).strip()
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
# Routes
# --------------------------------------------------------------------------------

@main_bp.route('/')
def index():
    """Home page."""
    return create_page('main.html', 'Home')

@main_bp.route('/login')
def login():
    """Login page."""
    return create_page('login.html', 'Login')

@main_bp.route('/logout')
def logout():
    """Logout page."""
    return create_page('logout.html', 'Logout')

@main_bp.route('/player')
def player():
    """Player page."""
    return create_page('player.html', 'Players')

@main_bp.route('/team')
def team():
    """Team page."""
    return create_page('team.html', 'Team')

@main_bp.route('/matches')
def matches():
    """Matches page."""
    return create_page('matches.html', 'Matches')

@main_bp.route('/training')
def training():
    """Training page."""
    return create_page('training.html', 'Training')

@main_bp.route('/update')
def update():
    """Update page."""
    return create_page('update.html', 'Update')

@main_bp.route('/settings')
def settings():
    """Settings page."""
    return create_page('settings.html', 'Settings')

@main_bp.route('/debug')
def debug():
    """Debug page."""
    return create_page('debug.html', 'Debug')