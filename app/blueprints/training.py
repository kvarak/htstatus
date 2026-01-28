"""Training routes blueprint for HT Status application."""

from datetime import date, timedelta

from flask import Blueprint, request, session
from sqlalchemy import text

from app.auth_utils import require_authentication
from app.utils import create_page

# Create Blueprint for training routes
training_bp = Blueprint("training", __name__)

# These will be set by setup_training_blueprint()
db = None
tracecolumns = []


def setup_training_blueprint(db_instance, trace_cols):
    """Initialize training blueprint with db instance and column definitions."""
    global db, tracecolumns
    db = db_instance
    tracecolumns = trace_cols


@training_bp.route("/training")
@require_authentication
def training():
    """Display player training progression and skill development."""
    from models import Players  # Import here to avoid circular dependencies
    from app.model_registry import get_user_model

    # Track user activity
    User = get_user_model()
    current_user = db.session.query(User).filter_by(ht_id=session["current_user_id"]).first()
    if current_user:
        current_user.training()
        db.session.commit()

    teamid = request.values.get("id")

    teamid = int(teamid) if teamid else request.form.get("id")
    all_teams = session["all_teams"]

    error = ""
    if teamid not in all_teams:
        error = "Wrong teamid, try the links."
        return create_page(template="training.html", title="Training")

    all_team_names = session["all_team_names"]
    teamname = all_team_names[all_teams.index(teamid)]

    # Get all players you have ever owned
    players_data = (
        db.session.query(Players)
        .filter_by(owner=teamid)
        .order_by(text("data_date"))
        .order_by(text("ht_id"))
        .all()
    )

    allplayerids = []
    allplayers = {}
    playernames = {}
    for entry in players_data:
        allplayers[entry.ht_id] = []
        if entry.number == 100:
            playernames[entry.ht_id] = entry.first_name + " " + entry.last_name
        else:
            playernames[entry.ht_id] = (
                str(entry.number) + ". " + entry.first_name + " " + entry.last_name
            )
        if entry.ht_id not in allplayerids:
            allplayerids.append(entry.ht_id)

    for player in players_data:
        allplayers[player.ht_id].append(
            [
                date(
                    player.data_date.year, player.data_date.month, player.data_date.day
                ),
                (
                    player.keeper,
                    player.defender,
                    player.playmaker,
                    player.winger,
                    player.passing,
                    player.scorer,
                    player.set_pieces,
                ),
            ]
        )

    increases = {}
    for i in allplayers:
        increases[i] = (
            allplayers[i][len(allplayers[i]) - 1][1][0] - allplayers[i][0][1][0]
        )
        for s in range(6):
            increases[i] = (
                increases[i]
                + allplayers[i][len(allplayers[i]) - 1][1][s]
                - allplayers[i][0][1][s]
            )

    # Sort player list based on increases
    allplayerids = sorted(allplayerids, key=lambda ele: increases[ele], reverse=True)

    for i in allplayers:
        # Date filler
        (firstdate, previousskill) = allplayers[i][0]
        (lastdate, x) = allplayers[i][len(allplayers[i]) - 1]

        friday = (
            firstdate
            - timedelta(days=firstdate.weekday())
            + timedelta(days=4, weeks=-1)
        )

        date_modified = friday
        datelist = [friday]

        while date_modified < lastdate:
            date_modified += timedelta(days=1)
            datelist.append(date_modified)

        newy = []
        for d in datelist:
            for da, y in allplayers[i]:
                if d == da:
                    previousskill = y
            newy.append([d, previousskill])

        # Just take every 7th
        weekly = newy[0::7]
        # add the last day if it's not the last day already
        (lastweekday, x) = weekly[len(weekly) - 1]
        if lastdate != lastweekday:
            weekly.append(allplayers[i][len(allplayers[i]) - 1])

        allplayers[i] = weekly

    # Deduplicate consecutive rows with identical skill values
    for player_id in allplayers:
        deduped = []
        prev_skills = None
        for entry in allplayers[player_id]:
            date_val, skills = entry
            if skills != prev_skills:
                deduped.append(entry)
                prev_skills = skills
        allplayers[player_id] = deduped

    # Calculate skill changes for arrows (newest first comparison)
    skill_changes = {}
    for player_id in allplayers:
        skill_changes[player_id] = []
        player_data = allplayers[player_id]

        # Simple approach: for each row, compare with the chronologically previous row
        for i, (date_val, skills) in enumerate(reversed(player_data)):
            if i == len(player_data) - 1:
                # Oldest row has no previous to compare with
                changes = [0] * 7
            else:
                # Compare current skills with chronologically older skills
                older_date, older_skills = list(reversed(player_data))[i + 1]
                # Positive change = improvement (show green ↑)
                changes = [skills[j] - older_skills[j] for j in range(7)]
            skill_changes[player_id].append((date_val, skills, changes))

    return create_page(
        template="training.html",
        teamname=teamname,
        error=error,
        skills=tracecolumns,
        teamid=teamid,
        increases=increases,
        playernames=playernames,
        allplayerids=allplayerids,
        allplayers=allplayers,
        skill_changes=skill_changes,
        title="Training",
    )
