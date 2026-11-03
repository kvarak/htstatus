"""Tests for AdminPreferences model date range functionality."""

import unittest

from models import AdminPreferences


class TestAdminPreferencesDateRange(unittest.TestCase):
    """Test AdminPreferences date range functionality."""

    def test_default_filter_settings_includes_date_range(self):
        """Test that default filter settings includes date range configuration."""
        preferences = AdminPreferences(user_id=1)
        default_settings = preferences._default_filter_settings()

        # Verify date range structure
        date_range = default_settings["date_range"]
        assert "months" in date_range

        # Verify default value: 1 year
        assert date_range["months"] == 12

        # Verify other settings remain intact
        assert default_settings["hide_admin_users"] is True
        assert default_settings["activity_table_rows"] == 20

    def test_admin_preferences_initialization_with_date_range(self):
        """Test AdminPreferences initialization includes date range."""
        preferences = AdminPreferences(
            user_id=1,
            filter_settings={"date_range": {"months": 3}},
        )

        # Verify filter settings contain date range
        date_range = preferences.filter_settings.get("date_range")
        assert date_range is not None
        assert date_range["months"] == 3


if __name__ == "__main__":
    unittest.main()
