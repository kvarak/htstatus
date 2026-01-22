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
    dprint(1, f"Found existing user: {existing_user.username if existing_user else 'None'}")

    # Handle password verification with migration support
    password_valid = False
    needs_migration = False

    if existing_user:
        dprint(1, f"Password format check - starts with MIGRATION_REQUIRED: {existing_user.password.startswith('MIGRATION_REQUIRED:')}")
        dprint(1, f"Password format check - starts with sha256: {existing_user.password.startswith('sha256$')}")
        dprint(1, f"Password format check - starts with scrypt: {existing_user.password.startswith('scrypt:')}")

        if (existing_user.password.startswith('MIGRATION_REQUIRED:') or
            existing_user.password.startswith('sha256$')):
            # User has an old SHA256 hash that needs migration
            needs_migration = True
            dprint(1, f"User {username} has legacy password hash requiring migration")
            # For migration users, we can't verify the old password
            # They need to either use OAuth or reset their password
        else:
            # Normal password verification for modern hashes (scrypt, pbkdf2)
            dprint(1, "Attempting normal password verification for modern hash")
            try:
                password_valid = check_password_hash(existing_user.password, password)
                dprint(1, f"Password verification result: {password_valid}")
            except ValueError as e:
                dprint(1, f"Password verification failed for {username}: {e}")
                # This might be another unsupported hash format, treat as migration needed
                needs_migration = True

    if existing_user and password_valid:
        # Existing user login with valid password
        dprint(1, f"Password validation successful for user: {username}")
        if existing_user.access_key and existing_user.access_secret:
            # User has OAuth tokens - log them in directly
            dprint(1, "User has valid OAuth tokens, logging in directly")
            session['access_key'] = existing_user.access_key
            session['access_secret'] = existing_user.access_secret
            session['current_user'] = existing_user.ht_user
            session['current_user_id'] = existing_user.ht_id

            # Setup team data from Hattrick API using OAuth tokens
            dprint(1, "Setting up team data for logged-in user")
            try:
                chpp = CHPP(consumer_key, consumer_secret,
                           existing_user.access_key, existing_user.access_secret)
                current_user = chpp.user()
                all_teams = current_user._teams_ht_id
                all_team_names = []
                for team_id in all_teams:
                    try:
                        team_name = chpp.team(ht_id=team_id).name
                        all_team_names.append(team_name)
                    except Exception as e:
                        dprint(1, f"Could not fetch team name for {team_id}: {e}")
                        all_team_names.append(f"Team {team_id}")

                session['all_teams'] = all_teams
                session['all_team_names'] = all_team_names
                session['team_id'] = all_teams[0]
                dprint(1, f"Team setup complete: {all_teams}")
            except Exception as e:
                dprint(1, f"Error fetching teams from Hattrick: {e}")
                # Fallback to stored user ID (this is wrong but prevents crash)
                session['all_teams'] = [existing_user.ht_id]
                session['all_team_names'] = ['Team']
                session['team_id'] = existing_user.ht_id

            return redirect('/')
        else:
            # Need to get OAuth tokens for existing user
            session['username'] = username
            session['password'] = generate_password_hash(password)
            return start_oauth_flow()

    # Handle authentication failures and migration cases
    if existing_user:
        if needs_migration:
            # User has an old SHA256 password that can't be verified
            if existing_user.access_key and existing_user.access_secret:
                # Try to use existing OAuth tokens
                try:
                    chpp = CHPP(consumer_key, consumer_secret,
                               existing_user.access_key, existing_user.access_secret)
                    current_user = chpp.user()

                    # DEBUG: Check what team data is available
                    dprint(1, f"DEBUG: current_user attributes = {[x for x in dir(current_user) if not x.startswith('_')]}")
                    dprint(1, f"DEBUG: current_user._teams_ht_id = {current_user._teams_ht_id if hasattr(current_user, '_teams_ht_id') else 'NO ATTRIBUTE'}")
                    if hasattr(current_user, 'teams'):
                        dprint(1, f"DEBUG: current_user.teams = {current_user.teams}")

                    # OAuth tokens still valid - log them in and offer password reset
                    session['access_key'] = existing_user.access_key
                    session['access_secret'] = existing_user.access_secret
                    session['current_user'] = existing_user.ht_user
                    session['current_user_id'] = existing_user.ht_id
                    session['password_migration_needed'] = True

                    # Setup team data
                    all_teams = current_user._teams_ht_id
                    all_team_names = []
                    for id in all_teams:
                        all_team_names.append(chpp.team(ht_id=id).name)
                    session['all_teams'] = all_teams
                    session['all_team_names'] = all_team_names
                    session['team_id'] = all_teams[0]

                    return redirect('/?migration_notice=true')

                except Exception as e:
                    dprint(1, f"OAuth tokens expired for migration user: {e}")
                    # OAuth tokens expired - need to re-authenticate

            return create_page(
                template='login.html',
                title='Login / Signup',
                error='Your password needs to be updated for security. Please <a href="/login/oauth">re-authenticate with Hattrick</a> to continue.')
        else:
            # Wrong password for normal user
            return create_page(
                template='login.html',
                title='Login / Signup',
                error='Invalid username or password')

    # New user - start OAuth flow
    session['username'] = username
    session['password'] = generate_password_hash(password)
    return start_oauth_flow()


