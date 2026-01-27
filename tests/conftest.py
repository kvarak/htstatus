"""Pytest configuration and fixtures for HT Status tests."""

import contextlib
import gc
import os

import pytest

# Import models to ensure they are registered with SQLAlchemy for all tests
import models  # noqa: F401
from app.factory import create_app, db
from config import TestConfig


def pytest_sessionstart(session):  # noqa: ARG001
    """Called after the Session object has been created."""
    # Ensure clean start for resource tracking
    # Close any existing SQLite connections that might be lingering
    with contextlib.suppress(Exception):
        # Force cleanup of any existing connections
        import gc

        gc.collect()


def pytest_sessionfinish(session, exitstatus):  # noqa: ARG001
    """Called after whole test run finished, right before returning the exit status to the system."""
    # Force complete cleanup to eliminate any remaining connections
    import gc
    import sqlite3

    # Ensure all SQLite connections are closed
    with contextlib.suppress(Exception):
        # Force garbage collection to trigger connection cleanup
        gc.collect()
        # Clear any remaining SQLite objects
        for obj in gc.get_objects():
            if isinstance(obj, sqlite3.Connection):
                with contextlib.suppress(Exception):
                    obj.close()

    # Final garbage collection
    gc.collect()


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    # Set testing environment
    os.environ["FLASK_ENV"] = "testing"

    app = create_app(TestConfig, include_routes=False)

    # Create application context
    with app.app_context():
        # Create test database tables (models imported at module level)
        db.create_all()
        yield app

        # Complete cleanup to eliminate ResourceWarnings
        with contextlib.suppress(Exception):
            # Remove any lingering sessions
            db.session.remove()

        with contextlib.suppress(Exception):
            # Drop all tables
            db.drop_all()

        with contextlib.suppress(Exception):
            # Dispose of the engine and close all connections
            db.engine.dispose()

        # Force garbage collection to clean up any remaining references
        gc.collect()


@pytest.fixture(scope="function", autouse=True)
def cleanup_connections(app):
    """Automatically clean up connections after each test to prevent ResourceWarnings."""
    yield  # Run the test

    # Clean up any connections that might be left open
    with app.app_context(), contextlib.suppress(Exception):
        # Close any active sessions
        db.session.close()


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Create a database session for testing with proper transaction isolation.

    Uses nested savepoint pattern to ensure test isolation even when route
    handlers commit transactions. This prevents test pollution where earlier
    tests contaminate database state for later tests.
    """
    with app.app_context():
        # Get a connection from the engine
        connection = db.engine.connect()
        # Start outer transaction
        transaction = connection.begin()

        # Store original session for restoration
        old_session = db.session

        # Create a scoped session (required by Flask-SQLAlchemy) bound to our connection
        from sqlalchemy.orm import scoped_session, sessionmaker

        session_factory = sessionmaker(bind=connection)
        session = scoped_session(session_factory)

        # Replace Flask-SQLAlchemy's session with our test session
        db.session = session

        # Create a nested savepoint (SAVEPOINT) for test isolation
        # This survives commits that happen during route execution
        connection.begin_nested()

        # Set up event listener to automatically recreate savepoint after commits
        # This ensures each test gets a clean slate even if routes commit
        from sqlalchemy import event

        @event.listens_for(session, "after_transaction_end")
        def restart_savepoint(_session, transaction):
            """Recreate savepoint after transaction ends."""
            if transaction.nested and not transaction._parent.nested:
                connection.begin_nested()

        try:
            yield session
        finally:
            # Clean up: remove session, rollback transaction, close connection
            with contextlib.suppress(Exception):
                session.remove()
            with contextlib.suppress(Exception):
                # Remove event listener to prevent memory leaks
                event.remove(session, "after_transaction_end", restart_savepoint)
            with contextlib.suppress(Exception):
                # Rollback the outer transaction (discards all changes)
                transaction.rollback()
            with contextlib.suppress(Exception):
                # Close the connection
                connection.close()
            with contextlib.suppress(Exception):
                # Restore original session
                db.session = old_session


@pytest.fixture(scope="function")
def authenticated_session(client, db_session):  # noqa: ARG001
    """Create an authenticated session for testing routes that require login."""
    # Mock authentication data
    with client.session_transaction() as session:
        session["access_key"] = "test_access_key"
        session["access_secret"] = "test_access_secret"
        session["current_user"] = "test_user"
        session["all_teams"] = [12345]
        session["all_team_names"] = ["Test Team"]

    yield client


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        "ht_id": 123456,
        "first_name": "Test",
        "nick_name": "TestPlayer",
        "last_name": "Player",
        "age": 25,
        "keeper": 5,
        "defender": 8,
        "playmaker": 6,
        "winger": 7,
        "passing": 6,
        "scorer": 9,
        "set_pieces": 4,
        "experience": 7,
        "loyalty": 8,
        "form": 6,
        "stamina": 8,
        "data_date": "2024-01-01",
    }


@pytest.fixture
def mock_chpp_response():
    """Mock CHPP API response data for testing."""
    return {
        "user": {"userId": 12345, "loginname": "testuser", "supporterTier": "none"},
        "team": {"teamId": 54321, "teamName": "Test Team", "shortTeamName": "Test"},
        "players": [
            {
                "playerId": 123456,
                "firstName": "Test",
                "nickName": "TestPlayer",
                "lastName": "Player",
                "age": 25,
                "keeperSkill": 5,
                "defenderSkill": 8,
                "playmakingSkill": 6,
                "wingerSkill": 7,
                "passingSkill": 6,
                "scoringSkill": 9,
                "setPiecesSkill": 4,
                "experience": 7,
                "loyalty": 8,
                "form": 6,
                "stamina": 8,
            }
        ],
    }


def create_mock_chpp_utilities(user_id=12345, team_ids=None, team_names=None):
    """Create standardized mock for CHPP utilities functions.

    Consolidates CHPP mocking patterns to reduce test duplication.
    Returns tuple of (mock_get_chpp_client, mock_get_context) for use with @patch decorators.

    Args:
        user_id: Mock user ID (default: 12345)
        team_ids: List of team IDs (default: [12345])
        team_names: List of team names (default: ["Test Team"])

    Returns:
        dict: Contains 'get_chpp_client' and 'get_context' mocks

    Example:
        @patch("app.chpp_utilities.get_current_user_context")
        @patch("app.chpp_utilities.get_chpp_client")
        def test_something(self, mock_get_chpp, mock_get_context):
            mocks = create_mock_chpp_utilities()
            mock_get_chpp.return_value = mocks['chpp_instance']
            mock_get_context.return_value = mocks['user_context']
    """
    from unittest.mock import Mock

    if team_ids is None:
        team_ids = [12345]
    if team_names is None:
        team_names = ["Test Team"]

    # Create mock CHPP instance
    mock_chpp_instance = Mock()
    mock_chpp_instance.user = Mock()
    mock_chpp_instance.team = Mock()

    # Create user context data
    user_context = {
        "user": Mock(username="testuser", user_id=user_id, ht_id=user_id),
        "team_ids": team_ids,
        "team_names": team_names,
        "ht_user": "testuser",
        "ht_id": user_id,
    }

    # Create team fetch data
    def mock_fetch_teams(_chpp):
        return team_ids, team_names

    return {
        "chpp_instance": mock_chpp_instance,
        "user_context": user_context,
        "fetch_teams": mock_fetch_teams,
    }

