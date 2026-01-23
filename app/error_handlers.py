"""Standardized error handling utilities for HTStatus application."""

from app.utils import create_page


class HTStatusError(Exception):
    """Base exception class for HTStatus application."""

    def __init__(self, message, error_code=None, template='main.html', title='Error'):
        self.message = message
        self.error_code = error_code
        self.template = template
        self.title = title
        super().__init__(self.message)


class AuthenticationError(HTStatusError):
    """Exception for authentication-related errors."""

    def __init__(self, message="Authentication required"):
        super().__init__(message, error_code='AUTH_001', template='login.html', title='Authentication Required')


class ValidationError(HTStatusError):
    """Exception for data validation errors."""

    def __init__(self, message, field_name=None):
        self.field_name = field_name
        error_code = f'VALIDATION_{field_name.upper()}' if field_name else 'VALIDATION_001'
        super().__init__(message, error_code=error_code)


class TeamAccessError(HTStatusError):
    """Exception for team access permission errors."""

    def __init__(self, message="Access denied for this team"):
        super().__init__(message, error_code='TEAM_ACCESS_001', template='main.html', title='Team Access Error')


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
            **context_vars
        )
    else:
        # Handle string errors or generic exceptions
        message = str(error) if error else "An unexpected error occurred"
        return create_page(
            template='main.html',
            title='Error',
            error=message,
            **context_vars
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
        raise ValidationError("Team ID is required", field_name='team_id')

    try:
        team_id = int(team_id_str)
        if team_id <= 0:
            raise ValidationError("Team ID must be positive", field_name='team_id')
        return team_id
    except (ValueError, TypeError):
        raise ValidationError("Invalid team ID format", field_name='team_id')


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
        raise ValidationError("Player ID is required", field_name='player_id')

    try:
        player_id = int(player_id_str)
        if player_id <= 0:
            raise ValidationError("Player ID must be positive", field_name='player_id')
        return player_id
    except (ValueError, TypeError):
        raise ValidationError("Invalid player ID format", field_name='player_id')
