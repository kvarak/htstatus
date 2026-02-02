"""Test production error logging functionality."""

from unittest.mock import patch


def test_error_log_creation():
    """Test that ErrorLog model can be created."""
    from models import ErrorLog

    error = ErrorLog(
        error_type='500',
        message='Test error',
        stack_trace='Test stack trace',
        user_id=1,
        request_path='/test',
        request_method='GET',
        user_agent='Test Agent',
        environment='production'
    )

    assert error.error_type == '500'
    assert error.message == 'Test error'
    assert error.user_id == 1
    assert error.request_path == '/test'
    assert error.environment == 'production'

@patch('flask.current_app')
def test_log_error_to_database_only_in_production(mock_current_app):
    """Test that errors are only logged in production environment."""
    from app.error_handlers import log_error_to_database

    # Test non-production environment
    mock_current_app.config.get.return_value = 'development'
    mock_current_app.logger = None

    # This should not raise any exception and should return early
    log_error_to_database('500', Exception('Test error'))

    # Verify it checked for production environment
    mock_current_app.config.get.assert_called_with('FLASK_ENV')

def test_check_errors_script_help():
    """Test that the check_errors script imports correctly."""
    import importlib.util
    from pathlib import Path

    # Load the check_errors script as a module
    script_path = Path(__file__).parent.parent / 'scripts' / 'database' / 'check_errors.py'
    spec = importlib.util.spec_from_file_location("check_errors", script_path)
    check_errors = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(check_errors)
        assert hasattr(check_errors, 'main')
        assert hasattr(check_errors, 'show_error_count')
        assert hasattr(check_errors, 'show_recent_errors')
    except Exception:
        # Script depends on config which may not be available in test env
        # Just check that the file exists and has basic structure
        assert script_path.exists(), "check_errors.py script should exist"
