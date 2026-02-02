"""Main and admin routes blueprint for HT Status application."""

import json
import os
import re
from datetime import date

from dateutil.relativedelta import relativedelta
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import text

from app.auth_utils import get_current_user_id, require_authentication
from app.model_registry import (
    get_group_model,
    get_player_setting_model,
    get_user_model,
)
from app.utils import create_page, diff_month, dprint

# Create Blueprint for main routes
main_bp = Blueprint("main", __name__)

# These will be set by setup_main_blueprint()
db = None
defaultcolumns = []
allcolumns = []
default_group_order = 99


def setup_main_blueprint(db_instance, cols, all_cols, group_order=99):
    """Initialize main blueprint with db instance and column definitions."""
    global db, defaultcolumns, allcolumns, default_group_order
    db = db_instance
    defaultcolumns = cols
    allcolumns = all_cols
    default_group_order = group_order


def get_releases_data():
    """Load recent user releases from JSON for display on main page."""
    try:
        # Use releases-full.json which contains all features per release
        releases_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'releases-full.json')
        with open(releases_path, encoding='utf-8') as f:
            releases_data = json.load(f)

        releases = []
        entries = releases_data.get('entries', [])

        # Get recent releases (already sorted newest first in JSON)
        for entry in entries:
            version = entry.get('version', '')
            period = entry.get('period', '')  # This is the formatted date
            features = entry.get('features', [])  # Full list of features

            # Format for main page display
            releases.append({
                'version': version,
                'date': period,
                'features': features  # All features from RELEASES.md
            })

        return releases[:6]  # Show recent 6 releases on main page
    except Exception as e:
        dprint(1, f"Error reading releases-full JSON: {e}")


@main_bp.route("/")
@main_bp.route("/index")
def index():
    """Display home page with user and team statistics."""
    User = get_user_model()
    allusers = db.session.query(User).all()
    time1m = date.today() - relativedelta(months=1)
    activeusers = db.session.query(User).filter(User.last_usage > time1m).all()

    if "current_user" not in session:
        return create_page(
            template="main.html",
            title="Home",
            usercount=len(allusers),
            activeusers=len(activeusers),
            releases=get_releases_data(),
        )

    # Check if session has team data (may be missing if CHPP failed during login)
    if "all_teams" not in session or not session["all_teams"]:
        session.clear()
        return redirect(url_for("auth.login"))

    all_teams = session["all_teams"]
    all_team_names = session["all_team_names"]
    updated = {}

    for i in range(len(all_teams)):
        updated[all_teams[i]] = all_team_names[i]

    dprint(2, updated)

    current_user_id = get_current_user_id()
    thisuserdata = db.session.query(User).filter_by(ht_id=current_user_id).first()

    if not thisuserdata:
        # User not found in database, clear session and redirect to login
        session.clear()
        return redirect(url_for("auth.login"))

    thisuser = {
        "id": thisuserdata.ht_id,
        "name": thisuserdata.ht_user,
        "role": thisuserdata.role,
        "c_team": thisuserdata.c_team,
        "c_training": thisuserdata.c_training,
        "c_player": thisuserdata.c_player,
        "c_matches": thisuserdata.c_matches,
        "c_login": thisuserdata.c_login,
        "c_update": thisuserdata.c_update,
        "last_update": thisuserdata.last_update,
        "last_usage": thisuserdata.last_usage,
        "last_login": thisuserdata.last_login,
        "created": thisuserdata.created,
    }

    dprint(2, thisuser)

    return create_page(
        template="main.html",
        title="Home",
        thisuser=thisuser,
        usercount=len(allusers),
        activeusers=len(activeusers),
        updated=updated,
        releases=get_releases_data(),
    )


