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
        assert "default_months" in date_range
        assert "start_date" in date_range
        assert "end_date" in date_range

        # Verify default values
        assert date_range["default_months"] == 6
        assert date_range["start_date"] is None
        assert date_range["end_date"] is None

        # Verify other settings remain intact
        assert default_settings["hide_admin_users"] is True
        assert default_settings["activity_table_rows"] == 20

    def test_admin_preferences_initialization_with_date_range(self):
        """Test AdminPreferences initialization includes date range."""
        preferences = AdminPreferences(
            user_id=1,
            filter_settings={
                "date_range": {
                    "default_months": 3,
                    "start_date": "2026-01-01",
                    "end_date": "2026-02-01"
                }
            }
        )

        # Verify filter settings contain date range
        date_range = preferences.filter_settings.get("date_range")
        assert date_range is not None
        assert date_range["default_months"] == 3
        assert date_range["start_date"] == "2026-01-01"
        assert date_range["end_date"] == "2026-02-01"


if __name__ == '__main__':
    unittest.main()
