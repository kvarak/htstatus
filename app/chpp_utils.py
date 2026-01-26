"""Shared CHPP client utilities.

Provides common CHPP functionality used across blueprints.
"""

from flask import current_app


def get_chpp_client():
    """Get CHPP client based on feature flag configuration.

    Returns the appropriate CHPP client class based on USE_CUSTOM_CHPP
    configuration flag:
    - Custom CHPP (app.chpp.CHPP) if USE_CUSTOM_CHPP is True
    - pychpp (pychpp.CHPP) if USE_CUSTOM_CHPP is False (default)

    This encapsulates the conditional import logic in a single place,
    eliminating duplication across blueprints.

    Returns:
        CHPP: The CHPP client class (either custom or pychpp)

    Example:
        >>> CHPP = get_chpp_client()
        >>> chpp = CHPP(consumer_key, consumer_secret, access_key, access_secret)
        >>> user = chpp.user()
    """
    if current_app.config.get('USE_CUSTOM_CHPP'):
        from app.chpp import CHPP
    else:
        from pychpp import CHPP
    return CHPP
