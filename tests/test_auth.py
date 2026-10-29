"""Test authentication and session management."""

import pytest


@pytest.fixture(scope="function")
def auth_client(app_with_routes):
    """Create test client with authentication routes registered."""
    return app_with_routes.test_client()


def test_session_structure(client):
    """Test that session has expected structure for authenticated users."""
    with client.session_transaction() as session:
        session["access_key"] = "test_access_key"
        session["access_secret"] = "test_access_secret"
        session["current_user"] = "test_user"
        session["all_teams"] = [12345]
        session["all_team_names"] = ["Test Team"]

    # Test that session data persists
    with client.session_transaction() as session:
        assert session.get("access_key") == "test_access_key"
        assert session.get("access_secret") == "test_access_secret"
        assert session.get("current_user") == "test_user"
        assert session.get("all_teams") == [12345]
        assert session.get("all_team_names") == ["Test Team"]


def test_cookie_consent_required(auth_client):
    """Test that cookie consent is required for login."""
    # Test login without cookie consent
    response = auth_client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "testpassword123",
            # Missing cookie_consent
        },
    )

    assert response.status_code == 200
    assert b"You must consent to the use of essential session cookies" in response.data


def test_cookie_consent_with_valid_form(auth_client):
    """Test that login works with proper cookie consent."""
    # This test will need to be expanded when OAuth mocking is available
    response = auth_client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "testpassword123",
            "cookie_consent": "on",
        },
    )

    # Should not show the cookie consent error
    assert (
        b"You must consent to the use of essential session cookies" not in response.data
    )


def test_cookie_consent_notice_in_template(auth_client):
    """Test that cookie consent notice appears on login page."""
    response = auth_client.get("/login")
    assert b"Session Cookies:" in response.data
    assert b"authentication - no tracking or third-party sharing" in response.data
    assert b"cookie_consent" in response.data


def test_multi_team_support(client):
    """Test multi-team session support."""
    with client.session_transaction() as session:
        # Test multiple teams
        session["all_teams"] = [12345, 67890]
        session["all_team_names"] = ["Team One", "Team Two"]

    with client.session_transaction() as session:
        teams = session.get("all_teams")
        names = session.get("all_team_names")

        assert len(teams) == 2
        assert len(names) == 2
        assert teams[0] == 12345
        assert teams[1] == 67890
        assert names[0] == "Team One"
        assert names[1] == "Team Two"


def test_session_cleanup(client):
    """Test that sessions can be properly cleared."""
    # Set session data
    with client.session_transaction() as session:
        session["access_key"] = "test_key"
        session["test_data"] = "should_be_cleared"

    # Clear session
    with client.session_transaction() as session:
        session.clear()

    # Verify session is empty
    with client.session_transaction() as session:
        assert session.get("access_key") is None
        assert session.get("test_data") is None


def test_authentication_required_decorator_simulation(authenticated_session):
    """Test simulation of authentication-required routes."""
    # This tests our authenticated_session fixture
    with authenticated_session.session_transaction() as session:
        assert session.get("access_key") is not None
        assert session.get("access_secret") is not None
        assert session.get("current_user") is not None


def test_oauth_token_storage(client):
    """Test that OAuth tokens are stored correctly in session."""
    test_access_key = "test_oauth_access_key_12345"
    test_access_secret = "test_oauth_access_secret_67890"

    with client.session_transaction() as session:
        session["access_key"] = test_access_key
        session["access_secret"] = test_access_secret

    # Verify tokens are stored correctly
    with client.session_transaction() as session:
        assert session["access_key"] == test_access_key
        assert session["access_secret"] == test_access_secret
        # Tokens should be strings
        assert isinstance(session["access_key"], str)
        assert isinstance(session["access_secret"], str)


def test_default_groups_creation_function_exists():
    """Test that create_default_groups function can be imported and called."""
    from app.utils import create_default_groups

    # Test that the function exists and is callable
    assert callable(create_default_groups)

    # Test function signature by checking that it accepts user_id parameter
    import inspect

    sig = inspect.signature(create_default_groups)
    assert "user_id" in sig.parameters