@main_bp.route("/settings", methods=["GET", "POST"])
@require_authentication
def settings():
    """Handle user settings for player groups and display columns."""
    # Get model classes from registry
    User = get_user_model()
    Group = get_group_model()
    PlayerSetting = get_player_setting_model()

    # Track settings page access
    current_user_id = get_current_user_id()
    user = db.session.query(User).filter_by(ht_id=current_user_id).first()
    if user:
        user.settings()
        db.session.commit()

    error = ""

    groupname = request.form.get("groupname")
    grouporder = request.form.get("grouporder")
    addgroup = request.form.get("addgroup")
    updategroup = request.form.get("updategroup")
    deletegroup = request.form.get("deletegroup")
    groupid = request.form.get("groupid")
    textcolor = request.form.get("textcolor")
    bgcolor = request.form.get("bgcolor")
    if not textcolor:
        textcolor = "#000000"
    if not bgcolor:
        bgcolor = "#FFFFFF"

    user = db.session.query(User).filter_by(ht_id=get_current_user_id()).first()
    columns = user.getColumns() if user else []
    if len(columns) == 0:
        columns = defaultcolumns

    columnsorder = request.form.get("columnsorder")
    setcolumnsdefault = request.form.get("defaultcolumns")
    showdefaultcolumns = False
    if columnsorder and columnsorder != "empty":
        columns = []
        columngroups = columnsorder.split("Hidden columns")
        # Columns to show
        for r in columngroups[0].split("<div"):
            r = r.strip()
            if r == "":
                continue
            key = re.search('id="(.+?)"', r)
            text_match = re.search(">(.+?)</div>", r)
            if key:
                columns.append((text_match.group(1), key.group(1)))
        if user:
            user.updateColumns(columns)
        db.session.commit()
    elif setcolumnsdefault == "defaultcolumns":
        columns = defaultcolumns
        showdefaultcolumns = True

    hiddencolumns = [item for item in allcolumns if item not in columns]

    if addgroup:
        if groupname and grouporder:
            newgroup = Group(
                user_id=get_current_user_id(),
                name=groupname,
                order=grouporder,
                textcolor=textcolor,
                bgcolor=bgcolor,
            )
            db.session.add(newgroup)
            db.session.commit()
        else:
            error = "Groups need both name and order."

    elif updategroup and groupid:
        if groupname and grouporder:
            (
                db.session.query(Group)
                .filter_by(id=groupid)
                .update(
                    {
                        "name": groupname,
                        "order": grouporder,
                        "textcolor": textcolor,
                        "bgcolor": bgcolor,
                    }
                )
            )
            db.session.commit()
        else:
            error = "Groups need both name and order."

    elif deletegroup and groupid:
        try:
            thegroup = db.session.query(Group).filter_by(id=groupid).first()
            db.session.delete(thegroup)
            db.session.commit()
        except Exception:
            error = "The group wasn't empty, removed all players from that group."
            db.session.rollback()

            # remove all connected players
            connections = (
                db.session.query(PlayerSetting)
                .filter_by(group_id=groupid, user_id=get_current_user_id())
                .all()
            )
            dprint(2, connections)

            for playersetting in connections:
                connection = (
                    db.session.query(PlayerSetting)
                    .filter_by(
                        player_id=playersetting.player_id, user_id=get_current_user_id()
                    )
                    .first()
                )
                db.session.delete(connection)
                db.session.commit()

            thegroup = db.session.query(Group).filter_by(id=groupid).first()
            db.session.delete(thegroup)
            db.session.commit()

    group_data = (
        db.session.query(Group)
        .filter_by(user_id=get_current_user_id())
        .order_by(Group.order)
        .all()
    )

    # Add a default group
    default_group = Group(
        user_id=0,
        name="<default>",
        order=default_group_order,
        textcolor="#000000",
        bgcolor="#FFFFFF",
    )
    before_default = [g for g in group_data if g.order < default_group_order]
    after_default = [g for g in group_data if g.order >= default_group_order]
    before_default.append(default_group)

    group_data = before_default + after_default

    return create_page(
        template="settings.html",
        title="Settings",
        columns=columns,
        hiddencolumns=hiddencolumns,
        showdefaultcolumns=showdefaultcolumns,
        group_data=group_data,
        error=error,
    )


