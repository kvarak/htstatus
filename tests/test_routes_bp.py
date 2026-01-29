"""Tests for app/routes_bp.py - Flask routes converted to Blueprint pattern."""

from unittest.mock import Mock, patch

from app.routes_bp import (
    debug,
    get_main_bp,
    index,
    initialize_routes,
    logout,
    matches,
    player,
    routes_bp,
    settings,
    team,
    training,
    update,
)


def test_module_imports():
    """Test that all routes_bp functions can be imported correctly."""
    assert routes_bp is not None
    assert callable(initialize_routes)
    assert callable(get_main_bp)
    assert callable(index)
    assert callable(player)
    assert callable(team)
    assert callable(settings)
    assert callable(logout)
    assert callable(matches)
    assert callable(training)
    assert callable(update)
    assert callable(debug)


class TestRoutesBlueprintObject:
    """Test routes_bp Blueprint object."""

    def test_routes_bp_is_blueprint(self):
        """Test routes_bp is a Flask Blueprint."""
        from flask import Blueprint
        assert isinstance(routes_bp, Blueprint)

    def test_routes_bp_name(self):
        """Test routes_bp has correct name."""
        assert routes_bp.name == "routes"


class TestInitializeRoutes:
    """Test initialize_routes function."""

    @patch('app.routes_bp.Bootstrap')
    @patch('app.utils.get_version_info')
    @patch('app.routes_bp.time')
    def test_initialize_routes_sets_globals(self, mock_time, mock_get_version, mock_bootstrap):
        """Test initialize_routes sets all global variables."""
        # Mock app with config
        mock_app = Mock()
        mock_app.config = Mock()
        mock_app.config.get.side_effect = lambda key, default=None: {
            "CONSUMER_KEY": "test_key",
            "CONSUMER_SECRETS": "test_secret",
            "DEBUG_LEVEL": 2
        }.get(key, default)

        # Mock version info
        mock_get_version.return_value = {
            "versionstr": "2.0.0",
            "fullversion": "2.0.0-dev",
            "version": "2.0"
        }

        # Mock time
        mock_time.strftime.return_value = "2026-01-01 12:00:00"

        # Mock database
        mock_db = Mock()

        # Call initialize_routes
        initialize_routes(mock_app, mock_db)

        # Verify Bootstrap initialized
        mock_bootstrap.assert_called_once_with(mock_app)

        # Verify version detection was called
        mock_get_version.assert_called_once()

        # Verify time formatting was called
        mock_time.strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")

    def test_initialize_routes_with_defaults(self):
        """Test initialize_routes with default config values."""
        from unittest.mock import patch

        # Mock app with minimal config
        mock_app = Mock()
        mock_app.config = Mock()
        mock_app.config.get.side_effect = lambda key, default=None: {
            "CONSUMER_KEY": "dev_key",
            "CONSUMER_SECRETS": "dev_secret",
            "DEBUG_LEVEL": 1
        }.get(key, default)

        mock_db = Mock()

        with patch('app.routes_bp.Bootstrap'), \
             patch('app.utils.get_version_info') as mock_version, \
             patch('app.routes_bp.time') as mock_time:

            mock_version.return_value = {"versionstr": "dev", "fullversion": "dev", "version": "dev"}
            mock_time.strftime.return_value = "test_time"

            # Should not raise any errors
            initialize_routes(mock_app, mock_db)


class TestRouteReferences:
    """Test route function references."""

    @patch('app.blueprints.main.index')
    def test_index_reference(self, mock_main_index):
        """Test index route reference."""
        mock_main_index.return_value = "test_response"
        index()
        mock_main_index.assert_called_once()

    @patch('app.blueprints.player.player')
    def test_player_reference(self, mock_player_func):
        """Test player route reference."""
        mock_player_func.return_value = "test_response"
        player()
        mock_player_func.assert_called_once()

    @patch('app.blueprints.team.team')
    def test_team_reference(self, mock_team_func):
        """Test team route reference."""
        mock_team_func.return_value = "test_response"
        team()
        mock_team_func.assert_called_once()

    @patch('app.blueprints.main.settings')
    def test_settings_reference(self, mock_settings_func):
        """Test settings route reference."""
        mock_settings_func.return_value = "test_response"
        settings()
        mock_settings_func.assert_called_once()

    @patch('app.blueprints.auth.logout')
    def test_logout_reference(self, mock_logout_func):
        """Test logout route reference."""
        mock_logout_func.return_value = "test_response"
        logout()
        mock_logout_func.assert_called_once()

    @patch('app.blueprints.matches.matches')
    def test_matches_reference(self, mock_matches_func):
        """Test matches route reference."""
        mock_matches_func.return_value = "test_response"
        matches()
        mock_matches_func.assert_called_once()

    @patch('app.blueprints.training.training')
    def test_training_reference(self, mock_training_func):
        """Test training route reference."""
        mock_training_func.return_value = "test_response"
        training()
        mock_training_func.assert_called_once()

    @patch('app.blueprints.team.update')
    def test_update_reference(self, mock_update_func):
        """Test update route reference."""
        mock_update_func.return_value = "test_response"
        update()
        mock_update_func.assert_called_once()

    @patch('app.blueprints.main.admin')
    def test_debug_reference(self, mock_admin_func):
        """Test debug route reference."""
        mock_admin_func.return_value = "test_response"
        debug()
        mock_admin_func.assert_called_once()


class TestGetMainBp:
    """Test get_main_bp function."""

    def test_get_main_bp_returns_blueprint(self):
        """Test get_main_bp returns a blueprint."""
        with patch('app.blueprints.main.main_bp') as mock_main_bp:
            result = get_main_bp()
            assert result is mock_main_bp


class TestDynamicAttributeAccess:
    """Test dynamic attribute access."""

    def test_main_bp_dynamic_access(self):
        """Test __getattr__ returns main_bp for backward compatibility."""
        import app.routes_bp as routes_module

        with patch('app.blueprints.main.main_bp') as mock_main_bp:
            result = routes_module.main_bp
            assert result is mock_main_bp

    def test_invalid_attribute_raises_error(self):
        """Test __getattr__ raises AttributeError for invalid attributes."""
        import pytest

        import app.routes_bp as routes_module

        with pytest.raises(AttributeError) as exc_info:
            _ = routes_module.nonexistent_attribute

        assert "has no attribute 'nonexistent_attribute'" in str(exc_info.value)


class TestModuleConstants:
    """Test module-level constants."""

    def test_module_constants_exist(self):
        """Test that expected module constants are defined."""
        import app.routes_bp as routes_module

        assert hasattr(routes_module, 'default_group_order')
        assert hasattr(routes_module, 'logfile')
        assert routes_module.default_group_order == 99
        assert routes_module.logfile == "htplanner.log"


class TestBackwardCompatibility:
    """Test backward compatibility features."""

    def test_blueprint_reference_access(self):
        """Test that blueprint references work for backward compatibility."""
        # Test that the module provides access to route functions
        assert callable(index)
        assert callable(player)
        assert callable(team)
        assert callable(settings)
        assert callable(logout)
        assert callable(matches)
        assert callable(training)
        assert callable(update)
        assert callable(debug)

    def test_initialization_function_exists(self):
        """Test that initialization function is available."""
        assert callable(initialize_routes)
