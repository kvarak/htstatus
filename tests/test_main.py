"""Tests for app/blueprints/main.py"""

import pytest

US = 9838


def _client(app_with_routes, db_session, admin=False):
    from tests.conftest import create_test_user
    from tests.factories import setup_authenticated_session

    user = create_test_user(db_session, user_id=US)
    if admin:
        user.role = "Admin"
    db_session.commit()
    client = setup_authenticated_session(app_with_routes.test_client(), US, "kvarak")
    with client.session_transaction() as sess:
        sess["all_teams"] = [US]
        sess["all_team_names"] = ["Dalby Stenbrotters FC"]
    return client


class TestMainRoutes:
    def test_index_anonymous(self, app_with_routes):
        response = app_with_routes.test_client().get("/")
        assert response.status_code == 200
        assert b"<html" in response.data

    def test_index_authenticated(self, app_with_routes, db_session):
        response = _client(app_with_routes, db_session).get("/")
        assert response.status_code == 200
        assert b"Dalby Stenbrotters FC" in response.data

    @pytest.mark.parametrize("path", ["/settings", "/debug"])
    def test_protected_pages_forward_to_login(self, app_with_routes, path):
        response = app_with_routes.test_client().get(path)
        assert response.status_code == 200
        assert b"/login" in response.data

    def test_settings_get(self, app_with_routes, db_session):
        response = _client(app_with_routes, db_session).get("/settings")
        assert response.status_code == 200
        assert b"<form" in response.data

    def test_changes_page(self, app_with_routes):
        response = app_with_routes.test_client().get("/changes")
        assert response.status_code == 200
        assert b"<html" in response.data

    def test_debug_forwards_non_admin_home(self, app_with_routes, db_session):
        response = _client(app_with_routes, db_session).get("/debug")
        assert response.status_code == 200
        assert b"/login" not in response.data

    def test_debug_renders_for_admin(self, app_with_routes, db_session):
        response = _client(app_with_routes, db_session, admin=True).get("/debug")
        assert response.status_code == 200
        assert b"kvarak" in response.data


class TestChangelogEscaping:
    """Changelog entries are rendered with |safe, so values must be escaped."""

    def test_commit_message_html_is_escaped(self, tmp_path):
        import json

        from app.factory import create_app
        from config import TestConfig

        (tmp_path / "changelog.json").write_text(
            json.dumps(
                {
                    "entries": [
                        {
                            "type": "commit",
                            "date": "2026-10-28 12:00",
                            "version": "v1<b>",
                            "message": "Fix <script>alert(1)</script> bug",
                        }
                    ]
                }
            )
        )
        test_app = create_app(TestConfig, include_routes=True)
        test_app.static_folder = str(tmp_path)

        response = test_app.test_client().get("/changes")

        assert response.status_code == 200
        assert b"<script>alert(1)</script>" not in response.data
        assert b"Fix &lt;script&gt;alert(1)&lt;/script&gt; bug" in response.data
        assert b"v1&lt;b&gt;" in response.data


class TestAdminRequiredResponse:
    """Shared admin gate used by debug and admin API routes."""

    @pytest.mark.parametrize(
        ("role", "expected_status"), [("Admin", None), ("User", 403), (None, 403)]
    )
    def test_admin_gate(self, app, role, expected_status):
        from unittest.mock import MagicMock, patch

        import app.blueprints.main as main_module

        user = None
        if role:
            user = MagicMock()
            user.is_admin.return_value = role == "Admin"
        with (
            app.test_request_context(),
            patch.object(main_module, "get_current_user", return_value=user),
        ):
            result = main_module.admin_required_response()

        if expected_status is None:
            assert result is None
        else:
            assert result[1] == expected_status


