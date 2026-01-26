"""Main CHPP client class.

Unified interface for CHPP API matching pychpp exactly.
Orchestrates OAuth, XML parsing, and data models.
"""

import xml.etree.ElementTree as ET
from typing import Any

from requests.adapters import HTTPAdapter
from requests_oauthlib import OAuth1Session
from urllib3.util.retry import Retry

from app.chpp.auth import get_access_token as auth_get_access_token
from app.chpp.auth import get_request_token as auth_get_request_token
from app.chpp.constants import (
    CHPP_BASE_URL,
    RETRY_BACKOFF_FACTOR,
    RETRY_REDIRECT,
    RETRY_TOTAL,
)
from app.chpp.exceptions import CHPPAPIError, CHPPAuthError
from app.chpp.models import CHPPMatch, CHPPPlayer, CHPPTeam, CHPPUser
from app.chpp.parsers import parse_players, parse_team, parse_user


class CHPP:
    """Main CHPP client matching pychpp interface exactly.

    Provides OAuth 1.0 authentication and data access for Hattrick CHPP API.
    Drop-in replacement for pychpp with zero breaking changes.

    Attributes:
        consumer_key: CHPP consumer key from config
        consumer_secret: CHPP consumer secret from config
        access_key: OAuth access token (optional for non-authenticated requests)
        access_secret: OAuth access token secret (optional)
        session: OAuth1Session instance for authenticated requests

    Example:
        # OAuth flow
        >>> chpp = CHPP(consumer_key, consumer_secret)
        >>> auth = chpp.get_auth(callback_url="http://localhost/callback")
        >>> # User visits auth["url"] and grants permission
        >>> tokens = chpp.get_access_token(auth["request_token"], auth["request_token_secret"], verifier)

        # Authenticated requests
        >>> chpp = CHPP(consumer_key, consumer_secret, tokens["key"], tokens["secret"])
        >>> user = chpp.user()
        >>> team = chpp.team(ht_id=user._teams_ht_id[0])
        >>> players = team.players()
    """

    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        access_token_key: str | None = None,
        access_token_secret: str | None = None,
    ) -> None:
        """Initialize CHPP client with OAuth credentials.

        Args:
            consumer_key: CHPP consumer key
            consumer_secret: CHPP consumer secret
            access_token_key: OAuth access token (optional)
            access_token_secret: OAuth access token secret (optional)
        """
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_key = access_token_key
        self.access_secret = access_token_secret
        self.session: OAuth1Session | None = None

        # Initialize session if access tokens provided
        if self.access_key and self.access_secret:
            self._open_session()

    def _open_session(self) -> None:
        """Initialize OAuth1Session with retry strategy.

        Sets up:
        - OAuth1Session with HMAC-SHA1 signatures
        - HTTPAdapter with exponential backoff retry
        - Automatic handling of transient failures

        Raises:
            CHPPAuthError: If session initialization fails
        """
        if not self.access_key or not self.access_secret:
            raise CHPPAuthError("Access tokens required for authenticated requests")

        try:
            self.session = OAuth1Session(
                client_key=self.consumer_key,
                client_secret=self.consumer_secret,
                resource_owner_key=self.access_key,
                resource_owner_secret=self.access_secret,
            )

            # Configure retry strategy for transient failures
            retry_strategy = Retry(
                total=RETRY_TOTAL,
                redirect=RETRY_REDIRECT,
                backoff_factor=RETRY_BACKOFF_FACTOR,
                status_forcelist=[500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("https://", adapter)

        except Exception as e:
            raise CHPPAuthError(f"Failed to initialize OAuth session: {e}") from e

    def get_auth(
        self,
        callback_url: str = "oob",
        scope: str = "",
    ) -> dict[str, str]:
        """Get OAuth request token and authorization URL.

        Step 1 of OAuth 1.0 flow.

        Args:
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
            >>> chpp = CHPP(consumer_key, consumer_secret)
            >>> auth = chpp.get_auth(callback_url="http://localhost/callback")
            >>> # Redirect user to auth["url"]
        """
        return auth_get_request_token(
            self.consumer_key,
            self.consumer_secret,
            callback_url,
            scope,
        )

    def get_access_token(
        self,
        request_token: str,
        request_token_secret: str,
        code: str,
    ) -> dict[str, str]:
        """Exchange request token for permanent access token.

        Step 3 of OAuth 1.0 flow (after user authorization).

        Args:
            request_token: Temporary token from get_auth()
            request_token_secret: Secret from get_auth()
            code: OAuth verifier code from callback

        Returns:
            Dictionary with:
                - key: Permanent access token
                - secret: Secret for permanent token

        Raises:
            CHPPAuthError: If access token exchange fails

        Example:
            >>> tokens = chpp.get_access_token(auth["request_token"], auth["request_token_secret"], verifier)
            >>> # Store tokens["key"] and tokens["secret"] in session
        """
        return auth_get_access_token(
            self.consumer_key,
            self.consumer_secret,
            request_token,
            request_token_secret,
            code,
        )

    def request(
        self,
        file: str,
        version: str,
        **params: Any,
    ) -> ET.Element:
        """Make authenticated CHPP API request.

        Low-level method for direct XML access. Most users should use
        user() or team() methods instead.

        Args:
            file: CHPP endpoint name (e.g., "managercompendium")
            version: API version (e.g., "1.6")
            **params: Additional query parameters

        Returns:
            ElementTree root element from XML response

        Raises:
            CHPPAuthError: If not authenticated or session invalid
            CHPPAPIError: If CHPP API returns error code

        Example:
            >>> root = chpp.request("managercompendium", "1.6")
            >>> user_id = root.find(".//Manager/UserId").text
        """
        if not self.session:
            self._open_session()

        if not self.session:
            raise CHPPAuthError("OAuth session not initialized")

        # Build request parameters
        request_params = {
            "file": file,
            "version": version,
            **params,
        }

        try:
            # Make authenticated request
            response = self.session.get(CHPP_BASE_URL, params=request_params)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)

            # Check for CHPP API errors
            error_code_elem = root.find(".//ErrorCode")
            if error_code_elem is not None and error_code_elem.text:
                error_code = int(error_code_elem.text)
                error_message_elem = root.find(".//Error")
                error_message = (
                    error_message_elem.text if error_message_elem is not None else "Unknown error"
                )
                raise CHPPAPIError(error_code, error_message)

            return root

        except CHPPAPIError:
            # Re-raise CHPP API errors
            raise
        except Exception as e:
            # Wrap other errors as auth errors
            raise CHPPAuthError(f"CHPP request failed: {e}") from e

    def user(self) -> CHPPUser:
        """Get current user information.

        Fetches user data from managercompendium endpoint.

        Returns:
            CHPPUser with ht_id, username, team IDs, youth team ID

        Raises:
            CHPPAuthError: If not authenticated
            CHPPAPIError: If CHPP API returns error

        Example:
            >>> user = chpp.user()
            >>> print(user.username, user.ht_id)
            >>> print(f"Teams: {user._teams_ht_id}")
        """
        root = self.request("managercompendium", "1.6")
        return parse_user(root)

    def team(self, ht_id: int) -> CHPPTeam:
        """Get team details including players.

        Fetches team data from teamdetails and players endpoints.

        Args:
            ht_id: Hattrick team ID

        Returns:
            CHPPTeam with name, league info, and players

        Raises:
            CHPPAuthError: If not authenticated
            CHPPAPIError: If CHPP API returns error (e.g., unknown team ID)

        Example:
            >>> team = chpp.team(ht_id=123456)
            >>> print(team.name, team.league_name)
            >>> for player in team.players():
            ...     print(player.first_name, player.scorer)
        """
        # Fetch team details
        team_root = self.request("teamdetails", "3.6", teamId=ht_id)
        team = parse_team(team_root)

        # Fetch players for this team
        players_root = self.request("players", "2.7", teamId=ht_id)
        players = parse_players(players_root)

        # Attach players to team (lazy loading pattern)
        team._players = players

        return team
    def player(self, id_: int) -> "CHPPPlayer":
        """Get individual player details.

        Fetches player data from player endpoint.

        Args:
            id_: Hattrick player ID

        Returns:
            CHPPPlayer with all player attributes

        Raises:
            CHPPAuthError: If not authenticated
            CHPPAPIError: If CHPP API returns error (e.g., unknown player ID)

        Example:
            >>> player = chpp.player(id_=480742036)
            >>> print(player.first_name, player.scorer)
        """
        from app.chpp.parsers import parse_player

        root = self.request("player", "2.4", playerId=id_)
        return parse_player(root)

    def matches_archive(self, id_: int, is_youth: bool = False) -> list["CHPPMatch"]:
        """Get match history for a team.

        Fetches match archive from matches endpoint.

        Args:
            id_: Hattrick team ID
            is_youth: Whether to fetch youth team matches (default: False)

        Returns:
            List of CHPPMatch objects representing team's match history

        Raises:
            CHPPAuthError: If not authenticated
            CHPPAPIError: If CHPP API returns error (e.g., unknown team ID)

        Example:
            >>> matches = chpp.matches_archive(id_=123456)
            >>> for match in matches:
            ...     print(f"{match.home_team_name} {match.home_goals}-{match.away_goals}")
        """
        from app.chpp.parsers import parse_matches

        root = self.request("matches", "2.6", teamId=id_, isYouthTeam=is_youth)
        return parse_matches(root)
