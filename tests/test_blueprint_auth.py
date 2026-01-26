"""
Comprehensive tests for authentication blueprint to achieve 80% coverage.
Tests OAuth flows, session management, and user authentication logic.
"""

import os
from unittest.mock import Mock, patch

import pytest
from werkzeug.security import generate_password_hash

from app.factory import create_app, db
from config import TestConfig
from models import User


@pytest.fixture(scope="function")
def auth_app():
    """Create application for authentication testing with transaction isolation."""
    os.environ["FLASK_ENV"] = "testing"
    app = create_app(TestConfig, include_routes=True)

    with app.app_context():
        # Create tables using the same pattern as conftest.py
        db.create_all()

        # Create connection and begin transaction for test isolation
        from sqlalchemy.orm import sessionmaker

        connection = db.engine.connect()
        transaction = connection.begin()

        # Configure session to use this connection
        session_factory = sessionmaker(bind=connection)
        scoped_session_test = db.scoped_session(session_factory)

        # Store original session to restore later
        original_session = db.session
        db.session = scoped_session_test

        yield app

        # Cleanup: restore session and rollback transaction
        db.session = original_session
        scoped_session_test.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(auth_app):
    """Create test client."""
    return auth_app.test_client()


@pytest.fixture(scope="function")
def sample_user(auth_app):  # noqa: ARG001
    """Create a sample user for testing."""
    user = User(
        ht_id=12345,
        ht_user="testuser",
        username="testuser",
        password=generate_password_hash("testpass123"),
        access_key="test_access_key",
        access_secret="test_access_secret",
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope="function")
def user_without_tokens(auth_app):  # noqa: ARG001
    """Create user without OAuth tokens."""
    user = User(
        ht_id=67890,
        ht_user="notoken",
        username="notoken",
        password=generate_password_hash("notoken123"),
        access_key=None,
        access_secret=None,
    )
    db.session.add(user)
    db.session.commit()
    return user


class TestAuthBlueprintLoginRoutes:
    """Test login route functionality."""

    def test_login_get_request(self, client):
        """Test GET request to login shows login form."""
        response = client.get("/login")
        assert response.status_code == 200
        # Should render login template
        assert b"login" in response.data.lower() or b"Login" in response.data

    def test_login_redirect_when_already_logged_in(self, client):
        """Test login redirects if user already logged in."""
        with client.session_transaction() as sess:
            sess["current_user"] = "testuser"

        response = client.get("/login")
        assert response.status_code == 302
        assert response.location == "/"

    def test_login_post_missing_username(self, client):
        """Test login with missing username returns error."""
        response = client.post("/login", data={"password": "testpass123"})
        assert response.status_code == 200
        assert b"Username is required" in response.data

    def test_login_post_missing_password(self, client):
        """Test login with missing password returns error."""
        response = client.post("/login", data={"username": "testuser"})
        assert response.status_code == 200
        assert b"Password is required" in response.data

    def test_login_post_short_password(self, client):
        """Test login with short password returns error."""
        response = client.post(
            "/login", data={"username": "testuser", "password": "123"}
        )
        assert response.status_code == 200
        assert b"Password must be at least 8 characters long" in response.data

    @patch("app.chpp_utils.get_chpp_client")
    def test_login_existing_user_with_tokens(
        self, mock_chpp_class, client, sample_user
    ):
        """Test successful login for existing user with OAuth tokens."""
        # Mock CHPP responses
        mock_chpp = Mock()
        mock_user = Mock()
        mock_user._teams_ht_id = [12345]
        mock_team = Mock()
        mock_team.name = "Test Team"

        mock_chpp.user.return_value = mock_user
        mock_chpp.team.return_value = mock_team
        mock_chpp_class.return_value = mock_chpp

        response = client.post(
            "/login", data={"username": "testuser", "password": "testpass123"}
        )

        assert response.status_code == 302
        assert response.location == "/"

        # Check session data
        with client.session_transaction() as sess:
            assert sess["current_user"] == "testuser"
            assert sess["current_user_id"] == 12345
            assert sess["access_key"] == "test_access_key"
            assert sess["access_secret"] == "test_access_secret"

    def test_login_existing_user_wrong_password(self, client, sample_user):
        """Test login with wrong password returns error."""
        response = client.post(
            "/login", data={"username": "testuser", "password": "wrongpass123"}
        )

        assert response.status_code == 200
        assert b"Invalid username or password" in response.data

    @patch("app.blueprints.auth.start_oauth_flow")
    def test_login_existing_user_without_tokens(
        self, mock_start_oauth, client, user_without_tokens
    ):
        """Test login for existing user without OAuth tokens starts OAuth flow."""
        from flask import redirect

        mock_start_oauth.return_value = redirect("/login")

        client.post("/login", data={"username": "notoken", "password": "notoken123"})

        # Should start OAuth flow
        mock_start_oauth.assert_called_once()

        # Check session data for OAuth flow
        with client.session_transaction() as sess:
            assert sess["username"] == "notoken"
            assert "password" in sess

    @patch("app.blueprints.auth.start_oauth_flow")
    def test_login_new_user_registration(self, mock_start_oauth, client):
        """Test new user registration starts OAuth flow."""
        from flask import redirect

        mock_start_oauth.return_value = redirect("/login")

        client.post("/login", data={"username": "newuser", "password": "newpass123"})

        # Should start OAuth flow for new user
        mock_start_oauth.assert_called_once()

        # Check session data for OAuth flow
        with client.session_transaction() as sess:
            assert sess["username"] == "newuser"
            assert "password" in sess


