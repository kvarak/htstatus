"""Team management routes blueprint for HT Status application."""

from datetime import datetime as dt
import time
import traceback

from flask import Blueprint, flash, redirect, request, session, url_for

from app import translations
from app.auth_utils import (
    get_current_user,
    get_current_user_id,
    require_authentication,
    track_activity,
)
from app.chpp_utilities import fetch_user_teams, get_chpp_client
from app.utils import create_page, diff, dprint

# Create Blueprint for team routes
team_bp = Blueprint("team", __name__)

# Set by setup_team_blueprint()
db = None


def setup_team_blueprint(db_instance):
    """Initialize team blueprint with the db instance."""
    global db
    db = db_instance


def get_owned_player_ids(players_model, teamid):
    """Return the set of player ids that currently have any record owned by teamid."""
    rows = (
        db.session.query(players_model.ht_id).filter_by(owner=teamid).distinct().all()
    )
    return {row.ht_id for row in rows}


def reconcile_roster(players_model, teamid, players_indb, players_fromht, playernames):
    """Compare stored roster with Hattrick roster and release departed players.

    Every record of a departed player is moved from owner=teamid to owner=0
    (keeping old_owner=teamid), so they disappear from the team's player lists.

    Returns:
        tuple: (new player ids, departed player ids)
    """
    players_new = diff(list(players_fromht), list(players_indb))
    players_left = diff(list(players_indb), list(players_fromht))
    dprint(1, f"Found {len(players_new)} new and {len(players_left)} departed players")

    for ht_id in players_left:
        if ht_id not in playernames:
            last_record = (
                db.session.query(players_model)
                .filter_by(ht_id=ht_id, owner=teamid)
                .order_by(players_model.data_date.desc())
                .first()
            )
            if last_record:
                playernames[ht_id] = f"{last_record.first_name} {last_record.last_name}"
        (
            db.session.query(players_model)
            .filter_by(ht_id=ht_id, owner=teamid)
            .update({"old_owner": teamid, "owner": 0})
        )
    db.session.commit()

    return players_new, players_left


# Team column -> (CHPP team attribute, default when missing)
TEAM_COMPETITION_FIELDS = {
    "league_name": ("league_name", None),
    "league_level": ("league_level", None),
    "power_rating": ("power_rating", None),
    "cup_still_in_cup": ("still_in_cup", False),
    "cup_cup_name": ("cup_name", None),
    "cup_cup_round": ("cup_level", None),
    "cup_cup_round_index": ("cup_match_rounds_left", 0),
    "dress_uri": ("dress_uri", None),
    "logo_url": ("logo_url", None),
}


def save_team_competition_data(teamid, the_team, user_id):
    """Create/update the Team row with CHPP competition data in one transaction.

    On failure the transaction is rolled back so the rest of the update (players,
    matches) can continue with a clean session. Returns True on success.
    """
    from models import Team

    try:
        team_record = Team.get_by_ht_id(teamid)
        if not team_record:
            team_record = Team(ht_id=teamid, team_name=the_team.name, user_id=user_id)
            db.session.add(team_record)

        team_record.update_competition_data(
            **{
                column: getattr(the_team, attr, default)
                for column, (attr, default) in TEAM_COMPETITION_FIELDS.items()
            }
        )
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        dprint(1, f"Warning: failed to store competition data for team {teamid}: {e}")
        return False


@team_bp.route("/team")
@require_authentication
@track_activity("team")
def team():
    """Display team information."""
    chpp = get_chpp_client(session)

    team_ids, team_names = fetch_user_teams(chpp)

    return create_page(template="team.html", title="Team")


def update_error_page(error, errorinfo=""):
    """Render the update error page with the session's team list."""
    return create_page(
        template="update_error.html",
        title="Update Failed",
        error=error,
        errorinfo=errorinfo,
        all_teams=session.get("all_teams", []),
        all_team_names=session.get("all_team_names", []),
    )


