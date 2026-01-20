"""Main and admin routes blueprint for HT Status application."""

import re
from datetime import date

from dateutil.relativedelta import relativedelta
from flask import Blueprint, render_template, request, session
from sqlalchemy import text

from app.routes_bp import create_page, diff_month, dprint
from models import Group, PlayerSetting, User

# Create Blueprint for main routes
main_bp = Blueprint('main', __name__)

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


@main_bp.route('/')
@main_bp.route('/index')
def index():
    """Display home page with user and team statistics."""
    allusers = db.session.query(User).all()
    time1m = date.today() - relativedelta(months=1)
    activeusers = db.session.query(User).filter(User.last_usage > time1m).all()

    if ('current_user') not in session:
        return create_page(
            template='main.html',
            title='Home',
            usercount=len(allusers),
            activeusers=len(activeusers))

    all_teams = session['all_teams']
    all_team_names = session['all_team_names']
    updated = {}

    for i in range(len(all_teams)):
        updated[all_teams[i]] = all_team_names[i]

    dprint(2, updated)

    thisuserdata = (db.session.query(User)
                    .filter_by(ht_id=session['current_user_id'])
                    .first())
    thisuser = {
        'id': thisuserdata.ht_id,
        'name': thisuserdata.ht_user,
        'role': thisuserdata.role,
        'c_team': thisuserdata.c_team,
        'c_training': thisuserdata.c_training,
        'c_player': thisuserdata.c_player,
        'c_matches': thisuserdata.c_matches,
        'c_login': thisuserdata.c_login,
        'c_update': thisuserdata.c_update,
        'last_update': thisuserdata.last_update,
        'last_usage': thisuserdata.last_usage,
        'last_login': thisuserdata.last_login,
        'created': thisuserdata.created}

    dprint(2, thisuser)

    return create_page(
        template='main.html',
        title='Home',
        thisuser=thisuser,
        usercount=len(allusers),
        activeusers=len(activeusers),
        updated=updated)


