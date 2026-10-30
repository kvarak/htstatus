"""Tests for FEAT-025: current bids on transfer-listed players (app/transfers.py)."""

from datetime import datetime
from types import SimpleNamespace

import pytest

from app import transfers
from app.chpp.models import BidderTeam, TransferDetails

NOW = datetime(2026, 10, 29, 20, 0, 0)


def _details(listed=True, highest_bid=0, bidder=None):
    return SimpleNamespace(
        transfer_listed=listed,
        transfer_details=TransferDetails(
            asking_price=1000000,
            deadline="2026-10-30 18:00:00",
            highest_bid=highest_bid,
            bidder_team=bidder,
        ),
    )


class TestFromDetails:
    def test_listed_player_with_bid(self):
        bid = transfers.from_details(
            _details(highest_bid=1200000, bidder=BidderTeam(7, "Buyers FC"))
        )
        assert bid == {
            "asking_price": 1000000,
            "highest_bid": 1200000,
            "deadline": "2026-10-30 18:00:00",
            "bidder": "Buyers FC",
        }

    def test_listed_player_without_bids(self):
        bid = transfers.from_details(_details())
        assert bid["highest_bid"] == 0
        assert bid["bidder"] is None

    def test_not_listed_or_no_details(self):
        assert transfers.from_details(_details(listed=False)) is None
        listed_without_details = SimpleNamespace(
            transfer_listed=True, transfer_details=None
        )
        assert transfers.from_details(listed_without_details) is None
        assert transfers.from_details(SimpleNamespace()) is None


class TestStatus:
    @pytest.mark.parametrize(
        ("deadline", "expected"),
        [
            ("2026-11-02 20:00:00", "active"),
            ("2026-10-30 19:59:59", "ending_soon"),
            ("2026-10-29 19:00:00", "deadline_passed"),
            ("not a date", "active"),
        ],
    )
    def test_status(self, deadline, expected):
        assert transfers.status({"deadline": deadline}, now=NOW) == expected

    def test_missing_deadline_is_active(self):
        assert transfers.status({}, now=NOW) == "active"


def test_format_money():
    assert transfers.format_money(2200000) == "2\u00a0200\u00a0000 SEK"
    assert transfers.format_money(None) == "0 SEK"


def test_snapshot_roundtrip_replaces_old_bids(app_with_routes):  # noqa: ARG001
    transfers.save_team_transfers(42, {101: {"highest_bid": 5}})
    assert transfers.team_transfers(42) == {101: {"highest_bid": 5}}

    transfers.save_team_transfers(42, {})
    assert transfers.team_transfers(42) == {}
    assert transfers.team_transfers(43) == {}  # never saved


def test_update_survives_unwritable_snapshot(
    app_with_routes, monkeypatch  # noqa: ARG001
):
    from app.blueprints.team import save_transfer_snapshot

    def fail(*_args):
        raise OSError("disk full")

    monkeypatch.setattr(transfers, "save_team_transfers", fail)
    save_transfer_snapshot(42, {})  # logged, not raised