def refresh_user_teams(chpp):
    """Sync the session's team list and Hattrick translations with Hattrick.

    A known CHPP "YouthTeamId" error on user() is tolerated; the session list
    is kept as is. Other errors propagate.
    """
    all_teams = session.get("all_teams", [])
    try:
        ht_user = chpp.user()
    except Exception as e:
        if "YouthTeamId" in str(e):
            dprint(1, f"YouthTeamId error, keeping session team list: {e}")
            return
        raise

    translations.refresh(chpp, ht_user.language_id)
    current_teams = ht_user._teams_ht_id

    if set(current_teams) == set(all_teams):
        return

    team_names = []
    for team_id in current_teams:
        try:
            team_names.append(chpp.team(ht_id=team_id).name)
        except Exception as e:
            dprint(1, f"Could not fetch name for team {team_id}: {e}")
            team_names.append(f"Team {team_id}")
    session["all_teams"] = current_teams
    session["all_team_names"] = team_names
    session.modified = True
    dprint(1, f"Team list changed, session now has: {team_names}")


def handle_archive_download(chpp, team_id_arg):
    """Download a team's full match archive, then go back to its matches page."""
    from app.utils import downloadMatches

    try:
        team_id = int(team_id_arg)
    except (ValueError, TypeError):
        flash("Invalid team ID format for archive download", "error")
        return redirect(url_for("matches.matches", id=team_id_arg or ""))

    if team_id not in session.get("all_teams", []):
        flash("Invalid team ID for archive download", "error")
        return redirect(url_for("matches.matches", id=team_id))

    try:
        user = get_current_user()
        if user:
            user.matches_archive()
            db.session.commit()

        result = downloadMatches(team_id, chpp)
        if result["success"]:
            flash(result["message"], "success")
        else:
            flash(result.get("message", "Archive download failed"), "error")
    except Exception as e:
        dprint(1, f"Archive download error: {e}")
        flash(f"Archive download failed: {e}", "error")

    return redirect(url_for("matches.matches", id=team_id))


SKILL_FIELDS = (
    "stamina",
    "keeper",
    "defender",
    "playmaker",
    "winger",
    "passing",
    "scorer",
    "set_pieces",
)


def _skill_or_previous(new_value, previous, field):
    """CHPP returns 0 for skills it doesn't expose; keep the last known value then."""
    if isinstance(new_value, int) and new_value > 0:
        return new_value
    return (getattr(previous, field, 0) or 0) if previous else 0


def build_player_record(p, details, previous, teamid):
    """Build today's Players row (as a dict) from CHPP data.

    Args:
        p: player from the team's player list (basic fields and skills)
        details: chpp.player() result (TSI, salary, goals, ...)
        previous: the player's latest stored row for this team, or None
        teamid: owning team ID
    """
    arrival = p.arrival_date
    record = {
        "ht_id": p.id,
        "first_name": p.first_name,
        "nick_name": p.nick_name,
        "last_name": p.last_name,
        "number": p.number,
        "category_id": p.category_id,
        "owner_notes": p.owner_notes,
        "age_years": p.age,
        "age_days": p.age_days,
        "age": p.age,
        "next_birthday": None,
        "arrival_date": (
            dt(arrival.year, arrival.month, arrival.day, arrival.hour, arrival.minute)
            if arrival
            else None
        ),
        "form": p.form,
        "cards": p.cards,
        "injury_level": p.injury_level,
        "statement": p.statement,
        "language": None,
        "language_id": getattr(p, "country_id", None),
        "agreeability": p.agreeability,
        "aggressiveness": p.aggressiveness,
        "honesty": p.honesty,
        "experience": p.experience,
        "loyalty": p.loyalty,
        "specialty": p.specialty,
        "native_country_id": getattr(p, "country_id", None),
        "native_league_id": None,
        "native_league_name": None,
        "tsi": details.tsi,
        "salary": details.salary,
        "caps": details.caps,
        "caps_u20": details.caps_u20,
        "career_goals": details.career_goals,
        "career_hattricks": details.career_hattricks,
        "league_goals": details.league_goals,
        "cup_goals": details.cup_goals,
        "friendly_goals": details.friendlies_goals,
        "current_team_matches": details.matches_current_team,
        "current_team_goals": details.goals_current_team,
        "national_team_id": details.national_team_id,
        "national_team_name": None,
        "is_transfer_listed": details.transfer_listed,
        "team_id": None,
        "mother_club_bonus": details.mother_club_bonus,
        "leadership": details.leadership,
        "data_date": time.strftime("%Y-%m-%d"),
        "owner": teamid,
    }
    for field in SKILL_FIELDS:
        record[field] = _skill_or_previous(getattr(p, field), previous, field)
    return record


