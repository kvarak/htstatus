from pprint import pprint
import subprocess
import time
import traceback

from flask import render_template, request, session
from flask_bootstrap import Bootstrap
from pychpp import CHPP
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, db
from models import Players, User

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

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------


@app.route('/')
@app.route('/index')
def index():
    if 'current_user' in session:
        current_user = session['current_user']
    else:
        False
    team_name = session['team_name'] if 'team_name' in session else False
    debug1 = ""
    debug2 = ""

    return render_template(
        'main.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        title='Home',
        apptitle=app.config['APP_NAME'],
        current_user=current_user,
        team=team_name,
        debug1=debug1,
        debug2=debug2)

# --------------------------------------------------------------------------------


@app.route('/profile')
def profile():
    if 'current_user' in session:
        current_user = session['current_user']
    else:
        False
    team_name = session['team_name'] if 'team_name' in session else False
    debug1 = ""
    debug2 = ""

    return render_template(
        'profile.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        title='Profile',
        apptitle=app.config['APP_NAME'],
        current_user=current_user,
        team=team_name,
        debug1=debug1,
        debug2=debug2)

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
        return render_template(
            'login.html',
            version=version,
            timenow=timenow,
            fullversion=fullversion,
            title='Login / Signup',
            apptitle=app.config['APP_NAME'])

    # Initialize CHPP instance
    chpp = CHPP(consumer_key, consumer_secret)

    # if this returns a user, then the user already exists in database
    user = db.session.query(User).filter_by(username=username).first()

    if username and user:
        if check_password_hash(user.password, password):
            print("Login success")
            # get stuff and add in session
            session['access_key'] = user.access_key
            session['access_secret'] = user.access_secret
            session['current_user'] = user.ht_user
            session['current_user_id'] = user.ht_id
        else:
            print("Login failed")
            return render_template(
                'login.html',
                version=version,
                timenow=timenow,
                fullversion=fullversion,
                title='Login / Signup',
                apptitle=app.config['APP_NAME'],
                error='Login failed')

    else:
        if not (oauth_verifier):
            # New user, connect to CHPP to be able to create user
            print("New user, connect to CHPP to be able to create user")

            if len(password) < 8:
                # Password too short
                print("Password too short")
                return render_template(
                    'login.html',
                    version=version,
                    timenow=timenow,
                    fullversion=fullversion,
                    title='Login / Signup',
                    apptitle=app.config['APP_NAME'],
                    error='Password too short')

            auth = chpp.get_auth(callback_url=app.config['CALLBACK_URL'],
                                 scope="")
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
            print("New access permissions from Hattrick")
            access_token = chpp.get_access_token(
                           request_token=session['request_token'],
                           request_token_secret=session['req_secret'],
                           code=oauth_verifier)

            session['access_key'] = access_token['key']
            session['access_secret'] = access_token['secret']

            chpp = CHPP(consumer_key,
                        consumer_secret,
                        session['access_key'],
                        session['access_secret'])

            current_user = chpp.user()
            session['current_user'] = current_user.username
            session['current_user_id'] = current_user.ht_id

            # check if the user exists already in the database
            ht_id = (db.session.query(User)
                     .filter_by(ht_id=current_user.ht_id)
                     .first())

            if ht_id:
                # existing ht_id in db
                # then reassign the ownership
                print("existing ht_id in db")
                User.claimUser(
                    ht_id,
                    username=session['username'],
                    password=session['password'],
                    access_key=session['access_key'],
                    access_secret=session['access_secret'])
                db.session.commit()

            else:
                # create new user with the form data.
                print("create new user")
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

    print("UserID: ", session['current_user_id'])

    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'])

    current_user = chpp.user()
    all_teams = current_user._teams_ht_id
    session['team_id'] = all_teams[0]
    session['team_name'] = chpp.team(ht_id=all_teams[0]).name

    user = db.session.query(User).filter_by(ht_id=current_user.ht_id).first()
    User.login(user)
    db.session.commit()

    return render_template(
        'login.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        title='Login',
        apptitle=app.config['APP_NAME'],
        current_user=session['current_user'],
        team=session['team_name'])

