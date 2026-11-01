"""FEAT-034: search engines see only the public pages, with good titles and previews."""

import json
import re

import pytest

from tests.factories import setup_authenticated_session

SITE = "https://planner.example.com"


@pytest.fixture
def client(app_with_routes):
    app_with_routes.config["CALLBACK_URL"] = f"{SITE}/login"
    return app_with_routes.test_client()


def test_robots_allows_only_public_pages_and_points_to_sitemap(client):
    response = client.get("/robots.txt")
    text = response.get_data(as_text=True)

    assert response.mimetype == "text/plain"
    assert "Allow: /$" in text
    assert "Allow: /changes" in text
    assert "Allow: /login" in text
    assert "Disallow: /\n" in text
    assert f"Sitemap: {SITE}/sitemap.xml" in text


def test_sitemap_lists_public_pages_with_the_public_address(client):
    response = client.get("/sitemap.xml")
    xml = response.get_data(as_text=True)

    assert response.mimetype == "application/xml"
    assert re.findall(r"<loc>([^<]+)</loc>", xml) == [f"{SITE}/", f"{SITE}/changes"]


def test_home_page_has_description_preview_and_structured_data(client):
    html = client.get("/").get_data(as_text=True)
    head = html[: html.index("</head>")]

    title = re.search(r"<title>([^<]+)</title>", head).group(1)
    assert title == "HattrickPlanner - Team Management Tool for Hattrick Managers"
    assert len(title) <= 60
    description = re.search(r'name="description" content="([^"]+)"', head).group(1)
    assert 120 <= len(description) <= 160
    assert f'<link rel="canonical" href="{SITE}/">' in head
    assert f'property="og:image" content="{SITE}/static/img/share.png"' in head
    assert 'name="twitter:card" content="summary_large_image"' in head
    assert "noindex" not in head

    data = json.loads(
        re.search(
            r'<script type="application/ld\+json">(.*?)</script>', head, re.S
        ).group(1)
    )
    assert data["@type"] == "WebApplication"
    assert data["url"] == f"{SITE}/"


def test_logged_in_pages_are_noindex_with_a_page_title(app_with_routes, db_session):
    from tests.conftest import create_test_user

    app_with_routes.config["CALLBACK_URL"] = f"{SITE}/login"
    user = create_test_user(db_session)
    client = setup_authenticated_session(app_with_routes.test_client(), user)

    html = client.get("/settings").get_data(as_text=True)
    head = html[: html.index("</head>")]

    assert '<meta name="robots" content="noindex, nofollow">' in head
    assert 'rel="canonical"' not in head
    assert "ld+json" not in head
    assert re.search(r"<title>Settings · \S", head)


def test_share_image_is_served(client):
    response = client.get("/static/img/share.png")
    assert response.status_code == 200
    assert response.mimetype == "image/png"


def test_site_icons_are_served_and_linked(client):
    favicon = client.get("/favicon.ico")
    assert favicon.status_code == 200
    assert favicon.mimetype == "image/x-icon"

    html = client.get("/").get_data(as_text=True)
    assert re.search(r'href="/static/img/icon\.svg"\s+type="image/svg\+xml"', html)
    assert 'rel="apple-touch-icon"' in html
    for name in ("icon.svg", "icon-192.png", "icon-512.png", "icon-maskable-512.png"):
        assert client.get(f"/static/img/{name}").status_code == 200
