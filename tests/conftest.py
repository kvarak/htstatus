"""Pytest configuration and fixtures for HT Status tests."""

import os

import pytest

from app.factory import create_app, db
from config import TestConfig


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

        # Clean up
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a database session for testing with transaction rollback."""
    with app.app_context():
        # Use the existing db.session for simpler compatibility
        # Start a transaction that we can rollback
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Create new session bound to this connection
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=connection)
        session = Session()

        yield session

        # Clean up
        session.close()
        transaction.rollback()
        connection.close()


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