class TestAuthBlueprintOAuthFlow:
    """Test OAuth authentication flow."""

    @patch("app.blueprints.auth.handle_oauth_callback")
    def test_oauth_callback_handling(self, mock_handle_callback, client):
        """Test OAuth callback handling."""
        from flask import redirect

        mock_handle_callback.return_value = redirect("/")

        client.get("/login?oauth_verifier=test_verifier")

        mock_handle_callback.assert_called_once_with("test_verifier")

    @patch("app.chpp_utils.get_chpp_client")
    @patch("app.blueprints.auth.render_template")
    def test_start_oauth_flow_function(
        self, mock_render_template, mock_chpp_class, auth_app
    ):
        """Test start_oauth_flow function."""
        with auth_app.test_request_context():
            mock_chpp = Mock()
            mock_auth = {
                "request_token": "test_token",
                "request_token_secret": "test_secret",
                "url": "http://test-oauth-url",
            }
            mock_chpp.get_auth.return_value = mock_auth
            mock_chpp_class.return_value = mock_chpp
            mock_render_template.return_value = "redirect_html"

            from app.blueprints.auth import start_oauth_flow

            response = start_oauth_flow()

            assert response == "redirect_html"
            mock_chpp.get_auth.assert_called_once()

    @patch("app.chpp_utils.get_chpp_client")
    @patch("app.blueprints.auth.User")
    def test_handle_oauth_callback_new_user(
        self, mock_user_class, mock_chpp_class, auth_app
    ):
        """Test OAuth callback for new user."""
        with auth_app.test_request_context(), auth_app.test_client() as client:
            with client.session_transaction() as sess:
                sess["username"] = "newuser"
                sess["password"] = generate_password_hash("newpass123")

            # Mock CHPP OAuth completion
            mock_chpp = Mock()
            mock_chpp.authorize_user.return_value = {
                "access_token": "new_access_key",
                "access_token_secret": "new_access_secret",
            }
            mock_user = Mock()
            mock_user.ht_id = 99999
            mock_user.ht_user = "NewHTUser"
            mock_user._teams_ht_id = [99999]
            mock_team = Mock()
            mock_team.name = "New Team"

            mock_chpp.user.return_value = mock_user
            mock_chpp.team.return_value = mock_team
            mock_chpp_class.return_value = mock_chpp

            # Mock User creation
            mock_user_instance = Mock()
            mock_user_class.return_value = mock_user_instance

            from app.blueprints.auth import handle_oauth_callback

            with patch.object(db.session, "add"), patch.object(db.session, "commit"):
                response = handle_oauth_callback("test_verifier")

            # Should return a redirect response as string
            assert response is not None
        """Test logout route clears session and redirects."""
        # Set up session
        with client.session_transaction() as sess:
            sess["current_user"] = "testuser"
            sess["access_key"] = "test_key"
            sess["access_secret"] = "test_secret"

        response = client.get("/logout")

        assert response.status_code == 302
        assert "/login" in response.location

        # Check session is cleared
        with client.session_transaction() as sess:
            assert sess.get("current_user") is None
            assert sess.get("access_key") is None


class TestAuthBlueprintErrorHandling:
    """Test error handling in authentication."""

    @patch("app.chpp_utils.get_chpp_client")
    def test_login_chpp_error_handling(self, mock_chpp_class, client, sample_user):
        """Test handling of CHPP errors during login."""
        # Mock CHPP to raise exception
        mock_chpp_class.side_effect = Exception("CHPP API Error")

        response = client.post(
            "/login", data={"username": "testuser", "password": "testpass123"}
        )

        # Should still redirect (graceful error handling)
        assert response.status_code == 302

    @patch("app.chpp_utils.get_chpp_client")
    def test_oauth_callback_error_handling(self, mock_chpp_class, auth_app):
        """Test OAuth callback error handling."""
        with auth_app.test_request_context(), auth_app.test_client() as client:
            with client.session_transaction() as sess:
                sess["username"] = "testuser"

            # Mock CHPP to raise exception
            mock_chpp_class.side_effect = Exception("OAuth Error")

            from app.blueprints.auth import handle_oauth_callback

            response = handle_oauth_callback("invalid_verifier")
            # Should handle error gracefully
            assert response is not None


class TestAuthBlueprintSetup:
    """Test blueprint setup and configuration."""

    def test_setup_auth_blueprint(self, auth_app):
        """Test authentication blueprint setup."""
        with auth_app.app_context():
            from app.blueprints.auth import setup_auth_blueprint

            setup_auth_blueprint(auth_app, db, "test_key", "test_secret")

            # Verify globals are set
            from app.blueprints import auth

            assert auth.app == auth_app
            assert auth.db == db
            assert auth.consumer_key == "test_key"
            assert auth.consumer_secret == "test_secret"

    def test_blueprint_registration(self, auth_app):
        """Test that auth blueprint is properly registered."""
        with auth_app.app_context():
            assert "auth" in auth_app.blueprints

            # Check routes are registered
            routes = [rule.rule for rule in auth_app.url_map.iter_rules()]
            assert "/login" in routes
            assert "/logout" in routes
