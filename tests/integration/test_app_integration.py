"""Integration tests for Flask app with services."""

import pytest
from sqlalchemy import text


@pytest.mark.integration
def test_app_with_database_services(app, db_session):  # noqa: ARG001
    """Test Flask app integration with database services."""
    with app.app_context():
        # Test that app can connect to database
        from app.factory import db

        assert db.engine is not None

        # Test basic database operation using modern SQLAlchemy pattern
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT current_database()"))
            db_name = result.fetchone()[0]

            # Should be connected to test database
            assert "test" in db_name.lower() or "htplanner" in db_name.lower()


@pytest.mark.integration
def test_app_configuration_integration(app):
    """Test that app configuration integrates properly with test environment."""
    # Test that testing configuration is active
    assert app.config["TESTING"] is True
    assert app.config["WTF_CSRF_ENABLED"] is False

    # Test that database URL is configured for testing
    db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
    assert "postgresql" in db_uri
    assert db_uri is not None


@pytest.mark.integration
def test_uv_environment_integration():
    """Test that tests run in UV-managed environment."""
    # We should be in some kind of managed environment
    # UV creates .venv directory, so check for that
    import sys

    executable_path = sys.executable

    # Should be running in some virtual environment
    assert ".venv" in executable_path or "virtual" in executable_path.lower()


@pytest.mark.integration
def test_flask_app_request_context(client):
    """Test that Flask request context works in testing."""
    # Test that the client can make a request without hanging
    # Since routes are disabled in testing, expect 404 but test context works
    response = client.get("/nonexistent-route")

    # Should get 404 since no routes are registered in test mode
    assert response.status_code == 404

    # Should have response headers
    assert "Content-Type" in response.headers


@pytest.mark.integration
def test_session_cookie_integration(client):
    """Test that session cookies work in integration tests."""
    with client.session_transaction() as session:
        session["test_key"] = "test_value"

    # Make a request to test session handling (expect 404 but session should work)
    _ = client.get("/test-session")

    # Check that session persists
    with client.session_transaction() as session:
        assert session.get("test_key") == "test_value"


@pytest.mark.integration
def test_database_transaction_isolation(app, db_session):
    """Test that database transactions are properly isolated."""
    with app.app_context():
        # This integration test ensures our transaction handling works

        # Create a temporary table in transaction
        db_session.execute(text("CREATE TEMP TABLE integration_test (id SERIAL)"))

        # Should be able to use the table in same transaction
        db_session.execute(text("INSERT INTO integration_test DEFAULT VALUES"))
        result = db_session.execute(text("SELECT count(*) FROM integration_test"))
        count = result.fetchone()[0]

        assert count == 1

        # Rollback should happen automatically after test
