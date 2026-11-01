"""Custom CHPP (Community Hattrick Public Platform) client.

- OAuth 1.0 authentication with HMAC-SHA1 signatures
- XML parsing of the CHPP files we use (see CHPP in client.py)
- YouthTeamId is optional (users without a youth team)
"""

from app.chpp.client import CHPP
from app.chpp.exceptions import CHPPAPIError, CHPPAuthError, CHPPError

__version__ = "1.0.0"
__all__ = ["CHPP", "CHPPError", "CHPPAuthError", "CHPPAPIError"]
