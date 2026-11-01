"""Global error pages and error logging to the database."""

from datetime import timedelta


def _error_page(message):
    from app.utils import create_page

    return create_page(template="error.html", title="Error", error=message)


# Keep the error log small on the Pi: drop old rows, skip repeats
ERROR_LOG_RETENTION = timedelta(days=90)
ERROR_LOG_DEDUP_WINDOW = timedelta(hours=1)


def log_error_to_database(error_type, error):
    """Log error to database for production monitoring.

    Rows older than ERROR_LOG_RETENTION are pruned, and an identical error
    (type, message, path) seen within ERROR_LOG_DEDUP_WINDOW is not stored again.

    Args:
        error_type: Type of error ('500', '404', 'Exception')
        error: The exception or error object
    """
    try:
        import traceback

        from flask import current_app, session
        from flask import request as flask_request

        from app import db
        from models import ErrorLog, utc_now

        # Only log errors in production environment
        if current_app.config.get("FLASK_ENV") != "production":
            return

        # Gather error context
        error_message = str(error) if error else "Unknown error"
        stack_trace = None

        # Get stack trace for exceptions
        if hasattr(error, "__traceback__"):
            stack_trace = "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
        elif error_type == "500":
            stack_trace = traceback.format_exc()

        # Get user context from session
        user_id = session.get("current_user_id") if session else None

        # Get request context
        request_path = None
        request_method = None
        user_agent = None

        if flask_request:
            request_path = flask_request.path
            request_method = flask_request.method
            user_agent = (
                flask_request.user_agent.string if flask_request.user_agent else None
            )

        # The failing request may have left the session mid-transaction
        db.session.rollback()

        now = utc_now()
        db.session.query(ErrorLog).filter(
            ErrorLog.timestamp < now - ERROR_LOG_RETENTION
        ).delete(synchronize_session=False)

        already_logged = (
            db.session.query(ErrorLog.id)
            .filter(
                ErrorLog.error_type == error_type,
                ErrorLog.message == error_message,
                ErrorLog.request_path == request_path,
                ErrorLog.timestamp >= now - ERROR_LOG_DEDUP_WINDOW,
            )
            .first()
        )
        if not already_logged:
            db.session.add(
                ErrorLog(
                    error_type=error_type,
                    message=error_message,
                    stack_trace=stack_trace,
                    user_id=user_id,
                    request_path=request_path,
                    request_method=request_method,
                    user_agent=user_agent,
                )
            )
        db.session.commit()

    except Exception as log_error:
        # Don't let logging errors crash the application
        # In production, we might want to log this to a file or syslog
        current_app.logger.error(f"Failed to log error to database: {log_error}")


def register_error_handlers(app):
    """Register global error handlers with the Flask application.

    Args:
        app: Flask application instance
    """

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 Internal Server Error."""
        log_error_to_database("500", error)
        return _error_page("Internal server error occurred"), 500

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found Error."""
        log_error_to_database("404", error)
        return _error_page("Page not found"), 404

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle any unhandled exception."""
        # Don't double-log HTTP errors that have specific handlers
        if hasattr(error, "code") and error.code in [404, 500]:
            raise error

        log_error_to_database("Exception", error)
        return _error_page("An unexpected error occurred"), 500
