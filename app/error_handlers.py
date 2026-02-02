"""Standardized error handling utilities for HTStatus application."""

from app.utils import create_page


class HTStatusError(Exception):
    """Base exception class for HTStatus application."""

    def __init__(self, message, error_code=None, template="main.html", title="Error"):
        self.message = message
        self.error_code = error_code
        self.template = template
        self.title = title
        super().__init__(self.message)


class AuthenticationError(HTStatusError):
    """Exception for authentication-related errors."""

    def __init__(self, message="Authentication required"):
        super().__init__(
            message,
            error_code="AUTH_001",
            template="login.html",
            title="Authentication Required",
        )


class ValidationError(HTStatusError):
    """Exception for data validation errors."""

    def __init__(self, message, field_name=None):
        self.field_name = field_name
        error_code = (
            f"VALIDATION_{field_name.upper()}" if field_name else "VALIDATION_001"
        )
        super().__init__(message, error_code=error_code)


class TeamAccessError(HTStatusError):
    """Exception for team access permission errors."""

    def __init__(self, message="Access denied for this team"):
        super().__init__(
            message,
            error_code="TEAM_ACCESS_001",
            template="main.html",
            title="Team Access Error",
        )


def handle_error(error, **context_vars):
    """Standardized error handler for all blueprints.

    Args:
        error: HTStatusError or string message
        **context_vars: Additional context variables for template

    Returns:
        Rendered error template with consistent structure
    """
    if isinstance(error, HTStatusError):
        return create_page(
            template=error.template,
            title=error.title,
            error=error.message,
            error_code=error.error_code,
            **context_vars,
        )
    else:
        # Handle string errors or generic exceptions
        message = str(error) if error else "An unexpected error occurred"
        return create_page(
            template="error.html", title="Error", error=message, **context_vars
        )


def validate_team_id(team_id_str):
    """Validate and convert team ID with standardized error handling.

    Args:
        team_id_str: Team ID as string from request

    Returns:
        int: Validated team ID

    Raises:
        ValidationError: If team ID is invalid
    """
    if not team_id_str:
        raise ValidationError("Team ID is required", field_name="team_id")

    try:
        team_id = int(team_id_str)
        if team_id <= 0:
            raise ValidationError("Team ID must be positive", field_name="team_id")
        return team_id
    except (ValueError, TypeError) as err:
        raise ValidationError("Invalid team ID format", field_name="team_id") from err


def validate_player_id(player_id_str):
    """Validate and convert player ID with standardized error handling.

    Args:
        player_id_str: Player ID as string from request

    Returns:
        int: Validated player ID

    Raises:
        ValidationError: If player ID is invalid
    """
    if not player_id_str:
        raise ValidationError("Player ID is required", field_name="player_id")

    try:
        player_id = int(player_id_str)
        if player_id <= 0:
            raise ValidationError("Player ID must be positive", field_name="player_id")
        return player_id
    except (ValueError, TypeError) as err:
        raise ValidationError(
            "Invalid player ID format", field_name="player_id"
        ) from err


def log_error_to_database(error_type, error, request_info=None):
    """Log error to database for production monitoring.

    Args:
        error_type: Type of error ('500', '404', 'Exception')
        error: The exception or error object
        request_info: Request context information
    """
    try:
        import traceback

        from flask import current_app, session
        from flask import request as flask_request

        from app import db
        from models import ErrorLog

        # Only log errors in production environment
        if current_app.config.get('FLASK_ENV') != 'production':
            return

        # Gather error context
        error_message = str(error) if error else "Unknown error"
        stack_trace = None

        # Get stack trace for exceptions
        if hasattr(error, '__traceback__'):
            stack_trace = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        elif error_type == '500':
            stack_trace = traceback.format_exc()

        # Get user context from session
        user_id = session.get('current_user_id') if session else None

        # Get request context
        request_path = None
        request_method = None
        user_agent = None

        if request_info:
            request_path = request_info.get('path')
            request_method = request_info.get('method')
            user_agent = request_info.get('user_agent')
        elif flask_request:
            request_path = flask_request.path
            request_method = flask_request.method
            user_agent = flask_request.user_agent.string if flask_request.user_agent else None

        # Create error log entry
        error_log = ErrorLog(
            error_type=error_type,
            message=error_message,
            stack_trace=stack_trace,
            user_id=user_id,
            request_path=request_path,
            request_method=request_method,
            user_agent=user_agent
        )

        # Save to database
        db.session.add(error_log)
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
        log_error_to_database('500', error)
        return handle_error("Internal server error occurred"), 500

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found Error."""
        log_error_to_database('404', error)
        return handle_error("Page not found"), 404

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle any unhandled exception."""
        # Don't double-log HTTP errors that have specific handlers
        if hasattr(error, 'code') and error.code in [404, 500]:
            raise error

        log_error_to_database('Exception', error)
        return handle_error("An unexpected error occurred"), 500
