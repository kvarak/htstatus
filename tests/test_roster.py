"""Tests for app/roster.py"""

import pytest

from app.roster import latest_player_records, oldest_player_records
from models import Players
from tests.factories import make_player_record

TEAM = 999002


def _add(db_session, ht_id, date, owner=TEAM, scorer=1):
    record = make_player_record(ht_id, owner)
    record.data_date = date
    record.scorer = scorer
    db_session.add(record)


def test_latest_and_oldest_records_per_player(db_session):
    _add(db_session, 1, "2026-01-01", scorer=3)
    _add(db_session, 1, "2026-02-01", scorer=4)
    _add(db_session, 2, "2026-01-15", scorer=5)
    _add(db_session, 3, "2026-02-01", owner=0)  # sold player
    db_session.flush()

    latest = latest_player_records(Players, TEAM)
    oldest = oldest_player_records(Players, TEAM)

    assert [(p.ht_id, p.scorer) for p in latest] == [(1, 4), (2, 5)]
    assert {ht_id: p.scorer for ht_id, p in oldest.items()} == {1: 3, 2: 5}


def test_empty_team(db_session):  # noqa: ARG001
    assert latest_player_records(Players, 424242) == []
    assert oldest_player_records(Players, 424242) == {}


class TestRosterPages:
    """Pages built on the roster queries show current players, not sold ones."""

    USER_TEAM = 12345

    @pytest.fixture
    def roster_client(self, app_with_routes, db_session):
        from models import User
        from tests.factories import setup_authenticated_session

        db_session.add(User(self.USER_TEAM, "owner", "owner", "x", "k", "s"))

        for ht_id, first, last, date in [
            (601, "Alfa", "Zettergren", "2026-01-01"),
            (601, "Alfa", "Zettergren", "2026-02-01"),
            (602, "Beta", "Quistorp", "2026-02-01"),
        ]:
            record = make_player_record(ht_id, self.USER_TEAM, first, last)
            record.data_date = date
            record.number = ht_id - 600
            db_session.add(record)
        sold = make_player_record(603, 0, "Gamma", "Bittnerson")
        sold.old_owner = self.USER_TEAM
        sold.data_date = "2026-01-01"
        db_session.add(sold)
        # Commit (inside the fixture's savepoint): request teardown discards flushes
        db_session.commit()

        client = app_with_routes.test_client()
        return setup_authenticated_session(client, self.USER_TEAM)

    @pytest.mark.parametrize(
        "url",
        [
            f"/training?id={USER_TEAM}",
            f"/formations?id={USER_TEAM}",
            f"/player/compare?team_id={USER_TEAM}&player_ids=601&player_ids=602",
        ],
    )
    def test_page_lists_current_players_only(self, roster_client, url):
        response = roster_client.get(url)

        assert response.status_code == 200
        assert b"Zettergren" in response.data
        assert b"Quistorp" in response.data
        assert b"Bittnerson" not in response.data

    def test_stats_counts_current_players_only(self, roster_client):
        import re

        response = roster_client.get(f"/stats?id={self.USER_TEAM}")

        assert response.status_code == 200
        total = re.search(rb'card-title mb-1">(\d+)</h6>', response.data)
        assert total and total.group(1) == b"2"

    def test_formations_page_script_is_valid_js(self, roster_client):
        import re
        import shutil
        import subprocess  # nosec B404 - static local syntax check only
        import tempfile

        html = roster_client.get(f"/formations?id={self.USER_TEAM}").get_data(
            as_text=True
        )
        assert "const TEAM_SIZE = 11;" in html
        assert "colourPitchByEffectiveness" in html

        if not shutil.which("node"):
            pytest.skip("Node.js not installed")
        for script in re.findall(r"<script>(.*?)</script>", html, re.S):
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
                f.write(script)
            check = subprocess.run(  # nosec B603 B607
                ["node", "--check", f.name], capture_output=True, text=True
            )
            assert check.returncode == 0, check.stderr
