"""Tests for app/error_handlers.py: global error pages."""


def test_404_renders_error_page_and_is_logged(app_with_routes, db_session, monkeypatch):
    from models import ErrorLog

    monkeypatch.setitem(app_with_routes.config, "FLASK_ENV", "production")
    response = app_with_routes.test_client().get("/no-such-page")

    assert response.status_code == 404
    html = response.get_data(as_text=True)
    assert "Page not found" in html
    assert 'class="page-header"' in html  # shared layout
    assert db_session.query(ErrorLog).filter_by(error_type="404").count() == 1
