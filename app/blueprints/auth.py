"""Authentication routes blueprint for HT Status application."""

from flask import Blueprint, make_response, redirect, render_template, request, session
from pychpp import CHPP
from werkzeug.security import check_password_hash, generate_password_hash

from app.utils import create_page, dprint
from models import User

# Create Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

# These will be set by setup_auth_blueprint()
app = None
db = None
consumer_key = None
consumer_secret = None


def setup_auth_blueprint(app_instance, db_instance, ck, cs):
    """Initialize authentication blueprint with app and db instances."""
    global app, db, consumer_key, consumer_secret
    app = app_instance
    db = db_instance
    consumer_key = ck
    consumer_secret = cs


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login and Hattrick OAuth authentication."""
    # Return early if already logged in
    if session.get('current_user'):
        return redirect('/')

    # Handle OAuth callback
    oauth_verifier = request.args.get('oauth_verifier')
    if oauth_verifier:
        return handle_oauth_callback(oauth_verifier)

    # Handle GET request - show login form
    if request.method == 'GET':
        return create_page(
            template='login.html',
            title='Login / Signup')

    # Handle POST request (form submission)
    username = request.form.get('username')
    password = request.form.get('password')

    # Validate form data
    if not username:
        return create_page(
            template='login.html',
            title='Login / Signup',
            error='Username is required')

    if not password:
        return create_page(
            template='login.html',
            title='Login / Signup',
            error='Password is required')

    if len(password) < 8:
        return create_page(
            template='login.html',
            title='Login / Signup',
            error='Password must be at least 8 characters long')

    # Check for existing user
    existing_user = User.query.filter_by(username=username).first()

    if existing_user and check_password_hash(existing_user.password, password):
        # Existing user login
        if existing_user.access_key and existing_user.access_secret:
            # User has OAuth tokens - log them in directly
            session['access_key'] = existing_user.access_key
            session['access_secret'] = existing_user.access_secret
            session['current_user'] = existing_user.ht_user
            session['current_user_id'] = existing_user.ht_id

            # Setup team data
            try:
                chpp = CHPP(consumer_key, consumer_secret,
                           session['access_key'], session['access_secret'])
                current_user = chpp.user()
                all_teams = current_user._teams_ht_id
                all_team_names = []
                for id in all_teams:
                    all_team_names.append(chpp.team(ht_id=id).name)
                session['all_teams'] = all_teams
                session['all_team_names'] = all_team_names
                session['team_id'] = all_teams[0]
            except Exception as e:
                dprint(1, f"Error setting up team data: {e}")

            return redirect('/')
        else:
            # Need to get OAuth tokens for existing user
            session['username'] = username
            session['password'] = generate_password_hash(password, method='sha256')
            return start_oauth_flow()

    # New user registration or invalid login
    if existing_user:
        # Wrong password
        return create_page(
            template='login.html',
            title='Login / Signup',
            error='Invalid username or password')

    # New user - start OAuth flow
    session['username'] = username
    session['password'] = generate_password_hash(password, method='sha256')
    return start_oauth_flow()


def start_oauth_flow():
    """Start OAuth flow with Hattrick."""
    chpp = CHPP(consumer_key, consumer_secret)
    auth = chpp.get_auth(callback_url=app.config['CALLBACK_URL'], scope="")

    session['request_token'] = auth["request_token"]
    session['req_secret'] = auth["request_token_secret"]

    return render_template('_forward.html', url=auth['url'])


def handle_oauth_callback(oauth_verifier):
    """Handle OAuth callback after authorization."""
    try:
        # Get access tokens
        chpp = CHPP(consumer_key, consumer_secret)
        access_token = chpp.get_access_token(
            request_token=session['request_token'],
            request_token_secret=session['req_secret'],
            code=oauth_verifier)

        session['access_key'] = access_token['key']
        session['access_secret'] = access_token['secret']

        # Get user from Hattrick
        chpp = CHPP(consumer_key, consumer_secret,
                   session['access_key'], session['access_secret'])
        current_user = chpp.user()

        session['current_user'] = current_user.username
        session['current_user_id'] = current_user.ht_id

        # Check if user exists in database
        existing_user = User.query.filter_by(ht_id=current_user.ht_id).first()

        if existing_user:
            # Update existing user with new tokens
            User.claimUser(
                existing_user,
                username=session.get('username', current_user.username),
                password=session.get('password', ''),
                access_key=session['access_key'],
                access_secret=session['access_secret'])
        else:
            # Create new user
            new_user = User(
                ht_id=current_user.ht_id,
                ht_user=current_user.username,
                username=session.get('username', current_user.username),
                password=session.get('password', ''),
                access_key=access_token['key'],
                access_secret=access_token['secret'])
            db.session.add(new_user)

        db.session.commit()

        # Setup team data
        all_teams = current_user._teams_ht_id
        all_team_names = []
        for id in all_teams:
            all_team_names.append(chpp.team(ht_id=id).name)
        session['all_teams'] = all_teams
        session['all_team_names'] = all_team_names
        session['team_id'] = all_teams[0]

        return redirect('/')

    except Exception as e:
        dprint(1, f"OAuth callback error: {e}")
        return create_page(
            template='login.html',
            title='Login / Signup',
            error='OAuth authentication failed. Please try again.')

@auth_bp.route('/logout')
def logout():
    """Handle user logout and session clearing."""
    dprint(1, f"Logging out user: {session.get('current_user', 'Unknown')}")

    # Clear session first
    session.clear()

    # Force explicit redirect
    response = make_response()
    response.status_code = 302
    response.headers['Location'] = '/login'
    return response
