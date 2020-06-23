from datetime import datetime, timedelta
import inspect
import subprocess
import time
import traceback

from flask import render_template, request, session
from flask_bootstrap import Bootstrap
from pychpp import CHPP
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, db
from models import Group, Players, PlayerSetting, User

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
bootstrap = Bootstrap(app)

# Set consumer_key and consumer_secret provided for your app by Hattrick
consumer_key = app.config['CONSUMER_KEY']
consumer_secret = app.config['CONSUMER_SECRETS']

versionstr = subprocess.check_output(["git", "describe", "--tags"]).strip()
versionstr = versionstr.decode("utf-8").split('-')
fullversion = versionstr[0] + "." + versionstr[1] + "-" + versionstr[2]
version = versionstr[0] + "." + versionstr[1]

timenow = time.strftime('%Y-%m-%d %H:%M:%S')

default_group_order = 99

logfile = "htplanner.log"
debug_level = app.config['DEBUG_LEVEL']

# --------------------------------------------------------------------------------
# Help functions
# --------------------------------------------------------------------------------


def dprint(lvl, *args):
    if lvl <= debug_level:
        # 0 represents this line, 1 represents line at caller
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        pstr = ""
        for a in args:
            pstr = pstr + str(a)
        print(now + " " + info.function + ":" + str(info.lineno) + " " + pstr)

# --------------------------------------------------------------------------------


def debug_print(route, function, *args):
    for arg in args:
        towrite = route + " [" + function + "]: " + arg
        dprint(2, towrite)
    if debug_level >= 3:
        file = open(logfile, "a")
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        for arg in args:
            towrite = now + " " + route + " [" + function + "]: " + arg + "\n"
            file.write(towrite)
        file.close()

# --------------------------------------------------------------------------------


def count_clicks(page):
    try:
        user = (db.session.query(User)
                .filter_by(ht_id=session['current_user_id'])
                .first())
    except Exception:
        return 1

    if page == "login.html":
        User.login(user)
    elif page == "player.html":
        User.player(user)
    elif page == "matches.html":
        User.matches(user)
    elif page == "team.html":
        User.team(user)
    elif page == "training.html":
        User.training(user)
    elif page == "update.html":
        User.updatedata(user)
    else:
        return 2

    db.session.commit()

    return 0

# --------------------------------------------------------------------------------


def create_page(template, title, **kwargs):
    if 'current_user' in session:
        current_user = session['current_user']
        all_teams = session['all_teams']
        all_team_names = session['all_team_names']
    else:
        current_user = False
        all_teams = False
        all_team_names = False

    count_clicks(template)

    return render_template(
        template,
        title=title,
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        apptitle=app.config['APP_NAME'],
        current_user=current_user,
        all_teams=all_teams,
        all_team_names=all_team_names,
        **kwargs)


# --------------------------------------------------------------------------------


def player_diff(playerid, daysago):
    # Prints the changes since <date>
    datetime_object = (datetime.now() - timedelta(days=daysago)).date()

    all_teams = session['all_teams']
    all_team_names = session['all_team_names']
    for owner in all_teams:
        foundit = db.session.query(Players).filter_by(
            ht_id=playerid,
            owner=owner).order_by(text("data_date desc")).first()
        if foundit:
            theteam = owner
            latest = foundit
            oldest = (db.session
                      .query(Players)
                      .filter_by(
                          ht_id=playerid,
                          owner=owner)
                      .filter(Players.data_date >= datetime_object)
                      .order_by("data_date")
                      .first())

    if not(oldest):
        return False

    teamname = all_team_names[all_teams.index(theteam)]

    ignore_list = [
        "data_date",
        "age_days",
        "age",
        "current_team_matches",
        "tsi",
        "salary",
        "career_goals",
        "cup_goals",
        "current_team_goals",
        "league_goals",
        "loyalty",
        "cards",
        "injury_level",
        "form",
        "stamina",
        "number"
    ]

    ret = []
    thediff = {}
    for key, elem in latest:
        thediff[key] = elem
    for key, elem in oldest:
        if key not in ignore_list:
            if elem != thediff[key]:
                retstr = [teamname]
                retstr.append(oldest.first_name)
                retstr.append(oldest.last_name)
                retstr.append(key)
                retstr.append(elem)
                retstr.append(thediff[key])
                ret.append(retstr)

    return ret


