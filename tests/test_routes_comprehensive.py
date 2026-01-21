"""Comprehensive route testing for HT Status application to achieve 70% coverage."""

import contextlib
import os
from unittest.mock import patch

import pytest

from app.factory import create_app, db
from config import TestConfig
from models import Group, Players, User
from tests.mock_chpp import create_mock_chpp_client


@pytest.fixture(scope='function')
def app_with_routes():
    """Create application for route testing with routes enabled."""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app(TestConfig, include_routes=True)

    with app.app_context():
        db.create_all()
        yield app
        # Aggressive cleanup to prevent hanging
        with contextlib.suppress(Exception):
            db.session.remove()
        with contextlib.suppress(Exception):
            db.session.close_all()
        with contextlib.suppress(Exception):
            db.drop_all()
        with contextlib.suppress(Exception):
            db.engine.dispose()


@pytest.fixture(scope='function')
def routes_client(app_with_routes):
    """Create a test client for the Flask application with routes."""
    return app_with_routes.test_client()


@pytest.fixture(scope='function')
def sample_user(app_with_routes):  # noqa: ARG001
    """Create a sample user for testing."""
    # First, clean up any existing user with this ID
    existing_user = db.session.query(User).filter_by(ht_id=12345).first()
    if existing_user:
        db.session.delete(existing_user)
        db.session.commit()

    user = User(
        ht_id=12345,
        ht_user='testuser',
        username='testuser',
        password='testpass',
        access_key='test_key',
        access_secret='test_secret'
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def authenticated_client(routes_client, sample_user):
    """Create an authenticated client session."""
    with routes_client.session_transaction() as sess:
        sess['current_user'] = sample_user.username
        sess['current_user_id'] = sample_user.ht_id
        sess['all_teams'] = [sample_user.ht_id]
        sess['all_team_names'] = ['Test Team']
        sess['access_key'] = 'mock_access_key'
        sess['access_secret'] = 'mock_access_secret'
    return routes_client


class TestIndexRoute:
    """Test index route functionality."""

    def test_index_route_unauthenticated(self, routes_client):
        """Test index route without authentication."""
        response = routes_client.get('/')
        assert response.status_code == 200
        # Should render index template with login prompt

    def test_index_route_authenticated(self, authenticated_client):
        """Test index route with authenticated user."""
        response = authenticated_client.get('/')
        assert response.status_code == 200


class TestBluerintRoutes:
    """Test blueprint route functionality."""

    def test_login_route(self, routes_client):
        """Test login route."""
        response = routes_client.get('/login')
        assert response.status_code == 200

    def test_logout_route(self, routes_client):
        """Test logout route."""
        response = routes_client.get('/logout')
        assert response.status_code == 302  # Should redirect to /login

    def test_player_route(self, routes_client):
        """Test player route."""
        response = routes_client.get('/player')
        assert response.status_code == 200

    def test_team_route(self, routes_client):
        """Test team route."""
        response = routes_client.get('/team')
        assert response.status_code == 200

    def test_matches_route(self, routes_client):
        """Test matches route."""
        response = routes_client.get('/matches')
        assert response.status_code == 200

    def test_training_route(self, routes_client):
        """Test training route."""
        response = routes_client.get('/training')
        assert response.status_code == 200

    def test_update_route(self, routes_client):
        """Test update route."""
        response = routes_client.get('/update')
        assert response.status_code == 200

    def test_settings_route(self, routes_client):
        """Test settings route."""
        response = routes_client.get('/settings')
        assert response.status_code == 200

    def test_debug_route(self, routes_client):
        """Test debug route."""
        response = routes_client.get('/debug')
        assert response.status_code == 200
class TestTemplateRenderingAndContext:
    """Test template rendering and context variables."""

    def test_main_template_context_unauthenticated(self, routes_client):
        """Test main template context for unauthenticated users."""
        response = routes_client.get('/')
        assert response.status_code == 200
        assert b'HT Status' in response.data or b'Home' in response.data

    def test_main_template_context_authenticated(self, authenticated_client, sample_user):
        """Test main template context for authenticated users."""
        response = authenticated_client.get('/')
        assert response.status_code == 200

    def test_template_version_variables(self, routes_client):
        """Test that templates can access version variables."""
        response = routes_client.get('/')
        assert response.status_code == 200
        # Template should render without version errors

    def test_template_with_user_data(self, authenticated_client, sample_user):
        """Test templates with user data context."""
        from datetime import datetime
        # Create some test data using proper model constructor
        player_data = {
            'ht_id': 123456,
            'first_name': 'Test',
            'nick_name': 'Test',
            'last_name': 'Player',
            'number': 1,
            'category_id': 0,
            'owner_notes': '',
            'age_years': 25,
            'age_days': 100,
            'age': '25.100',
            'next_birthday': datetime(2024, 6, 1),
            'arrival_date': datetime(2024, 1, 1),
            'form': 7,
            'cards': 0,
            'injury_level': 0,
            'statement': '',
            'language': 'English',
            'language_id': 2,
            'agreeability': 3,
            'aggressiveness': 3,
            'honesty': 3,
            'experience': 5,
            'loyalty': 10,
            'specialty': 0,
            'native_country_id': 1,
            'native_league_id': 1,
            'native_league_name': 'Test League',
            'tsi': 1000,
            'salary': 5000,
            'caps': 0,
            'caps_u20': 0,
            'career_goals': 10,
            'career_hattricks': 1,
            'league_goals': 5,
            'cup_goals': 2,
            'friendly_goals': 3,
            'current_team_matches': 20,
            'current_team_goals': 8,
            'national_team_id': None,
            'national_team_name': '',
            'is_transfer_listed': False,
            'team_id': 12345,
            'stamina': 6,
            'keeper': 3,
            'defender': 7,
            'playmaker': 8,
            'winger': 5,
            'passing': 6,
            'scorer': 9,
            'set_pieces': 4,
            'owner': sample_user.ht_id,
            'old_owner': None,
            'mother_club_bonus': False,
            'leadership': 5
        }
        player = Players(player_data)
        db.session.add(player)
        db.session.commit()

        response = authenticated_client.get('/player')
        assert response.status_code == 200


class TestDatabaseAccess:
    """Test database access patterns in routes."""

    def test_user_query_patterns(self, routes_client, sample_user):
        """Test user query patterns used in routes."""
        response = routes_client.get('/')
        assert response.status_code == 200
        # Should handle user queries without errors

    def test_player_query_patterns(self, authenticated_client, sample_user):
        """Test player query patterns."""
        from datetime import datetime
        # Create test players
        for i in range(3):
            player_data = {
                'ht_id': 123456 + i,
                'first_name': f'Test{i}',
                'nick_name': f'Test{i}',
                'last_name': f'Player{i}',
                'number': i + 1,
                'category_id': 0,
                'owner_notes': '',
                'age_years': 25,
                'age_days': 100,
                'age': '25.100',
                'next_birthday': datetime(2024, 6, 1),
                'arrival_date': datetime(2024, 1, 1),
                'form': 7,
                'cards': 0,
                'injury_level': 0,
                'statement': '',
                'language': 'English',
                'language_id': 2,
                'agreeability': 3,
                'aggressiveness': 3,
                'honesty': 3,
                'experience': 5,
                'loyalty': 10,
                'specialty': 0,
                'native_country_id': 1,
                'native_league_id': 1,
                'native_league_name': 'Test League',
                'tsi': 1000,
                'salary': 5000,
                'caps': 0,
                'caps_u20': 0,
                'career_goals': 10,
                'career_hattricks': 1,
                'league_goals': 5,
                'cup_goals': 2,
                'friendly_goals': 3,
                'current_team_matches': 20,
                'current_team_goals': 8,
                'national_team_id': None,
                'national_team_name': '',
                'is_transfer_listed': False,
                'team_id': 12345,
                'stamina': 6,
                'keeper': 3,
                'defender': 7,
                'playmaker': 8,
                'winger': 5,
                'passing': 6,
                'scorer': 9,
                'set_pieces': 4,
                'owner': sample_user.ht_id,
                'old_owner': None,
                'mother_club_bonus': False,
                'leadership': 5
            }
            player = Players(player_data)
            db.session.add(player)
        db.session.commit()

        response = authenticated_client.get('/player')
        assert response.status_code == 200

    def test_group_query_patterns(self, authenticated_client, sample_user):
        """Test group query patterns."""
        # Create test group using correct constructor parameters
        group = Group(
            user_id=sample_user.ht_id,
            name='Test Group',
            order=1,
            textcolor='#000000',
            bgcolor='#ffffff'
        )
        db.session.add(group)
        db.session.commit()

        response = authenticated_client.get('/settings')
        assert response.status_code == 200


class TestSessionHandling:
    """Test session management across routes."""

    def test_session_data_access(self, authenticated_client):
        """Test that routes properly access session data."""
        response = authenticated_client.get('/')
        assert response.status_code == 200

    def test_unauthenticated_access(self, routes_client):
        """Test that routes handle unauthenticated access properly."""
        response = routes_client.get('/')
        assert response.status_code == 200

    @patch('app.blueprints.team.CHPP')
    def test_session_persistence(self, mock_chpp_class, authenticated_client):
        """Test session persistence across multiple requests."""
        # Set up mock CHPP client
        mock_chpp = create_mock_chpp_client()
        mock_chpp_class.return_value = mock_chpp

        response1 = authenticated_client.get('/')
        assert response1.status_code == 200

        response2 = authenticated_client.get('/team')
        assert response2.status_code == 200


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_routes(self, routes_client):
        """Test that invalid routes return 404."""
        response = routes_client.get('/nonexistent')
        assert response.status_code == 404

    def test_malformed_requests(self, routes_client):
        """Test routes with malformed requests."""
        # Test with invalid HTTP methods where not allowed
        response = routes_client.delete('/')
        assert response.status_code in [405, 404]  # Method not allowed or not found

    @patch('app.blueprints.team.CHPP')
    def test_missing_database_data(self, mock_chpp_class, authenticated_client):
        """Test routes when expected database data is missing."""
        # Set up mock CHPP client
        mock_chpp = create_mock_chpp_client()
        mock_chpp_class.return_value = mock_chpp

        # All routes should handle missing data gracefully
        routes_to_test = ['/', '/team', '/player', '/matches', '/training', '/settings']
        for route in routes_to_test:
            response = authenticated_client.get(route)
            assert response.status_code == 200


class TestHelperFunctions:
    """Test helper functions used by routes."""

    def test_create_page_function(self, app_with_routes):
        """Test create_page helper function."""
        with app_with_routes.test_client() as client:
            with client.session_transaction() as sess:
                sess['current_user'] = 'testuser'
                sess['all_teams'] = ['12345']
                sess['all_team_names'] = ['Test Team']

            # Test create_page function with request context
            with app_with_routes.test_request_context():
                from app.utils import create_page
                result = create_page('main.html', 'Test Title')
                assert result is not None  # Should return rendered template

    def test_version_detection(self, app_with_routes):
        """Test version detection in routes initialization."""
        with app_with_routes.app_context():
            # Should handle version detection gracefully
            import app.routes_bp
            assert hasattr(app.routes_bp, 'version')
            assert hasattr(app.routes_bp, 'fullversion')


class TestRouteInitialization:
    """Test route initialization and setup."""

    def test_routes_are_registered(self, app_with_routes):
        """Test that all routes are properly registered."""
        with app_with_routes.app_context():
            # Get all registered routes
            routes = [rule.rule for rule in app_with_routes.url_map.iter_rules()]

            # Check that expected routes are registered
            expected_routes = ['/', '/login', '/logout', '/player', '/team', '/matches', '/training', '/update', '/settings', '/debug']
            for expected_route in expected_routes:
                assert expected_route in routes or any(expected_route in route for route in routes)

    def test_blueprint_registration(self, app_with_routes):
        """Test that blueprint is properly registered."""
        with app_with_routes.app_context():
            # Check that main blueprint is registered
            assert 'main' in app_with_routes.blueprints

    def test_route_configuration_access(self, app_with_routes):
        """Test that routes can access configuration values."""
        with app_with_routes.app_context():
            assert app_with_routes.config['TESTING'] is True
            assert app_with_routes.config['CONSUMER_KEY'] == 'test-consumer-key'


class TestPerformanceBasics:
    """Test basic performance characteristics."""

    def test_route_response_times(self, routes_client):
        """Test that routes respond within reasonable time."""
        import time

        routes_to_test = ['/', '/login', '/debug']
        for route in routes_to_test:
            start = time.time()
            response = routes_client.get(route)
            end = time.time()

            assert response.status_code == 200
            assert (end - start) < 2.0  # Should respond within 2 seconds

    def test_concurrent_access_basic(self, routes_client):
        """Test basic concurrent access patterns."""
        import threading

        results = []

        def make_request():
            response = routes_client.get('/')
            results.append(response.status_code)

        threads = [threading.Thread(target=make_request) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert all(status == 200 for status in results)


class TestGlobalVariables:
    """Test global variables and module state."""

    def test_module_initialization(self, app_with_routes):
        """Test that route modules are properly initialized."""
        with app_with_routes.app_context():
            import app.routes_bp

            # Check that global variables are set
            assert app.routes_bp.consumer_key is not None
            assert app.routes_bp.consumer_secret is not None
            assert app.routes_bp.version is not None

    def test_configuration_access(self, app_with_routes):
        """Test configuration access in route modules."""
        with app_with_routes.app_context():
            assert app_with_routes.config.get('DEBUG_LEVEL', 1) >= 0
            assert app_with_routes.config.get('APP_NAME', 'HT Status') is not None
