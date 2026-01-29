"""Tests for app/utils.py - Utility functions."""

import subprocess
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.utils import (
    create_page,
    debug_print,
    diff,
    diff_month,
    dprint,
    get_training,
    get_version_info,
    initialize_utils,
)


def test_module_imports():
    """Test that utils module imports without errors."""
    import app.utils
    assert app.utils is not None


class TestInitializeUtils:
    """Test initialize_utils function."""

    def test_initialize_utils_sets_globals(self):
        """Test initialize_utils sets global variables correctly."""
        mock_app = Mock()
        mock_db = Mock()
        debug_level_value = 2

        initialize_utils(mock_app, mock_db, debug_level_value)

        import app.utils
        assert app.utils.db == mock_db
        assert app.utils.debug_level == debug_level_value


class TestDebugPrint:
    """Test debug printing functions."""

    @patch('app.utils.debug_level', 2)
    @patch('builtins.print')
    def test_dprint_prints_when_level_allowed(self, mock_print):
        """Test dprint prints when debug level allows."""
        dprint(1, "test", "message")

        mock_print.assert_called_once()
        # Should include filename and arguments
        args = mock_print.call_args[0]
        assert any("[" in str(arg) and "]" in str(arg) for arg in args)  # filename
        assert "test" in str(args)
        assert "message" in str(args)

    @patch('app.utils.debug_level', 0)
    @patch('builtins.print')
    def test_dprint_doesnt_print_when_level_too_high(self, mock_print):
        """Test dprint doesn't print when debug level too low."""
        dprint(1, "test", "message")

        mock_print.assert_not_called()

    @patch('app.utils.debug_level', None)
    @patch('builtins.print')
    def test_dprint_prints_when_debug_level_none(self, mock_print):
        """Test dprint prints when debug_level is None."""
        dprint(1, "test", "message")

        mock_print.assert_called_once()

    @patch('app.utils.debug_level', 2)
    @patch('builtins.print')
    def test_debug_print_enhanced_format(self, mock_print):
        """Test debug_print with enhanced route formatting."""
        debug_print("test_route", "test_function", "arg1", "arg2")

        mock_print.assert_called_once()
        args = str(mock_print.call_args)
        assert "test_route::test_function()" in args
        assert "arg1" in args
        assert "arg2" in args

    @patch('app.utils.debug_level', 1)
    @patch('builtins.print')
    def test_debug_print_doesnt_print_low_level(self, mock_print):
        """Test debug_print doesn't print when debug level too low."""
        debug_print("test_route", "test_function", "arg1")

        mock_print.assert_not_called()


class TestDateUtilities:
    """Test date and comparison utilities."""

    def test_diff_month_same_year(self):
        """Test diff_month calculation for dates in same year."""
        d1 = datetime(2024, 6, 15)
        d2 = datetime(2024, 3, 10)

        result = diff_month(d1, d2)
        assert result == 3

    def test_diff_month_different_years(self):
        """Test diff_month calculation across years."""
        d1 = datetime(2025, 2, 1)
        d2 = datetime(2024, 11, 1)

        result = diff_month(d1, d2)
        assert result == 3

    def test_diff_month_negative(self):
        """Test diff_month with first date earlier."""
        d1 = datetime(2024, 3, 1)
        d2 = datetime(2024, 6, 1)

        result = diff_month(d1, d2)
        assert result == -3

    def test_diff_with_none_values(self):
        """Test diff function with None values."""
        assert diff(None, 5) is None
        assert diff(5, None) is None
        assert diff(None, None) is None

    def test_diff_with_numeric_values(self):
        """Test diff function with numeric values."""
        assert diff(10, 3) == 7
        assert diff(5.5, 2.2) == pytest.approx(3.3)

    def test_diff_with_lists(self):
        """Test diff function with lists."""
        first = [1, 2, 3, 4]
        second = [2, 4, 5]

        result = diff(first, second)
        assert set(result) == {1, 3}

    def test_diff_with_sets(self):
        """Test diff function with sets."""
        first = {1, 2, 3, 4}
        second = {2, 4, 5}

        result = diff(first, second)
        assert set(result) == {1, 3}


