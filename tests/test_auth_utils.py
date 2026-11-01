"""Tests for app/auth_utils.py - Authentication utilities and decorators."""

from unittest.mock import patch

import pytest

from app.auth_utils import current_team, get_current_user_id, require_authentication


class TestGetCurrentUserId:
    """Test get_current_user_id function."""

    def test_returns_user_id_when_present(self):
        """Test returns user ID when present in session."""
        with patch("app.auth_utils.session", {"current_user_id": 12345}):
            result = get_current_user_id()
            assert result == 12345

    def test_returns_none_when_not_present(self):
        """Test returns None when user ID not in session."""
        with patch("app.auth_utils.session", {}):
            result = get_current_user_id()
            assert result is None


class TestCurrentTeam:
    TEAMS = {"all_teams": [111, 222], "all_team_names": ["First", "Second"]}

    def _request(self, app, query):
        ctx = app.test_request_context(query)
        ctx.push()
        from flask import session

        session.update(self.TEAMS)
        return ctx

    def test_reads_id_from_request(self, app):
        ctx = self._request(app, "/x?id=222")
        try:
            assert current_team() == (222, "Second")
        finally:
            ctx.pop()

    @pytest.mark.parametrize("query", ["/x", "/x?id=", "/x?id=abc", "/x?id=999"])
    def test_missing_malformed_or_foreign_id(self, app, query):
        ctx = self._request(app, query)
        try:
            assert current_team() == (None, None)
        finally:
            ctx.pop()

    def test_explicit_id_wins(self, app):
        ctx = self._request(app, "/x?id=222")
        try:
            assert current_team("111") == (111, "First")
        finally:
            ctx.pop()


class TestRequireAuthenticationDecorator:
    """Test require_authentication decorator."""

    @patch("app.auth_utils.render_template")
    def test_redirects_when_not_authenticated(self, mock_render):
        """Test decorator redirects to login when not authenticated."""
        mock_render.return_value = "forward_template"

        with patch("app.auth_utils.session", {}):

            @require_authentication
            def test_route():
                return "protected_content"

            result = test_route()

            assert result == "forward_template"
            mock_render.assert_called_once_with("_forward.html", url="/login")

    @patch("app.auth_utils.get_current_user", return_value=object())
    def test_allows_access_when_authenticated(self, _mock_user):
        """Test decorator allows access when authenticated."""
        with patch("app.auth_utils.session", {"current_user": "testuser"}):

            @require_authentication
            def test_route():
                return "protected_content"

            result = test_route()

            assert result == "protected_content"

    @patch("app.auth_utils.get_current_user", return_value=None)
    @patch("app.auth_utils.render_template", return_value="forward_template")
    def test_logs_out_session_without_user_row(self, mock_render, _mock_user):
        """A session pointing to a deleted/missing User is cleared (FEAT-018)."""
        fake_session = {"current_user": "ghost", "current_user_id": 404}
        with patch("app.auth_utils.session", fake_session):

            @require_authentication
            def test_route():
                return "protected_content"

            assert test_route() == "forward_template"

        assert fake_session == {}
        mock_render.assert_called_once_with("_forward.html", url="/login")

    def test_preserves_function_metadata(self):
        """Test decorator preserves original function metadata."""
        with patch("app.auth_utils.session", {"current_user": "testuser"}):

            @require_authentication
            def test_route():
                """Test route docstring."""
                return "protected_content"

            assert test_route.__name__ == "test_route"
            assert test_route.__doc__ == "Test route docstring."

    @patch("app.auth_utils.get_current_user", return_value=object())
    def test_passes_arguments_and_kwargs(self, _mock_user):
        """Test decorator passes through arguments and keyword arguments."""
        with patch("app.auth_utils.session", {"current_user": "testuser"}):

            @require_authentication
            def test_route(arg1, arg2, kwarg1=None):
                return f"{arg1}-{arg2}-{kwarg1}"

            result = test_route("a", "b", kwarg1="c")

            assert result == "a-b-c"


class TestCurrentUserAndActivity:
    """get_current_user caches per request; track_activity counts page visits."""

    @staticmethod
    def _user(db_session, ht_id=777001):
        from models import User

        user = User(
            ht_id=ht_id,
            ht_user="tracker",
            username="tracker",
            password="x",
            access_key="k",
            access_secret="s",
        )
        db_session.add(user)
        db_session.flush()
        return user

    def test_get_current_user_queries_once_per_request(self, app, db_session):
        from sqlalchemy import event

        from app.auth_utils import get_current_user

        self._user(db_session)
        statements = []

        def count(*_args, **_kwargs):
            statements.append(1)

        engine = db_session.get_bind().engine
        event.listen(engine, "before_cursor_execute", count)
        try:
            with app.test_request_context():
                from flask import session

                session["current_user_id"] = 777001
                first = get_current_user()
                second = get_current_user()
        finally:
            event.remove(engine, "before_cursor_execute", count)

        assert first is second
        assert first.ht_user == "tracker"
        assert len(statements) == 1

    def test_get_current_user_without_session(self, app):
        from app.auth_utils import get_current_user

        with app.test_request_context():
            assert get_current_user() is None

    def test_track_activity_counts_visit(self, app, db_session):
        from app.auth_utils import track_activity

        user = self._user(db_session)

        @track_activity("training")
        def view():
            return "ok"

        with app.test_request_context():
            from flask import session

            session["current_user_id"] = 777001
            assert view() == "ok"
            assert view() == "ok"

        assert user.c_training == 2
        assert user.last_usage

    def test_track_activity_ignores_anonymous(self, app):
        from app.auth_utils import track_activity

        @track_activity("training")
        def view():
            return "ok"

        with app.test_request_context():
            assert view() == "ok"