def start_oauth_flow():
    """Start OAuth flow with Hattrick."""
    try:
        chpp = CHPP(consumer_key, consumer_secret)
        auth = chpp.get_auth(callback_url=app.config['CALLBACK_URL'], scope="")

        dprint(1, f"OAuth auth response keys: {list(auth.keys()) if auth else 'None'}")

        # Handle different possible response structures
        if 'request_token' in auth:
            session['request_token'] = auth["request_token"]
            session['req_secret'] = auth["request_token_secret"]
        elif 'oauth_token' in auth:
            session['request_token'] = auth["oauth_token"]
            session['req_secret'] = auth.get("oauth_token_secret", "")
        else:
            dprint(1, f"Unexpected OAuth response format: {auth}")
            raise ValueError("Invalid OAuth response format")

        return render_template('_forward.html', url=auth['url'])

    except Exception as e:
        dprint(1, f"OAuth flow error: {e}")
        return create_page(
            template='login.html',
            title='Login / Signup',
            error='Failed to start OAuth authentication. Please try again.')


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

        # Get user from Hattrick with error handling for CHPP library issues
        chpp = CHPP(consumer_key, consumer_secret,
                   session['access_key'], session['access_secret'])

        current_user = None
        try:
            current_user = chpp.user()
            session['current_user'] = current_user.username
            session['current_user_id'] = current_user.ht_id
        except Exception as chpp_error:
            dprint(1, f"CHPP user() error (likely YouthTeamId issue): {chpp_error}")
            # This is a known CHPP library issue where YouthTeamId field is None
            # We can still proceed with OAuth tokens but need to handle user data differently

            # Try to find existing user by OAuth tokens since we can't get user ID from CHPP
            existing_user = None

            # First try to find by username if available (from form login)
            if session.get('username'):
                existing_user = User.query.filter_by(username=session['username']).first()
                dprint(1, f"Found user by session username: {existing_user.username if existing_user else 'None'}")

            # If no username in session (direct OAuth), try to find by access tokens
            if not existing_user:
                existing_user = User.query.filter_by(
                    access_key=session['access_key']
                ).first()
                dprint(1, f"Found user by access_key: {existing_user.username if existing_user else 'None'}")

            # If still no user found, try to find any user with legacy password hash
            if not existing_user:
                existing_user = User.query.filter(
                    User.password.startswith('MIGRATION_REQUIRED:')
                ).first()
                dprint(1, f"Found legacy user needing migration: {existing_user.username if existing_user else 'None'}")

            if existing_user:
                # Use existing user's Hattrick data
                session['current_user'] = existing_user.ht_user
                session['current_user_id'] = existing_user.ht_id
                dprint(1, f"Using existing user data: {existing_user.ht_user} ({existing_user.ht_id})")

                # Create a minimal current_user object for the rest of the function
                class MinimalUser:
                    def __init__(self, ht_id, username, teams_ht_id=None):
                        self.ht_id = ht_id
                        self.username = username
                        self._teams_ht_id = teams_ht_id or [ht_id]  # Use ht_id as team if no teams available

                # Get team IDs from existing user if available, otherwise use the ht_id
                teams_ht_id = getattr(existing_user, 'team_ids', None) or [existing_user.ht_id]
                current_user = MinimalUser(existing_user.ht_id, existing_user.ht_user, teams_ht_id)
            else:
                # Cannot proceed without user identification
                return create_page(
                    template='login.html',
                    title='Login / Signup',
                    error='There was an issue with Hattrick authentication. Please try logging in with your username and password instead.')

        # Check if user exists in database
        existing_user = User.query.filter_by(ht_id=current_user.ht_id).first()

        if existing_user:
            # Check if this is a migration user who needs password update
            if existing_user.password.startswith('MIGRATION_REQUIRED:'):
                # User had old SHA256 hash, upgrade to modern hash if they provided a new password
                new_password = session.get('password', '')
                if new_password:
                    # User provided a new password during this OAuth flow, upgrade their hash
                    dprint(1, f"Upgrading password hash for migration user: {existing_user.username}")
                    User.claimUser(
                        existing_user,
                        username=session.get('username', current_user.username),
                        password=new_password,  # This will be a modern scrypt hash
                        access_key=session['access_key'],
                        access_secret=session['access_secret'])
                else:
                    # No new password, just update OAuth tokens but keep migration marker
                    User.claimUser(
                        existing_user,
                        username=session.get('username', current_user.username),
                        password=existing_user.password,  # Keep migration marker
                        access_key=session['access_key'],
                        access_secret=session['access_secret'])
            else:
                # Normal existing user update
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

        # Setup team data with error handling
        try:
            all_teams = current_user._teams_ht_id
            all_team_names = []

            for id in all_teams:
                try:
                    team_name = chpp.team(ht_id=id).name
                    all_team_names.append(team_name)
                except Exception as team_error:
                    dprint(1, f"Could not get team name for {id}: {team_error}")
                    all_team_names.append(f"Team {id}")  # Fallback team name

            session['all_teams'] = all_teams
            session['all_team_names'] = all_team_names
            session['team_id'] = all_teams[0]
        except Exception as team_setup_error:
            dprint(1, f"Team setup error: {team_setup_error}")
            # Fallback team setup if everything fails
            session['all_teams'] = [current_user.ht_id]
            session['all_team_names'] = [f"Team {current_user.ht_id}"]
            session['team_id'] = current_user.ht_id

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


@auth_bp.route('/login/oauth')
def oauth_direct():
    """Direct OAuth authentication for password migration users."""
    dprint(1, "Starting direct OAuth flow for password migration")

    # Clear existing session to force fresh authentication
    if session.get('current_user'):
        dprint(1, "Clearing existing session for password migration flow")
        session.clear()

    # Start OAuth flow
    return start_oauth_flow()