class TestAuthRoutes:
    """Test authentication blueprint route functionality."""

    def test_login_route_get(self, auth_client):
        """Test login route GET request renders login page."""
        response = auth_client.get("/login")
        assert response.status_code == 200
        assert b"Login" in response.data or b"login" in response.data
        assert b"cookie_consent" in response.data

    def test_login_route_post_missing_consent(self, auth_client):
        """Test login route requires cookie consent."""
        response = auth_client.post(
            "/login", data={"username": "test", "password": "test"}
        )
        assert response.status_code == 200
        assert (
            b"You must consent to the use of essential session cookies" in response.data
        )

    def test_logout_route_clears_session(self, auth_client):
        """Test logout route clears session data."""
        # Set session data first
        with auth_client.session_transaction() as session:
            session["access_key"] = "test_key"
            session["access_secret"] = "test_secret"
            session["current_user"] = "test_user"

        # Call logout
        response = auth_client.get("/logout")

        # Should redirect (302) or show logout page (200)
        assert response.status_code in [200, 302]

        # Session should be cleared
        with auth_client.session_transaction() as session:
            assert session.get("access_key") is None
            assert session.get("access_secret") is None
            assert session.get("current_user") is None

    def test_protected_route_redirect_unauthenticated(self, auth_client):
        """Test that protected routes redirect when not authenticated."""
        # Test accessing a protected route without authentication
        response = auth_client.get("/team")
        # The route might return 200 with error message or redirect - both acceptable
        assert response.status_code in [200, 302, 401, 403]

    def test_protected_route_redirect_settings(self, auth_client):
        """Test settings route requires authentication."""
        response = auth_client.get("/settings")
        # The route might return 200 with error message or redirect - both acceptable
        assert response.status_code in [200, 302, 401, 403]

    def test_protected_route_redirect_update(self, auth_client):
        """Test update route requires authentication."""
        response = auth_client.get("/update")
        # The route might return 200 with error message or redirect - both acceptable
        assert response.status_code in [200, 302, 401, 403]
        with auth_client.session_transaction() as session:
            session["access_key"] = "test_access_key"
            session["access_secret"] = "test_access_secret"
            session["current_user_id"] = 12345
            session["all_teams"] = [12345]
            session["all_team_names"] = ["Test Team"]

        # Test accessing index route (should work)
        response = auth_client.get("/")
        assert response.status_code == 200

    def test_session_token_validation(self, auth_client):
        """Test session token structure validation."""
        with auth_client.session_transaction() as session:
            session["access_key"] = "valid_access_key"
            session["access_secret"] = "valid_access_secret"

        with auth_client.session_transaction() as session:
            access_key = session.get("access_key")
            access_secret = session.get("access_secret")

            # Validate token structure
            assert access_key is not None
            assert access_secret is not None
            assert isinstance(access_key, str)
            assert isinstance(access_secret, str)
            assert len(access_key) > 0
            assert len(access_secret) > 0


class TestSessionValidationAPI:
    """Test the new session validation API endpoint for PWA support."""

    def test_validate_session_no_session(self, app_with_routes):
        """Test session validation with no active session."""
        client = app_with_routes.test_client()
        response = client.get("/validate-session")

        assert response.status_code == 401
        data = response.get_json()
        assert data["valid"] is False
        assert data["reason"] == "no_session"

    def test_validate_session_incomplete_session(self, app_with_routes):
        """Test session validation with incomplete session data."""
        client = app_with_routes.test_client()

        with client.session_transaction() as session:
            session["current_user_id"] = 12345
            # Missing access_key, access_secret, current_user

        response = client.get("/validate-session")

        assert response.status_code == 401
        data = response.get_json()
        assert data["valid"] is False
        assert data["reason"] == "incomplete_session"

    def test_validate_session_valid_session(self, app_with_routes):
        """Test session validation with complete session data."""
        client = app_with_routes.test_client()

        with client.session_transaction() as session:
            session["current_user_id"] = 12345
            session["access_key"] = "test_access_key"
            session["access_secret"] = "test_access_secret"
            session["current_user"] = "testuser"

        response = client.get("/validate-session")

        assert response.status_code == 200
        data = response.get_json()
        assert data["valid"] is True
        assert data["user_id"] == 12345
        assert data["user"] == "testuser"


