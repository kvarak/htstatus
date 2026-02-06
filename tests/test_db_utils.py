#!/usr/bin/env python3
"""
Tests for database utility functions in scripts/database/db_utils.py.

This test module restores coverage for database utilities and validates
database URL parsing functionality used throughout database scripts.
"""

import os

# Import the module under test
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts', 'database'))
from db_utils import load_database_config, parse_database_url


class TestParseDatabaseUrl:
    """Test the parse_database_url function."""

    def test_parse_complete_url(self):
        """Test parsing a complete PostgreSQL URL with all components."""
        url = "postgresql://user:password@localhost:5432/testdb"
        result = parse_database_url(url)

        assert result == {
            'host': 'localhost',
            'port': '5432',
            'user': 'user',
            'password': 'password',
            'database': 'testdb'
        }

    def test_parse_url_without_password(self):
        """Test parsing URL without password component."""
        url = "postgresql://user@localhost:5432/testdb"
        result = parse_database_url(url)

        assert result == {
            'host': 'localhost',
            'port': '5432',
            'user': 'user',
            'password': None,
            'database': 'testdb'
        }

    def test_parse_url_without_port(self):
        """Test parsing URL without port (should default to 5432)."""
        url = "postgresql://user:password@localhost/testdb"
        result = parse_database_url(url)

        assert result == {
            'host': 'localhost',
            'port': '5432',
            'user': 'user',
            'password': 'password',
            'database': 'testdb'
        }

    def test_parse_url_minimal(self):
        """Test parsing minimal URL with just user and host."""
        url = "postgresql://user@localhost/testdb"
        result = parse_database_url(url)

        assert result == {
            'host': 'localhost',
            'port': '5432',
            'user': 'user',
            'password': None,
            'database': 'testdb'
        }

    def test_parse_url_with_special_characters_in_password(self):
        """Test parsing URL with special characters in password."""
        url = "postgresql://user:p%40ss%3Aword@localhost:5432/testdb"
        result = parse_database_url(url)

        assert result == {
            'host': 'localhost',
            'port': '5432',
            'user': 'user',
            'password': 'p%40ss%3Aword',  # URL-encoded version
            'database': 'testdb'
        }

    def test_parse_url_invalid_prefix(self):
        """Test parsing URL with invalid prefix raises ValueError."""
        url = "mysql://user:password@localhost:3306/testdb"

        with pytest.raises(ValueError, match="Invalid DATABASE_URL format"):
            parse_database_url(url)

    def test_parse_url_missing_auth(self):
        """Test parsing URL without auth section raises ValueError."""
        url = "postgresql://localhost:5432/testdb"

        with pytest.raises(ValueError, match="Invalid DATABASE_URL format: missing auth"):
            parse_database_url(url)

    def test_parse_url_missing_database(self):
        """Test parsing URL without database name raises ValueError."""
        url = "postgresql://user:password@localhost:5432"

        with pytest.raises(ValueError, match="Invalid DATABASE_URL format: missing database"):
            parse_database_url(url)

    def test_parse_url_empty_string(self):
        """Test parsing empty string raises ValueError."""
        url = ""

        with pytest.raises(ValueError, match="Invalid DATABASE_URL format"):
            parse_database_url(url)

    def test_parse_url_with_remote_host(self):
        """Test parsing URL with remote host and different port."""
        url = "postgresql://dbuser:secret@db.example.com:9432/production_db"
        result = parse_database_url(url)

        assert result == {
            'host': 'db.example.com',
            'port': '9432',
            'user': 'dbuser',
            'password': 'secret',
            'database': 'production_db'
        }


class TestLoadDatabaseConfig:
    """Test the load_database_config function."""

    @patch('db_utils.load_dotenv')
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://user:pass@localhost:5432/testdb'})
    def test_load_valid_config(self, mock_load_dotenv):
        """Test loading valid database configuration from environment."""
        result = load_database_config()

        mock_load_dotenv.assert_called_once()
        assert result == {
            'host': 'localhost',
            'port': '5432',
            'user': 'user',
            'password': 'pass',
            'database': 'testdb'
        }

    @patch('db_utils.load_dotenv')
    @patch.dict(os.environ, {}, clear=True)
    def test_load_missing_env_var(self, mock_load_dotenv):
        """Test loading config when DATABASE_URL environment variable is missing."""
        with pytest.raises(ValueError, match="DATABASE_URL environment variable not set"):
            load_database_config()

        mock_load_dotenv.assert_called_once()

    @patch('db_utils.load_dotenv')
    @patch.dict(os.environ, {'DATABASE_URL': ''})
    def test_load_empty_env_var(self, mock_load_dotenv):
        """Test loading config when DATABASE_URL environment variable is empty."""
        with pytest.raises(ValueError, match="DATABASE_URL environment variable not set"):
            load_database_config()

    @patch('db_utils.load_dotenv')
    @patch.dict(os.environ, {'DATABASE_URL': 'invalid-url'})
    def test_load_invalid_url_format(self, mock_load_dotenv):
        """Test loading config with invalid URL format propagates parse error."""
        with pytest.raises(ValueError, match="Invalid DATABASE_URL format"):
            load_database_config()

    @patch('db_utils.load_dotenv')
    @patch.dict(os.environ, {'DATABASE_URL': 'postgresql://user@localhost/testdb'})
    def test_load_minimal_config(self, mock_load_dotenv):
        """Test loading minimal database configuration."""
        result = load_database_config()

        assert result == {
            'host': 'localhost',
            'port': '5432',
            'user': 'user',
            'password': None,
            'database': 'testdb'
        }


class TestDatabaseUtilsIntegration:
    """Integration tests for database utility functions."""

    @patch('db_utils.load_dotenv')
    def test_end_to_end_database_config_loading(self, mock_load_dotenv):
        """Test end-to-end database configuration loading."""
        test_url = "postgresql://htuser:securepass@proddb.example.com:5432/htstatus_production"

        with patch.dict(os.environ, {'DATABASE_URL': test_url}):
            config = load_database_config()

            # Verify all components are correctly parsed
            assert config['host'] == 'proddb.example.com'
            assert config['port'] == '5432'
            assert config['user'] == 'htuser'
            assert config['password'] == 'securepass'
            assert config['database'] == 'htstatus_production'

    def test_multiple_url_parsing_consistency(self):
        """Test that parsing multiple URLs gives consistent results."""
        urls = [
            "postgresql://user1:pass1@host1:5432/db1",
            "postgresql://user2@host2/db2",
            "postgresql://user3:pass3@host3:9999/db3"
        ]

        results = [parse_database_url(url) for url in urls]

        # Verify each result has all required keys
        for result in results:
            assert all(key in result for key in ['host', 'port', 'user', 'password', 'database'])

        # Verify specific parsing
        assert results[0]['host'] == 'host1'
        assert results[1]['password'] is None
        assert results[2]['port'] == '9999'


def test_module_imports():
    """Test that the db_utils module can be imported successfully."""
    import db_utils

    # Verify required functions exist
    assert hasattr(db_utils, 'parse_database_url')
    assert hasattr(db_utils, 'load_database_config')

    # Verify functions are callable
    assert callable(db_utils.parse_database_url)
    assert callable(db_utils.load_database_config)