class TestVersionInfo:
    """Test version detection utilities."""

    @patch('subprocess.check_output')
    def test_get_version_info_with_git_tags(self, mock_subprocess):
        """Test get_version_info with git tag output."""
        # Mock git describe output
        mock_subprocess.side_effect = [
            b"3.0-16-gb9fb21c",  # git describe
            b"abc1234 Add feature: new functionality\ndef5678 Implement user system",  # feature commits
            b"5"  # commits since last feature
        ]

        result = get_version_info()

        assert result["version"] == "3.2"  # major=3, features=2
        assert result["fullversion"] == "3.2.5-gb9fb21c"
        assert result["versionstr"] == "3.2.5-gb9fb21c"

    @patch('subprocess.check_output')
    def test_get_version_info_no_features(self, mock_subprocess):
        """Test get_version_info with no feature commits."""
        mock_subprocess.side_effect = [
            b"2.0-10-gab1234",  # git describe
            b"",  # no feature commits
            b"10"  # commits since major version
        ]

        result = get_version_info()

        assert result["version"] == "2.0"  # major=2, features=0
        assert result["fullversion"] == "2.0.10-gab1234"

    @patch('subprocess.check_output', side_effect=subprocess.CalledProcessError(1, 'git'))
    def test_get_version_info_fallback(self, mock_subprocess):
        """Test get_version_info fallback when git fails."""
        result = get_version_info()

        assert result["version"] == "2.0.0"
        assert result["fullversion"] == "2.0.0-dev"
        assert result["versionstr"] == "2.0.0-dev"

    @patch('subprocess.check_output')
    def test_get_version_info_simple_tag(self, mock_subprocess):
        """Test get_version_info with simple tag (no build info)."""
        mock_subprocess.return_value = b"v1.0"

        result = get_version_info()

        assert result["version"] == "v1.0"
        assert result["fullversion"] == "v1.0"
        assert result["versionstr"] == "v1.0"


class TestCreatePage:
    """Test create_page template utility."""

    def setup_method(self):
        """Set up test environment."""
        from app.factory import create_app
        from config import TestConfig

        self.app = create_app(TestConfig, include_routes=False)

    @patch('app.utils.render_template')
    @patch('app.utils.get_version_info')
    def test_create_page_basic(self, mock_version_info, mock_render):
        """Test create_page with basic parameters."""
        mock_version_info.return_value = {
            "version": "2.0", "fullversion": "2.0.0-dev", "versionstr": "2.0.0-dev"
        }
        mock_render.return_value = "rendered_template"

        with self.app.test_request_context():
            result = create_page("test.html", "Test Title")

            assert result == "rendered_template"
            mock_render.assert_called_once()

            # Check template variables
            call_kwargs = mock_render.call_args[1]
            assert call_kwargs["title"] == "Test Title"
            assert call_kwargs["apptitle"] == "HattrickPlanner"  # Matches config.py
            assert call_kwargs["version"] == "2.0"

    @patch('app.utils.render_template')
    @patch('app.utils.get_version_info')
    @patch('models.User')
    def test_create_page_with_session(self, mock_user_model, mock_version_info, mock_render):
        """Test create_page with user session data."""
        mock_version_info.return_value = {
            "version": "2.0", "fullversion": "2.0.0-dev", "versionstr": "2.0.0-dev"
        }
        mock_render.return_value = "rendered_template"

        # Mock User query to return None (no admin role)
        mock_user_model.query.filter_by.return_value.first.return_value = None

        with self.app.test_request_context():
            from flask import session
            session["current_user"] = "testuser"
            session["current_user_id"] = 12345
            session["all_teams"] = [54321]
            session["all_team_names"] = ["Test Team"]

            create_page("test.html", "Test Title")

            call_kwargs = mock_render.call_args[1]
            assert call_kwargs["current_user"] == "testuser"
            assert call_kwargs["current_user_id"] == 12345
            assert call_kwargs["all_teams"] == [54321]

    @patch('app.utils.render_template')
    @patch('app.utils.get_version_info')
    @patch('models.User')
    def test_create_page_with_admin_user(self, mock_user, mock_version_info, mock_render):
        """Test create_page with admin user role."""
        mock_version_info.return_value = {
            "version": "2.0", "fullversion": "2.0.0-dev", "versionstr": "2.0.0-dev"
        }
        mock_render.return_value = "rendered_template"

        # Mock admin user
        admin_user = Mock()
        admin_user.role = "Admin"
        mock_user.query.filter_by.return_value.first.return_value = admin_user

        with self.app.test_client() as client:
            with client.session_transaction() as sess:
                sess["current_user"] = "admin"
                sess["current_user_id"] = 12345

            with self.app.test_request_context():
                from flask import session
                session["current_user"] = "admin"
                session["current_user_id"] = 12345

                create_page("admin.html", "Admin Panel")

                call_kwargs = mock_render.call_args[1]
                assert call_kwargs["role"] == "Admin"

    @patch('app.utils.render_template')
    @patch('app.utils.get_version_info')
    def test_create_page_with_custom_kwargs(self, mock_version_info, mock_render):
        """Test create_page with additional custom template variables."""
        mock_version_info.return_value = {
            "version": "2.0", "fullversion": "2.0.0-dev", "versionstr": "2.0.0-dev"
        }
        mock_render.return_value = "rendered_template"

        with self.app.test_request_context():
            create_page("test.html", "Test", custom_var="custom_value", count=42)

            call_kwargs = mock_render.call_args[1]
            assert call_kwargs["custom_var"] == "custom_value"
            assert call_kwargs["count"] == 42


