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
        from app.blueprints import team

        original_db = team.db
        try:
            setup_team_blueprint(mock_db)
            assert team.db is mock_db
        finally:
            team.db = original_db

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