@main_bp.route("/changes")
def changes():
    """Public changes and changelog page."""
    # Track changes page access for authenticated users
    if "current_user_id" in session:
        User = get_user_model()
        current_user_id = get_current_user_id()
        user = db.session.query(User).filter_by(ht_id=current_user_id).first()
        if user:
            user.changes()
            db.session.commit()
    changelogfull = []
    try:
        import json

        all_entries = []

        # Read commits JSON
        commits_path = os.path.join(current_app.static_folder, 'changelog.json')
        try:
            with open(commits_path, encoding='utf-8') as f:
                commits_data = json.load(f)
                all_entries.extend(commits_data.get('entries', []))
        except Exception as e:
            dprint(1, f"Error reading commits JSON: {e}")

        # Read user releases JSON
        releases_path = os.path.join(current_app.static_folder, 'releases.json')
        try:
            with open(releases_path, encoding='utf-8') as f:
                releases_data = json.load(f)
                all_entries.extend(releases_data.get('entries', []))
        except Exception as e:
            dprint(1, f"Error reading releases JSON: {e}")

        # Read internal releases JSON
        internal_path = os.path.join(current_app.static_folder, 'releases-internal.json')
        try:
            with open(internal_path, encoding='utf-8') as f:
                internal_data = json.load(f)
                all_entries.extend(internal_data.get('entries', []))
        except Exception as e:
            dprint(1, f"Error reading internal releases JSON: {e}")

        # Sort all entries by date (newest first) with commit priority
        # When timestamps are equal, commits should appear before releases
        def sort_key(entry):
            entry_type = entry.get('type', 'unknown')
            date_val = entry.get('date') or ''

            # Convert date to make it sortable, then invert priority logic
            # We want commits to appear BEFORE releases when dates are equal
            # So commits get priority 0 (lower) and releases get priority 1 (higher)
            # With reverse=True, commits (0) will come before releases (1)
            type_priority = {'commit': 0, 'user_release': 1, 'internal_release': 1}
            priority = type_priority.get(entry_type, 1)

            return (date_val, priority)

        # Sort by date descending, then commits before releases for same dates
        all_entries.sort(key=sort_key, reverse=True)

        # Format entries for display and group commits with releases
        current_release_id = None
        release_counter = 0

        for _i, entry in enumerate(all_entries):
            entry_type = entry.get('type', 'unknown')
            full_date = entry.get('date', '')
            date = full_date.split(' ')[0]  # Get just the date part for display

            if entry_type == 'commit':
                version = entry.get('version', 'unknown')
                message = entry.get('message', '')
                # Add data attributes to group commits with their release
                commit_class = f'commit-group-{current_release_id}' if current_release_id else ''
                line = f'<div class="mb-1 py-1 px-2 border-left border-success bg-light {commit_class}" style="border-left-width: 3px !important; font-size: 0.9rem;"><small class="text-muted mr-2">{date}</small><code class="text-info small mr-2">{version}</code><span class="text-dark">{message}</span></div>'
            elif entry_type == 'user_release':
                version = entry.get('version', '')
                message = entry.get('message', '')
                line = f'<div class="bg-success text-white p-2 mb-2 rounded shadow-sm"><strong><i class="fas fa-rocket"></i> {date} 🎉 {version} USER RELEASE</strong><br><small>{message}</small></div>'
                # Reset current release for grouping
                current_release_id = None
            elif entry_type == 'internal_release':
                version = entry.get('version', '')
                message = entry.get('message', '')
                release_counter += 1
                current_release_id = release_counter
                # Make technical releases clickable with prominent expand symbol
                line = f'<div class="bg-info text-white p-2 mb-2 rounded shadow-sm" style="cursor: pointer;" onclick="toggleCommits({current_release_id})" title="Click to expand/collapse commit details"><strong><span id="chevron-{current_release_id}" style="display: inline-block; transition: transform 0.2s;">▼</span> <i class="fas fa-cog"></i> {date} 🔧 {version} TECHNICAL RELEASE</strong><br><small>{message}</small></div>'
            else:
                line = f'<div class="mb-2 p-2 border border-warning bg-warning-light"><span class="text-muted">{date}</span> <span class="text-warning font-weight-bold">[UNKNOWN]</span> {entry}</div>'
                # Reset current release for grouping
                current_release_id = None

            changelogfull.append(line)

        dprint(2, f"Loaded {len(changelogfull)} combined changelog entries")

    except Exception as e:
        dprint(1, f"Error reading changelog JSON files: {e}")
        changelogfull = ["Error loading changelog - run 'make changelog' to generate JSON files"]

    return create_page(
        template="changes.html",
        title="Changes & Development History",
        changelogfull=changelogfull,
    )