class TestGetTraining:
    """Test get_training data processing utility."""

    def test_get_training_empty_data(self):
        """Test get_training with empty player data."""
        result = get_training([])
        assert result == ([], {}, {})

    def test_get_training_none_data(self):
        """Test get_training with None player data."""
        result = get_training(None)
        assert result == ([], {}, {})

    def test_get_training_with_players(self):
        """Test get_training with actual player data."""
        # Mock player data
        player1 = Mock()
        player1.ht_id = 12345
        player1.first_name = "John"
        player1.last_name = "Doe"
        player1.data_date = datetime(2024, 1, 15)
        player1.keeper = 5
        player1.defender = 8
        player1.playmaker = 6
        player1.winger = 4
        player1.passing = 7
        player1.scorer = 9
        player1.set_pieces = 3

        player2 = Mock()
        player2.ht_id = 12345  # Same player, different date
        player2.first_name = "John"
        player2.last_name = "Doe"
        player2.data_date = datetime(2024, 2, 15)
        player2.keeper = 6  # Skill improvement
        player2.defender = 8
        player2.playmaker = 7  # Skill improvement
        player2.winger = 4
        player2.passing = 7
        player2.scorer = 9
        player2.set_pieces = 3

        allplayerids, allplayers, playernames = get_training([player1, player2])

        # Check player IDs
        assert 12345 in allplayerids

        # Check player names
        assert playernames[12345] == "John Doe"

        # Check timeline data (sorted by date)
        timeline = allplayers[12345]
        assert len(timeline) == 2
        assert timeline[0][0] == "2024-01-15"  # First date
        assert timeline[1][0] == "2024-02-15"  # Second date

        # Check skills array format [keeper, defender, playmaker, winger, passing, scorer, set_pieces]
        first_skills = timeline[0][1]
        second_skills = timeline[1][1]
        assert first_skills == [5, 8, 6, 4, 7, 9, 3]
        assert second_skills == [6, 8, 7, 4, 7, 9, 3]

    def test_get_training_multiple_players(self):
        """Test get_training with multiple different players."""
        player1 = Mock()
        player1.ht_id = 12345
        player1.first_name = "John"
        player1.last_name = "Doe"
        player1.data_date = datetime(2024, 1, 15)
        player1.keeper = 5
        player1.defender = 8
        player1.playmaker = 6
        player1.winger = 4
        player1.passing = 7
        player1.scorer = 9
        player1.set_pieces = 3

        player2 = Mock()
        player2.ht_id = 67890  # Different player
        player2.first_name = "Jane"
        player2.last_name = "Smith"
        player2.data_date = datetime(2024, 1, 15)
        player2.keeper = 3
        player2.defender = 10
        player2.playmaker = 8
        player2.winger = 6
        player2.passing = 9
        player2.scorer = 7
        player2.set_pieces = 5

        allplayerids, allplayers, playernames = get_training([player1, player2])

        # Should have both players
        assert len(allplayerids) == 2
        assert 12345 in allplayerids
        assert 67890 in allplayerids

        # Check names
        assert playernames[12345] == "John Doe"
        assert playernames[67890] == "Jane Smith"

        # Check separate timelines
        assert len(allplayers[12345]) == 1
        assert len(allplayers[67890]) == 1

    def test_get_training_none_skills(self):
        """Test get_training handles None skill values."""
        player = Mock()
        player.ht_id = 12345
        player.first_name = "Test"
        player.last_name = "Player"
        player.data_date = datetime(2024, 1, 15)
        player.keeper = None
        player.defender = 8
        player.playmaker = None
        player.winger = 4
        player.passing = None
        player.scorer = 9
        player.set_pieces = None

        allplayerids, allplayers, playernames = get_training([player])

        timeline = allplayers[12345]
        skills = timeline[0][1]

        # None values should become 0
        assert skills == [0, 8, 0, 4, 0, 9, 0]


