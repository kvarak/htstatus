"""Every page shares one look and uses the user's Hattrick terms and level format."""

from datetime import datetime, timedelta
import re

import pytest

from app import translations
from models import Group, PlayerSetting, User
from tests.factories import make_player_record, setup_authenticated_session
from tests.test_matches import _played_match
from tests.test_translations import FRENCH

TEAM = 12345
PAGES = {
    "player": f"/player?id={TEAM}",
    "stats": f"/stats?id={TEAM}",
    "training": f"/training?id={TEAM}",
    "formations": f"/formations?id={TEAM}",
    "compare": f"/player/compare?team_id={TEAM}&player_ids=601&player_ids=602",
    "settings": "/settings",
    "matches": f"/matches?id={TEAM}",
    "feedback": "/feedback/",
    "feedback-new": "/feedback/new",
    "main": "/",
    "changes": "/changes",
}
BOOTSTRAP_BLUE = re.compile(r"#007bff|#17a2b8|#42a5f5|rgba\(0, ?123, ?255", re.I)


@pytest.fixture
def french_words_client(app_with_routes, db_session):
    """Logged-in client with French terms cached and levels shown as words."""
    user = User(TEAM, "kvarak", "kvarak", "x", "k", "s")
    db_session.add(user)
    db_session.flush()
    for ht_id, last in ((601, "Keeper"), (602, "Winger")):
        for days, keeper in ((20, 6), (2, 7)):
            row = make_player_record(ht_id, TEAM, "Test", last)
            row.data_date = datetime.now() - timedelta(days=days)
            row.number = ht_id - 600
            row.keeper = keeper
            row.native_country_id = 1  # Sweden
            db_session.add(row)
    group = Group(TEAM, "Main Squad", 1, "#ffffff", "#2e7d32")
    db_session.add(group)
    db_session.flush()
    db_session.add(PlayerSetting(601, TEAM, group.id))
    db_session.add(_played_match(TEAM))
    db_session.commit()

    with app_with_routes.test_request_context("/"):
        translations._write(5, FRENCH)
    client = setup_authenticated_session(app_with_routes.test_client(), TEAM, "kvarak")
    with client.session_transaction() as sess:
        sess["ht_language_id"] = 5
        sess["access_key"] = "k"
        sess["access_secret"] = "s"
    client.set_cookie(translations.LEVEL_FORMAT_COOKIE, "words")
    return client


@pytest.mark.parametrize("name", PAGES)
def test_page_uses_shared_layout(french_words_client, name):
    response = french_words_client.get(PAGES[name])
    html = response.get_data(as_text=True)

    assert response.status_code == 200, html[:300]
    assert html.count('class="page-header"') == 1
    assert html.count('class="site-footer') == 1
    assert "css/theme.css" in html
    assert not BOOTSTRAP_BLUE.search(html), BOOTSTRAP_BLUE.search(html)


def test_training_uses_terms_and_level_words(french_words_client):
    html = french_words_client.get(PAGES["training"]).get_data(as_text=True)
    assert ">Gardien</th>" in html
    assert '"Gardien"' in html  # chart series name
    assert "honorable" in html  # keeper 7 as a word


def test_compare_uses_terms_and_level_words(french_words_client):
    html = french_words_client.get(PAGES["compare"]).get_data(as_text=True)
    assert "<strong>Coup franc</strong>" in html
    assert "honorable" in html
    assert 'cdn.jsdelivr.net/npm/chart.js"' not in html  # Chart.js loaded once


def test_stats_position_chart_uses_hattrick_positions(french_words_client):
    html = french_words_client.get(PAGES["stats"]).get_data(as_text=True)
    assert '"Gardien de but"' in html
    assert '"Attaquant"' in html


def test_stats_country_charts_keep_flag_colors(french_words_client):
    """The one exception to the few-colors rule: country charts use flag colors."""
    html = french_words_client.get(PAGES["stats"]).get_data(as_text=True)
    assert '"#006AA7"' in html  # Swedish blue


def test_formations_tooltip_levels_follow_setting(french_words_client):
    html = french_words_client.get(PAGES["formations"]).get_data(as_text=True)
    assert '"7": "honorable"' in html
    assert "levelText(data.keeper || 0)" in html
