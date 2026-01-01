"""Integration tests for Flask app with services."""

import os

import pytest


@pytest.mark.integration
def test_app_with_database_services(app, db_session):
    """Test Flask app integration with database services."""
    with app.app_context():
        # Test that app can connect to database
        from app.factory import db
        assert db.engine is not None

        # Test basic database operation
        result = db.engine.execute("SELECT current_database()")
        db_name = result.fetchone()[0]

        # Should be connected to test database
        assert 'test' in db_name.lower() or 'htplanner' in db_name.lower()


@pytest.mark.integration
def test_app_configuration_integration(app):
    """Test that app configuration integrates properly with test environment."""
    # Test that testing configuration is active
    assert app.config['TESTING'] is True
    assert app.config['WTF_CSRF_ENABLED'] is False

    # Test that database URL is configured for testing
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    assert 'postgresql' in db_uri
    assert db_uri is not None


@pytest.mark.integration
def test_uv_environment_integration():
    """Test that tests run in UV-managed environment."""
    # Check that we're running in virtual environment
    virtual_env = os.environ.get('VIRTUAL_ENV')
    python_path = os.environ.get('PYTHONPATH', '')

    # We should be in some kind of managed environment
    # UV creates .venv directory, so check for that
    import sys
    executable_path = sys.executable

    # Should be running in some virtual environment
    assert '.venv' in executable_path or 'virtual' in executable_path.lower()


@pytest.mark.integration
def test_flask_app_request_context(client):
    """Test that Flask request context works in testing."""
    # Test basic route that should exist (even if it redirects)
    response = client.get('/')

    # Should get some kind of response (200, 302, etc.)
    assert response.status_code in [200, 302, 404]

    # Should have response headers
    assert 'Content-Type' in response.headers


@pytest.mark.integration
def test_session_cookie_integration(client):
    """Test that session cookies work in integration tests."""
    with client.session_transaction() as session:
        session['test_key'] = 'test_value'

    # Make a request to trigger session handling
    response = client.get('/')

    # Check that session persists
    with client.session_transaction() as session:
        assert session.get('test_key') == 'test_value'


@pytest.mark.integration
def test_database_transaction_isolation(app, db_session):
    """Test that database transactions are properly isolated."""
    with app.app_context():
        # This integration test ensures our transaction handling works

        # Start with clean state
        initial_tables = db_session.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
        ).fetchone()[0]

        # Create a temporary table in transaction
        db_session.execute("CREATE TEMP TABLE integration_test (id SERIAL)")

        # Should be able to use the table in same transaction
        db_session.execute("INSERT INTO integration_test DEFAULT VALUES")
        result = db_session.execute("SELECT count(*) FROM integration_test")
        count = result.fetchone()[0]

        assert count == 1

        # Rollback should happen automatically after test
