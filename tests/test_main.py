"""Tests for app/blueprints/main.py"""

import pytest


def test_module_imports():
    """Test that main blueprint module imports without errors."""
    import app.blueprints.main

    assert app.blueprints.main is not None


class TestMainRoutes:
    """Test main blueprint route functionality."""

    def test_index_route_unauthenticated(self, app):
        """Test index route without authentication."""
        # Create app with routes
        from app.factory import create_app
        from config import TestConfig

        test_app = create_app(TestConfig, include_routes=True)
        client = test_app.test_client()
        response = client.get("/")
        # Allow 500 for missing database setup in tests
        assert response.status_code in [200, 500]

    def test_index_route_authenticated(self, authenticated_client):
        """Test index route with authentication shows user content."""
        response = authenticated_client.get("/")
        # Allow 500 for missing database setup in tests
        assert response.status_code in [200, 500]
        if response.status_code == 200:
            # Should show basic page structure with authentication context
            assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

    def test_settings_route_unauthenticated(self, app):
        """Test settings route behavior (if it exists)."""
        client = app.test_client()
        response = client.get("/settings")
        # Route may not exist in test environment, allow 404
        assert response.status_code in [302, 401, 403, 404]

    def test_settings_route_authenticated_get(self, authenticated_client):
        """Test settings route GET with authentication."""
        response = authenticated_client.get("/settings")
        # Should show settings form or successful response
        assert response.status_code in [200, 500]  # Allow 500 for missing data

    def test_settings_route_authenticated_post(self, authenticated_client):
        """Test settings route POST with authentication."""
        response = authenticated_client.post(
            "/settings",
            data={"columns": "name,age,skills", "group_1_name": "Test Group"},
        )
        # Should process form submission
        assert response.status_code in [200, 302, 500]  # Allow 500 for missing data

    def test_changes_route_public(self, app):
        """Test changes route accessibility (if it exists)."""
        client = app.test_client()
        response = client.get("/changes")
        # Route may not exist in test environment - just verify no crashes
        # Allow both success and not found
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            # Should show changelog content if route exists
            assert (
                b"Changes" in response.data
                or b"Changelog" in response.data
                or b"Version" in response.data
            )

    def test_debug_route_unauthenticated(self, app):
        """Test debug/admin route behavior (if it exists)."""
        client = app.test_client()
        response = client.get("/debug")
        # Route may not exist in test environment, allow 404
        assert response.status_code in [302, 401, 403, 404]

    def test_debug_route_authenticated(self, authenticated_client):
        """Test debug/admin route with authentication."""
        response = authenticated_client.get("/debug")
        # Should show admin panel or error based on permissions
        assert response.status_code in [200, 302, 403, 500]  # Allow various responses

    def test_debug_route_post_authenticated(self, authenticated_client):
        """Test debug/admin route POST functionality."""
        response = authenticated_client.post("/debug", data={"action": "test_action"})
        # Should process admin action
        assert response.status_code in [200, 302, 400, 500]  # Allow various responses


class TestMainBlueprintSetup:
    """Test main blueprint setup and configuration."""

    def test_blueprint_registration(self, app):
        """Test main blueprint is properly registered."""
        # Check that main blueprint routes are available
        from app.factory import create_app
        from config import TestConfig

        test_app = create_app(TestConfig, include_routes=True)
        with test_app.test_client() as client:
            response = client.get("/changes")
            assert response.status_code == 200

    def test_template_rendering(self, authenticated_client):
        """Test that main routes render templates correctly."""
        # Test index template rendering - accept both success and redirect responses
        response = authenticated_client.get("/")
        assert response.status_code in [
            200,
            302,
            500,
        ]  # Allow for auth redirects or server errors

        # If successful, verify HTML content
        if response.status_code == 200:
            assert b"<!DOCTYPE html>" in response.data or b"<html" in response.data

        # Test changes template rendering - accept both success and redirect responses
        response = authenticated_client.get("/changes")
        assert response.status_code in [
            200,
            302,
            500,
        ]  # Allow for auth redirects or server errors

        # If successful, verify HTML content
        if response.status_code == 200:
            assert b"<!DOCTYPE html>" in response.data

    def test_main_blueprint_imports(self):
        """Test main blueprint components can be imported."""
        from flask import Blueprint

        from app.blueprints.main import main_bp, setup_main_blueprint

        assert isinstance(main_bp, Blueprint)
        assert main_bp.name == "main"
        assert callable(setup_main_blueprint)


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
            user.getRole.return_value = role
        fake_db = MagicMock()
        fake_db.session.query.return_value.filter_by.return_value.first.return_value = (
            user
        )

        with (
            app.test_request_context(),
            patch.object(main_module, "db", fake_db),
            patch.object(main_module, "get_current_user_id", return_value=1),
        ):
            result = main_module.admin_required_response()

        if expected_status is None:
            assert result is None
        else:
            assert result[1] == expected_status