def save_player_snapshot(record):
    """Store today's snapshot, replacing an earlier one from today, in one commit."""
    from models import Players

    existing = (
        db.session.query(Players)
        .filter_by(ht_id=record["ht_id"], data_date=record["data_date"])
        .first()
    )
    if existing:
        db.session.delete(existing)
        db.session.flush()
    db.session.add(Players(record))
    db.session.commit()


def download_recent_matches(chpp, team_ids):
    """Download recent/upcoming matches for each team; failures don't stop the update."""
    from app.utils import downloadRecentMatches

    results, recent, upcoming = {}, 0, 0
    for teamid in team_ids:
        try:
            result = downloadRecentMatches(teamid, chpp)
        except Exception as e:
            dprint(1, f"Match download failed for team {teamid}: {e}")
            continue
        results[teamid] = result
        if result["success"]:
            recent += result["recent_count"]
            upcoming += result["upcoming_count"]
        else:
            dprint(1, f"Match download failed for team {teamid}: {result.get('error')}")
    return results, recent, upcoming


@team_bp.route("/update")
@require_authentication
def update():
    """Update player data from Hattrick API (the only routine CHPP sync)."""
    from app.roster import latest_player_records
    from app.utils import get_team_timeline
    from models import Players

    try:
        chpp = get_chpp_client(session)
        refresh_user_teams(chpp)
    except Exception as e:
        dprint(1, f"CHPP initialization failed: {traceback.format_exc()}")
        return update_error_page(
            f"Cannot connect to Hattrick API: {e}",
            "Please check your internet connection and try again. If the problem "
            "persists, Hattrick servers may be unavailable.",
        )

    if request.args.get("archive") and request.args.get("id"):
        return handle_archive_download(chpp, request.args.get("id"))

    all_teams = session["all_teams"]
    updated = {}
    timeline_changes = {}
    new_players = []
    left_players = []
    playernames = {}

    for teamid in all_teams:
        try:
            the_team = chpp.team(ht_id=teamid)
            updated[teamid] = [the_team.name]
            session["all_team_names"][all_teams.index(teamid)] = the_team.name
            session.modified = True
            # Stored so stats pages don't need CHPP calls
            save_team_competition_data(teamid, the_team, get_current_user_id())
        except Exception as e:
            return update_error_page(
                f"Failed to fetch team data for team {teamid}: {e}",
                traceback.format_exc(),
            )

        try:
            team_players = the_team.players()
        except Exception as e:
            return update_error_page(
                "Cannot access player data. Is your team playing a match right now?",
                "If your team is not currently playing, please report this as a bug."
                f"\n\nTechnical details: {e}\n\n{traceback.format_exc()}",
            )

        # Snapshot the stored roster before today's rows are inserted
        players_indb = get_owned_player_ids(Players, teamid)
        previous = {p.ht_id: p for p in latest_player_records(Players, teamid)}

        players_fromht = []
        for p in team_players:
            record = build_player_record(
                p, chpp.player(id_=p.id), previous.get(p.id), teamid
            )
            playernames[p.id] = f"{p.first_name} {p.last_name}"
            try:
                save_player_snapshot(record)
            except Exception as e:
                db.session.rollback()
                name = playernames[p.id]
                return update_error_page(
                    f"Database error while saving player data: {e}",
                    f"Failed to save {name} to database.\n\n{traceback.format_exc()}",
                )
            players_fromht.append(p.id)

        timeline_changes[teamid] = get_team_timeline(teamid)
        updated[teamid] += [f"/player?id={teamid}", "players"]

        players_new, players_left = reconcile_roster(
            Players, teamid, players_indb, players_fromht, playernames
        )
        team_name = updated[teamid][0]
        new_players += [
            [team_name, playernames.get(p, "Unknown Player")] for p in players_new
        ]
        left_players += [
            [team_name, playernames.get(p, "Unknown Player")] for p in players_left
        ]

    matches_results, total_recent, total_upcoming = download_recent_matches(
        chpp, all_teams
    )

    user = get_current_user()
    if user:
        user.updatedata()
        db.session.commit()

    return create_page(
        template="update_timeline.html",
        title="Update Complete - Timeline View",
        updated=updated,
        timeline_changes=timeline_changes,
        left_players=left_players,
        new_players=new_players,
        matches_results=matches_results,
        total_recent_matches=total_recent,
        total_upcoming_matches=total_upcoming,
    )