# --------------------------------------------------------------------------------
# Route functions
# --------------------------------------------------------------------------------


@app.route('/')
@app.route('/index')
def index():
    f = open('app/static/changelog.txt')
    changelog = f.readlines()

    return create_page(
        template='main.html',
        title='Home',
        changelog=changelog)

# --------------------------------------------------------------------------------


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    error = ""
    if not('current_user') in session:
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
            error = "The group isn't empty, you can't delete it."
            db.session.rollback()

    group_data = (db.session.query(Group)
                  .filter_by(user_id=session['current_user_id'])
                  .order_by("order")
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
        template='profile.html',
        title='Profile',
        group_data=group_data,
        error=error)

# --------------------------------------------------------------------------------


@app.route('/login', methods=['GET', 'POST'])
def login():

    # this comes from form
    username = request.form.get('username')
    password = request.form.get('password')
    # this comes from CHPP
    oauth_verifier = request.values.get('oauth_verifier')
    oa = oauth_verifier

    if not(oa) and not(username) and session.get('current_user') is None:
        return create_page(
            template='login.html',
            title='Login / Signup')

    # Initialize CHPP instance
    chpp = CHPP(consumer_key, consumer_secret)

    # if this returns a user, then the user already exists in database
    user = db.session.query(User).filter_by(username=username).first()

    if username and user:
        if check_password_hash(user.password, password):
            dprint(1, "Login success")
            # get stuff and add in session
            session['access_key'] = user.access_key
            session['access_secret'] = user.access_secret
            session['current_user'] = user.ht_user
            session['current_user_id'] = user.ht_id
        else:
            error = "Login failed"
            return create_page(
                template='login.html',
                title='Login / Signup',
                error=error)

    else:
        if not (oauth_verifier):
            # New user, connect to CHPP to be able to create user
            dprint(1, "New user, connect to CHPP to be able to create user")

            if len(password) < 8:
                # Password too short
                error = "Password too short"
                return create_page(
                    template='login.html',
                    title='Login / Signup',
                    error=error)

            auth = chpp.get_auth(callback_url=app.config['CALLBACK_URL'],
                                 scope="")
            debug_print("login", "chpp.get_auth", auth._SOURCE_FILE)
            session['request_token'] = auth["request_token"]
            session['req_secret'] = auth["request_token_secret"]
            session['username'] = username
            session['password'] = generate_password_hash(password,
                                                         method='sha256')
            return render_template(
                '_forward.html',
                url=auth['url'])

        else:
            # New access permissions from Hattrick
            dprint(1, "New access permissions from Hattrick")
            access_token = chpp.get_access_token(
                           request_token=session['request_token'],
                           request_token_secret=session['req_secret'],
                           code=oauth_verifier)

            debug_print(
                "login",
                "chpp.get_access_token",
                access_token._SOURCE_FILE)

            session['access_key'] = access_token['key']
            session['access_secret'] = access_token['secret']

            chpp = CHPP(consumer_key,
                        consumer_secret,
                        session['access_key'],
                        session['access_secret'])

            current_user = chpp.user()
            debug_print("login", "chpp.user", current_user._SOURCE_FILE)
            session['current_user'] = current_user.username
            session['current_user_id'] = current_user.ht_id

            # check if the user exists already in the database
            ht_id = (db.session.query(User)
                     .filter_by(ht_id=current_user.ht_id)
                     .first())

            if ht_id:
                # existing ht_id in db
                # then reassign the ownership
                dprint(1, "existing ht_id in db")
                User.claimUser(
                    ht_id,
                    username=session['username'],
                    password=session['password'],
                    access_key=session['access_key'],
                    access_secret=session['access_secret'])
                db.session.commit()

            else:
                # create new user with the form data.
                dprint(1, "create new user")
                new_user = User(
                    ht_id=current_user.ht_id,
                    ht_user=current_user.username,
                    username=session['username'],
                    password=session['password'],
                    access_key=access_token['key'],
                    access_secret=access_token['secret'])
                # add the new user to the database
                db.session.add(new_user)
                db.session.commit()

    dprint(1, "UserID: ", session['current_user_id'])

    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'])

    current_user = chpp.user()
    debug_print("login", "chpp.user", current_user._SOURCE_FILE)
    all_teams = current_user._teams_ht_id
    all_team_names = []
    for id in all_teams:
        all_team_names.append(chpp.team(ht_id=id).name)
    session['all_teams'] = all_teams
    session['all_team_names'] = all_team_names

    session['team_id'] = all_teams[0]

    return create_page(
        template='login.html',
        title='Login')

