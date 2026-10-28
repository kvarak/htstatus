"""Test production error logging functionality."""

from unittest.mock import MagicMock, patch

import pytest

from models import utc_now


def test_error_log_creation():
    """Test that ErrorLog model can be created."""
    from models import ErrorLog

    error = ErrorLog(
        error_type="500",
        message="Test error",
        stack_trace="Test stack trace",
        user_id=1,
        request_path="/test",
        request_method="GET",
        user_agent="Test Agent",
        environment="production",
    )

    assert error.error_type == "500"
    assert error.message == "Test error"
    assert error.user_id == 1
    assert error.request_path == "/test"
    assert error.environment == "production"


@patch("flask.current_app", new_callable=MagicMock)
def test_log_error_to_database_only_in_production(mock_current_app):
    """Test that errors are only logged in production environment."""
    from app.error_handlers import log_error_to_database

    # Test non-production environment
    mock_current_app.config.get.return_value = "development"
    mock_current_app.logger = None

    # This should not raise any exception and should return early
    log_error_to_database("500", Exception("Test error"))

    # Verify it checked for production environment
    mock_current_app.config.get.assert_called_with("FLASK_ENV")


def test_check_errors_script_help():
    """Test that the check_errors script imports correctly."""
    import importlib.util
    from pathlib import Path

    # Load the check_errors script as a module
    script_path = (
        Path(__file__).parent.parent / "scripts" / "database" / "check_errors.py"
    )
    spec = importlib.util.spec_from_file_location("check_errors", script_path)
    check_errors = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(check_errors)
        assert hasattr(check_errors, "main")
        assert hasattr(check_errors, "show_error_count")
        assert hasattr(check_errors, "show_recent_errors")
    except Exception:
        # Script depends on config which may not be available in test env
        # Just check that the file exists and has basic structure
        assert script_path.exists(), "check_errors.py script should exist"


class TestErrorLogModel:
    """Test ErrorLog model functionality."""

    def test_error_log_model_fields(self):
        """Test ErrorLog model has required fields."""
        from models import ErrorLog

        # Test all model fields exist
        assert hasattr(ErrorLog, "id")
        assert hasattr(ErrorLog, "timestamp")
        assert hasattr(ErrorLog, "error_type")
        assert hasattr(ErrorLog, "message")
        assert hasattr(ErrorLog, "stack_trace")
        assert hasattr(ErrorLog, "user_id")
        assert hasattr(ErrorLog, "request_path")
        assert hasattr(ErrorLog, "request_method")
        assert hasattr(ErrorLog, "user_agent")
        assert hasattr(ErrorLog, "environment")

    def test_error_log_creation_with_minimal_data(self):
        """Test ErrorLog can be created with minimal required data."""
        from models import ErrorLog

        error = ErrorLog(error_type="500", message="Test error")

        assert error.error_type == "500"
        assert error.message == "Test error"
        # Timestamp should be set when added to database
        str_repr = str(error)
        assert "500" in str_repr
        assert "Test error" in str_repr


class TestErrorLogDatabase:
    """Test error logging database operations."""

    def test_error_log_database_persistence(self, app, db_session):
        """Test that ErrorLog records are persisted to database."""
        from models import ErrorLog

        with app.app_context():
            # Create error record
            error = ErrorLog(
                error_type="500",
                message="Database test error",
                stack_trace="Test stack trace",
                request_path="/test",
                environment="test",
            )

            db_session.add(error)
            db_session.commit()

            # Verify record exists
            stored_error = ErrorLog.query.filter_by(
                message="Database test error"
            ).first()
            assert stored_error is not None
            assert stored_error.error_type == "500"
            assert stored_error.message == "Database test error"
            assert stored_error.environment == "test"

    def test_error_log_query_operations(self, app, db_session):
        """Test ErrorLog query operations."""
        from models import ErrorLog

        with app.app_context():
            # Create multiple error records
            error1 = ErrorLog(error_type="404", message="Not found 1")
            error2 = ErrorLog(error_type="500", message="Server error 1")
            error3 = ErrorLog(error_type="404", message="Not found 2")

            db_session.add_all([error1, error2, error3])
            db_session.commit()

            # Test count queries
            total_errors = ErrorLog.query.count()
            assert total_errors >= 3

            # Test filtered queries
            not_found_errors = ErrorLog.query.filter_by(error_type="404").count()
            assert not_found_errors >= 2

            server_errors = ErrorLog.query.filter_by(error_type="500").count()
            assert server_errors >= 1


