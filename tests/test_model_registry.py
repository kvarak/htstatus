"""Tests for app/model_registry.py - Model registry for circular import resolution."""


import pytest

from app.model_registry import (
    ModelRegistry,
    get_group_model,
    get_match_model,
    get_match_play_model,
    get_player_setting_model,
    get_players_model,
    get_user_model,
)


def test_module_imports():
    """Test that all model registry functions can be imported correctly."""
    assert ModelRegistry is not None
    assert callable(get_user_model)
    assert callable(get_players_model)
    assert callable(get_group_model)
    assert callable(get_player_setting_model)
    assert callable(get_match_model)
    assert callable(get_match_play_model)


class TestModelRegistry:
    """Test ModelRegistry class."""

    def test_register_model(self):
        """Test registering a model class."""
        class TestModel:
            pass

        ModelRegistry.register("TestModel", TestModel)

        assert "TestModel" in ModelRegistry._models
        assert ModelRegistry._models["TestModel"] is TestModel

    def test_get_registered_model(self):
        """Test getting a registered model."""
        # Clear models for this test
        ModelRegistry._models.clear()

        class TestModel:
            pass

        ModelRegistry.register("TestModel", TestModel)
        result = ModelRegistry.get("TestModel")

        assert result is TestModel

    def test_get_unregistered_model_raises_error(self):
        """Test getting an unregistered model raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            ModelRegistry.get("NonExistentModel")

        assert "Model 'NonExistentModel' not found in registry" in str(exc_info.value)

    def test_lazy_initialization(self):
        """Test lazy initialization imports and registers models."""
        # Trigger lazy initialization
        result = ModelRegistry.get("User")

        # Check initialization occurred
        assert ModelRegistry._initialized is True
        assert result is not None

        # Verify all expected models are registered
        assert "User" in ModelRegistry._models
        assert "Players" in ModelRegistry._models
        assert "Group" in ModelRegistry._models
        assert "PlayerSetting" in ModelRegistry._models
        assert "Match" in ModelRegistry._models
        assert "MatchPlay" in ModelRegistry._models

        # Check models are actually classes
        assert hasattr(ModelRegistry._models["User"], '__name__')
        assert hasattr(ModelRegistry._models["Players"], '__name__')
        assert hasattr(ModelRegistry._models["Group"], '__name__')
        assert hasattr(ModelRegistry._models["PlayerSetting"], '__name__')
        assert hasattr(ModelRegistry._models["Match"], '__name__')
        assert hasattr(ModelRegistry._models["MatchPlay"], '__name__')

    def test_lazy_initialization_only_runs_once(self):
        """Test lazy initialization only runs once."""
        class TestModel:
            pass

        # Initialize once
        ModelRegistry.register("TestModel", TestModel)
        ModelRegistry._initialized = True

        # Register another model
        class AnotherModel:
            pass
        ModelRegistry.register("AnotherModel", AnotherModel)

        # Should not re-initialize
        result = ModelRegistry.get("AnotherModel")
        assert result is AnotherModel


class TestConvenienceFunctions:
    """Test convenience functions for getting model classes."""

    def setup_method(self):
        """Reset registry state and register mock models."""
        ModelRegistry._models.clear()
        ModelRegistry._initialized = False

        # Register mock model classes
        self.mock_user = type('User', (), {})
        self.mock_players = type('Players', (), {})
        self.mock_group = type('Group', (), {})
        self.mock_player_setting = type('PlayerSetting', (), {})
        self.mock_match = type('Match', (), {})
        self.mock_match_play = type('MatchPlay', (), {})

        ModelRegistry.register("User", self.mock_user)
        ModelRegistry.register("Players", self.mock_players)
        ModelRegistry.register("Group", self.mock_group)
        ModelRegistry.register("PlayerSetting", self.mock_player_setting)
        ModelRegistry.register("Match", self.mock_match)
        ModelRegistry.register("MatchPlay", self.mock_match_play)
        ModelRegistry._initialized = True

    def test_get_user_model(self):
        """Test get_user_model convenience function."""
        result = get_user_model()
        assert result is self.mock_user

    def test_get_players_model(self):
        """Test get_players_model convenience function."""
        result = get_players_model()
        assert result is self.mock_players

    def test_get_group_model(self):
        """Test get_group_model convenience function."""
        result = get_group_model()
        assert result is self.mock_group

    def test_get_player_setting_model(self):
        """Test get_player_setting_model convenience function."""
        result = get_player_setting_model()
        assert result is self.mock_player_setting

    def test_get_match_model(self):
        """Test get_match_model convenience function."""
        result = get_match_model()
        assert result is self.mock_match

    def test_get_match_play_model(self):
        """Test get_match_play_model convenience function."""
        result = get_match_play_model()
        assert result is self.mock_match_play


class TestIntegration:
    """Test integration scenarios."""

    def test_registry_state_isolation(self):
        """Test that registry state is properly managed."""
        # Start clean
        ModelRegistry._models.clear()
        ModelRegistry._initialized = False

        # Register a model
        class TestModel:
            pass
        ModelRegistry.register("TestModel", TestModel)

        # Verify state
        assert not ModelRegistry._initialized
        assert "TestModel" in ModelRegistry._models

        # Access should not affect initialization state for manual registration
        result = ModelRegistry.get("TestModel")
        assert result is TestModel

    def test_registry_error_handling(self):
        """Test error handling in various scenarios."""
        ModelRegistry._models.clear()
        ModelRegistry._initialized = True  # Bypass initialization

        # Test getting non-existent model
        with pytest.raises(ValueError):
            ModelRegistry.get("DoesNotExist")
