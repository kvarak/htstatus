"""Player management routes blueprint for HT Status application."""

import math

from flask import Blueprint, request, session
from sqlalchemy import text

from app.auth_utils import (
    get_current_user_id,
    get_team_info,
    get_user_teams,
    require_authentication,
)
from app.error_handlers import (
    TeamAccessError,
    ValidationError,
    handle_error,
    validate_team_id,
)
from app.utils import create_page, dprint, get_training

# Create Blueprint for player routes
player_bp = Blueprint("player", __name__)

# These will be set by setup_player_blueprint()
db = None
defaultcolumns = []
calccolumns = []
tracecolumns = []
default_group_order = 99


def setup_player_blueprint(
    db_instance, def_cols, calc_cols, trace_cols, group_order=99
):
    """Initialize player blueprint with db instance and column definitions."""
    global db, defaultcolumns, calccolumns, tracecolumns, default_group_order
    db = db_instance
    defaultcolumns = def_cols
    calccolumns = calc_cols
    tracecolumns = trace_cols
    default_group_order = group_order


@player_bp.route("/player", methods=["GET", "POST"])
@require_authentication
def player():
    """Display player list with skill tracking and grouping."""
    # Get model classes from registry
    from app.model_registry import (
        get_group_model,
        get_match_play_model,
        get_player_setting_model,
        get_players_model,
        get_user_model,
    )

    PlayerSetting = get_player_setting_model()
    Group = get_group_model()
    Players = get_players_model()
    User = get_user_model()
    MatchPlay = get_match_play_model()

    updategroup = request.form.get("updategroup")
    playerid = request.form.get("playerid")
    groupid = request.form.get("groupid")

    teamid = request.values.get("id")

    try:
        teamid = validate_team_id(teamid if teamid else request.form.get("id"))
    except ValidationError as e:
        return handle_error(e)

    dprint(1, teamid)

    # Validate team access using consolidated function
    all_teams, all_team_names = get_user_teams()
    is_valid, teamname, error_msg = get_team_info(teamid, (all_teams, all_team_names))

    if not is_valid:
        return handle_error(TeamAccessError(error_msg))

    if updategroup and playerid and groupid:
        current_user_id = get_current_user_id()
        if int(groupid) < 0:
            theconnection = (
                db.session.query(PlayerSetting)
                .filter_by(player_id=int(playerid), user_id=current_user_id)
                .first()
            )
            if theconnection:
                db.session.delete(theconnection)
                db.session.commit()
        else:
            connection = (
                db.session.query(PlayerSetting)
                .filter_by(player_id=int(playerid), user_id=current_user_id)
                .first()
            )
            if connection:
                (
                    db.session.query(PlayerSetting)
                    .filter_by(player_id=int(playerid), user_id=current_user_id)
                    .update({"group_id": groupid})
                )
                db.session.commit()
            else:
                newconnection = PlayerSetting(
                    player_id=int(playerid), user_id=current_user_id, group_id=groupid
                )
                db.session.add(newconnection)
                db.session.commit()

    group_data = (
        db.session.query(Group)
        .filter_by(user_id=session["current_user_id"])
        .order_by(Group.order)
        .all()
    )

    into_groups = (
        db.session.query(PlayerSetting)
        .filter_by(user_id=session["current_user_id"])
        .all()
    )

    # Of each of the players you ever have owned, get the last download
    players_data = (
        db.session.query(Players)
        .filter_by(owner=teamid)
        .order_by(text("data_date"))
        .order_by(text("number"))
        .all()
    )

    (allplayerids, allplayers, playernames) = get_training(players_data)

    newlst = {}
    for thislist in players_data:
        newlst[thislist.ht_id] = dict(iter(thislist))
    players_now = []
    for _k, val in newlst.items():
        players_now.append(val)

    # Of each of the players you ever have owned, get the first download
    players_data = (
        db.session.query(Players)
        .filter_by(owner=teamid)
        .order_by(text("data_date desc"))
        .all()
    )
    newlst = {}
    for thislist in players_data:
        newlst[thislist.ht_id] = dict(iter(thislist))
    players_oldest_dict = {}
    for _k, val in newlst.items():
        players_oldest_dict[val["ht_id"]] = val

    # Add stars to the list of players
    for p in players_now:
        dbmatch = (
            db.session.query(MatchPlay)
            .filter_by(player_id=p["ht_id"])
            .order_by(text("rating_stars desc"))
            .all()
        )
        p["max_stars"] = "-"
        for m in dbmatch:
            if m.rating_stars is not None:
                p["max_stars"] = m.rating_stars
                p["max_stars_match_id"] = m.match_id
                break
        dbmatch = (
            db.session.query(MatchPlay)
            .filter_by(player_id=p["ht_id"])
            .order_by(text("datetime desc"))
            .all()
        )
        p["last_stars"] = "-"
        for m in dbmatch:
            if m.rating_stars is not None and m.rating_stars != 0:
                p["last_stars"] = m.rating_stars
                p["last_stars_match_id"] = m.match_id
                break

    # Get the columns
    user = db.session.query(User).filter_by(ht_id=session["current_user_id"]).first()
    columns = User.getColumns(user)
    if len(columns) == 0:
        columns = defaultcolumns

    # Import calculateContribution from routes module for backward compatibility
    from app.utils import calculateContribution, calculateManmark

    # Calculate contributions
    for _x, c in columns:
        if c in calccolumns:
            for p in players_now:
                p[c] = calculateContribution(c, p)
                p["MMC"] = calculateManmark(p)

    for _x, c in columns:
        for p in players_now:
            bestposition = "-"
            bestval = 0
            for c in calccolumns:
                tmp = calculateContribution(c, p)
                if tmp > bestval:
                    bestposition = c
                    bestval = tmp
            p["bestposition"] = bestposition
            # Form multiplies to skills
            p["formfactor"] = round(math.pow(((p["form"] - 0.5) / 7), 0.45), 2)

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
    )
