"""Tests for app/auth_utils.py - Authentication utilities and decorators."""

from unittest.mock import patch

from app.auth_utils import (
    get_current_user_id,
    get_team_info,
    get_user_teams,
    is_authenticated,
    require_authentication,
)


def test_module_imports():
    """Test that all auth utility functions can be imported correctly."""
    assert callable(get_current_user_id)
    assert callable(get_user_teams)
    assert callable(is_authenticated)
    assert callable(get_team_info)
    assert callable(require_authentication)


class TestGetCurrentUserId:
    """Test get_current_user_id function."""

    def test_returns_user_id_when_present(self):
        """Test returns user ID when present in session."""
        with patch('app.auth_utils.session', {"current_user_id": 12345}):
            result = get_current_user_id()
            assert result == 12345

    def test_returns_none_when_not_present(self):
        """Test returns None when user ID not in session."""
        with patch('app.auth_utils.session', {}):
            result = get_current_user_id()
            assert result is None


class TestIsAuthenticated:
    """Test is_authenticated function."""

    def test_returns_true_when_user_present(self):
        """Test returns True when current_user in session."""
        with patch('app.auth_utils.session', {"current_user": "some_user"}):
            result = is_authenticated()
            assert result is True

    def test_returns_false_when_user_not_present(self):
        """Test returns False when current_user not in session."""
        with patch('app.auth_utils.session', {}):
            result = is_authenticated()
            assert result is False


class TestGetUserTeams:
    """Test get_user_teams function."""

    def test_returns_teams_when_present(self):
        """Test returns teams and team names from session."""
        session_data = {
            "all_teams": [12345, 67890],
            "all_team_names": ["Team A", "Team B"]
        }
        with patch('app.auth_utils.session', session_data):
            team_ids, team_names = get_user_teams()
            assert team_ids == [12345, 67890]
            assert team_names == ["Team A", "Team B"]

    def test_returns_empty_lists_when_not_present(self):
        """Test returns empty lists when teams not in session."""
        with patch('app.auth_utils.session', {}):
            team_ids, team_names = get_user_teams()
            assert team_ids == []
            assert team_names == []


class TestGetTeamInfo:
    """Test get_team_info function."""

    def test_valid_team_id_returns_success(self):
        """Test valid team ID returns success status."""
        user_teams = ([12345, 67890], ["Team A", "Team B"])

        is_valid, team_name, error = get_team_info(12345, user_teams)

        assert is_valid is True
        assert team_name == "Team A"
        assert error is None

    def test_invalid_team_id_returns_error(self):
        """Test invalid team ID returns error status."""
        user_teams = ([12345, 67890], ["Team A", "Team B"])

        is_valid, team_name, error = get_team_info(99999, user_teams)

        assert is_valid is False
        assert team_name is None
        assert error == "Wrong teamid, try the links."

    def test_uses_session_when_no_user_teams_provided(self):
        """Test function uses session data when user_teams not provided."""
        session_data = {
            "all_teams": [12345, 67890],
            "all_team_names": ["Team A", "Team B"]
        }
        with patch('app.auth_utils.session', session_data):
            is_valid, team_name, error = get_team_info(12345)

            assert is_valid is True
            assert team_name == "Team A"
            assert error is None

    def test_second_team_in_list(self):
        """Test retrieving second team from list."""
        user_teams = ([12345, 67890], ["Team A", "Team B"])

        is_valid, team_name, error = get_team_info(67890, user_teams)

        assert is_valid is True
        assert team_name == "Team B"
        assert error is None


class TestRequireAuthenticationDecorator:
    """Test require_authentication decorator."""

    @patch('app.auth_utils.render_template')
    def test_redirects_when_not_authenticated(self, mock_render):
        """Test decorator redirects to login when not authenticated."""
        mock_render.return_value = "forward_template"

        with patch('app.auth_utils.session', {}):
            @require_authentication
            def test_route():
                return "protected_content"

            result = test_route()

            assert result == "forward_template"
            mock_render.assert_called_once_with("_forward.html", url="/login")

    def test_allows_access_when_authenticated(self):
        """Test decorator allows access when authenticated."""
        with patch('app.auth_utils.session', {"current_user": "testuser"}):
            @require_authentication
            def test_route():
                return "protected_content"

            result = test_route()

            assert result == "protected_content"

    def test_preserves_function_metadata(self):
        """Test decorator preserves original function metadata."""
        with patch('app.auth_utils.session', {"current_user": "testuser"}):
            @require_authentication
            def test_route():
                """Test route docstring."""
                return "protected_content"

            assert test_route.__name__ == "test_route"
            assert test_route.__doc__ == "Test route docstring."

    def test_passes_arguments_and_kwargs(self):
        """Test decorator passes through arguments and keyword arguments."""
        with patch('app.auth_utils.session', {"current_user": "testuser"}):
            @require_authentication
            def test_route(arg1, arg2, kwarg1=None):
                return f"{arg1}-{arg2}-{kwarg1}"

            result = test_route("a", "b", kwarg1="c")

            assert result == "a-b-c"