# --------------------------------------------------------------------------------


@app.route('/logout')
def logout():
    session.clear()
    return create_page(
        template='logout.html',
        title='Logout')

# --------------------------------------------------------------------------------


@app.route('/update')
def update():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'])

    all_teams = session['all_teams']
    all_team_names = session['all_team_names']

    updated = {}
    changesplayers_day = []
    changesplayers_week = []

    for i in range(len(all_teams)):
        updated[all_teams[i]] = [all_team_names[i]]

    for teamid in all_teams:

        the_team = chpp.team(ht_id=teamid)
        debug_print("update", "chpp.team", the_team._SOURCE_FILE)

        try:
            dprint(2, the_team.players)
        except Exception:
            errorincode = traceback.format_exc()
            error = "Is your team playing a game?"
            errorinfo = "If this isn't the case, please report this as a "
            errorinfo += "bug. " + errorincode
            return render_template(
                'update.html',
                version=version,
                timenow=timenow,
                fullversion=fullversion,
                title='Update',
                current_user=session['current_user'],
                error=error,
                errorinfo=errorinfo,
                all_teams=session['all_teams'],
                all_team_names=session['all_team_names'])

        players = []
        for p in the_team.players:

            thisplayer = {}

            thisplayer['ht_id'] = p.ht_id
            thisplayer['first_name'] = p.first_name
            thisplayer['nick_name'] = p.nick_name
            thisplayer['last_name'] = p.last_name
            thisplayer['number'] = p.number
            thisplayer['category_id'] = p.category_id
            thisplayer['owner_notes'] = p.owner_notes
            thisplayer['age_years'] = p.age_years
            thisplayer['age_days'] = p.age_days
            thisplayer['age'] = p.age
            thisplayer['next_birthday'] = p.next_birthday
            thisplayer['arrival_date'] = p.arrival_date
            thisplayer['form'] = p.form
            thisplayer['cards'] = p.cards
            thisplayer['injury_level'] = p.injury_level
            thisplayer['statement'] = p.statement
            thisplayer['language'] = p.language
            thisplayer['language_id'] = p.language_id
            thisplayer['agreeability'] = p.agreeability
            thisplayer['aggressiveness'] = p.aggressiveness
            thisplayer['honesty'] = p.honesty
            thisplayer['experience'] = p.experience
            thisplayer['loyalty'] = p.loyalty
            thisplayer['aggressiveness'] = p.aggressiveness
            thisplayer['specialty'] = p.specialty
            thisplayer['native_country_id'] = p.native_country_id
            thisplayer['native_league_id'] = p.native_league_id
            thisplayer['native_league_name'] = p.native_league_name
            thisplayer['tsi'] = p.tsi
            thisplayer['salary'] = p.salary
            thisplayer['caps'] = p.caps
            thisplayer['caps_u20'] = p.caps_u20
            thisplayer['career_goals'] = p.career_goals
            thisplayer['career_hattricks'] = p.career_hattricks
            thisplayer['league_goals'] = p.league_goals
            thisplayer['cup_goals'] = p.cup_goals
            thisplayer['friendly_goals'] = p.friendly_goals
            thisplayer['current_team_matches'] = p.current_team_matches
            thisplayer['current_team_goals'] = p.current_team_goals
            thisplayer['national_team_id'] = p.national_team_id
            thisplayer['national_team_name'] = p.national_team_name
            thisplayer['is_transfer_listed'] = p.is_transfer_listed
            thisplayer['team_id'] = p.team_id

            thisplayer['stamina'] = p.skills['stamina']
            thisplayer['keeper'] = p.skills['keeper']
            thisplayer['defender'] = p.skills['defender']
            thisplayer['playmaker'] = p.skills['playmaker']
            thisplayer['winger'] = p.skills['winger']
            thisplayer['passing'] = p.skills['passing']
            thisplayer['scorer'] = p.skills['scorer']
            thisplayer['set_pieces'] = p.skills['set_pieces']

            thisplayer['data_date'] = time.strftime('%Y-%m-%d')

            thisplayer['owner'] = teamid

            dbplayer = db.session.query(Players).filter_by(
                ht_id=thisplayer['ht_id'],
                data_date=thisplayer['data_date']).first()

            if dbplayer:
                dprint(
                    1,
                    " - ",
                    thisplayer['first_name'],
                    thisplayer['last_name'],
                    " already exists for today.")
                db.session.delete(dbplayer)
                db.session.commit()

            newplayer = Players(thisplayer)
            db.session.add(newplayer)
            db.session.commit()
            dprint(
                1,
                "+ Added ",
                thisplayer['first_name'],
                thisplayer['last_name'],
                " for today.")

            players.append(thisplayer)

            thischanges = player_diff(thisplayer['ht_id'], 1)
            if thischanges:
                changesplayers_day.append(thischanges)
                dprint(2, thischanges)

            thischanges = player_diff(thisplayer['ht_id'], 7)
            if thischanges:
                changesplayers_week.append(thischanges)
                dprint(2, thischanges)

        # updated[teamid] = ['/player?id=' + str(teamid), 'players']
        updated[teamid].append('/player?id=' + str(teamid))
        updated[teamid].append('players')

    return create_page(
        template='update.html',
        title='Update',
        updated=updated,
        changes_day=changesplayers_day,
        changes_week=changesplayers_week)

