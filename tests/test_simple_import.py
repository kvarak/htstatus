"""Simple import test to verify basic functionality."""


def test_basic_imports():
    """Test that we can import basic modules without circular dependencies."""
    # Test that we can import models directly
    import models

    assert models is not None

    # Test that we can import factory
    from app.factory import create_app, db

    assert db is not None
    assert create_app is not None


def test_app_creation_with_test_config():
    """Test that we can create an app with test configuration."""
    from app.factory import create_app
    from config import TestConfig

    # Create app with test config to bypass complex routes
    app = create_app(TestConfig)
    assert app is not None
    assert app.config["TESTING"] is True


def test_database_connection():
    """Test basic database functionality."""
    from app.factory import create_app, db
    from config import TestConfig

    app = create_app(TestConfig)

    with app.app_context():
        # Test database connection
        try:
            # Simple query to test connection
            result = db.session.execute(db.text("SELECT 1 as test"))
            row = result.fetchone()
            assert row[0] == 1
        except Exception as e:
            # If connection fails, it's likely a configuration issue
            # but the test framework is working
            raise AssertionError(f"Database connection failed: {e}") from None
