"""OAuth 1.0 authentication for CHPP API.

Handles request token generation and access token exchange using HMAC-SHA1 signatures.
Uses requests-oauthlib for automatic OAuth signature handling.
"""


from requests_oauthlib import OAuth1Session

from app.chpp.constants import (
    CHPP_ACCESS_TOKEN_URL,
    CHPP_AUTHORIZE_URL,
    CHPP_REQUEST_TOKEN_URL,
)
from app.chpp.exceptions import CHPPAuthError


def get_request_token(
    consumer_key: str,
    consumer_secret: str,
    callback_url: str = "oob",
    scope: str = "",
) -> dict[str, str]:
    """Get OAuth request token from Hattrick CHPP API.

    Step 1 of OAuth 1.0 flow. Generates temporary credentials for user authorization.

    Args:
        consumer_key: CHPP consumer key (from config)
        consumer_secret: CHPP consumer secret (from config)
        callback_url: URL for OAuth callback (default "oob" for manual)
        scope: Permissions scope (default "" for read-only)

    Returns:
        Dictionary with:
            - request_token: Temporary OAuth token
            - request_token_secret: Secret for temporary token
            - url: Authorization URL for user redirect

    Raises:
        CHPPAuthError: If request token fetch fails

    Example:
        >>> auth = get_request_token(key, secret, "http://localhost/callback")
        >>> redirect_user_to(auth["url"])
    """
    try:
        oauth = OAuth1Session(
            client_key=consumer_key,
            client_secret=consumer_secret,
            callback_uri=callback_url,
        )

        # Fetch request token from CHPP
        tokens = oauth.fetch_request_token(CHPP_REQUEST_TOKEN_URL)

        # Build authorization URL
        auth_url = oauth.authorization_url(CHPP_AUTHORIZE_URL, scope=scope)

        return {
            "request_token": tokens.get("oauth_token", ""),
            "request_token_secret": tokens.get("oauth_token_secret", ""),
            "url": auth_url,
        }

    except Exception as e:
        raise CHPPAuthError(f"Failed to get request token: {e}") from e


def get_access_token(
    consumer_key: str,
    consumer_secret: str,
    request_token: str,
    request_token_secret: str,
    verifier: str,
) -> dict[str, str]:
    """Exchange request token for permanent access token.

    Step 3 of OAuth 1.0 flow (after user authorization in step 2).
    Converts temporary credentials into permanent access tokens.

    Args:
        consumer_key: CHPP consumer key (from config)
        consumer_secret: CHPP consumer secret (from config)
        request_token: Temporary token from get_request_token()
        request_token_secret: Secret from get_request_token()
        verifier: OAuth verifier code from callback

    Returns:
        Dictionary with:
            - key: Permanent access token
            - secret: Secret for permanent token

    Raises:
        CHPPAuthError: If access token exchange fails

    Example:
        >>> tokens = get_access_token(key, secret, req_token, req_secret, verifier)
        >>> session["access_key"] = tokens["key"]
        >>> session["access_secret"] = tokens["secret"]
    """
    try:
        oauth = OAuth1Session(
            client_key=consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=request_token,
            resource_owner_secret=request_token_secret,
            verifier=verifier,
        )

        # Exchange temporary tokens for permanent access tokens
        tokens = oauth.fetch_access_token(CHPP_ACCESS_TOKEN_URL)

        return {
            "key": tokens.get("oauth_token", ""),
            "secret": tokens.get("oauth_token_secret", ""),
        }

    except Exception as e:
        raise CHPPAuthError(f"Failed to get access token: {e}") from e