# --------------------------------------------------------------------------------


@app.route('/debug')
def admin():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    allusers = db.session.query(User).all()
    users = []
    for user in allusers:
        thisuser = {
            'id': user.ht_id,
            'c_team': user.c_team,
            'c_training': user.c_training,
            'c_player': user.c_player,
            'c_matches': user.c_matches,
            'c_login': user.c_login,
            'c_update': user.c_update,
            'last_update': user.last_update,
            'last_usage': user.last_usage,
            'last_login': user.last_login,
            'created': user.created}
        users.append(thisuser)

    f = open('app/static/changelog.txt')
    changelog = f.readlines()

    return create_page(
        template='debug.html',
        title='Debug',
        changelog=changelog,
        users=users)

# --------------------------------------------------------------------------------


@app.route('/team')
def team():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'])

    current_user = chpp.user()
    debug_print("team", "chpp.user", current_user._SOURCE_FILE)
    all_teams = current_user._teams_ht_id

    teams = []
    for teamid in all_teams:
        dprint(1, teamid)
        this_team = chpp.team(ht_id=teamid)
        dprint(2, vars(this_team))
        teams.append(this_team.name)

    return create_page(
        template='team.html',
        title='Team')

# --------------------------------------------------------------------------------


@app.route('/player', methods=['GET', 'POST'])
def player():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    updategroup = request.form.get('updategroup')
    playerid = request.form.get('playerid')
    groupid = request.form.get('groupid')

    teamid = request.values.get('id')

    if teamid:
        teamid = int(teamid)
    else:
        teamid = request.form.get('id')

    dprint(1, teamid)

    all_teams = session['all_teams']

    if teamid not in all_teams:
        error = "Wrong teamid, try the links."
        return create_page(
            template='player.html',
            title='Players',
            error=error)

    all_team_names = session['all_team_names']
    teamname = all_team_names[all_teams.index(teamid)]

    if updategroup and playerid and groupid:
        if int(groupid) < 0:
            theconnection = (db.session
                             .query(PlayerSetting)
                             .filter_by(player_id=playerid,
                                        user_id=session['current_user_id'])
                             .first())
            db.session.delete(theconnection)
            db.session.commit()
        else:
            connection = (db.session
                          .query(PlayerSetting)
                          .filter_by(player_id=playerid,
                                     user_id=session['current_user_id'])
                          .first())
            if connection:
                (db.session
                 .query(PlayerSetting)
                 .filter_by(player_id=playerid,
                            user_id=session['current_user_id'])
                 .update({"group_id": groupid}))
                db.session.commit()
            else:
                newconnection = PlayerSetting(
                    player_id=playerid,
                    user_id=session['current_user_id'],
                    group_id=groupid)
                db.session.add(newconnection)
                db.session.commit()

    group_data = (db.session.query(Group)
                  .filter_by(user_id=session['current_user_id'])
                  .order_by("order")
                  .all())

    into_groups = (db.session
                   .query(PlayerSetting)
                   .filter_by(user_id=session['current_user_id'])
                   .all())

    dprint(3, group_data)
    dprint(3, into_groups)

    # Of each of the players you ever have owned, get the last download
    players_data = (db.session.query(Players)
                    .filter_by(owner=teamid)
                    .order_by("number")
                    .order_by("data_date")
                    .all())
    newlst = {}
    for thislist in players_data:
        newlst[thislist.ht_id] = dict(iter(thislist))
    players_now = []
    for _k, val in newlst.items():
        players_now.append(val)

    # Of each of the players you ever have owned, get the first download
    players_data = (db.session.query(Players)
                    .filter_by(owner=teamid)
                    .order_by(text("data_date desc"))
                    .all())
    newlst = {}
    for thislist in players_data:
        newlst[thislist.ht_id] = dict(iter(thislist))
    players_oldest_dict = {}
    for _k, val in newlst.items():
        players_oldest_dict[val['ht_id']] = val

    # Group the players into groups
    tmp_player = players_now
    grouped_players_now = {}
    for group in group_data:
        in_this_group = (
            [elem.player_id
             for elem in into_groups
             if elem.group_id == group.id])
        grouped_players_now[group.id] = (
            [player
             for player in tmp_player
             if player['ht_id'] in in_this_group])
        players_now = (
            [player
             for player in players_now
             if player['ht_id'] not in in_this_group])

    # Add a default group
    default_group = Group(
        user_id=0,
        name="",
        order=default_group_order,
        textcolor="#000000",
        bgcolor="#FFFFFF")
    before_default = [g for g in group_data if g.order < default_group_order]
    after_default = [g for g in group_data if g.order >= default_group_order]
    before_default.append(default_group)

    group_data = before_default + after_default

    grouped_players_now[default_group.id] = players_now

    return create_page(
        template='player.html',
        title=teamname,
        teamid=teamid,
        grouped_players=grouped_players_now,
        players=players_now,
        players_data=players_data,
        players_oldest=players_oldest_dict,
        group_data=group_data)

# --------------------------------------------------------------------------------


@app.route('/matches')
def matches():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    return create_page(
        template='matches.html',
        title='Matches')

# --------------------------------------------------------------------------------


@app.route('/training')
def training():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    return create_page(
        template='training.html',
        title='Training')