@main_bp.route("/debug", methods=["GET", "POST"])
@require_authentication
def admin():
    """Admin dashboard for user management."""
    # Get model classes from registry
    User = get_user_model()

    form_error = ""

    try:
        user = db.session.query(User).filter_by(ht_id=get_current_user_id()).first()
        role = user.getRole() if user else "User"
        if role != "Admin":
            return render_template("_forward.html", url="/")
    except Exception:
        return render_template("_forward.html", url="/")

    adminchecked = request.form.get("admin")
    userid = request.form.get("userid")

    dprint(2, "Checkbox: ", adminchecked)
    dprint(2, userid)

    if userid:
        try:
            user = db.session.query(User).filter_by(ht_id=userid).first()
            updateto = "Admin" if adminchecked else "User"

            dprint(2, updateto)

            if user:
                user.setRole(updateto)
            db.session.commit()

        except Exception:
            form_error = "couldn't change user"

    allusers = db.session.query(User).order_by(text("last_usage desc")).all()
    users = []
    for user in allusers:
        if (user.last_update - user.created).days < 1:
            active_time = "< 1 day"
        elif (user.last_update - user.created).days == 1:
            active_time = "1 day"
        elif diff_month(user.last_update, user.created) < 2:
            active_time = str((user.last_update - user.created).days) + " days"
        else:
            active_time = str(diff_month(user.last_update, user.created)) + " months"

        thisuser = {
            "id": user.ht_id,
            "name": user.ht_user,
            "role": user.role,
            "c_team": user.c_team,
            "c_training": user.c_training,
            "c_player": user.c_player,
            "c_matches": user.c_matches,
            "c_login": user.c_login,
            "c_update": user.c_update,
            "c_settings": user.c_settings or 0,
            "c_changes": user.c_changes or 0,
            "c_feedback": user.c_feedback or 0,
            "c_formation": user.c_formation or 0,
            "c_stats": user.c_stats or 0,
            "last_update": user.last_update,
            "last_usage": user.last_usage,
            "last_login": user.last_login,
            "created": user.created,
            "active_time": active_time,
        }
        users.append(thisuser)

    # Get recent errors for display
    from models import ErrorLog
    recent_errors = db.session.query(ErrorLog).order_by(ErrorLog.timestamp.desc()).limit(10).all()

    errors = []
    for error in recent_errors:
        error_data = {
            "id": error.id,
            "timestamp": error.timestamp,
            "error_type": error.error_type,
            "message": error.message[:100] + "..." if error.message and len(error.message) > 100 else error.message or "No message",
            "user_id": error.user_id,
            "request_path": error.request_path,
            "environment": error.environment
        }
        errors.append(error_data)

    return create_page(
        template="debug.html",
        title="Debug",
        users=users,
        errors=errors,
        form_error=form_error,
    )
