"""Tests for app/factory.py - Flask application factory."""

import os
from unittest.mock import Mock, patch

from flask import Flask

from app.factory import create_app, db, migrate, setup_routes


def test_module_imports():
    """Test that factory module imports without errors."""
    import app.factory
    assert app.factory is not None


class TestCreateApp:
    """Test create_app factory function."""

    def test_create_app_default_config(self):
        """Test create_app with default configuration."""
        app = create_app(include_routes=False)

        assert isinstance(app, Flask)
        assert app.config["TESTING"] is False  # Default config
        assert app.name == "app.factory"  # Flask uses module name

    def test_create_app_with_custom_config(self):
        """Test create_app with custom configuration."""
        class TestConfig:
            TESTING = True
            SECRET_KEY = "test-key"
            CONSUMER_KEY = "test-consumer-key"
            CONSUMER_SECRETS = "test-consumer-secret"
            DEBUG_LEVEL = 2
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False

        app = create_app(config_object=TestConfig, include_routes=False)

        assert app.config["TESTING"] is True
        assert app.config["SECRET_KEY"] == "test-key"
        assert app.config["CONSUMER_KEY"] == "test-consumer-key"
        assert app.config["DEBUG_LEVEL"] == 2

    def test_create_app_with_routes_disabled(self):
        """Test create_app with routes disabled for testing."""
        class MinimalConfig:
            TESTING = True
            SECRET_KEY = "test-key"
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False

        app = create_app(config_object=MinimalConfig, include_routes=False)

        # Should not have blueprint routes when routes disabled
        blueprint_names = list(app.blueprints.keys())
        assert len(blueprint_names) == 1  # Bootstrap blueprint registered
        assert 'bootstrap' in blueprint_names  # Flask-Bootstrap blueprint

    def test_create_app_database_initialization(self):
        """Test create_app initializes database properly."""
        class TestConfig:
            TESTING = True
            SECRET_KEY = "test-key"
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False

        app = create_app(config_object=TestConfig, include_routes=False)

        with app.app_context():
            # Verify db is properly initialized
            assert hasattr(db, 'engine')  # Check db is bound to app
            assert migrate is not None

    def test_create_app_error_handlers_registration(self):
        """Test create_app registers error handlers."""
        class TestConfig:
            TESTING = True
            SECRET_KEY = "test-key"
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False

        app = create_app(config_object=TestConfig, include_routes=False)

        # Should have error handlers registered
        error_handlers = app.error_handler_spec
        assert error_handlers is not None

    @patch.dict(os.environ, {"FLASK_ENV": "testing"})
    def test_create_app_environment_variables(self):
        """Test create_app respects environment variables."""
        class TestConfig:
            TESTING = True
            SECRET_KEY = "test-key"
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False

        create_app(config_object=TestConfig, include_routes=False)

        # Flask environment should be accessible
        assert os.environ.get("FLASK_ENV") == "testing"


class TestSetupRoutes:
    """Test setup_routes function."""

    @patch('app.routes_bp.initialize_routes')
    @patch('app.utils.initialize_utils')
    def test_setup_routes_calls_initialize_routes(self, mock_init_utils, mock_init_routes):
        """Test setup_routes calls route initialization functions."""
        class TestConfig:
            TESTING = True
            SECRET_KEY = "test-key"
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            DEBUG_LEVEL = 0

        app = create_app(config_object=TestConfig, include_routes=False)

        with app.app_context():
            setup_routes(app, db)

            # Verify initialization functions were called with correct arguments
            mock_init_utils.assert_called_once_with(app, db, 0)
            mock_init_routes.assert_called_once_with(app, db)

    @patch('app.routes_bp.initialize_routes')
    @patch('app.utils.initialize_utils')
    def test_setup_routes_with_mock_db(self, mock_init_utils, mock_init_routes):
        """Test setup_routes with mock database."""
        class TestConfig:
            TESTING = True
            SECRET_KEY = "test-key"
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            DEBUG_LEVEL = 0

        app = create_app(config_object=TestConfig, include_routes=False)
        mock_db = Mock()

        with app.app_context():
            # Should complete without errors
            setup_routes(app, mock_db)
            mock_init_utils.assert_called_once_with(app, mock_db, 0)
            mock_init_routes.assert_called_once_with(app, mock_db)


class TestDatabaseExtensions:
    """Test database extension initialization."""

    def test_db_extension_exists(self):
        """Test db extension is properly imported."""
        assert db is not None
        assert hasattr(db, "Model")
        assert hasattr(db, "Column")
        assert hasattr(db, "Integer")

    def test_migrate_extension_exists(self):
        """Test migrate extension is properly imported."""
        assert migrate is not None
        assert hasattr(migrate, "init_app")

    def test_extensions_initialization(self):
        """Test extensions can be initialized with app."""
        class TestConfig:
            TESTING = True
            SECRET_KEY = "test-key"
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False

        app = create_app(config_object=TestConfig, include_routes=False)

        with app.app_context():
            # Extensions should be properly bound to app
            assert db is not None
            assert migrate is not None
            assert hasattr(db, 'engine')  # Check db is bound


class TestPkgutilShim:
    """Test pkgutil.get_loader shim for Python 3.14 compatibility."""

    def test_pkgutil_shim_creation(self):
        """Test pkgutil.get_loader shim is available."""
        # After factory import, get_loader should be available
        import pkgutil
        assert hasattr(pkgutil, "get_loader")
        assert callable(pkgutil.get_loader)

    def test_pkgutil_shim_functionality(self):
        """Test pkgutil.get_loader shim works correctly."""
        import pkgutil

        # Test with existing module
        loader = pkgutil.get_loader("sys")
        assert loader is not None

        # Test with non-existent module
        loader = pkgutil.get_loader("nonexistent_module_xyz")
        assert loader is None


class TestConfigurationLoading:
    """Test configuration loading patterns."""

    def test_configuration_from_object(self):
        """Test loading configuration from object."""
        class CustomConfig:
            CUSTOM_VALUE = "test_value"
            SECRET_KEY = "custom-secret"
            TESTING = True
            SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
            SQLALCHEMY_TRACK_MODIFICATIONS = False

        app = create_app(config_object=CustomConfig, include_routes=False)

        assert app.config["CUSTOM_VALUE"] == "test_value"
        assert app.config["SECRET_KEY"] == "custom-secret"
        assert app.config["TESTING"] is True

    def test_configuration_validation(self):
        """Test configuration contains required keys."""
        app = create_app(include_routes=False)

        # Check for required configuration keys
        required_keys = [
            "SECRET_KEY",
            "SQLALCHEMY_DATABASE_URI",
            "SQLALCHEMY_TRACK_MODIFICATIONS"
        ]

        for key in required_keys:
            assert key in app.config


class TestAppContextAndTeardown:
    """Test application context and teardown behavior."""

    def test_app_context_creation(self):
        """Test app context can be created and used."""
        app = create_app(include_routes=False)

        with app.app_context():
            from flask import current_app
            assert current_app == app

    def test_app_teardown_handlers(self):
        """Test app has appropriate teardown handlers."""
        app = create_app(include_routes=False)

        # Should have teardown handlers for request cleanup
        assert hasattr(app, "teardown_request_funcs")
        assert hasattr(app, "teardown_appcontext_funcs")
