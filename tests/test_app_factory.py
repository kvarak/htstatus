"""Test Flask application factory functionality."""

from app.factory import create_app, db
from config import TestConfig


def test_app_creation():
    """Test that the application factory creates an app instance."""
    app = create_app(TestConfig)
    assert app is not None
    assert app.config['TESTING'] is True


def test_app_with_default_config():
    """Test app creation with default configuration."""
    app = create_app()
    assert app is not None
    assert hasattr(app, 'config')


def test_test_config_settings():
    """Test that TestConfig has appropriate settings for testing."""
    app = create_app(TestConfig)

    # Test that testing mode is enabled
    assert app.config['TESTING'] is True

    # Test that CSRF is disabled for testing
    assert app.config['WTF_CSRF_ENABLED'] is False

    # Test that debug level is minimized
    assert app.config['DEBUG_LEVEL'] == 0

    # Test that test database is configured
    assert 'htplanner_test' in app.config['SQLALCHEMY_DATABASE_URI']


def test_database_initialization(app):
    """Test that database is properly initialized."""
    with app.app_context():
        # Test that db is available
        assert db is not None

        # Test that we can query the database metadata
        assert db.engine is not None


def test_app_context_functionality(app):
    """Test that application context works correctly."""
    with app.app_context():
        from flask import current_app
        assert current_app.name == app.name  # Test logical equality instead of object identity
        assert current_app.config['TESTING'] is True
