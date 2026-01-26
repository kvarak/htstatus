"""Main CHPP client class.

Unified interface for CHPP API matching pychpp exactly.
Orchestrates OAuth, XML parsing, and data models.
"""

import logging
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

logger = logging.getLogger(__name__)


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
            # Log request details for debugging OAuth issues
            logger.debug(f"CHPP request: file={file}, version={version}, params={params}")
            logger.debug(f"Full request params: {request_params}")

            # Make authenticated GET request
            response = self.session.get(CHPP_BASE_URL, params=request_params)

            # Log response details
            logger.debug(f"CHPP response status: {response.status_code}")
            logger.debug(f"CHPP response headers: {dict(response.headers)}")
            logger.debug(f"CHPP request URL: {response.url}")
            logger.debug(f"CHPP request method: {response.request.method}")
            logger.debug(f"CHPP request headers: {dict(response.request.headers)}")

            # Log Authorization header details (without exposing signature)
            auth_header = response.request.headers.get('Authorization', '')
            if isinstance(auth_header, bytes):
                auth_header = auth_header.decode('utf-8', errors='replace')

            if auth_header.startswith('OAuth '):
                # Parse OAuth params (safe to log since it's public info)
                oauth_params = {}
                for part in auth_header[6:].split(', '):
                    if '=' in part:
                        key, val = part.split('=', 1)
                        # Truncate long values but show structure
                        display_val = val[:40] + '...' if len(val) > 40 else val
                        oauth_params[key] = display_val
                logger.debug(f"OAuth parameters: {oauth_params}")

            # Log request body if present
            if response.request.body:
                logger.debug(f"CHPP request body: {response.request.body[:200]}")

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
            logger.error(f"CHPP request failed: {e}", exc_info=True)
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
        root = self.request("managercompendium", "1.5")
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
        team_root = self.request("teamdetails", "3.7", teamId=ht_id)
        team = parse_team(team_root)

        # Fetch basic players list first
        players_root = self.request("players", "2.7", teamId=ht_id)
        basic_players = parse_players(players_root)

        # Then fetch detailed info for each player to get skills and goal data
        detailed_players = []
        for basic_player in basic_players:
            try:
                print(f"[DEBUG] Fetching detailed info for player {basic_player.player_id} ({basic_player.first_name} {basic_player.last_name})")
                detailed_player = self.player(basic_player.player_id)
                print(f"[DEBUG] Success: {detailed_player.first_name} {detailed_player.last_name}, goals_current_team={getattr(detailed_player, 'goals_current_team', 'MISSING')}, matches_current_team={getattr(detailed_player, 'matches_current_team', 'MISSING')}, career_goals={getattr(detailed_player, 'career_goals', 'MISSING')}")
                detailed_players.append(detailed_player)
            except Exception as e:
                # If individual player fetch fails, use basic info
                print(f"[WARNING] Failed to fetch details for player {basic_player.player_id}: {e}")
                print(f"[DEBUG] Using basic info: goals_current_team={getattr(basic_player, 'goals_current_team', 'MISSING')}")
                detailed_players.append(basic_player)

        # Attach detailed players to team
        team._players = detailed_players

        return team
    def player(self, id_: int) -> "CHPPPlayer":
        """Get individual player details.

        Fetches player data from playerdetails endpoint.

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

        # Use playerdetails endpoint with playerID parameter (GET request)
        # Try latest version and include match info to ensure all goal fields are available
        root = self.request("playerdetails", "3.1", playerID=id_, includeMatchInfo="true")
        print(f"[DEBUG] API 3.1 request for player {id_}")
        return parse_player(root)

    def matches_archive(self, id_: int, is_youth: bool = False) -> list["CHPPMatch"]:
        """Get match history for a team.

        Fetches match archive from matchesarchive endpoint.

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

        # Use matchesarchive endpoint with teamID parameter (GET request)
        root = self.request("matchesarchive", "1.5", teamID=id_, isYouthTeam=is_youth)
        return parse_matches(root)
