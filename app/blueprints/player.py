"""Player management routes blueprint for HT Status application."""

from flask import Blueprint, request, session

from app import transfers
from app.auth_utils import (
    current_team,
    get_current_user,
    require_authentication,
    track_activity,
    WRONG_TEAM,
)
from app.columns import user_columns
from app.utils import create_page, dprint, get_training

# Create Blueprint for player routes
player_bp = Blueprint("player", __name__)

# These will be set by setup_player_blueprint()
db = None
calccolumns = []
tracecolumns = []
default_group_order = 99


def setup_player_blueprint(db_instance, calc_cols, trace_cols, group_order=99):
    """Initialize player blueprint with db instance and column definitions."""
    global db, calccolumns, tracecolumns, default_group_order
    db = db_instance
    calccolumns = calc_cols
    tracecolumns = trace_cols
    default_group_order = group_order


def add_transfer_bids(teamid, players):
    """Attach the bid snapshot from the last Update to transfer-listed players."""
    bids = transfers.team_transfers(teamid)
    for p in players:
        bid = bids.get(p["ht_id"]) if p.get("is_transfer_listed") else None
        if bid:
            p["transfer"] = {**bid, "status": transfers.status(bid)}


def add_star_ratings(match_play_model, players):
    """Set max_stars/last_stars (and their match ids) on each player dict.

    Uses one query for all players instead of two per player.
    """
    for p in players:
        p["max_stars"] = "-"
        p["last_stars"] = "-"
    by_id = {p["ht_id"]: p for p in players}
    if not by_id:
        return

    rated_plays = (
        db.session.query(match_play_model)
        .filter(match_play_model.player_id.in_(list(by_id)))
        .filter(match_play_model.rating_stars.isnot(None))
        .order_by(match_play_model.datetime.desc())
        .all()
    )
    for play in rated_plays:
        p = by_id[play.player_id]
        if p["max_stars"] == "-" or play.rating_stars > p["max_stars"]:
            p["max_stars"] = play.rating_stars
            p["max_stars_match_id"] = play.match_id
        if p["last_stars"] == "-" and play.rating_stars != 0:
            p["last_stars"] = play.rating_stars
            p["last_stars_match_id"] = play.match_id


@player_bp.route("/player", methods=["GET", "POST"])
@require_authentication
@track_activity("player")
def player():
    """Display player list with skill tracking and grouping."""
    from models import Group, MatchPlay, Players, PlayerSetting

    updategroup = request.form.get("updategroup")
    playerid = request.form.get("playerid")
    groupid = request.form.get("groupid")

    teamid, teamname = current_team()
    if teamid is None:
        return create_page(template="main.html", title="Players", error=WRONG_TEAM)

    # Get 4-week timeline for this team
    from app.utils import get_team_timeline

    timeline_changes = get_team_timeline(teamid)

    if updategroup and playerid and groupid:
        if int(groupid) < 0:
            theconnection = (
                db.session.query(PlayerSetting)
                .filter_by(player_id=int(playerid), user_id=session["current_user_id"])
                .first()
            )
            if theconnection:
                db.session.delete(theconnection)
                db.session.commit()
        else:
            connection = (
                db.session.query(PlayerSetting)
                .filter_by(player_id=int(playerid), user_id=session["current_user_id"])
                .first()
            )
            if connection:
                (
                    db.session.query(PlayerSetting)
                    .filter_by(
                        player_id=int(playerid), user_id=session["current_user_id"]
                    )
                    .update({"group_id": groupid})
                )
                db.session.commit()
            else:
                newconnection = PlayerSetting(
                    player_id=int(playerid),
                    user_id=session["current_user_id"],
                    group_id=groupid,
                )
                db.session.add(newconnection)
                db.session.commit()

    group_data = (
        db.session.query(Group)
        .filter_by(user_id=session["current_user_id"])
        .order_by(Group.order)
        .all()
    )

    # Create default groups if user has none
    if not group_data:
        try:
            from app.utils import create_default_groups

            created_groups = create_default_groups(session["current_user_id"])
            if created_groups:
                group_data = created_groups
                dprint(
                    1,
                    f"Created {len(created_groups)} default groups for user {session['current_user_id']}",
                )
        except Exception as e:
            dprint(1, f"Failed to create default groups: {e}")

    into_groups = (
        db.session.query(PlayerSetting)
        .filter_by(user_id=session["current_user_id"])
        .all()
    )

    # Of each of the players you ever have owned, get the last download
    players_data = (
        db.session.query(Players)
        .filter_by(owner=teamid)
        .order_by(Players.data_date, Players.number)
        .all()
    )

    allplayerids, allplayers, playernames = get_training(players_data)

    # players_data is oldest-first: keep the first and the last record per player
    players_oldest_dict = {}
    latest_by_player = {}
    for record in players_data:
        record_dict = dict(iter(record))
        players_oldest_dict.setdefault(record.ht_id, record_dict)
        latest_by_player[record.ht_id] = record_dict
    players_now = list(latest_by_player.values())
    add_transfer_bids(teamid, players_now)

    add_star_ratings(MatchPlay, players_now)

    # Get the columns
    user = get_current_user()
    columns = user_columns(user)

    from app.utils import best_position, calculateContribution, calculateManmark

    shown_calc_columns = [key for _title, key in columns if key in calccolumns]
    for p in players_now:
        for key in shown_calc_columns:
            p[key] = calculateContribution(key, p)
        p["MMC"] = calculateManmark(p)
        p["bestposition"] = best_position(p)

    # Group the players into groups
    tmp_player = players_now
    grouped_players_now = {}
    for group in group_data:
        in_this_group = [
            elem.player_id for elem in into_groups if elem.group_id == group.id
        ]
        grouped_players_now[group.id] = [
            player for player in tmp_player if player["ht_id"] in in_this_group
        ]
        players_now = [
            player for player in players_now if player["ht_id"] not in in_this_group
        ]

    # Add a default group
    default_group = Group(
        user_id=0,
        name="",
        order=default_group_order,
        textcolor="#000000",
        bgcolor="#FFFFFF",
    )
    before_default = [g for g in group_data if g.order < default_group_order]
    after_default = [g for g in group_data if g.order >= default_group_order]
    before_default.append(default_group)

    group_data = before_default + after_default

    grouped_players_now[default_group.id] = players_now

    return create_page(
        template="player.html",
        title=teamname,
        teamid=teamid,
        columns=columns,
        tracecolumns=tracecolumns,
        calccolumns=calccolumns,
        grouped_players=grouped_players_now,
        players=players_now,
        players_data=players_data,
        players_oldest=players_oldest_dict,
        group_data=group_data,
        skills=tracecolumns,
        playernames=playernames,
        allplayerids=allplayerids,
        allplayers=allplayers,
        timeline_changes=timeline_changes,
        last_update=user.last_update if user else None,
        format_money=transfers.format_money,
    )
