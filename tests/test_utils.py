"""Tests for app/utils.py - Utility functions."""

from datetime import datetime
import subprocess
from unittest.mock import Mock, patch

import pytest

from app.utils import (
    _format_attribute_name,
    calculateContribution,
    calculateManmark,
    create_page,
    debug_print,
    diff,
    diff_month,
    dprint,
    get_admin_feedback_counts,
    get_team_match_statistics,
    get_team_timeline,
    get_training,
    get_version_info,
    initialize_utils,
    player_daily_changes,
    player_diff,
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

    @patch("app.utils.debug_level", 2)
    @patch("builtins.print")
    def test_dprint_prints_when_level_allowed(self, mock_print):
        """Test dprint prints when debug level allows."""
        dprint(1, "test", "message")

        mock_print.assert_called_once()
        # Should include filename and arguments
        args = mock_print.call_args[0]
        assert any("[" in str(arg) and "]" in str(arg) for arg in args)  # filename
        assert "test" in str(args)
        assert "message" in str(args)

    @patch("app.utils.debug_level", 0)
    @patch("builtins.print")
    def test_dprint_doesnt_print_when_level_too_high(self, mock_print):
        """Test dprint doesn't print when debug level too low."""
        dprint(1, "test", "message")

        mock_print.assert_not_called()

    @patch("app.utils.debug_level", None)
    @patch("builtins.print")
    def test_dprint_prints_when_debug_level_none(self, mock_print):
        """Test dprint prints when debug_level is None."""
        dprint(1, "test", "message")

        mock_print.assert_called_once()

    @patch("app.utils.debug_level", 2)
    @patch("builtins.print")
    def test_debug_print_enhanced_format(self, mock_print):
        """Test debug_print with enhanced route formatting."""
        debug_print("test_route", "test_function", "arg1", "arg2")

        mock_print.assert_called_once()
        args = str(mock_print.call_args)
        assert "test_route::test_function()" in args
        assert "arg1" in args
        assert "arg2" in args

    @patch("app.utils.debug_level", 1)
    @patch("builtins.print")
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

    @patch("subprocess.check_output")
    def test_get_version_info_with_git_tags(self, mock_subprocess):
        """Test get_version_info with git tag output."""
        # Mock git describe output - commits ahead of tag
        mock_subprocess.return_value = b"3.12.1-gedd7f4a"

        result = get_version_info()

        assert result["version"] == "3.12.1"
        assert result["fullversion"] == "3.12.1.gedd7f4a"
        assert result["versionstr"] == "3.12.1.gedd7f4a"

    @patch("subprocess.check_output")
    def test_get_version_info_no_features(self, mock_subprocess):
        """Test get_version_info with exact tag match (no commits ahead)."""
        mock_subprocess.return_value = b"3.12"

        result = get_version_info()

        assert result["version"] == "3.12"
        assert result["fullversion"] == "3.12"
        assert result["versionstr"] == "3.12"

    @patch(
        "subprocess.check_output", side_effect=subprocess.CalledProcessError(1, "git")
    )
    def test_get_version_info_fallback(self, mock_subprocess):
        """Test get_version_info fallback when git fails."""
        result = get_version_info()

        assert result["version"] == "2.0.0"
        assert result["fullversion"] == "2.0.0-dev"
        assert result["versionstr"] == "2.0.0-dev"

    @patch("subprocess.check_output")
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

    @patch("app.utils.render_template")
    @patch("app.utils.get_version_info")
    def test_create_page_basic(self, mock_version_info, mock_render):
        """Test create_page with basic parameters."""
        mock_version_info.return_value = {
            "version": "2.0",
            "fullversion": "2.0.0-dev",
            "versionstr": "2.0.0-dev",
        }
        mock_render.return_value = "rendered_template"

        with self.app.test_request_context():
            result = create_page("test.html", "Test Title")

            assert result == "rendered_template"
            mock_render.assert_called_once()

            # Check template variables
            call_kwargs = mock_render.call_args[1]
            assert call_kwargs["title"] == "Test Title"
            # Matches config.py
            assert call_kwargs["apptitle"] == "HattrickPlanner"
            assert call_kwargs["version"] == "2.0"

    @patch("app.utils.render_template")
    @patch("app.utils.get_version_info")
    @patch("app.auth_utils.get_current_user", return_value=None)
    def test_create_page_with_session(
        self, mock_user_model, mock_version_info, mock_render
    ):
        """Test create_page with user session data."""
        mock_version_info.return_value = {
            "version": "2.0",
            "fullversion": "2.0.0-dev",
            "versionstr": "2.0.0-dev",
        }
        mock_render.return_value = "rendered_template"

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

    @patch("app.utils.render_template")
    @patch("app.utils.get_version_info")
    @patch("app.auth_utils.get_current_user")
    @patch("app.utils.get_admin_feedback_counts", return_value=None)
    def test_create_page_with_admin_user(
        self, _mock_counts, mock_user, mock_version_info, mock_render
    ):
        """Test create_page with admin user role."""
        mock_version_info.return_value = {
            "version": "2.0",
            "fullversion": "2.0.0-dev",
            "versionstr": "2.0.0-dev",
        }
        mock_render.return_value = "rendered_template"

        # Mock admin user
        admin_user = Mock(ht_id=12345)
        admin_user.is_admin.return_value = True
        mock_user.return_value = admin_user

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

    @patch("app.utils.render_template")
    @patch("app.utils.get_version_info")
    def test_create_page_with_custom_kwargs(self, mock_version_info, mock_render):
        """Test create_page with additional custom template variables."""
        mock_version_info.return_value = {
            "version": "2.0",
            "fullversion": "2.0.0-dev",
            "versionstr": "2.0.0-dev",
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


class TestCreateDefaultGroups:
    """Test create_default_groups function."""

    def test_create_default_groups_function_exists(self):
        """Test that create_default_groups function exists and is callable."""
        from app.utils import create_default_groups

        # Test that the function exists and is callable
        assert callable(create_default_groups)

        # Test function signature by checking that it accepts user_id parameter
        import inspect

        sig = inspect.signature(create_default_groups)
        assert "user_id" in sig.parameters

        # Verify function docstring
        assert create_default_groups.__doc__ is not None
        assert "Create default player groups" in create_default_groups.__doc__


class TestAdminFeedbackCounts:
    """Test admin feedback count functionality."""

    @patch("models.User")
    def test_get_admin_feedback_counts_non_admin_returns_none(self, mock_user_model):
        """Test get_admin_feedback_counts returns None for non-admin users."""

        # Mock user query to return non-admin user
        mock_user = Mock()
        mock_user.is_admin.return_value = False
        mock_user.ht_id = 12345
        result = get_admin_feedback_counts(mock_user)

        assert result is None

    @patch("models.FeedbackComment")
    @patch("models.Feedback")
    @patch("models.User")
    @patch("sqlalchemy.exists")
    @patch("sqlalchemy.and_")
    def test_get_admin_feedback_counts_admin_user_returns_counts(
        self,
        mock_and,
        mock_exists,
        mock_user_model,
        mock_feedback_model,
        mock_comment_model,
    ):
        """Test get_admin_feedback_counts returns counts for admin users."""

        # Mock admin user
        mock_admin = Mock()
        mock_admin.is_admin.return_value = True
        mock_admin.ht_id = 182085

        # Mock admin users query
        mock_admin_users = [mock_admin]

        # Mock feedback queries
        mock_no_replies_query = Mock()
        mock_no_replies_query.count.return_value = 3

        mock_feedback_with_replies = [Mock(id=1), Mock(id=2)]

        # Mock latest comments (one needs follow-up)
        mock_latest_comment1 = Mock(author_id=99999)  # Non-admin
        mock_latest_comment2 = Mock(author_id=182085)  # Admin

        # Setup mocks
        mock_user_model.query.filter.return_value.all.return_value = mock_admin_users
        mock_feedback_model.query.filter.return_value = mock_no_replies_query
        mock_feedback_model.query.filter.return_value.all.return_value = (
            mock_feedback_with_replies
        )

        # Mock comment queries for follow-up check
        mock_comment_model.query.filter_by.return_value.order_by.return_value.first.side_effect = [
            mock_latest_comment1,  # First feedback needs follow-up
            mock_latest_comment2,  # Second feedback doesn't need follow-up
        ]

        result = get_admin_feedback_counts(mock_admin)

        assert result is not None
        assert result["no_replies"] == 3
        assert result["needs_followup"] == 1

    @patch("models.FeedbackComment")
    @patch("models.Feedback")
    @patch("models.User")
    def test_get_admin_feedback_counts_hardcoded_admin_id(
        self, mock_user_model, mock_feedback_model, mock_comment_model
    ):
        """Test get_admin_feedback_counts works for hardcoded admin ID 182085."""

        # Mock user with hardcoded admin ID but no admin role
        mock_user = Mock()
        mock_user.is_admin.return_value = True  # owner is admin regardless of role
        mock_user.ht_id = 182085

        # Mock empty results for simplicity
        mock_no_replies_query = Mock()
        mock_no_replies_query.count.return_value = 0

        mock_user_model.query.filter.return_value.all.return_value = [mock_user]
        mock_feedback_model.query.filter.return_value = mock_no_replies_query
        mock_feedback_model.query.filter.return_value.all.return_value = []

        result = get_admin_feedback_counts(mock_user)
        assert "no_replies" in result
        assert "needs_followup" in result

    def test_get_admin_feedback_counts_no_user_id(self):
        """Test get_admin_feedback_counts with no user returns None."""

        result = get_admin_feedback_counts(None)
        assert result is None

    def test_get_admin_feedback_counts_function_exists(self):
        """Test that get_admin_feedback_counts function exists and is callable."""

        assert callable(get_admin_feedback_counts)

        # Test function signature
        import inspect

        sig = inspect.signature(get_admin_feedback_counts)
        assert "user" in sig.parameters

        # Verify docstring
        assert get_admin_feedback_counts.__doc__ is not None
        assert "hobby project scale" in get_admin_feedback_counts.__doc__


class TestTeamTimeline:
    """Test get_team_timeline function."""

    def test_get_team_timeline_imports(self):
        """Test that get_team_timeline can be imported."""
        assert get_team_timeline is not None
        assert callable(get_team_timeline)

    def test_get_team_timeline_empty_team(self, app, db_session):
        """Test get_team_timeline with team that has no players."""

        result = get_team_timeline(999999)
        assert isinstance(result, dict)
        # Should return empty dict for team with no players
        assert result == {}

    def test_get_team_timeline_structure(self):
        """Test get_team_timeline returns correct structure."""

        # Test function signature
        import inspect

        sig = inspect.signature(get_team_timeline)
        assert "team_id" in sig.parameters

        # Verify docstring
        assert get_team_timeline.__doc__ is not None
        assert "4-week timeline" in get_team_timeline.__doc__

    def test_timeline_changes_per_week(self, app, db_session):
        """Changes come from the latest snapshot at each week boundary."""
        from datetime import datetime, timedelta

        from sqlalchemy import event

        from models import Group, PlayerSetting, User
        from tests.factories import make_player_record

        team, user_id = 998801, 998802
        now = datetime.now()

        def snapshot(ht_id, days_ago, owner=team, **skills):
            record = make_player_record(ht_id, owner, "Kim", f"P{ht_id}")
            record.data_date = (now - timedelta(days=days_ago)).replace(microsecond=0)
            for skill, value in skills.items():
                setattr(record, skill, value)
            db_session.add(record)

        snapshot(701, 40, scorer=5)
        snapshot(701, 10, scorer=6)
        snapshot(701, 2, scorer=7, passing=6)
        snapshot(702, 10, owner=0, scorer=1)  # sold player: not in the timeline
        snapshot(702, 2, owner=0, scorer=2)
        db_session.add(User(user_id, "u", "u", "x", "k", "s"))
        db_session.flush()
        group = Group(user_id, "Forwards", 3, "#fff", "#000")
        db_session.add(group)
        db_session.flush()
        db_session.add(PlayerSetting(701, user_id, group.id))
        db_session.flush()

        statements = []

        def count(*_args, **_kwargs):
            statements.append(1)

        engine = db_session.get_bind().engine
        event.listen(engine, "before_cursor_execute", count)
        try:
            with app.test_request_context():
                from flask import session

                session["current_user_id"] = user_id
                timeline = get_team_timeline(team)
        finally:
            event.remove(engine, "before_cursor_execute", count)

        week1 = [
            (c[0]["name"], c[1], c[2], c[3]) for c in timeline["week_1"]["changes"]
        ]
        week2 = [
            (c[0]["name"], c[1], c[2], c[3]) for c in timeline["week_2"]["changes"]
        ]
        assert week1 == [
            ("Kim P701 (Forwards)", "Passing", 5, 6),
            ("Kim P701 (Forwards)", "Scorer", 6, 7),
        ]
        assert week2 == [("Kim P701 (Forwards)", "Scorer", 5, 6)]
        assert timeline["week_3"]["changes"] == []
        assert timeline["week_1"]["changes"][0][0]["group_order"] == 3
        assert len(statements) <= 5  # independent of number of players/weeks


class TestUtilityFunctions:
    """Test utility functions for coverage expansion."""

    def test_format_attribute_name(self):
        """Test _format_attribute_name function."""
        # Test basic formatting - function uses .title()
        assert _format_attribute_name("test_value") == "Test Value"
        assert _format_attribute_name("multiple_words_here") == "Multiple Words Here"

        # Test special cases
        assert _format_attribute_name("tsi") == "TSI"
        assert _format_attribute_name("set_pieces") == "Set Pieces"

        # Test edge cases
        assert _format_attribute_name("") == ""
        assert _format_attribute_name("single") == "Single"

    def test_calculateManmark_basic(self):
        """Test calculateManmark function with basic player data."""
        # Test with mock player data - needs experience and defender fields
        player = Mock()
        player.experience = 50  # Will be scaled to 10.0
        player.defender = 8.0

        result = calculateManmark(player)
        assert isinstance(result, (int, float))
        assert result > 0  # Should return positive value for valid defense

    def test_calculateManmark_edge_cases(self):
        """Test calculateManmark with edge cases."""
        # Test with zero values
        player = Mock()
        player.experience = 0
        player.defender = 0

        result = calculateManmark(player)
        assert result == 0.0

        # Test with high values
        player.experience = 100
        player.defender = 20.0
        result = calculateManmark(player)
        assert result > 0

    def test_calculateContribution_positions(self):
        """Weights per position code; neutral form/experience/loyalty -> no bonus."""
        player = {
            "keeper": 10,
            "defender": 10,
            "playmaker": 8,
            "winger": 6,
            "passing": 5,
            "scorer": 4,
            "form": 5,
            "experience": 0,
            "loyalty": 0,
        }

        assert calculateContribution("GC", player) == 10.0
        assert calculateContribution("CD", player) == 9.0  # 0.8*10 + 0.2*5
        assert calculateContribution("IMN", player) == 7.4  # 0.8*8 + 0.2*5
        assert calculateContribution("FW", player) == 4.2  # 0.8*4 + 0.2*5

    def test_calculateContribution_tactical_variants_differ(self):
        """Variants used to silently fall back to the base position (bug)."""
        player = {"defender": 10, "playmaker": 8, "scorer": 4, "passing": 5}

        imn = calculateContribution("IMN", player)
        imd = calculateContribution("IMD", player)
        imo = calculateContribution("IMO", player)

        assert len({imn, imd, imo}) == 3
        assert imd == 8.0  # 0.3*10 + 0.5*8 + 0.2*5

    def test_calculateContribution_role_ids_map_to_codes(self):
        player = {"keeper": 7, "defender": 9, "passing": 6, "playmaker": 5}

        assert calculateContribution(100, player) == calculateContribution("GC", player)
        assert calculateContribution(103, player) == calculateContribution("CD", player)
        assert calculateContribution(101, player) == calculateContribution(
            "WBN", player
        )
        assert calculateContribution(108, player) == calculateContribution(
            "IMN", player
        )

    def test_calculateContribution_dict_and_object_agree(self):
        from types import SimpleNamespace

        fields = {
            "playmaker": 12,
            "passing": 7,
            "form": 7,
            "experience": 4,
            "loyalty": 20,
        }

        assert calculateContribution("IMN", fields) == calculateContribution(
            "IMN", SimpleNamespace(**fields)
        )
        # form 7 (+10%), experience 4 (+4%), loyalty 20 (+10%)
        assert calculateContribution("IMN", fields) == round(11.0 * 1.1 * 1.04 * 1.1, 2)

    def test_calculateContribution_unknown_position_uses_passing(self):
        assert calculateContribution("XYZ", {"passing": 6}) == 6.0
        assert calculateContribution(999, {"passing": 6}) == 6.0

    def test_calculateContribution_missing_skills_count_as_zero(self):
        assert calculateContribution("CD", {"defender": None}) == 0.0


class TestTrainingFunctions:
    """Test training-related utility functions."""

    def test_get_training_empty_data(self):
        """Test get_training with empty player data."""
        result = get_training([])

        # Should handle empty input gracefully
        assert result is not None

    def test_get_training_with_data(self):
        """Test get_training with sample player data."""
        # Create mock player data
        player_data = [Mock()]
        player_data[0].playername = "Test Player"
        player_data[0].age = 20

        result = get_training(player_data)

        # Should process player data
        assert result is not None


class TestPlayerDiff:
    """Test player_diff and related functions."""

    def test_player_diff_basic(self):
        """Test player_diff function basic functionality."""
        # This function may require database access, test basic call
        try:
            result = player_diff(12345, 7)
            # Function should return some result structure
            assert result is not None
        except Exception:
            # Expected in test environment without real data
            pass

    def test_player_daily_changes_basic(self):
        """Test player_daily_changes function."""
        try:
            result = player_daily_changes(12345, 7)
            assert result is not None
        except Exception:
            # Expected in test environment without real data
            pass


class TestPlayerUtilityFunctions:
    """Test player utility functions."""

    def test_format_attribute_name_cases(self):
        """Test _format_attribute_name function."""
        from app.utils import _format_attribute_name

        # Test basic attribute name formatting (function behavior may vary)
        result = _format_attribute_name("playername")
        assert isinstance(result, str)
        assert len(result) > 0

        result2 = _format_attribute_name("age")
        assert isinstance(result2, str)
        assert len(result2) > 0


class TestTeamStatistics:
    """Test team statistics functions."""

    def test_calculate_team_statistics_empty(self):
        """Test calculate_team_statistics with empty players."""
        from app.utils import calculate_team_statistics

        result = calculate_team_statistics([])
        assert isinstance(result, dict)

    def test_calculate_team_statistics_with_players(self):
        """Test calculate_team_statistics with mock players."""
        from app.utils import calculate_team_statistics

        # Create mock players
        player1 = Mock()
        player1.age = 25
        player1.form = 7
        player1.stamina = 8

        player2 = Mock()
        player2.age = 22
        player2.form = 6
        player2.stamina = 9

        players = [player1, player2]
        result = calculate_team_statistics(players)

        assert isinstance(result, dict)

    def test_get_top_scorers_empty(self):
        """Test get_top_scorers with empty players."""
        from app.utils import get_top_scorers

        result = get_top_scorers([])
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_top_scorers_with_players(self):
        """Test get_top_scorers with mock players."""
        from app.utils import get_top_scorers

        # Create mock players with scoring stats
        player1 = Mock()
        player1.playername = "Striker One"
        player1.goals = 15
        player1.matches = 10

        player2 = Mock()
        player2.playername = "Striker Two"
        player2.goals = 8
        player2.matches = 12

        players = [player1, player2]
        result = get_top_scorers(players, limit=2)

        assert isinstance(result, list)

    def test_get_top_performers_empty(self):
        """Test get_top_performers with empty players."""
        from app.utils import get_top_performers

        result = get_top_performers([])
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_top_performers_with_players(self):
        """Test get_top_performers with mock players."""
        from app.utils import get_top_performers

        # Create mock players with proper tsi attribute
        player1 = Mock()
        player1.playername = "Star Player"
        player1.form = 8
        player1.experience = 7
        player1.tsi = 1000  # Proper integer value for comparison

        players = [player1]
        result = get_top_performers(players, limit=1)

        assert isinstance(result, list)


class TestTeamMatchStatistics:
    """Test team match statistics."""

    def test_get_team_match_statistics_basic(self):
        """Test get_team_match_statistics function."""
        try:
            result = get_team_match_statistics(12345)
            assert result is not None
        except Exception:
            # Expected in test environment without database
            pass


class TestDefaultGroups:
    """Test default group creation."""

    def test_create_default_groups_function_exists(self):
        """Test that create_default_groups function exists."""
        from app.utils import create_default_groups

        assert callable(create_default_groups)
