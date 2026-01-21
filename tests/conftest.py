"""Pytest configuration and fixtures for HT Status tests."""

import contextlib
import gc
import os

import pytest

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


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Set testing environment
    os.environ['FLASK_ENV'] = 'testing'

    app = create_app(TestConfig, include_routes=False)

    # Create application context
    with app.app_context():
        # Create test database tables
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


@pytest.fixture(scope='function', autouse=True)
def cleanup_connections(app):
    """Automatically clean up connections after each test to prevent ResourceWarnings."""
    yield  # Run the test

    # Clean up any connections that might be left open
    with app.app_context(), contextlib.suppress(Exception):
        # Close any active sessions
        db.session.close()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a database session for testing with proper transaction isolation."""
    with app.app_context():
        # Create a nested transaction (savepoint) for proper test isolation
        connection = db.engine.connect()
        transaction = connection.begin()

        # Bind the session to the transaction
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=connection)
        session_instance = Session()

        # Override Flask-SQLAlchemy's session with our test session
        old_session = db.session

        # Create a new scoped session that uses our connection
        from sqlalchemy.orm import scoped_session
        test_session = scoped_session(sessionmaker(bind=connection))
        db.session = test_session

        try:
            yield test_session
        finally:
            # Complete resource cleanup with proper isolation
            with contextlib.suppress(Exception):
                # Rollback all changes made during the test
                test_session.remove()
            with contextlib.suppress(Exception):
                # Rollback the transaction to ensure clean state
                transaction.rollback()
            with contextlib.suppress(Exception):
                # Close the connection
                connection.close()
            with contextlib.suppress(Exception):
                # Restore original session
                db.session = old_session
@pytest.fixture(scope='function')
def authenticated_session(client, db_session):
    """Create an authenticated session for testing routes that require login."""
    # Mock authentication data
    with client.session_transaction() as session:
        session['access_key'] = 'test_access_key'
        session['access_secret'] = 'test_access_secret'
        session['current_user'] = 'test_user'
        session['all_teams'] = [12345]
        session['all_team_names'] = ['Test Team']

    yield client


@pytest.fixture
def sample_player_data():
    """Sample player data for testing."""
    return {
        'ht_id': 123456,
        'first_name': 'Test',
        'nick_name': 'TestPlayer',
        'last_name': 'Player',
        'age': 25,
        'keeper': 5,
        'defender': 8,
        'playmaker': 6,
        'winger': 7,
        'passing': 6,
        'scorer': 9,
        'set_pieces': 4,
        'experience': 7,
        'loyalty': 8,
        'form': 6,
        'stamina': 8,
        'data_date': '2024-01-01'
    }


@pytest.fixture
def mock_chpp_response():
    """Mock CHPP API response data for testing."""
    return {
        'user': {
            'userId': 12345,
            'loginname': 'testuser',
            'supporterTier': 'none'
        },
        'team': {
            'teamId': 54321,
            'teamName': 'Test Team',
            'shortTeamName': 'Test'
        },
        'players': [
            {
                'playerId': 123456,
                'firstName': 'Test',
                'nickName': 'TestPlayer',
                'lastName': 'Player',
                'age': 25,
                'keeperSkill': 5,
                'defenderSkill': 8,
                'playmakingSkill': 6,
                'wingerSkill': 7,
                'passingSkill': 6,
                'scoringSkill': 9,
                'setPiecesSkill': 4,
                'experience': 7,
                'loyalty': 8,
                'form': 6,
                'stamina': 8
            }
        ]
    }
