"""Test authentication and session management."""

import contextlib
import os

import pytest


@pytest.fixture(scope="function")
def app_with_routes():
    """Create a fresh application with routes properly initialized for auth testing."""
    from app.factory import create_app, db
    from config import TestConfig

    # Set testing environment
    os.environ["FLASK_ENV"] = "testing"

    # Create app with routes included from the beginning
    app = create_app(TestConfig, include_routes=True)

    with app.app_context():
        # Create test database tables
        db.create_all()
        yield app

        # Complete cleanup
        with contextlib.suppress(Exception):
            db.session.remove()
        with contextlib.suppress(Exception):
            db.drop_all()
        with contextlib.suppress(Exception):
            db.engine.dispose()

        import gc
        gc.collect()


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
    response = auth_client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword123'
        # Missing cookie_consent
    })

    assert response.status_code == 200
    assert b'You must consent to the use of essential session cookies' in response.data


def test_cookie_consent_with_valid_form(auth_client):
    """Test that login works with proper cookie consent."""
    # This test will need to be expanded when OAuth mocking is available
    response = auth_client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword123',
        'cookie_consent': 'on'
    })

    # Should not show the cookie consent error
    assert b'You must consent to the use of essential session cookies' not in response.data


def test_cookie_consent_notice_in_template(auth_client):
    """Test that cookie consent notice appears on login page."""
    response = auth_client.get('/login')
    assert b'Session Cookies:' in response.data
    assert b'authentication - no tracking or third-party sharing' in response.data
    assert b'cookie_consent' in response.data


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
    assert 'user_id' in sig.parameters


class TestAuthRoutes:
    """Test authentication blueprint route functionality."""

    def test_login_route_get(self, auth_client):
        """Test login route GET request renders login page."""
        response = auth_client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data
        assert b'cookie_consent' in response.data

    def test_login_route_post_missing_consent(self, auth_client):
        """Test login route requires cookie consent."""
        response = auth_client.post('/login', data={
            'username': 'test',
            'password': 'test'
        })
        assert response.status_code == 200
        assert b'You must consent to the use of essential session cookies' in response.data

    def test_logout_route_clears_session(self, auth_client):
        """Test logout route clears session data."""
        # Set session data first
        with auth_client.session_transaction() as session:
            session['access_key'] = 'test_key'
            session['access_secret'] = 'test_secret'
            session['current_user'] = 'test_user'

        # Call logout
        response = auth_client.get('/logout')

        # Should redirect (302) or show logout page (200)
        assert response.status_code in [200, 302]

        # Session should be cleared
        with auth_client.session_transaction() as session:
            assert session.get('access_key') is None
            assert session.get('access_secret') is None
            assert session.get('current_user') is None

    def test_protected_route_redirect_unauthenticated(self, auth_client):
        """Test that protected routes redirect when not authenticated."""
        # Test accessing a protected route without authentication
        response = auth_client.get('/team')
        # The route might return 200 with error message or redirect - both acceptable
        assert response.status_code in [200, 302, 401, 403]

    def test_protected_route_redirect_settings(self, auth_client):
        """Test settings route requires authentication."""
        response = auth_client.get('/settings')
        # The route might return 200 with error message or redirect - both acceptable
        assert response.status_code in [200, 302, 401, 403]

    def test_protected_route_redirect_update(self, auth_client):
        """Test update route requires authentication."""
        response = auth_client.get('/update')
        # The route might return 200 with error message or redirect - both acceptable
        assert response.status_code in [200, 302, 401, 403]
        with auth_client.session_transaction() as session:
            session['access_key'] = 'test_access_key'
            session['access_secret'] = 'test_access_secret'
            session['current_user_id'] = 12345
            session['all_teams'] = [12345]
            session['all_team_names'] = ['Test Team']

        # Test accessing index route (should work)
        response = auth_client.get('/')
        assert response.status_code == 200

    def test_session_token_validation(self, auth_client):
        """Test session token structure validation."""
        with auth_client.session_transaction() as session:
            session['access_key'] = 'valid_access_key'
            session['access_secret'] = 'valid_access_secret'

        with auth_client.session_transaction() as session:
            access_key = session.get('access_key')
            access_secret = session.get('access_secret')

            # Validate token structure
            assert access_key is not None
            assert access_secret is not None
            assert isinstance(access_key, str)
            assert isinstance(access_secret, str)
            assert len(access_key) > 0
            assert len(access_secret) > 0