class TestGetPlayerChanges:
    """Test get_player_changes function with simplified approach."""

    def _create_mock_player_record(self, first_name, last_name, date, **kwargs):
        """Helper to create mock player records with default attributes."""
        record = Mock()
        record.first_name = first_name
        record.last_name = last_name
        record.data_date = date

        # Set defaults for all expected attributes
        defaults = {
            "keeper": 0, "defender": 0, "playmaker": 0, "winger": 0,
            "passing": 0, "scorer": 0, "set_pieces": 0, "experience": 0,
            "age_years": 25, "cards": 0, "injury_level": -1
        }
        defaults.update(kwargs)

        for attr, value in defaults.items():
            setattr(record, attr, value)

        return record

    @patch('app.utils.db')
    @patch('app.utils._get_player_display_data')
    def test_get_player_changes_basic_functionality(self, mock_display_data, mock_db):
        """Test basic get_player_changes functionality."""
        from app.utils import get_player_changes

        old_record = self._create_mock_player_record("Test", "Player", datetime(2024, 1, 8), keeper=5)
        new_record = self._create_mock_player_record("Test", "Player", datetime(2024, 1, 15), keeper=6)

        # Mock the display data
        mock_display_data.return_value = {
            'name': "Test Player",
            'group_name': None,
            'text_color': None,
            'bg_color': None
        }

        mock_db.session.query.return_value.filter_by.return_value.filter.return_value.order_by.return_value.first.side_effect = [
            old_record, new_record
        ]

        result = get_player_changes(123456, 7, 0)

        assert len(result) == 1
        change = result[0]
        assert change[1] == "Keeper"  # Attribute name
        assert change[2] == 5  # Old value
        assert change[3] == 6  # New value
        assert change[4] == "skill"  # Change type

        # Check player data structure
        player_data = change[0]
        assert player_data['name'] == "Test Player"
        mock_display_data.assert_called_once_with(123456, new_record)

    @patch('app.utils.db')
    def test_get_player_changes_no_records(self, mock_db):
        """Test get_player_changes with no records found."""
        from app.utils import get_player_changes

        mock_db.session.query.return_value.filter_by.return_value.filter.return_value.order_by.return_value.first.return_value = None

        result = get_player_changes(123456, 7, 0)
        assert result == []

    @patch('app.utils.db')
    def test_get_player_changes_exception_handling(self, mock_db):
        """Test get_player_changes exception handling."""
        from app.utils import get_player_changes

        mock_db.session.query.side_effect = Exception("Database error")

        result = get_player_changes(123456, 7, 0)
        assert result == []


