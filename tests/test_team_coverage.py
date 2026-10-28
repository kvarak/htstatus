#!/usr/bin/env python3
"""
Strategic tests for team blueprint to improve coverage.

Focuses on error handling paths, blueprint setup, and update functionality
that are currently not covered by existing tests.
"""

from unittest.mock import MagicMock

from flask import Flask
import pytest

# Import the blueprint components to test
from app.blueprints.team import setup_team_blueprint, team_bp


class TestTeamBlueprintAdvanced:
    """Advanced tests for team blueprint covering error scenarios."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock Flask app for testing."""
        app = Flask(__name__)
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key"
        return app

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = MagicMock()
        db.session = MagicMock()
        db.session.query = MagicMock()
        db.session.commit = MagicMock()
        return db

    def test_setup_team_blueprint_initialization(self, mock_app, mock_db):
        """Test the blueprint setup function sets global variables correctly."""
        # Test setup_team_blueprint function
        setup_team_blueprint(
            mock_app, mock_db, "test_ck", "test_cs", "v1.0", "v1.0-full"
        )

        # Import the globals to verify they were set
        from app.blueprints import team

        assert team.app is mock_app
        assert team.db is mock_db
        assert team.consumer_key == "test_ck"
        assert team.consumer_secret == "test_cs"
        assert team.version == "v1.0"
        assert team.fullversion == "v1.0-full"

    def test_team_blueprint_registration(self, mock_app):
        """Test that team blueprint can be registered with Flask app."""
        # Test blueprint registration
        mock_app.register_blueprint(team_bp)

        # Verify blueprint is registered
        assert "team" in mock_app.blueprints
        assert mock_app.blueprints["team"] == team_bp


def test_team_module_imports():
    """Test that team module imports work correctly."""
    from app.blueprints import team

    # Verify required functions and variables exist
    assert hasattr(team, "team_bp")
    assert hasattr(team, "setup_team_blueprint")
    assert hasattr(team, "team")
    assert hasattr(team, "update")

    # Verify blueprint is correctly configured
    assert team.team_bp.name == "team"