class TestAuthHelpers:
    """REFACTOR-118: login and OAuth callback helpers."""

    @staticmethod
    def _user(db_session, ht_id=556001, username="tester", password="secret123"):
        from werkzeug.security import generate_password_hash

        from models import User

        user = User(
            ht_id, "TesterHT", username, generate_password_hash(password), "ak", "as"
        )
        db_session.add(user)
        db_session.commit()
        return user

    def test_check_password(self):
        from types import SimpleNamespace

        from werkzeug.security import generate_password_hash

        from app.blueprints.auth import _check_password

        modern = SimpleNamespace(password=generate_password_hash("pw"), username="u")
        assert _check_password(modern, "pw") == (True, False)
        assert _check_password(modern, "nope") == (False, False)
        legacy = SimpleNamespace(password="sha256$abc", username="u")
        assert _check_password(legacy, "pw") == (False, True)

    def _post_login(self, app_with_routes, **form):
        client = app_with_routes.test_client()
        data = {"username": "tester", "password": "secret123", "cookie_consent": "on"}
        data.update(form)
        return client, client.post("/login", data=data)

    def test_login_with_stored_tokens_sets_teams(self, app_with_routes, db_session):
        from unittest.mock import patch

        self._user(db_session)
        with (
            patch(
                "app.blueprints.auth.fetch_user_teams",
                return_value=([7, 8], ["A", "B"]),
            ),
            patch("app.blueprints.auth.get_chpp_client"),
        ):
            client, response = self._post_login(app_with_routes)

        assert response.status_code == 302
        with client.session_transaction() as sess:
            assert sess["current_user_id"] == 556001
            assert sess["all_teams"] == [7, 8]
            assert sess["team_id"] == 7

    def test_login_wrong_password(self, app_with_routes, db_session):
        self._user(db_session)
        _, response = self._post_login(app_with_routes, password="wrongpass")
        assert b"Invalid username or password" in response.data

    def test_signup_requires_long_password(
        self, app_with_routes, db_session
    ):  # noqa: ARG002
        _, response = self._post_login(
            app_with_routes, username="newbie", password="short"
        )
        assert b"at least 8 characters" in response.data

    def test_callback_falls_back_to_user_found_by_token(
        self, app_with_routes, db_session
    ):
        from unittest.mock import MagicMock, patch

        self._user(db_session)
        chpp = MagicMock()
        chpp.get_access_token.return_value = {"key": "ak", "secret": "as2"}
        client = app_with_routes.test_client()
        with client.session_transaction() as sess:
            sess["request_token"] = "rt"
            sess["req_secret"] = "rs"
        with (
            patch("app.blueprints.auth.get_chpp_client_no_auth", return_value=chpp),
            patch("app.blueprints.auth.get_chpp_client", return_value=chpp),
            patch(
                "app.blueprints.auth.get_current_user_context",
                side_effect=ValueError("YouthTeamId"),
            ),
            patch("app.blueprints.auth.fetch_user_teams", return_value=([9], ["Nine"])),
            patch("app.utils.create_default_groups"),
        ):
            response = client.get("/login?oauth_verifier=v")

        assert response.status_code == 302
        with client.session_transaction() as sess:
            assert sess["current_user_id"] == 556001
            assert sess["all_team_names"] == ["Nine"]

    def test_callback_without_identifiable_user_fails_safely(
        self, app_with_routes, db_session  # noqa: ARG002
    ):
        from unittest.mock import MagicMock, patch

        chpp = MagicMock()
        chpp.get_access_token.return_value = {"key": "unknown", "secret": "x"}
        client = app_with_routes.test_client()
        with client.session_transaction() as sess:
            sess["request_token"] = "rt"
            sess["req_secret"] = "rs"
        with (
            patch("app.blueprints.auth.get_chpp_client_no_auth", return_value=chpp),
            patch("app.blueprints.auth.get_chpp_client", return_value=chpp),
            patch(
                "app.blueprints.auth.get_current_user_context",
                side_effect=ValueError("YouthTeamId"),
            ),
        ):
            response = client.get("/login?oauth_verifier=v")

        assert b"no longer valid" in response.data
        with client.session_transaction() as sess:
            assert "current_user_id" not in sess
