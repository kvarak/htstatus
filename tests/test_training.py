"""Tests for app/blueprints/training.py"""


def test_module_imports():
    """Test that training blueprint module imports without errors."""
    import app.blueprints.training

    assert app.blueprints.training is not None
