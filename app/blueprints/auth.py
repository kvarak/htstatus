"""Authentication routes blueprint for HT Status application."""

from flask import (
    Blueprint,
    make_response,
    redirect,
    render_template,
    request,
    session,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.chpp_utilities import (
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


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login and Hattrick OAuth authentication."""
    from models import User

    dprint(1, "=== LOGIN FUNCTION START ===")

    # Return early if already logged in
    if session.get("current_user"):
        dprint(1, "User already logged in, redirecting")
        return redirect("/")

    # Handle OAuth callback
    oauth_verifier = request.args.get("oauth_verifier")
    if oauth_verifier:
        dprint(1, "Handling OAuth callback")
        return handle_oauth_callback(oauth_verifier)

    # Handle GET request - show login form
    if request.method == "GET":
        dprint(1, "Showing login form")
        return create_page(template="login.html", title="Login / Signup")

    # Handle POST request (form submission)
    dprint(1, "Processing POST login request")
    username = request.form.get("username")
    password = request.form.get("password")
    dprint(1, f"Login attempt for username: {username}")
    dprint(1, f"Password provided: {bool(password)}, length: {len(password) if password else 0}")

    # Validate form data
    if not username:
        return create_page(
            template="login.html", title="Login / Signup", error="Username is required"
        )

    if not password:
        return create_page(
            template="login.html", title="Login / Signup", error="Password is required"
        )

    if len(password) < 8:
        return create_page(
            template="login.html",
            title="Login / Signup",
            error="Password must be at least 8 characters long",
        )

    # Check for existing user
    existing_user = User.query.filter_by(username=username).first()
    dprint(
        1, f"Found existing user: {existing_user.username if existing_user else 'None'}"
    )

    # Handle password verification with migration support
    password_valid = False
    needs_migration = False

    if existing_user:
        dprint(
            1,
            f"Password format check - starts with MIGRATION_REQUIRED: {existing_user.password.startswith('MIGRATION_REQUIRED:')}",
        )
        dprint(
            1,
            f"Password format check - starts with sha256: {existing_user.password.startswith('sha256$')}",
        )
        dprint(
            1,
            f"Password format check - starts with scrypt: {existing_user.password.startswith('scrypt:')}",
        )

        if existing_user.password.startswith(
            "MIGRATION_REQUIRED:"
        ) or existing_user.password.startswith("sha256$"):
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
        dprint(1, f"User has access_key: {bool(existing_user.access_key)}")
        dprint(1, f"User has access_secret: {bool(existing_user.access_secret)}")
        if existing_user.access_key and existing_user.access_secret:
            # User has OAuth tokens - log them in directly
            dprint(1, "User has valid OAuth tokens, logging in directly")
            session["access_key"] = existing_user.access_key
            session["access_secret"] = existing_user.access_secret
            session["current_user"] = existing_user.ht_user
            session["current_user_id"] = existing_user.ht_id
            dprint(1, f"Set session current_user: {existing_user.ht_user}")
            dprint(1, f"Set session current_user_id: {existing_user.ht_id}")

            # Setup team data from Hattrick API using OAuth tokens
            print("Setting up team data")
            dprint(1, "Setting up team data for logged-in user")
            try:
                # Create temporary session with user's OAuth tokens for CHPP client
                temp_session = {
                    "access_key": existing_user.access_key,
                    "access_secret": existing_user.access_secret,
                }
                dprint(1, "Initializing CHPP client with user credentials")
                chpp = get_chpp_client(temp_session)
                dprint(1, "Created CHPP instance")

                # Try to get user and teams, handling YouthTeamId error gracefully
                try:
                    dprint(1, "Fetching user context from CHPP")
                    user_context = get_current_user_context(chpp)
                    dprint(1, f"Got user context: {user_context['ht_user']}")
                    all_teams = user_context["team_ids"]
                    dprint(1, f"Got teams from user: {all_teams}")
                except Exception as user_error:
                    dprint(1, f"Exception in chpp.user(): {user_error}")
                    # YouthTeamId is optional but pychpp treats it as required
                    # Work around by accessing teams data directly
                    if "YouthTeamId" in str(user_error):
                        dprint(1, f"YouthTeamId parsing error (user has no youth team): {user_error}")
                        # Try to get teams by accessing the raw data directly
                        try:
                            # chpp.request() returns already-parsed ElementTree Element
                            root = chpp.request(file="managercompendium", version="1.6")

                            # Extract team IDs from XML
                            team_nodes = root.findall(".//Team/TeamId")
                            all_teams = [int(node.text) for node in team_nodes if node.text]
                            dprint(1, f"Extracted team IDs from XML: {all_teams}")
                        except Exception as xml_error:
                            dprint(1, f"Failed to extract teams from XML: {xml_error}")
                            dprint(1, f"XML error type: {type(xml_error)}")
                            import traceback
                            dprint(1, f"XML error traceback: {traceback.format_exc()}")
                            raise Exception("Cannot get team IDs from CHPP - authentication failed") from None
                    else:
                        raise user_error

                all_team_names = []
                for team_id in all_teams:
                    try:
                        dprint(1, f"Fetching team name for team_id: {team_id}")
                        team_name = chpp.team(ht_id=team_id).name
                        dprint(1, f"Got team name: {team_name}")
                        all_team_names.append(team_name)
                    except Exception as e:
                        dprint(1, f"Could not fetch team name for {team_id}: {e}")
                        all_team_names.append(f"Team {team_id}")

                session["all_teams"] = all_teams
                session["all_team_names"] = all_team_names
                session["team_id"] = all_teams[0]
                dprint(1, f"Team setup complete: {all_teams} with names: {all_team_names}")
            except Exception as e:
                dprint(1, f"Error fetching teams from Hattrick: {e}")
                dprint(1, f"Error type: {type(e)}")
                import traceback
                dprint(1, f"Full traceback: {traceback.format_exc()}")
                return create_page(
                    template="login.html",
                    title="Login",
                    error="Unable to fetch team data from Hattrick. Please try again or contact support.",
                )

            dprint(1, "Login successful, redirecting to /")
            return redirect("/")
        else:
            # Need to get OAuth tokens for existing user
            dprint(1, "User needs OAuth tokens, starting OAuth flow")
            session["username"] = username
            session["password"] = generate_password_hash(password)
            return start_oauth_flow()

    # Handle authentication failures and migration cases
    if existing_user:
        if needs_migration:
            return create_page(
                template="login.html",
                title="Login / Signup",
                error="Your password needs to be updated. Please use the 'Register via Hattrick' button to log in with your Hattrick account.",
            )
        else:
            # Wrong password
            return create_page(
                template="login.html",
                title="Login / Signup",
                error="Invalid username or password",
            )
    else:
        # Store new user credentials and start OAuth flow
        session["username"] = username
        session["password"] = generate_password_hash(password)
        return start_oauth_flow()

    print("ERROR: Reached end of login function without returning - this should not happen!")


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


def handle_oauth_callback(oauth_verifier):
    """Handle OAuth callback after authorization."""
    from models import User

    try:
        # Get access tokens
        chpp = get_chpp_client_no_auth()
        access_token = chpp.get_access_token(
            request_token=session["request_token"],
            request_token_secret=session["req_secret"],
            code=oauth_verifier,
        )

        session["access_key"] = access_token["key"]
        session["access_secret"] = access_token["secret"]

        # Get user from Hattrick with error handling for CHPP library issues
        chpp = get_chpp_client(session)

        current_user = None
        try:
            user_context = get_current_user_context(chpp)
            session["current_user"] = user_context["ht_user"]
            session["current_user_id"] = user_context["ht_id"]
        except Exception as chpp_error:
            dprint(1, f"CHPP user() error (likely YouthTeamId issue): {chpp_error}")
            # This is a known CHPP library issue where YouthTeamId field is None
            # We can still proceed with OAuth tokens but need to handle user data differently

            # Try to find existing user by OAuth tokens since we can't get user ID from CHPP
            existing_user = None

            # First try to find by username if available (from form login)
            if session.get("username"):
                existing_user = User.query.filter_by(
                    username=session["username"]
                ).first()
                dprint(
                    1,
                    f"Found user by session username: {existing_user.username if existing_user else 'None'}",
                )

            # If no username in session (direct OAuth), try to find by access tokens
            if not existing_user:
                existing_user = User.query.filter_by(
                    access_key=session["access_key"]
                ).first()
                dprint(
                    1,
                    f"Found user by access_key: {existing_user.username if existing_user else 'None'}",
                )

            # If still no user found, try to find any user with legacy password hash
            if not existing_user:
                existing_user = User.query.filter(
                    User.password.startswith("MIGRATION_REQUIRED:")
                ).first()
                dprint(
                    1,
                    f"Found legacy user needing migration: {existing_user.username if existing_user else 'None'}",
                )

            if existing_user:
                # Use existing user's Hattrick data
                session["current_user"] = existing_user.ht_user
                session["current_user_id"] = existing_user.ht_id
                dprint(
                    1,
                    f"Using existing user data: {existing_user.ht_user} ({existing_user.ht_id})",
                )

                # Create a minimal current_user object for the rest of the function
                class MinimalUser:
                    def __init__(self, ht_id, username, teams_ht_id=None):
                        self.ht_id = ht_id
                        self.username = username
                        self._teams_ht_id = teams_ht_id or [
                            ht_id
                        ]  # Use ht_id as team if no teams available

                # Get team IDs from existing user if available, otherwise use the ht_id
                teams_ht_id = getattr(existing_user, "team_ids", None) or [
                    existing_user.ht_id
                ]
                current_user = MinimalUser(
                    existing_user.ht_id, existing_user.ht_user, teams_ht_id
                )
            else:
                # Cannot proceed without user identification
                # Clear session to prevent conflicting success/failure messages
                session.pop("current_user", None)
                session.pop("current_user_id", None)
                return create_page(
                    template="login.html",
                    title="Login / Signup",
                    error="There was an issue with Hattrick authentication. Please try logging in with your username and password instead.",
                )

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

        # Setup team data with error handling
        try:
            all_teams = current_user._teams_ht_id
            all_team_names = []

            for id in all_teams:
                try:
                    team_name = chpp.team(ht_id=id).name
                    all_team_names.append(team_name)
                    dprint(1, f"Fetched team name: {team_name} for ID {id}")
                except Exception as team_error:
                    dprint(1, f"Could not get team name for {id}: {team_error}")
                    all_team_names.append(f"Team {id}")  # Fallback team name

            session["all_teams"] = all_teams
            session["all_team_names"] = all_team_names
            session["team_id"] = all_teams[0]
            dprint(1, f"OAuth callback team setup complete: {all_teams} with names: {all_team_names}")
        except Exception as team_setup_error:
            # YouthTeamId is optional but pychpp treats it as required
            if "YouthTeamId" in str(team_setup_error):
                dprint(1, f"YouthTeamId parsing error (user has no youth team): {team_setup_error}")
                try:
                    # Work around by accessing raw XML directly
                    import xml.etree.ElementTree as ET
                    user_xml = chpp.request(file="managercompendium", version="1.6")
                    root = ET.fromstring(user_xml)

                    # Extract team IDs from XML
                    team_nodes = root.findall(".//Team/TeamId")
                    all_teams = [int(node.text) for node in team_nodes if node.text]
                    dprint(1, f"Extracted team IDs from raw XML: {all_teams}")

                    # Get team names
                    all_team_names = []
                    for team_id in all_teams:
                        try:
                            team_name = chpp.team(ht_id=team_id).name
                            all_team_names.append(team_name)
                        except Exception:
                            all_team_names.append(f"Team {team_id}")

                    session["all_teams"] = all_teams
                    session["all_team_names"] = all_team_names
                    session["team_id"] = all_teams[0]
                    dprint(1, f"Team setup complete via XML: {all_teams} with names: {all_team_names}")
                except Exception as xml_error:
                    dprint(1, f"Failed to extract teams from XML: {xml_error}")
                    # Clear session to prevent conflicting success/failure messages
                    session.pop("current_user", None)
                    session.pop("current_user_id", None)
                    return create_page(
                        template="login.html",
                        title="Login",
                        error="Unable to fetch team data from Hattrick. Please try again or contact support.",
                    )
            else:
                dprint(1, f"Team setup error: {team_setup_error}")
                # Clear session to prevent conflicting success/failure messages
                session.pop("current_user", None)
                session.pop("current_user_id", None)
                return create_page(
                    template="login.html",
                    title="Login",
                    error="Unable to fetch team data from Hattrick. Please try again or contact support.",
                )

        return redirect("/")

    except Exception as e:
        dprint(1, f"OAuth callback error: {e}")
        return create_page(
            template="login.html",
            title="Login / Signup",
            error="OAuth authentication failed. Please try again.",
        )


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
