from flask import session, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth, OAuthError
from pprint import pprint
from pychpp import CHPP

from config import Config
from app import app, db
from models import Usage

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

bootstrap = Bootstrap(app)

# Set consumer_key and consumer_secret provided for your app by Hattrick
consumer_key = app.config['CONSUMER_KEY']
consumer_secret = app.config['CONSUMER_SECRETS']

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():
    current_user = session['current_user'] if 'current_user' in session else False
    team_name = session['team_name'] if 'team_name' in session else False
    debug1 = ""
    debug2 = ""

    return render_template(
        'main.html',
        title = 'Home',
        apptitle = app.config['APP_NAME'],
        current_user = current_user,
        team = team_name,
        debug1 = debug1,
        debug2 = debug2,
        )

# --------------------------------------------------------------------------------
@app.route('/login')
def login():

    # Initialize CHPP instance
    chpp = CHPP(consumer_key, consumer_secret)

    oauth_verifier = request.values.get('oauth_verifier')

    if not(oauth_verifier):

        # Get url, request_token and request_token_secret to request API access
        # You can set callback_url and scope
        auth = chpp.get_auth(callback_url = app.config['CALLBACK_URL'], scope = "")
        session['request_token'] = auth["request_token"]
        session['request_token_secret'] = auth["request_token_secret"]

        # auth['url'] contains the url to which the user can grant the application
        # access to the Hattrick API
        # Once the user has entered their credentials,
        # a code is returned by Hattrick (directly or to the given callback url)
        return render_template(
            'login.html',
            title = 'Login page',
            apptitle = app.config['APP_NAME'],
            accesslink = auth['url'],
            )

    # Get access token from Hattrick
    # access_token['key'] and access_token['secret'] have to be stored
    # in order to be used later by the app
    access_token = chpp.get_access_token(
                    request_token = session['request_token'],
                    request_token_secret = session['request_token_secret'],
                    code = oauth_verifier,
                    )

    session['access_key']    = access_token['key']
    session['access_secret'] = access_token['secret']

    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'],
                )

    current_user = chpp.user()
    session['current_user'] = current_user.username

    all_teams = current_user._teams_ht_id
    session['team_id'] = all_teams[0]
    session['team_name'] = chpp.team(ht_id = all_teams[0]).name

    notnew = db.session.query(Usage).filter_by(user_id = current_user.ht_id).first()
    if not notnew:
        u = Usage(current_user.ht_id)
        db.session.add(u)
        db.session.commit()
    else:
        user = db.session.query(Usage).filter_by(user_id = current_user.ht_id).first()
        u = Usage.login(user)
        db.session.commit()

    return render_template(
        'login.html',
        title = 'Login',
        apptitle = app.config['APP_NAME'],
        current_user = session['current_user'],
        team = session['team_name'],
        )

# --------------------------------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html', title='Logout')

# --------------------------------------------------------------------------------
@app.route('/admin')
def admin():
    allusers = db.session.query(Usage).all()

    users = []

    for user in allusers:
        thisuser = {
            'id': user.user_id,
            'c_team': user.c_team,
            'c_training': user.c_training,
            'c_player': user.c_player,
            'c_matches': user.c_matches,
            'c_login': user.c_login,
            'last_login': user.last_login,
            'last_usage': user.last_usage,
            }
        users.append(thisuser)

    return render_template(
        'admin.html',
        title = 'Admin',
        current_user = session['current_user'],
        team = session['team_name'],
        users = users,
        )

# --------------------------------------------------------------------------------
@app.route('/team')
def team():
    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'],
                )

    current_user = chpp.user()
    all_teams = current_user._teams_ht_id

    teams = []
    for teamid in all_teams:
        print(teamid)
        this_team = chpp.team(ht_id = teamid)
        pprint(vars(this_team))
        teams.append(this_team.name)

    user = db.session.query(Usage).filter_by(user_id = current_user.ht_id).first()
    u = Usage.team(user)
    db.session.commit()

    return render_template(
        'team.html',
        title = 'Team',
        current_user = session['current_user'],
        teams = teams,
        team = session['team_name'],
        )

# --------------------------------------------------------------------------------
@app.route('/player')
def player():
    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'],
                )

    the_team = chpp.team(ht_id = session['team_id'])

    pprint(the_team.players)

    players = []
    for p in the_team.players:
        skills = [
            int(p.skills['stamina']),
            int(p.skills['keeper']),
            int(p.skills['defender']),
            int(p.skills['playmaker']),
            int(p.skills['winger']),
            int(p.skills['passing']),
            int(p.skills['scorer']),
            int(p.skills['set_pieces']),
        ]
        thisplayer = {
            'name': p.first_name + " " + p.last_name,
            'age': p.age_years,
            'country': p.language_id,
            'number': p.number if p.number < 100 else "-",
            'skills': skills,
            }
        players.append(thisplayer)

    current_user = chpp.user()
    user = db.session.query(Usage).filter_by(user_id = current_user.ht_id).first()
    u = Usage.player(user)
    db.session.commit()

    return render_template(
        'player.html',
        title = 'Players',
        current_user = session['current_user'],
        team = session['team_name'],
        players = players,
        )

# --------------------------------------------------------------------------------
@app.route('/matches')
def matches():
    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'],
                )

    current_user = chpp.user()
    user = db.session.query(Usage).filter_by(user_id = current_user.ht_id).first()
    u = Usage.matches(user)
    db.session.commit()

    return render_template(
        'matches.html',
        title = 'Matches',
        current_user = session['current_user'],
        team = session['team_name'],
        )

# --------------------------------------------------------------------------------
@app.route('/training')
def training():
    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'],
                )

    current_user = chpp.user()
    user = db.session.query(Usage).filter_by(user_id = current_user.ht_id).first()
    u = Usage.training(user)
    db.session.commit()

    return render_template(
        'training.html',
        title = 'Training',
        current_user = session['current_user'],
        team = session['team_name'],
        )

# --------------------------------------------------------------------------------
@app.route('/trainingcycle')
def trainingcycle():
    return render_template(
        'trainingcycle.html',
        title = 'Training cycles',
        )

# --------------------------------------------------------------------------------
@app.route('/basiccycle')
def basiccycle():
    return render_template(
        'basiccycle.html',
        title = 'Basic cycle',
        )

# --------------------------------------------------------------------------------
@app.route('/complexcycle')
def complexcycle():
    return render_template(
        'complexcycle.html',
        title = 'Complex cycle',
        )
