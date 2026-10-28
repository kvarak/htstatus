"""Tests for app/chpp/exceptions.py"""

import pytest

from app.chpp.exceptions import CHPPAPIError, CHPPAuthError, CHPPError


def test_exception_hierarchy():
    assert issubclass(CHPPAuthError, CHPPError)
    assert issubclass(CHPPAPIError, CHPPError)
    assert issubclass(CHPPError, Exception)


def test_api_error_known_code_message():
    error = CHPPAPIError(50, "team 123 missing")

    assert error.code == 50
    assert error.message == "team 123 missing"
    assert str(error) == "CHPP Error 50 (Unknown team ID): team 123 missing"


def test_api_error_unknown_code_message():
    error = CHPPAPIError(999, "boom")

    assert str(error) == "CHPP Error 999 (Unknown CHPP error): boom"


def test_api_error_is_catchable_as_base():
    with pytest.raises(CHPPError):
        raise CHPPAPIError(56, "no player")