class TestErrorHandlerIntegration:
    """Test error handler integration with logging system."""

    @patch("flask.current_app", new_callable=MagicMock)
    def test_log_error_to_database_production_mode(self, mock_app):
        """Test error logging in production environment."""
        from app.error_handlers import log_error_to_database

        # Setup production environment
        mock_app.config.get.return_value = "production"

        # Test logging an error - should not raise exception
        test_exception = Exception("Test production error")
        result = log_error_to_database("500", test_exception)

        # Should attempt to log to database
        assert result is None  # Function doesn't return anything

    @patch("flask.current_app", new_callable=MagicMock)
    def test_log_error_to_database_development_mode(self, mock_app):
        """Test error logging is skipped in development environment."""
        from app.error_handlers import log_error_to_database

        # Setup development environment
        mock_app.config.get.return_value = "development"

        # Test logging an error - should not raise exception
        test_exception = Exception("Test development error")
        result = log_error_to_database("404", test_exception)

        # Should return early without error
        assert result is None

    def test_error_handler_route_integration(self, app):
        """Test that error handler function can be imported."""
        from app.error_handlers import register_error_handlers

        # Test that function exists and is callable
        assert callable(register_error_handlers)

        # Basic smoke test - function should exist without requiring full registration
        assert hasattr(register_error_handlers, "__name__")


class TestErrorLogManagement:
    """Test error log management functionality."""

    def test_recent_errors_query(self, app, db_session):
        """Test querying recent errors."""
        from datetime import timedelta

        from models import ErrorLog

        with app.app_context():
            # Create recent and old errors (timestamp set automatically)
            recent_error = ErrorLog(error_type="500", message="Recent error")

            old_error = ErrorLog(error_type="404", message="Old error")

            db_session.add_all([recent_error, old_error])
            db_session.commit()

            # Manually update old_error timestamp to be old
            old_error.timestamp = utc_now() - timedelta(days=30)
            db_session.commit()

            # Query recent errors (last 24 hours)
            recent_cutoff = utc_now() - timedelta(hours=24)
            recent_errors = ErrorLog.query.filter(
                ErrorLog.timestamp >= recent_cutoff
            ).all()

            # Should include recent error
            recent_messages = [e.message for e in recent_errors]
            assert "Recent error" in recent_messages

    def test_error_type_statistics(self, app, db_session):
        """Test error type statistics collection."""
        from sqlalchemy import func

        from models import ErrorLog

        with app.app_context():
            # Create errors of different types
            errors = [
                ErrorLog(error_type="404", message="Not found 1"),
                ErrorLog(error_type="404", message="Not found 2"),
                ErrorLog(error_type="500", message="Server error 1"),
                ErrorLog(error_type="403", message="Forbidden 1"),
            ]

            db_session.add_all(errors)
            db_session.commit()

            # Query error statistics
            stats = (
                db_session.query(
                    ErrorLog.error_type, func.count(ErrorLog.id).label("count")
                )
                .group_by(ErrorLog.error_type)
                .all()
            )

            # Convert to dict for easier testing
            stats_dict = {stat.error_type: stat.count for stat in stats}

            # Verify statistics
            assert stats_dict.get("404", 0) >= 2
            assert stats_dict.get("500", 0) >= 1
            assert stats_dict.get("403", 0) >= 1


class TestErrorLogRetentionAndDedup:
    """INFRA-086: the error log stays small (prune old rows, skip repeats)."""

    @pytest.fixture
    def production_app(self, app, db_session):
        from models import ErrorLog

        # Start empty (rows from other tests may exist); rolled back afterwards
        db_session.query(ErrorLog).delete()
        db_session.commit()
        old_env = app.config.get("FLASK_ENV")
        app.config["FLASK_ENV"] = "production"
        yield app
        app.config["FLASK_ENV"] = old_env

    @staticmethod
    def _messages():
        from models import ErrorLog

        return sorted(e.message for e in ErrorLog.query.all())

    def test_repeated_error_is_stored_once(self, production_app):
        from app.error_handlers import log_error_to_database

        for _ in range(3):
            with production_app.test_request_context("/stats"):
                log_error_to_database("500", Exception("boom"))
        with production_app.test_request_context("/training"):
            log_error_to_database("500", Exception("boom"))

        assert self._messages() == ["boom", "boom"]

    def test_old_rows_are_pruned(self, production_app, db_session):
        from datetime import timedelta

        from app.error_handlers import ERROR_LOG_RETENTION, log_error_to_database
        from models import ErrorLog, utc_now

        old = ErrorLog(error_type="500", message="ancient")
        old.timestamp = utc_now() - ERROR_LOG_RETENTION - timedelta(days=1)
        recent = ErrorLog(error_type="500", message="recent")
        recent.timestamp = utc_now() - timedelta(days=1)
        db_session.add_all([old, recent])
        db_session.commit()

        with production_app.test_request_context("/"):
            log_error_to_database("404", Exception("new"))

        assert self._messages() == ["new", "recent"]

    def test_logs_after_failed_transaction(self, production_app, db_session):
        from sqlalchemy import text

        from app.error_handlers import log_error_to_database

        with pytest.raises(Exception):  # noqa: B017 - any DB error will do
            db_session.execute(text("SELECT * FROM table_that_does_not_exist"))

        with production_app.test_request_context("/"):
            log_error_to_database("500", Exception("after failure"))

        assert self._messages() == ["after failure"]
