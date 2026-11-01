"""The guided tours point at elements that really exist on their pages."""

from pathlib import Path
import re

import pytest

TUTORIAL_JS = Path("app/static/js/tutorial-manager.js").read_text()


def _tour_ids(start_marker, end_marker):
    """``#id`` targets of the tour between two markers in tutorial-manager.js."""
    block = TUTORIAL_JS[TUTORIAL_JS.index(start_marker) : TUTORIAL_JS.index(end_marker)]
    return re.findall(r"element: '#([\w-]+)'", block)


@pytest.fixture
def logged_in(app_with_routes, db_session):
    from tests.conftest import create_test_user
    from tests.factories import setup_authenticated_session

    create_test_user(db_session)
    db_session.commit()
    return setup_authenticated_session(app_with_routes.test_client(), 12345)


@pytest.mark.parametrize(
    ("page", "start", "end"),
    [
        ("/", "startWelcomeTour() {", "markWelcomeTourCompleted() {"),
        ("/player?id=12345", "'player-management': {", "'data-update': {"),
    ],
)
def test_tour_targets_exist(logged_in, page, start, end):
    ids = _tour_ids(start, end)
    assert ids, "tour has element targets"
    html = logged_in.get(page).get_data(as_text=True)
    missing = [i for i in ids if f'id="{i}"' not in html]
    assert not missing, f"{page} lacks tour targets {missing}"


def test_tutorial_storage_is_separate_from_session_storage():
    session_js = Path("app/static/js/session-persistence.js").read_text()
    assert "ht_tutorial_progress" in TUTORIAL_JS
    assert "ht_tutorial_progress" not in session_js
