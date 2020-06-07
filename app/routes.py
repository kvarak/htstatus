from flask import session, render_template, redirect, url_for, request
from app import app
from authlib.integrations.flask_client import OAuth, OAuthError
from flask_bootstrap import Bootstrap
from pychpp import CHPP

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

bootstrap = Bootstrap(app)

#oauth = OAuth(app)
#oauth.register(
#    name = 'chpp',
#    api_base_url = 'https://api.twitter.com/1.1/',
#    request_token_url = app.config['REQUEST_TOKEN_PATH'],
#    access_token_url = app.config['ACCESS_TOKEN_PATH'],
#    authorize_url = app.config['AUTHORIZE_PATH'],
#    fetch_token = lambda: session.get('token'),  # DON'T DO IT IN PRODUCTION
#)

# Set consumer_key and consumer_secret provided for your app by Hattrick
consumer_key = app.config['CONSUMER_KEY']
consumer_secret = app.config['CONSUMER_SECRETS']

# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------

#@app.before_first_request
#def do_something_only_once():
    # Initialize CHPP instance
#    chpp = CHPP(consumer_key, consumer_secret)

    # Get url, request_token and request_token_secret to request API access
    # You can set callback_url and scope
#    auth = chpp.get_auth(callback_url = app.config['CALLBACK_URL'], scope = "")

    # auth['url'] contains the url to which the user can grant the application
    # access to the Hattrick API
    # Once the user has entered their credentials,
    # a code is returned by Hattrick (directly or to the given callback url)

# --------------------------------------------------------------------------------
#@app.errorhandler(OAuthError)
#def handle_error(error):
#    return render_template('error.html', error=error)

# --------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():
    user = {'username': session.get('user')}
    if 'current_user' in session:
        current_user = session['current_user']
    else:
        current_user = False
    return render_template('main.html', title='Home', apptitle = app.config['APP_NAME'], current_user = current_user)

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
        return render_template('login.html', title = 'Login page', apptitle = app.config['APP_NAME'], accesslink = auth['url'])

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

    # Now you can use chpp methods to get datas from Hattrick API
    # For example :
    current_user = chpp.user()

    all_teams = current_user.teams

    best_team_ever = chpp.team(ht_id=9838)

    session['current_user'] = current_user.username

    return render_template('login.html', title = 'Login page', apptitle = app.config['APP_NAME'], team = best_team_ever, current_user = session['current_user'])

# --------------------------------------------------------------------------------
@app.route('/team')
def team():
    # Once you have obtained access_token for a user
    # You can use it to call Hattrick API
    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'],
                )

    return render_template('team.html', title='Team data', current_user = session['current_user'])

# --------------------------------------------------------------------------------
@app.route('/player')
def player():
    return render_template('player.html', title='Player data', current_user = session['current_user'])

# --------------------------------------------------------------------------------
@app.route('/matches')
def matches():
    return render_template('matches.html', title='Matches data', current_user = session['current_user'])

# --------------------------------------------------------------------------------
@app.route('/training')
def training():
    return render_template('training.html', title='Training data', current_user = session['current_user'])

# --------------------------------------------------------------------------------
@app.route('/trainingcycle')
def trainingcycle():
    return render_template('trainingcycle.html', title='Training cycles', current_user = session['current_user'])

# --------------------------------------------------------------------------------
@app.route('/basiccycle')
def basiccycle():
    return render_template('basiccycle.html', title='Basic cycle', current_user = session['current_user'])

# --------------------------------------------------------------------------------
@app.route('/complexcycle')
def complexcycle():
    return render_template('complexcycle.html', title='Complex cycle', current_user = session['current_user'])

# --------------------------------------------------------------------------------
#@app.route('/auth')
#def auth():
#    token = oauth.chpp.authorize_access_token()
#    url = 'account/verify_credentials.json'
#    resp = oauth.chpp.get(url, params={'skip_status': True})
#    user = resp.json()
#    # DON'T DO IT IN PRODUCTION, SAVE INTO DB IN PRODUCTION
#    session['token'] = token
#    session['user'] = user
#    return redirect('/')

# --------------------------------------------------------------------------------
#@app.route('/logout')
#def logout():
#    session.pop('token', None)
#    session.pop('user', None)
#    return redirect('/')
