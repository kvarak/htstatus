"""CHPP API constants and configuration.

Hattrick CHPP API endpoints, versions, and error code mappings.
"""

# OAuth Endpoints
CHPP_REQUEST_TOKEN_URL = "https://chpp.hattrick.org/oauth/request_token.ashx"
CHPP_ACCESS_TOKEN_URL = "https://chpp.hattrick.org/oauth/access_token.ashx"
CHPP_AUTHORIZE_URL = "https://chpp.hattrick.org/oauth/authorize.aspx"

# API Base URL
CHPP_BASE_URL = "https://chpp.hattrick.org/chppxml.ashx"

# CHPP Error Codes (from TEST-016 research)
# Source: https://chpp.hattrick.org/
ERROR_CODES = {
    50: "Unknown team ID",
    51: "Unknown match ID",
    52: "Unknown action type",
    54: "Unknown youth team ID",
    55: "Unknown youth player ID",
    56: "Unknown player ID",
    59: "Team not owned by user",
    70: "Challenge error (multiple sub-cases)",
    # Additional error codes to be added as discovered
}

# Retry Strategy Configuration
RETRY_TOTAL = 5
RETRY_BACKOFF_FACTOR = 0.5
RETRY_REDIRECT = 5
