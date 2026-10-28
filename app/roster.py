"""Team roster queries over the per-day Players snapshot table.

Players has one row per player per data_date. Players who left a team have
owner=0 (see team.reconcile_roster), so filtering on owner=teamid only returns
players currently in the team.
"""

from app import db


def _snapshot_per_player(players_model, teamid, newest):
    date_order = (
        players_model.data_date.desc() if newest else players_model.data_date.asc()
    )
    return (
        db.session.query(players_model)
        .filter_by(owner=teamid)
        .distinct(players_model.ht_id)
        .order_by(players_model.ht_id, date_order)
        .all()
    )


def latest_player_records(players_model, teamid):
    """Return the newest record of each player in the team, newest data first."""
    records = _snapshot_per_player(players_model, teamid, newest=True)
    return sorted(records, key=lambda p: p.data_date, reverse=True)


def oldest_player_records(players_model, teamid):
    """Return {ht_id: oldest record} for each player in the team."""
    return {
        p.ht_id: p for p in _snapshot_per_player(players_model, teamid, newest=False)
    }