class TestDebugPageAccessibility:
    """Debug charts page renders accessible controls and valid inline JS."""

    def test_admin_debug_page(self, authenticated_client, db_session):
        import re
        import shutil
        import subprocess  # nosec B404 - static local syntax check only
        import tempfile

        from models import User

        admin = User(12345, "admin", "admin", "x", "k", "s")
        admin.setRole("Admin")
        db_session.add(admin)
        db_session.commit()

        with authenticated_client.session_transaction() as sess:
            sess["current_user"] = "admin"
        response = authenticated_client.get("/debug")
        html = response.get_data(as_text=True)

        assert response.status_code == 200
        assert 'id="dateRangeError"' in html and 'role="alert"' in html
        assert '<legend class="sr-only">Chart date range</legend>' in html
        assert (
            'role="img"' in html
            and 'aria-describedby="userActivityChartDescription"' in html
        )
        assert 'aria-label="Shrink User Activity chart"' in html
        assert 'tabindex="0"' in html
        assert html.index("debug-date-filter.js") < html.index("debug-charts.js")

        if shutil.which("node"):
            scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
            inline = max(scripts, key=len)
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
                f.write(inline)
            check = subprocess.run(  # nosec B603 B607
                ["node", "--check", f.name], capture_output=True, text=True
            )
            assert check.returncode == 0, check.stderr


def test_load_changelog_entries_groups_commits_under_technical_releases(tmp_path):
    import json

    from app.blueprints.main import load_changelog_entries

    (tmp_path / "changelog.json").write_text(
        json.dumps(
            {
                "entries": [
                    {"type": "commit", "date": "2026-10-03 10:00", "message": "c3"},
                    {"type": "commit", "date": "2026-10-02 10:00", "message": "c2"},
                    {"type": "commit", "date": "2026-10-01 10:00", "message": "c1"},
                ]
            }
        )
    )
    (tmp_path / "releases-internal.json").write_text(
        json.dumps(
            {
                "entries": [
                    {"type": "internal_release", "date": "2026-10-03 10:00"},
                    {"type": "internal_release", "date": "2026-10-01 12:00"},
                ]
            }
        )
    )
    (tmp_path / "releases.json").write_text(
        json.dumps({"entries": [{"type": "user_release", "date": "2026-10-02 12:00"}]})
    )

    entries = load_changelog_entries(str(tmp_path))

    assert [(e["type"], e.get("message"), e["group"]) for e in entries] == [
        ("internal_release", "", 1),
        ("commit", "c3", 1),
        ("user_release", "", None),
        ("commit", "c2", None),
        ("internal_release", "", 2),
        ("commit", "c1", 2),
    ]
    assert entries[0]["date"] == "2026-10-03"


def test_load_changelog_entries_missing_files(tmp_path):
    from app.blueprints.main import load_changelog_entries

    assert load_changelog_entries(str(tmp_path)) == []


def test_pages_render_without_flask_bootstrap(app_with_routes):
    """REFACTOR-103: pages use our own skeleton and only Bootstrap 4."""
    html = app_with_routes.test_client().get("/changes").get_data(as_text=True)

    assert html.lstrip().startswith("<!DOCTYPE html>")
    assert '<html lang="en">' in html
    assert html.count("<title>") == 1
    assert "bootstrap/4.5.0/css/bootstrap.min.css" in html
    assert "bootstrap/3" not in html


def test_pages_include_dark_mode(app_with_routes):
    """UI-014: pre-paint snippet before CSS, toggle button, stylesheet and script."""
    html = app_with_routes.test_client().get("/changes").get_data(as_text=True)

    head = html[: html.index("</head>")]
    assert 'localStorage.getItem("htstatus-dark-mode")' in head
    assert head.index("htstatus-dark-mode") < head.index("stylesheet")
    assert 'id="dark-mode-toggle"' in html
    assert 'aria-label="Toggle dark mode"' in html
    assert 'id="dark-mode-icon">&#127769;</span>' in html
    assert "css/dark-mode.css" in html
    assert "js/dark-mode.js" in html


def test_loading_spinner_is_hidden_when_coming_back(app_with_routes):
    """Back/forward restores a page with the spinner that loading() showed on leaving."""
    html = app_with_routes.test_client().get("/changes").get_data(as_text=True)

    handler = html[html.index('addEventListener("pageshow"') :]
    assert '$("#loading").hide();' in handler[: handler.index("});")]
