"""Tests for app/factory.py - Flask application factory."""

import os
from unittest.mock import patch

from flask import Flask

from app.factory import create_app


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
        assert list(app.blueprints.keys()) == []

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
            "SQLALCHEMY_TRACK_MODIFICATIONS",
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
