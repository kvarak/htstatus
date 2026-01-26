"""Model registry to resolve circular import issues.

This module provides a centralized way to access model classes
without creating circular dependencies between models.py and blueprints.
"""

from typing import TypeVar

ModelType = TypeVar("ModelType")


class ModelRegistry:
    """Central registry for model classes to avoid circular imports."""

    _models: dict[str, type] = {}
    _initialized = False

    @classmethod
    def register(cls, name: str, model_class: type) -> None:
        """Register a model class by name."""
        cls._models[name] = model_class

    @classmethod
    def get(cls, name: str) -> type:
        """Get a model class by name."""
        if not cls._initialized:
            cls._lazy_initialize()

        if name not in cls._models:
            raise ValueError(f"Model '{name}' not found in registry")
        return cls._models[name]

    @classmethod
    def _lazy_initialize(cls) -> None:
        """Lazy initialization to avoid circular imports."""
        if cls._initialized:
            return

        # Import models here to avoid circular dependency
        import models

        # Register all model classes
        cls.register("User", models.User)
        cls.register("Players", models.Players)
        cls.register("Group", models.Group)
        cls.register("PlayerSetting", models.PlayerSetting)
        cls.register("Match", models.Match)
        cls.register("MatchPlay", models.MatchPlay)

        cls._initialized = True


# Convenience functions for blueprints
def get_user_model() -> type:
    """Get User model class."""
    return ModelRegistry.get("User")


def get_players_model() -> type:
    """Get Players model class."""
    return ModelRegistry.get("Players")


def get_group_model() -> type:
    """Get Group model class."""
    return ModelRegistry.get("Group")


def get_player_setting_model() -> type:
    """Get PlayerSetting model class."""
    return ModelRegistry.get("PlayerSetting")


def get_match_model() -> type:
    """Get Match model class."""
    return ModelRegistry.get("Match")


def get_match_play_model() -> type:
    """Get MatchPlay model class."""
    return ModelRegistry.get("MatchPlay")
