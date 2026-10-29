"""Authentication routes blueprint for HT Status application."""

import traceback
from types import SimpleNamespace

from flask import (
    Blueprint,
    make_response,
    redirect,
    render_template,
    request,
    session,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app import translations
from app.chpp_utilities import (
    fetch_user_teams,
    get_chpp_client,
    get_chpp_client_no_auth,
    get_current_user_context,
)
from app.utils import create_page, dprint

# Create Blueprint for authentication routes
auth_bp = Blueprint("auth", __name__)

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


LOGIN_TITLE = "Login / Signup"
TEAM_FETCH_ERROR = (
    "Unable to fetch team data from Hattrick. Please try again or contact support."
)


def _login_page(error=None):
    extra = {"error": error} if error else {}
    return create_page(template="login.html", title=LOGIN_TITLE, **extra)


def _clear_login_session():
    for key in ("current_user", "current_user_id", "access_key", "access_secret"):
        session.pop(key, None)


def _set_session_teams(team_ids, team_names):
    session["all_teams"] = team_ids
    session["all_team_names"] = team_names
    session["team_id"] = team_ids[0]


def _check_password(user, password):
    """Return (valid, needs_migration) for a stored password hash."""
    if user.password.startswith(("MIGRATION_REQUIRED:", "sha256$")):
        # Legacy SHA256 hash: can't be verified, user must log in via Hattrick
        return False, True
    try:
        return check_password_hash(user.password, password), False
    except ValueError as e:
        dprint(1, f"Unsupported password hash for {user.username}: {e}")
        return False, True


def _login_with_stored_tokens(user):
    """Log in a user whose Hattrick OAuth tokens are already stored."""
    session["access_key"] = user.access_key
    session["access_secret"] = user.access_secret
    session["current_user"] = user.ht_user
    session["current_user_id"] = user.ht_id
    user.login()
    db.session.commit()

    try:
        chpp = get_chpp_client(
            {"access_key": user.access_key, "access_secret": user.access_secret}
        )
        ht_user = chpp.user()
        team_ids, team_names = fetch_user_teams(chpp, ht_user)
        if not team_ids:
            raise ValueError("No teams found for this Hattrick user")
        _set_session_teams(team_ids, team_names)
    except Exception:
        dprint(1, f"Error fetching teams from Hattrick: {traceback.format_exc()}")
        return _login_page(TEAM_FETCH_ERROR)
    translations.refresh(chpp, ht_user.language_id)
    return redirect("/")


def _start_signup_oauth(username, password):
    """Remember the chosen credentials and send the user to Hattrick to authorize."""
    session["username"] = username
    session["password"] = generate_password_hash(password)
    return start_oauth_flow()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login and Hattrick OAuth authentication."""
    from models import User

    if session.get("current_user"):
        return redirect("/")

    oauth_verifier = request.args.get("oauth_verifier")
    if oauth_verifier:
        return handle_oauth_callback(oauth_verifier)

    if request.method == "GET":
        return _login_page()

    username = request.form.get("username")
    password = request.form.get("password")
    if not username:
        return _login_page("Username is required")
    if not password:
        return _login_page("Password is required")
    if not request.form.get("cookie_consent"):
        return _login_page(
            "You must consent to the use of essential session cookies to log in"
        )

    user = User.query.filter_by(username=username).first()
    if not user:
        if len(password) < 8:
            return _login_page("Password must be at least 8 characters long")
        return _start_signup_oauth(username, password)

    valid, needs_migration = _check_password(user, password)
    if valid:
        if user.access_key and user.access_secret:
            return _login_with_stored_tokens(user)
        return _start_signup_oauth(username, password)
    if needs_migration:
        return _login_page(
            "Your password needs to be updated. Please use the 'Register via "
            "Hattrick' button to log in with your Hattrick account."
        )
    return _login_page("Invalid username or password")


def start_oauth_flow():
    """Start OAuth flow with Hattrick."""
    try:
        chpp = get_chpp_client_no_auth()
        auth = chpp.get_auth(callback_url=app.config["CALLBACK_URL"], scope="")

        dprint(1, f"OAuth auth response keys: {list(auth.keys()) if auth else 'None'}")

        # Handle different possible response structures
        if "request_token" in auth:
            session["request_token"] = auth["request_token"]
            session["req_secret"] = auth["request_token_secret"]
        elif "oauth_token" in auth:
            session["request_token"] = auth["oauth_token"]
            session["req_secret"] = auth.get("oauth_token_secret", "")
        else:
            dprint(1, f"Unexpected OAuth response format: {auth}")
            raise ValueError("Invalid OAuth response format")

        return render_template("_forward.html", url=auth["url"])

    except Exception as e:
        dprint(1, f"OAuth flow error: {e}")
        return create_page(
            template="login.html",
            title="Login / Signup",
            error="Failed to start OAuth authentication. Please try again.",
        )


def _save_oauth_user(current_user, access_token):
    """Create the User row, or update the existing one with fresh OAuth tokens."""
    from models import User

    # Check if user exists in database
    existing_user = User.query.filter_by(ht_id=current_user.ht_id).first()

    if existing_user:
        # Check if this is a migration user who needs password update
        if existing_user.password.startswith("MIGRATION_REQUIRED:"):
            # User had old SHA256 hash, upgrade to modern hash if they provided a new password
            new_password = session.get("password", "")
            if new_password:
                # User provided a new password during this OAuth flow, upgrade their hash
                dprint(
                    1,
                    f"Upgrading password hash for migration user: {existing_user.username}",
                )
                User.claimUser(
                    existing_user,
                    username=session.get("username", current_user.username),
                    password=new_password,  # This will be a modern scrypt hash
                    access_key=session["access_key"],
                    access_secret=session["access_secret"],
                )
            else:
                # No new password, just update OAuth tokens but keep migration marker
                User.claimUser(
                    existing_user,
                    username=session.get("username", current_user.username),
                    password=existing_user.password,  # Keep migration marker
                    access_key=session["access_key"],
                    access_secret=session["access_secret"],
                )
        else:
            # Normal existing user update
            User.claimUser(
                existing_user,
                username=session.get("username", current_user.username),
                password=session.get("password", ""),
                access_key=session["access_key"],
                access_secret=session["access_secret"],
            )
    else:
        # Create new user
        new_user = User(
            ht_id=current_user.ht_id,
            ht_user=current_user.username,
            username=session.get("username", current_user.username),
            password=session.get("password", ""),
            access_key=access_token["key"],
            access_secret=access_token["secret"],
        )
        db.session.add(new_user)

    db.session.commit()


def _find_user_for_tokens():
    """Find our User when CHPP user() fails: by form username, then by token."""
    from models import User

    user = None
    if session.get("username"):
        user = User.query.filter_by(username=session["username"]).first()
    if not user:
        user = User.query.filter_by(access_key=session["access_key"]).first()
    return user


def handle_oauth_callback(oauth_verifier):
    """Handle OAuth callback after authorization."""
    try:
        chpp = get_chpp_client_no_auth()
        access_token = chpp.get_access_token(
            request_token=session["request_token"],
            request_token_secret=session["req_secret"],
            code=oauth_verifier,
        )
        session["access_key"] = access_token["key"]
        session["access_secret"] = access_token["secret"]
        chpp = get_chpp_client(session)

        teams = None
        language_id = None
        try:
            context = get_current_user_context(chpp)
            hattrick_user = SimpleNamespace(
                ht_id=context["ht_id"], username=context["ht_user"]
            )
            language_id = context["user"].language_id
            teams = (context["team_ids"], context["team_names"])
        except Exception as chpp_error:
            dprint(1, f"CHPP user() failed (likely YouthTeamId): {chpp_error}")
            # Only fall back to a user we can identify by form username or token;
            # never guess, to avoid logging into someone else's account
            existing_user = _find_user_for_tokens()
            if not existing_user:
                _clear_login_session()
                return _login_page(
                    "Your Hattrick authentication tokens are no longer valid. "
                    "Please log in again."
                )
            hattrick_user = SimpleNamespace(
                ht_id=existing_user.ht_id, username=existing_user.ht_user
            )

        session["current_user"] = hattrick_user.username
        session["current_user_id"] = hattrick_user.ht_id
        _save_oauth_user(hattrick_user, access_token)

        try:
            from app.utils import create_default_groups

            create_default_groups(hattrick_user.ht_id)
        except Exception as group_error:
            dprint(1, f"Failed to create default groups: {group_error}")

        try:
            team_ids, team_names = teams or fetch_user_teams(chpp)
            if not team_ids:
                raise ValueError("No teams found for this Hattrick user")
        except Exception:
            dprint(1, f"Team setup error: {traceback.format_exc()}")
            session.pop("current_user", None)
            session.pop("current_user_id", None)
            return _login_page(TEAM_FETCH_ERROR)

        _set_session_teams(team_ids, team_names)
        translations.refresh(chpp, language_id)
        return redirect("/")

    except Exception as e:
        dprint(1, f"OAuth callback error: {e}")
        return _login_page("OAuth authentication failed. Please try again.")


@auth_bp.route("/validate-session")
def validate_session():
    """API endpoint to validate current session for PWA."""
    try:
        # Check if user is logged in
        user_id = session.get("current_user_id")
        if not user_id:
            return {"valid": False, "reason": "no_session"}, 401

        # Check if session data is complete
        required_keys = ["access_key", "access_secret", "current_user"]
        missing_keys = [key for key in required_keys if not session.get(key)]

        if missing_keys:
            dprint(2, f"Session missing keys: {missing_keys}")
            return {"valid": False, "reason": "incomplete_session"}, 401

        # Session appears valid
        return {
            "valid": True,
            "user_id": user_id,
            "user": session.get("current_user"),
        }, 200

    except Exception as e:
        dprint(1, f"Session validation error: {e}")
        return {"valid": False, "reason": "error"}, 500


@auth_bp.route("/logout")
def logout():
    """Handle user logout and session clearing."""
    dprint(1, f"Logging out user: {session.get('current_user', 'Unknown')}")

    # Clear session first
    session.clear()

    # Force explicit redirect
    response = make_response()
    response.status_code = 302
    response.headers["Location"] = "/login"
    return response


@auth_bp.route("/login/oauth")
def oauth_direct():
    """Direct OAuth authentication for password migration users."""
    dprint(1, "Starting direct OAuth flow for password migration")

    # Clear existing session to force fresh authentication
    if session.get("current_user"):
        dprint(1, "Clearing existing session for password migration flow")
        session.clear()

    # Start OAuth flow
    return start_oauth_flow()
