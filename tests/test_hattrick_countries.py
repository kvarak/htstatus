"""Tests for app/hattrick_countries.py"""

import pytest

from app.hattrick_countries import (
    COUNTRIES,
    get_country_color,
    get_country_display,
    get_country_flag,
    get_country_info,
    get_country_name,
)

UNKNOWN = {"name": "Unknown", "flag": "🏳️", "color": "#6B7280"}


def test_known_country_lookups():
    assert get_country_name(1) == "Sweden"
    assert get_country_flag(1) == "🇸🇪"
    assert get_country_color(1) == "#006AA7"
    assert get_country_info(1) == {"name": "Sweden", "flag": "🇸🇪", "color": "#006AA7"}


@pytest.mark.parametrize("country_id", [None, -1, 999999])
def test_unknown_country_defaults(country_id):
    assert get_country_name(country_id) == UNKNOWN["name"]
    assert get_country_flag(country_id) == UNKNOWN["flag"]
    assert get_country_color(country_id) == UNKNOWN["color"]
    assert get_country_info(country_id) == UNKNOWN


def test_country_display_with_and_without_flag():
    assert get_country_display(1) == "🇸🇪 Sweden"
    assert get_country_display(1, include_flag=False) == "Sweden"
    assert get_country_display(None) == "🏳️ Unknown"


def test_country_data_integrity():
    for country_id, data in COUNTRIES.items():
        assert isinstance(country_id, int)
        assert data["name"], country_id
        assert data["flag"], country_id
        if "color" in data:
            assert data["color"].startswith("#"), country_id