@main_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """Handle user settings for player groups and display columns."""
    error = ""
    if ('current_user') not in session:
        return render_template(
            '_forward.html',
            url='/')

    groupname = request.form.get('groupname')
    grouporder = request.form.get('grouporder')
    addgroup = request.form.get('addgroup')
    updategroup = request.form.get('updategroup')
    deletegroup = request.form.get('deletegroup')
    groupid = request.form.get('groupid')
    textcolor = request.form.get('textcolor')
    bgcolor = request.form.get('bgcolor')
    if not textcolor:
        textcolor = "#000000"
    if not bgcolor:
        bgcolor = "#FFFFFF"

    user = (db.session.query(User)
            .filter_by(ht_id=session['current_user_id'])
            .first())
    columns = User.getColumns(user)
    if len(columns) == 0:
        columns = defaultcolumns

    columnsorder = request.form.get('columnsorder')
    setcolumnsdefault = request.form.get('defaultcolumns')
    showdefaultcolumns = False
    if columnsorder and columnsorder != "empty":
        columns = []
        columngroups = columnsorder.split('Hidden columns')
        # Columns to show
        for r in columngroups[0].split('<div'):
            r = r.strip()
            if r == "":
                continue
            key = re.search('id="(.+?)"', r)
            text_match = re.search('>(.+?)</div>', r)
            if key:
                columns.append((text_match.group(1), key.group(1)))
        User.updateColumns(user, columns)
        db.session.commit()
    elif setcolumnsdefault == "defaultcolumns":
        columns = defaultcolumns
        showdefaultcolumns = True

    hiddencolumns = [item for item in allcolumns if item not in columns]

    if addgroup:
        if groupname and grouporder:
            newgroup = Group(
                user_id=session['current_user_id'],
                name=groupname,
                order=grouporder,
                textcolor=textcolor,
                bgcolor=bgcolor)
            db.session.add(newgroup)
            db.session.commit()
        else:
            error = "Groups need both name and order."

    elif updategroup and groupid:
        if groupname and grouporder:
            (db.session
             .query(Group)
             .filter_by(id=groupid)
             .update({"name": groupname,
                      "order": grouporder,
                      "textcolor": textcolor,
                      "bgcolor": bgcolor}))
            db.session.commit()
        else:
            error = "Groups need both name and order."

    elif deletegroup and groupid:
        try:
            thegroup = (db.session
                        .query(Group)
                        .filter_by(id=groupid)
                        .first())
            db.session.delete(thegroup)
            db.session.commit()
        except Exception:
            error = "The group wasn't empty, removed all players from that group."
            db.session.rollback()

            # remove all connected players
            connections = (db.session.query(PlayerSetting)
                           .filter_by(group_id=groupid,
                                      user_id=session['current_user_id'])
                           .all())
            dprint(2, connections)

            for playersetting in connections:
                connection = (db.session
                              .query(PlayerSetting)
                              .filter_by(player_id=playersetting.player_id,
                                         user_id=session['current_user_id'])
                              .first())
                db.session.delete(connection)
                db.session.commit()

            thegroup = (db.session
                        .query(Group)
                        .filter_by(id=groupid)
                        .first())
            db.session.delete(thegroup)
            db.session.commit()

    group_data = (db.session.query(Group)
                  .filter_by(user_id=session['current_user_id'])
                  .order_by(Group.order)
                  .all())

    # Add a default group
    default_group = Group(
        user_id=0,
        name="<default>",
        order=default_group_order,
        textcolor="#000000",
        bgcolor="#FFFFFF")
    before_default = [g for g in group_data if g.order < default_group_order]
    after_default = [g for g in group_data if g.order >= default_group_order]
    before_default.append(default_group)

    group_data = before_default + after_default

    return create_page(
        template='settings.html',
        title='Settings',
        columns=columns,
        hiddencolumns=hiddencolumns,
        showdefaultcolumns=showdefaultcolumns,
        group_data=group_data,
        error=error)


@main_bp.route('/debug', methods=['GET', 'POST'])
def admin():
    """Admin dashboard for user management."""
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/')

    error = ""

    try:
        user = (db.session.query(User)
                .filter_by(ht_id=session['current_user_id'])
                .first())
        role = User.getRole(user)
        if role != "Admin":
            return render_template(
                '_forward.html',
                url='/')
    except Exception:
        return render_template(
            '_forward.html',
            url='/')

    adminchecked = request.form.get('admin')
    userid = request.form.get('userid')

    dprint(2, "Checkbox: ", adminchecked)
    dprint(2, userid)

    if userid:
        try:
            user = (db.session.query(User)
                    .filter_by(ht_id=userid)
                    .first())
            updateto = "Admin" if adminchecked else "User"

            dprint(2, updateto)

            User.setRole(user, updateto)
            db.session.commit()

        except Exception:
            error = "couldn't change user"

    allusers = db.session.query(User).order_by(text('last_usage desc')).all()
    users = []
    for user in allusers:
        if (user.last_update - user.created).days < 1:
            active_time = "< 1 day"
        elif (user.last_update - user.created).days == 1:
            active_time = "1 day"
        elif diff_month(user.last_update, user.created) < 2:
            active_time = str((user.last_update - user.created).days) + " days"
        else:
            active_time = (str(diff_month(user.last_update, user.created)) +
                           " months")

        thisuser = {
            'id': user.ht_id,
            'name': user.ht_user,
            'role': user.role,
            'c_team': user.c_team,
            'c_training': user.c_training,
            'c_player': user.c_player,
            'c_matches': user.c_matches,
            'c_login': user.c_login,
            'c_update': user.c_update,
            'last_update': user.last_update,
            'last_usage': user.last_usage,
            'last_login': user.last_login,
            'created': user.created,
            'active_time': active_time}
        users.append(thisuser)

    return create_page(
        template='debug.html',
        title='Debug',
        users=users,
        error=error)