# --------------------------------------------------------------------------------


@app.route('/logout')
def logout():
    session.clear()
    return render_template(
        'logout.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
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

    the_team = chpp.team(ht_id=session['team_id'])

    try:
        pprint(the_team.players)
    except Exception:
        errorincode = traceback.format_exc()
        error = "Something went wrong, couldn't download player data."
        errorinfo = "Most likely your team is playing a game."
        errorinfo += "If this isn't the case, please report this as a"
        errorinfo += "bug.<br><br>" + errorincode
        return render_template(
            'update.html',
            version=version,
            timenow=timenow,
            fullversion=fullversion,
            title='Update',
            current_user=session['current_user'],
            team=session['team_name'],
            error=error,
            errorinfo=errorinfo)

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

        thisplayer['owner'] = session['team_id']

        dbplayer = db.session.query(Players).filter_by(
            ht_id=thisplayer['ht_id'],
            data_date=thisplayer['data_date']).first()

        if dbplayer:
            print(" - ",
                  thisplayer['first_name'],
                  thisplayer['last_name'],
                  " already exists for today.")
            db.session.delete(dbplayer)
            db.session.commit()

        newplayer = Players(thisplayer)
        db.session.add(newplayer)
        db.session.commit()
        print("+ Added ",
              thisplayer['first_name'],
              thisplayer['last_name'],
              " for today.")

        players.append(thisplayer)

    user = (db.session.query(User)
            .filter_by(ht_id=session['current_user_id'])
            .first())
    User.updatedata(user)
    db.session.commit()

    return render_template(
        'update.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        title='Update',
        current_user=session['current_user'],
        team=session['team_name'])

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

    return render_template(
        'debug.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        title='Debug',
        current_user=session['current_user'],
        team=session['team_name'],
        users=users,
        changelog=changelog)

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
    all_teams = current_user._teams_ht_id

    teams = []
    for teamid in all_teams:
        print(teamid)
        this_team = chpp.team(ht_id=teamid)
        pprint(vars(this_team))
        teams.append(this_team.name)

    user = (db.session.query(User)
            .filter_by(ht_id=session['current_user_id'])
            .first())
    User.team(user)
    db.session.commit()

    return render_template(
        'team.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        title='Team',
        current_user=session['current_user'],
        teams=teams,
        team=session['team_name'])

# --------------------------------------------------------------------------------


@app.route('/player')
def player():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    # Of each of the players you ever have owned, get the last download
    players_data = (db.session.query(Players)
                    .filter_by(owner=session['team_id'])
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
                    .filter_by(owner=session['team_id'])
                    .order_by(text("data_date desc"))
                    .all())
    newlst = {}
    for thislist in players_data:
        newlst[thislist.ht_id] = dict(iter(thislist))
    players_oldest_dict = {}
    for _k, val in newlst.items():
        players_oldest_dict[val['ht_id']] = val

    user = (db.session.query(User)
            .filter_by(ht_id=session['current_user_id'])
            .first())
    User.player(user)
    db.session.commit()

    return render_template(
        'player.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        title='Players',
        current_user=session['current_user'],
        team=session['team_name'],
        players=players_now,
        players_data=players_data,
        players_oldest=players_oldest_dict)

# --------------------------------------------------------------------------------


@app.route('/matches')
def matches():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    user = (db.session.query(User)
            .filter_by(ht_id=session['current_user_id'])
            .first())
    User.player(user)
    db.session.commit()

    return render_template(
        'matches.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        title='Matches',
        current_user=session['current_user'],
        team=session['team_name'])

# --------------------------------------------------------------------------------


@app.route('/training')
def training():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    user = (db.session.query(User)
            .filter_by(ht_id=session['current_user_id'])
            .first())
    User.player(user)
    db.session.commit()

    return render_template(
        'training.html',
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        title='Training',
        current_user=session['current_user'],
        team=session['team_name'])
