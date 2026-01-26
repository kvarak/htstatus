"""Custom exception classes for CHPP client.

Provides structured error handling for OAuth failures and CHPP API errors.
"""

from app.chpp.constants import ERROR_CODES


class CHPPError(Exception):
    """Base exception for all CHPP client errors."""

    pass


class CHPPAuthError(CHPPError):
    """OAuth authentication and authorization failures.

    Raised when:
    - Request token fetch fails
    - Access token exchange fails
    - Invalid OAuth credentials provided
    - OAuth session initialization fails
    """

    pass


class CHPPAPIError(CHPPError):
    """CHPP API errors with structured error codes.

    Attributes:
        code: CHPP error code (50-70 range)
        message: Human-readable error description
    """

    def __init__(self, code: int, message: str):
        """Initialize API error with code and message.

        Args:
            code: CHPP error code
            message: Error description from API response
        """
        self.code = code
        self.message = message
        error_type = ERROR_CODES.get(code, "Unknown CHPP error")
        super().__init__(f"CHPP Error {code} ({error_type}): {message}")
