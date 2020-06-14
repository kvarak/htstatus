from flask import session, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth, OAuthError
from pprint import pprint
from pychpp import CHPP
import time

from config import Config
from app import app, db
from models import Usage, Players

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
    session['current_user_id'] = current_user.ht_id

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
@app.route('/update')
def update():
    if session.get('current_user') is None:
        return render_template('notloggedin.html')

    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'],
                )

    the_team = chpp.team(ht_id = session['team_id'])

#    pprint(the_team.players)

    players = []
    for p in the_team.players:

        thisplayer = {}

        thisplayer['ht_id']                = p.ht_id
        thisplayer['first_name']           = p.first_name
        thisplayer['nick_name']            = p.nick_name
        thisplayer['last_name']            = p.last_name
        thisplayer['number']               = p.number
        thisplayer['category_id']          = p.category_id
        thisplayer['owner_notes']          = p.owner_notes
        thisplayer['age_years']            = p.age_years
        thisplayer['age_days']             = p.age_days
        thisplayer['age']                  = p.age
        thisplayer['next_birthday']        = p.next_birthday
        thisplayer['arrival_date']         = p.arrival_date
        thisplayer['form']                 = p.form
        thisplayer['cards']                = p.cards
        thisplayer['injury_level']         = p.injury_level
        thisplayer['statement']            = p.statement
        thisplayer['language']             = p.language
        thisplayer['language_id']          = p.language_id
        thisplayer['agreeability']         = p.agreeability
        thisplayer['aggressiveness']       = p.aggressiveness
        thisplayer['honesty']              = p.honesty
        thisplayer['experience']           = p.experience
        thisplayer['loyalty']              = p.loyalty
        thisplayer['aggressiveness']       = p.aggressiveness
        thisplayer['specialty']            = p.specialty
        thisplayer['native_country_id']    = p.native_country_id
        thisplayer['native_league_id']     = p.native_league_id
        thisplayer['native_league_name']   = p.native_league_name
        thisplayer['tsi']                  = p.tsi
        thisplayer['salary']               = p.salary
        thisplayer['caps']                 = p.caps
        thisplayer['caps_u20']             = p.caps_u20
        thisplayer['career_goals']         = p.career_goals
        thisplayer['career_hattricks']     = p.career_hattricks
        thisplayer['league_goals']         = p.league_goals
        thisplayer['cup_goals']            = p.cup_goals
        thisplayer['friendly_goals']       = p.friendly_goals
        thisplayer['current_team_matches'] = p.current_team_matches
        thisplayer['current_team_goals']   = p.current_team_goals
        thisplayer['national_team_id']     = p.national_team_id
        thisplayer['national_team_name']   = p.national_team_name
        thisplayer['is_transfer_listed']   = p.is_transfer_listed
        thisplayer['team_id']              = p.team_id

        thisplayer['stamina']    = p.skills['stamina']
        thisplayer['keeper']     = p.skills['keeper']
        thisplayer['defender']   = p.skills['defender']
        thisplayer['playmaker']  = p.skills['playmaker']
        thisplayer['winger']     = p.skills['winger']
        thisplayer['passing']    = p.skills['passing']
        thisplayer['scorer']     = p.skills['scorer']
        thisplayer['set_pieces'] = p.skills['set_pieces']

        thisplayer['data_date']  = time.strftime('%Y-%m-%d')

        thisplayer['owner']      = session['team_id']


        dbplayer = db.session.query(Players).filter_by(
            ht_id = thisplayer['ht_id'],
            data_date = thisplayer['data_date']
            ).first()

        if dbplayer:
            print (thisplayer['first_name'], thisplayer['last_name'], " already exists for today.")
        else:
            newplayer = Players(thisplayer)
            db.session.add(newplayer)
            db.session.commit()
            print ("Added ", thisplayer['first_name'], thisplayer['last_name'], " for today.")

        players.append(thisplayer)

    user = db.session.query(Usage).filter_by(user_id = session['current_user_id']).first()
    u = Usage.updatedata(user)
    db.session.commit()

    return render_template(
        'update.html',
        title = 'Update',
        current_user = session['current_user'],
        team = session['team_name'],
        )

# --------------------------------------------------------------------------------
@app.route('/admin')
def admin():
    if session.get('current_user') is None:
        return render_template('notloggedin.html')

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
            'c_update': user.c_update,
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
    if session.get('current_user') is None:
        return render_template('notloggedin.html')

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

    user = db.session.query(Usage).filter_by(user_id = session['current_user_id']).first()
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
    if session.get('current_user') is None:
        return render_template('notloggedin.html')

    players = db.session.query(Players).filter_by(owner = session['team_id']).all()

    pprint(session['team_id'])
    pprint(players)

#    for player in players:
#        olddata = db.session.query(Players).filter_by(ht_id = player.ht_id).order_by("data_date desc").first()
#        pprint(olddata.data_date)

    user = db.session.query(Usage).filter_by(user_id = session['current_user_id']).first()
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
    if session.get('current_user') is None:
        return render_template('notloggedin.html')

    user = db.session.query(Usage).filter_by(user_id = session['current_user_id']).first()
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
    if session.get('current_user') is None:
        return render_template('notloggedin.html')

    user = db.session.query(Usage).filter_by(user_id = session['current_user_id']).first()
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
