"""Authentication routes blueprint for HT Status application."""

from flask import Blueprint, make_response, render_template, request, session
from pychpp import CHPP
from werkzeug.security import check_password_hash, generate_password_hash

from app.routes_bp import create_page, debug_print, dprint
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


def login():
    """Handle user login and Hattrick OAuth authentication."""
    # this comes from form
    username = request.form.get('username')
    password = request.form.get('password')
    # this comes from CHPP
    oauth_verifier = request.values.get('oauth_verifier')
    oa = oauth_verifier

    if not (oa) and not (username) and session.get('current_user') is None:
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
            # debug_print("login", "chpp.get_auth", auth._SOURCE_FILE)
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

            # debug_print(
            #     "login",
            #     "chpp.get_access_token",
            #     access_token._SOURCE_FILE)

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
        template='main.html',
        title='Logged in')


def logout():
    """Handle user logout and session clearing."""
    dprint(1, f"Logging out user: {session.get('current_user', 'Unknown')}")

    # Clear session first
    user_before = session.get('current_user', 'No user')
    session.clear()

    # Force explicit redirect
    response = make_response()
    response.status_code = 302
    response.headers['Location'] = '/login'
    return response