class TestGetPlayerDisplayName:
    """Test _get_player_display_name helper function."""

    def _create_mock_player_record(self, first_name, last_name):
        """Helper to create simple mock player records."""
        record = Mock()
        record.first_name = first_name
        record.last_name = last_name
        return record

    def test_get_player_display_name_basic(self):
        """Test basic player display name without group."""
        from app.utils import _get_player_display_name

        player_record = self._create_mock_player_record("John", "Doe")

        with patch('app.utils.session', {}):
            result = _get_player_display_name(123456, player_record)
            assert result == "John Doe"

    @patch('app.utils.db')
    @patch('app.utils.session', {"current_user_id": 12345})
    def test_get_player_display_name_with_group(self, mock_db):
        """Test player display name with group using direct patching."""
        from app.utils import _get_player_display_name

        player_record = self._create_mock_player_record("Jane", "Smith")

        # Mock PlayerSetting and Group instances with proper attribute setup
        mock_player_setting = Mock()
        mock_player_setting.group_id = 5

        mock_group = Mock()
        mock_group.name = "Defenders"  # Set as direct attribute, not a Mock
        mock_group.textcolor = "#ffffff"
        mock_group.bgcolor = "#ff0000"

        # Simple mock setup - return PlayerSetting, then Group
        mock_db.session.query.return_value.filter_by.return_value.first.side_effect = [
            mock_player_setting, mock_group
        ]

        # Mock successful model imports
        with patch('models.PlayerSetting'), patch('models.Group'):
            result = _get_player_display_name(123456, player_record)
            assert result == "Jane Smith (Defenders)"


class TestGetPlayerDisplayData:
    """Test _get_player_display_data helper function."""

    def _create_mock_player_record(self, first_name, last_name):
        """Helper to create simple mock player records."""
        record = Mock()
        record.first_name = first_name
        record.last_name = last_name
        return record

    def test_get_player_display_data_basic(self):
        """Test basic player display data without group."""
        from app.utils import _get_player_display_data

        player_record = self._create_mock_player_record("John", "Doe")

        with patch('app.utils.session', {}):
            result = _get_player_display_data(123456, player_record)
            expected = {
                'name': 'John Doe',
                'group_name': None,
                'group_order': None,
                'text_color': None,
                'bg_color': None
            }
            assert result == expected

    @patch('app.utils.db')
    @patch('app.utils.session', {"current_user_id": 12345})
    def test_get_player_display_data_with_group(self, mock_db):
        """Test player display data with group and colors."""
        from app.utils import _get_player_display_data

        player_record = self._create_mock_player_record("Jane", "Smith")

        # Mock PlayerSetting and Group instances with color info
        mock_player_setting = Mock()
        mock_player_setting.group_id = 5

        mock_group = Mock()
        mock_group.name = "Defenders"
        mock_group.order = 2
        mock_group.textcolor = "#ffffff"
        mock_group.bgcolor = "#ff0000"

        # Simple mock setup - return PlayerSetting, then Group
        mock_db.session.query.return_value.filter_by.return_value.first.side_effect = [
            mock_player_setting, mock_group
        ]

        # Mock successful model imports
        with patch('models.PlayerSetting'), patch('models.Group'):
            result = _get_player_display_data(123456, player_record)
            expected = {
                'name': 'Jane Smith (Defenders)',
                'group_name': 'Defenders',
                'group_order': 2,
                'text_color': '#ffffff',
                'bg_color': '#ff0000'
            }
            assert result == expected

    @patch('app.utils.db')
    @patch('app.utils.session', {"current_user_id": 12345})
    def test_get_player_display_data_no_group(self, mock_db):
        """Test player display data when no group is found."""
        from app.utils import _get_player_display_data

        player_record = self._create_mock_player_record("Bob", "Jones")

        # Mock no PlayerSetting found
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = None

        with patch('models.PlayerSetting'), patch('models.Group'):
            result = _get_player_display_data(123456, player_record)
            expected = {
                'name': 'Bob Jones',
                'group_name': None,
                'group_order': None,
                'text_color': None,
                'bg_color': None
            }
            assert result == expected


class TestFormatAttributeName:
    """Test _format_attribute_name helper function."""

    def test_format_attribute_name_basic_cases(self):
        """Test basic attribute name formatting."""
        from app.utils import _format_attribute_name

        assert _format_attribute_name("keeper") == "Keeper"
        assert _format_attribute_name("defender") == "Defender"
        assert _format_attribute_name("playmaker") == "Playmaker"

    def test_format_attribute_name_special_cases(self):
        """Test special case attribute name formatting."""
        from app.utils import _format_attribute_name

        assert _format_attribute_name("set_pieces") == "Set Pieces"
        assert _format_attribute_name("tsi") == "TSI"
        assert _format_attribute_name("injury_level") == "Injury Level"
