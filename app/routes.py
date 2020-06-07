from flask import session, render_template, redirect, url_for
from app import app
from authlib.integrations.flask_client import OAuth, OAuthError
from flask_bootstrap import Bootstrap

bootstrap = Bootstrap(app)

oauth = OAuth(app)
oauth.register(
    name = 'chpp',
    api_base_url = 'https://api.twitter.com/1.1/',
    request_token_url = app.config['REQUEST_TOKEN_PATH'],
    access_token_url = app.config['ACCESS_TOKEN_PATH'],
    authorize_url = app.config['AUTHORIZE_PATH'],
    fetch_token=lambda: session.get('token'),  # DON'T DO IT IN PRODUCTION
)

@app.errorhandler(OAuthError)
def handle_error(error):
    return render_template('error.html', error=error)

@app.route('/')
@app.route('/index')
def index():
    user = {'username': session.get('user')}
    debug = {'print': 'oauth.chpp.authorize_redirect(request_token_url)'}
    return render_template('base.html', title='Home', user=user, debug=debug)

@app.route('/player')
def player():
    return render_template('player.html', title='Player data')

@app.route('/matches')
def matches():
    return render_template('matches.html', title='Matches data')

@app.route('/training')
def training():
    return render_template('training.html', title='Training data')

@app.route('/download')
def download():
    return render_template('download.html', title='Login')

@app.route('/login')
def login():
    #redirect_uri = url_for('auth', _external=True)
    #return oauth.chpp.authorize_redirect(redirect_uri)
    return render_template('login.html', title='Login')

@app.route('/auth')
def auth():
    token = oauth.chpp.authorize_access_token()
    url = 'account/verify_credentials.json'
    resp = oauth.chpp.get(url, params={'skip_status': True})
    user = resp.json()
    # DON'T DO IT IN PRODUCTION, SAVE INTO DB IN PRODUCTION
    session['token'] = token
    session['user'] = user
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('user', None)
    return redirect('/')
