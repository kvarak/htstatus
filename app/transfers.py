"""Transfer list bids for your own players (FEAT-025).

Bids come from CHPP playerdetails, which Update already fetches for every
player, so this costs no extra CHPP calls. The snapshot is stored per team as
JSON in the instance folder (no database change) and shown until the next Update.
A sold player leaves the roster at the next Update, so "sold" needs no status.
"""

from datetime import datetime, timedelta

from app import instance_cache

FOLDER = "transfers"
ENDING_SOON = timedelta(hours=24)
DEADLINE_FORMAT = "%Y-%m-%d %H:%M:%S"


def from_details(details):
    """Bid snapshot from a CHPP player details object, or None if not listed."""
    transfer = getattr(details, "transfer_details", None)
    if not getattr(details, "transfer_listed", False) or transfer is None:
        return None
    bidder = transfer.bidder_team
    return {
        "asking_price": transfer.asking_price or 0,
        "highest_bid": transfer.highest_bid or 0,
        "deadline": transfer.deadline or "",
        "bidder": bidder.team_name if bidder else None,
    }


def save_team_transfers(team_id, transfers):
    """Replace the team's snapshot (``{player_id: bid snapshot}``)."""
    instance_cache.write_json(
        FOLDER, team_id, {str(k): v for k, v in transfers.items()}
    )


def team_transfers(team_id):
    """The team's last saved snapshot as ``{player_id: bid snapshot}``."""
    stored = instance_cache.read_json(FOLDER, team_id) or {}
    return {int(k): v for k, v in stored.items()}


def status(transfer, now=None):
    """ "active", "ending_soon" (under 24 h left) or "deadline_passed"."""
    try:
        deadline = datetime.strptime(transfer["deadline"], DEADLINE_FORMAT)
    except (KeyError, TypeError, ValueError):
        return "active"
    left = deadline - (now or datetime.now())
    if left <= timedelta(0):
        return "deadline_passed"
    return "ending_soon" if left <= ENDING_SOON else "active"


def format_money(amount):
    """CHPP amounts are in SEK, e.g. 2200000 -> "2 200 000 SEK"."""
    return f"{amount or 0:,} SEK".replace(",", "\u00a0")
