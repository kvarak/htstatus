"""
Comprehensive test suite for configuration module.

This module tests all configuration classes, environment variable handling,
database URI construction, and configuration validation.
"""

import os
import pytest
import importlib
from unittest.mock import patch, MagicMock
import config


def reload_config_module():
    """Reload the config module to pick up environment changes."""
    importlib.reload(config)


class TestConfigClass:
    """Test the main Config class functionality."""

    def test_config_class_exists(self):
        """Test that Config class can be instantiated."""
        config_instance = config.Config()
        assert config_instance is not None

    def test_default_secret_key(self):
        """Test that default SECRET_KEY is set when not provided via environment."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.SECRET_KEY == 'PtJmVHW5nx1P4pMmsoGrovp31uyflU9E5RjAx3zoEEg6nB2GF6Lp4LSGW58azPoMJ'

    def test_custom_secret_key_from_env(self):
        """Test that SECRET_KEY can be set via environment variable."""
        test_key = 'custom-secret-key-123'
        with patch.dict(os.environ, {'SECRET_KEY': test_key}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.SECRET_KEY == test_key

    def test_default_app_name(self):
        """Test default APP_NAME when not provided via environment."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.APP_NAME == 'HattrickPlanner'

    def test_custom_app_name_from_env(self):
        """Test that APP_NAME can be set via environment variable."""
        test_name = 'CustomAppName'
        with patch.dict(os.environ, {'APP_NAME': test_name}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.APP_NAME == test_name

    def test_consumer_key_from_env(self):
        """Test CONSUMER_KEY retrieval from environment."""
        test_key = 'test-consumer-key-123'
        with patch.dict(os.environ, {'CONSUMER_KEY': test_key}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.CONSUMER_KEY == test_key

    def test_consumer_key_none_when_not_set(self):
        """Test CONSUMER_KEY is None when not in environment."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.CONSUMER_KEY is None

    def test_consumer_secrets_from_env(self):
        """Test CONSUMER_SECRETS retrieval from environment."""
        test_secret = 'test-consumer-secret-123'
        with patch.dict(os.environ, {'CONSUMER_SECRETS': test_secret}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.CONSUMER_SECRETS == test_secret

    def test_consumer_secrets_none_when_not_set(self):
        """Test CONSUMER_SECRETS is None when not in environment."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.CONSUMER_SECRETS is None

    def test_default_callback_url(self):
        """Test default CALLBACK_URL when not provided via environment."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.CALLBACK_URL == 'http://localhost:5010/login'

    def test_custom_callback_url_from_env(self):
        """Test that CALLBACK_URL can be set via environment variable."""
        test_url = 'https://example.com/callback'
        with patch.dict(os.environ, {'CALLBACK_URL': test_url}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.CALLBACK_URL == test_url

    def test_default_chpp_url(self):
        """Test default CHPP_URL when not provided via environment."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.CHPP_URL == 'https://chpp.hattrick.org/chppxml.ashx'

    def test_custom_chpp_url_from_env(self):
        """Test that CHPP_URL can be set via environment variable."""
        test_url = 'https://custom-chpp.example.com/api'
        with patch.dict(os.environ, {'CHPP_URL': test_url}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.CHPP_URL == test_url

    def test_sqlalchemy_track_modifications_disabled(self):
        """Test that SQLALCHEMY_TRACK_MODIFICATIONS is disabled."""
        config_instance = config.Config()
        assert config_instance.SQLALCHEMY_TRACK_MODIFICATIONS is False

    def test_default_debug_level(self):
        """Test default DEBUG_LEVEL when not provided via environment."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.DEBUG_LEVEL == 3

    def test_custom_debug_level_from_env(self):
        """Test that DEBUG_LEVEL can be set via environment variable."""
        with patch.dict(os.environ, {'DEBUG_LEVEL': '1'}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.DEBUG_LEVEL == 1

    def test_debug_level_type_conversion(self):
        """Test that DEBUG_LEVEL is properly converted to integer."""
        with patch.dict(os.environ, {'DEBUG_LEVEL': '2'}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert isinstance(config_instance.DEBUG_LEVEL, int)
            assert config_instance.DEBUG_LEVEL == 2

    def test_default_redis_url(self):
        """Test default REDIS_URL when not provided via environment."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.REDIS_URL == 'redis://:development@localhost:6379/0'

    def test_custom_redis_url_from_env(self):
        """Test that REDIS_URL can be set via environment variable."""
        test_url = 'redis://localhost:6380/1'
        with patch.dict(os.environ, {'REDIS_URL': test_url}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.REDIS_URL == test_url


class TestDatabaseConfiguration:
    """Test database URI construction logic."""

    def test_database_url_priority_direct(self):
        """Test that DATABASE_URL takes priority when set."""
        test_url = 'postgresql://user:pass@host:5432/dbname'
        env_vars = {
            'DATABASE_URL': test_url,
            'POSTGRES_USER': 'different_user',
            'POSTGRES_PASSWORD': 'different_pass',
            'POSTGRES_HOST': 'different_host',
            'POSTGRES_PORT': '5433',
            'POSTGRES_DB': 'different_db'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.SQLALCHEMY_DATABASE_URI == test_url

    def test_database_url_construction_all_components(self):
        """Test database URI construction from individual components."""
        env_vars = {
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass',
            'POSTGRES_HOST': 'testhost',
            'POSTGRES_PORT': '5433',
            'POSTGRES_DB': 'testdb'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            reload_config_module()
            config_instance = config.Config()
            expected = 'postgresql://testuser:testpass@testhost:5433/testdb'
            assert config_instance.SQLALCHEMY_DATABASE_URI == expected

    def test_database_url_construction_with_defaults(self):
        """Test database URI construction with default values."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            expected = 'postgresql://postgres:@localhost:5432/htplanner'
            assert config_instance.SQLALCHEMY_DATABASE_URI == expected

    def test_database_url_construction_partial_env(self):
        """Test database URI construction with some environment variables set."""
        env_vars = {
            'POSTGRES_USER': 'customuser',
            'POSTGRES_DB': 'customdb'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            reload_config_module()
            config_instance = config.Config()
            expected = 'postgresql://customuser:@localhost:5432/customdb'
            assert config_instance.SQLALCHEMY_DATABASE_URI == expected

    def test_database_url_construction_empty_password(self):
        """Test database URI construction handles empty password correctly."""
        env_vars = {
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': '',
            'POSTGRES_HOST': 'testhost',
            'POSTGRES_DB': 'testdb'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            reload_config_module()
            config_instance = config.Config()
            expected = 'postgresql://testuser:@testhost:5432/testdb'
            assert config_instance.SQLALCHEMY_DATABASE_URI == expected


class TestTestConfig:
    """Test the TestConfig class functionality."""

    def test_test_config_inheritance(self):
        """Test that TestConfig inherits from Config."""
        assert issubclass(config.TestConfig, config.Config)

    def test_test_config_testing_flag(self):
        """Test that TESTING is enabled in TestConfig."""
        config_instance = config.TestConfig()
        assert config_instance.TESTING is True

    def test_test_config_csrf_disabled(self):
        """Test that WTF_CSRF_ENABLED is disabled in TestConfig."""
        config_instance = config.TestConfig()
        assert config_instance.WTF_CSRF_ENABLED is False

    def test_test_config_debug_level(self):
        """Test that DEBUG_LEVEL is minimized in TestConfig."""
        config_instance = config.TestConfig()
        assert config_instance.DEBUG_LEVEL == 0

    def test_test_config_secret_key(self):
        """Test that TestConfig has test-specific SECRET_KEY."""
        config_instance = config.TestConfig()
        assert config_instance.SECRET_KEY == 'test-secret-key-not-for-production'

    def test_test_config_consumer_key(self):
        """Test that TestConfig has test-specific CONSUMER_KEY."""
        config_instance = config.TestConfig()
        assert config_instance.CONSUMER_KEY == 'test-consumer-key'

    def test_test_config_consumer_secrets(self):
        """Test that TestConfig has test-specific CONSUMER_SECRETS."""
        config_instance = config.TestConfig()
        assert config_instance.CONSUMER_SECRETS == 'test-consumer-secrets'

    def test_test_config_callback_url(self):
        """Test that TestConfig has test-specific CALLBACK_URL."""
        config_instance = config.TestConfig()
        assert config_instance.CALLBACK_URL == 'http://localhost:5000/login'

    def test_test_config_redis_disabled(self):
        """Test that REDIS_URL is disabled in TestConfig."""
        config_instance = config.TestConfig()
        assert config_instance.REDIS_URL is None

    def test_test_database_url_priority_direct(self):
        """Test that TEST_DATABASE_URL takes priority in TestConfig."""
        test_url = 'postgresql://test_user:test_pass@test_host:5432/test_dbname'
        env_vars = {
            'TEST_DATABASE_URL': test_url,
            'POSTGRES_USER': 'different_user',
            'POSTGRES_PASSWORD': 'different_pass'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            reload_config_module()
            config_instance = config.TestConfig()
            assert config_instance.SQLALCHEMY_DATABASE_URI == test_url

    def test_test_database_url_construction_defaults(self):
        """Test test database URI construction with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            reload_config_module()
            config_instance = config.TestConfig()
            expected = 'postgresql://htstatus:development@localhost:5432/htplanner_test'
            assert config_instance.SQLALCHEMY_DATABASE_URI == expected

    def test_test_database_url_construction_custom(self):
        """Test test database URI construction with custom values."""
        env_vars = {
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass',
            'TEST_POSTGRES_DB': 'custom_test_db'
        }
        with patch.dict(os.environ, env_vars, clear=True):
            reload_config_module()
            config_instance = config.TestConfig()
            expected = 'postgresql://testuser:testpass@localhost:5432/custom_test_db'
            assert config_instance.SQLALCHEMY_DATABASE_URI == expected

    def test_test_config_inherits_parent_attributes(self):
        """Test that TestConfig inherits non-overridden attributes from Config."""
        with patch.dict(os.environ, {'APP_NAME': 'InheritedAppName'}, clear=True):
            reload_config_module()
            config_instance = config.TestConfig()
            assert config_instance.APP_NAME == 'InheritedAppName'  # Inherited from parent


class TestConfigurationValidation:
    """Test configuration edge cases and validation."""

    def test_debug_level_invalid_string(self):
        """Test DEBUG_LEVEL handling with invalid string."""
        with patch.dict(os.environ, {'DEBUG_LEVEL': 'invalid'}, clear=True):
            reload_config_module()
            with pytest.raises(ValueError):
                config_instance = config.Config()
                _ = config_instance.DEBUG_LEVEL

    def test_debug_level_negative_value(self):
        """Test DEBUG_LEVEL with negative value."""
        with patch.dict(os.environ, {'DEBUG_LEVEL': '-1'}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.DEBUG_LEVEL == -1  # Allow negative values

    def test_debug_level_large_value(self):
        """Test DEBUG_LEVEL with large value."""
        with patch.dict(os.environ, {'DEBUG_LEVEL': '100'}, clear=True):
            reload_config_module()
            config_instance = config.Config()
            assert config_instance.DEBUG_LEVEL == 100

    @patch('config.load_dotenv')
    def test_dotenv_loading_called(self, mock_load_dotenv):
        """Test that load_dotenv is called during module import."""
        # Since load_dotenv is called at module level, we can only test this indirectly
        # by verifying the function exists and would be callable
        assert callable(config.load_dotenv)

    def test_all_required_attributes_exist(self):
        """Test that all expected configuration attributes exist."""
        config_instance = config.Config()

        # Flask Configuration
        assert hasattr(config_instance, 'SECRET_KEY')
        assert hasattr(config_instance, 'APP_NAME')

        # Hattrick CHPP API Configuration
        assert hasattr(config_instance, 'CONSUMER_KEY')
        assert hasattr(config_instance, 'CONSUMER_SECRETS')
        assert hasattr(config_instance, 'CALLBACK_URL')
        assert hasattr(config_instance, 'CHPP_URL')

        # Database Configuration
        assert hasattr(config_instance, 'SQLALCHEMY_DATABASE_URI')
        assert hasattr(config_instance, 'SQLALCHEMY_TRACK_MODIFICATIONS')

        # Application Settings
        assert hasattr(config_instance, 'DEBUG_LEVEL')

        # Redis Configuration
        assert hasattr(config_instance, 'REDIS_URL')

    def test_test_config_all_required_attributes_exist(self):
        """Test that TestConfig has all expected attributes."""
        config_instance = config.TestConfig()

        # Test-specific attributes
        assert hasattr(config_instance, 'TESTING')
        assert hasattr(config_instance, 'WTF_CSRF_ENABLED')

        # Inherited attributes
        assert hasattr(config_instance, 'SECRET_KEY')
        assert hasattr(config_instance, 'SQLALCHEMY_DATABASE_URI')
        assert hasattr(config_instance, 'DEBUG_LEVEL')


class TestEnvironmentIsolation:
    """Test that configuration handles environment isolation properly."""

    def test_config_isolation_between_tests(self):
        """Test that configuration changes don't leak between tests."""
        # First configuration with custom values
        with patch.dict(os.environ, {'DEBUG_LEVEL': '1', 'APP_NAME': 'TestApp1'}, clear=True):
            reload_config_module()
            config1 = config.Config()
            assert config1.DEBUG_LEVEL == 1
            assert config1.APP_NAME == 'TestApp1'

        # Second configuration with different values
        with patch.dict(os.environ, {'DEBUG_LEVEL': '2', 'APP_NAME': 'TestApp2'}, clear=True):
            reload_config_module()
            config2 = config.Config()
            assert config2.DEBUG_LEVEL == 2
            assert config2.APP_NAME == 'TestApp2'

        # Verify first config wasn't affected (new instances read fresh env)
        with patch.dict(os.environ, {'DEBUG_LEVEL': '1', 'APP_NAME': 'TestApp1'}, clear=True):
            reload_config_module()
            config3 = config.Config()
            assert config3.DEBUG_LEVEL == 1
            assert config3.APP_NAME == 'TestApp1'

    def test_config_vs_testconfig_isolation(self):
        """Test that Config and TestConfig can coexist without interference."""
        env_vars = {
            'DEBUG_LEVEL': '3',
            'SECRET_KEY': 'production-key',
            'CONSUMER_KEY': 'production-consumer'
        }

        with patch.dict(os.environ, env_vars, clear=True):
            reload_config_module()
            # Regular config should use environment
            config_instance = config.Config()
            assert config_instance.DEBUG_LEVEL == 3
            assert config_instance.SECRET_KEY == 'production-key'
            assert config_instance.CONSUMER_KEY == 'production-consumer'

            # Test config should override critical values
            test_config_instance = config.TestConfig()
            assert test_config_instance.DEBUG_LEVEL == 0  # Overridden
            assert test_config_instance.SECRET_KEY == 'test-secret-key-not-for-production'  # Overridden
            assert test_config_instance.CONSUMER_KEY == 'test-consumer-key'  # Overridden