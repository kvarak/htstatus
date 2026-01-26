"""Custom CHPP (Community Hattrick Public Platform) client.

This module provides a drop-in replacement for pychpp with:
- Zero breaking changes (matches pychpp interface exactly)
- OAuth 1.0 authentication with HMAC-SHA1 signatures
- XML parsing for 4 endpoints (managercompendium, teamdetails, players, match)
- YouthTeamId bug fix (handles as optional field)
- Comprehensive error handling
- Easy testing with OAuth1Session mocking

Version: 1.0.0
"""

from app.chpp.client import CHPP
from app.chpp.exceptions import CHPPAuthError, CHPPAPIError, CHPPError

__version__ = "1.0.0"
__all__ = ["CHPP", "CHPPError", "CHPPAuthError", "CHPPAPIError"]
