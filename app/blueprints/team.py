"""Team management routes blueprint for HT Status application."""

import time
import traceback
from datetime import datetime as dt

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.auth_utils import get_current_user_id, get_user_teams, require_authentication
from app.chpp_utilities import fetch_user_teams, get_chpp_client
from app.model_registry import get_user_model
from app.utils import create_page, diff, dprint

# Create Blueprint for team routes
team_bp = Blueprint("team", __name__)

# These will be set by setup_team_blueprint()
app = None
db = None
consumer_key = None
consumer_secret = None
version = None
timenow = None
fullversion = None


def setup_team_blueprint(app_instance, db_instance, ck, cs, v, fv):
    """Initialize team blueprint with app and db instances."""
    global app, db, consumer_key, consumer_secret, version, fullversion
    app = app_instance
    db = db_instance
    consumer_key = ck
    consumer_secret = cs
    version = v
    fullversion = fv


@team_bp.route("/team")
@require_authentication
def team():
    """Display team information."""
    # Track user activity
    User = get_user_model()
    current_user = db.session.query(User).filter_by(ht_id=session["current_user_id"]).first()
    if current_user:
        current_user.team()
        db.session.commit()

    chpp = get_chpp_client(session)

    team_ids, team_names = fetch_user_teams(chpp)

    return create_page(template="team.html", title="Team")


@team_bp.route("/update")
@require_authentication
def update():
    """Update player data from Hattrick API."""
    from models import Players  # Import here to avoid circular dependencies

    dprint(1, "=== DATA UPDATE PROCESS STARTED ===")

    # Session state validation using standardized functions
    current_user_id = get_current_user_id()
    all_teams, all_team_names = get_user_teams()

    dprint(1, f"Current user ID: {current_user_id}")
    dprint(1, f"Access key available: {bool(session.get('access_key'))}")
    dprint(1, f"Access secret available: {bool(session.get('access_secret'))}")
    dprint(1, f"All teams: {all_teams}")
    dprint(1, f"Team names: {all_team_names}")

    try:
        # Initialize CHPP with enhanced error handling
        dprint(1, "Initializing CHPP client...")
        chpp = get_chpp_client(session)
        dprint(1, "CHPP client initialized successfully")

        # Test basic API connectivity with YouthTeamId error handling
        dprint(1, "Testing CHPP API connectivity...")
        try:
            test_user = chpp.user()
            dprint(1, f"API connectivity test successful, user ID: {test_user.ht_id}")
        except Exception as chpp_user_error:
            if "YouthTeamId" in str(chpp_user_error):
                dprint(
                    1,
                    f"YouthTeamId error encountered, continuing with limited functionality: {chpp_user_error}",
                )
                # We can still proceed with team data updates despite user() failing
                test_user = None
            else:
                raise chpp_user_error

    except Exception as e:
        error_details = traceback.format_exc()
        dprint(1, f"CRITICAL ERROR: CHPP initialization failed: {str(e)}")
        dprint(1, f"Full error traceback: {error_details}")

        return create_page(
            template="update_error.html",
            title="Update Failed",
            error=f"Cannot connect to Hattrick API: {str(e)}",
            errorinfo="Please check your internet connection and try again. If the problem persists, Hattrick servers may be unavailable.",
            all_teams=session.get("all_teams", []),
            all_team_names=session.get("all_team_names", []),
        )

    all_teams = session["all_teams"]
    all_team_names = session["all_team_names"]

    # Handle archive download request (CHPP policy compliant)
    archive_request = request.args.get('archive')
    archive_team_id = request.args.get('id')

    if archive_request and archive_team_id:
        try:
            archive_team_id = int(archive_team_id)
            if archive_team_id in all_teams:
                from app.utils import downloadMatches

                dprint(1, f"Archive download requested for team {archive_team_id}")
                result = downloadMatches(archive_team_id, chpp)

                if result["success"]:
                    flash(result["message"], "success")
                else:
                    flash(result.get("message", "Archive download failed"), "error")
            else:
                flash("Invalid team ID for archive download", "error")

        except (ValueError, TypeError):
            flash("Invalid team ID format for archive download", "error")
        except Exception as e:
            flash(f"Archive download failed: {str(e)}", "error")

        # Redirect back to matches page after archive download
        return redirect(url_for('matches.matches', id=archive_team_id))

    updated = {}
    timeline_changes = {}  # Collect timeline changes for all teams

    new_players = []
    left_players = []
    playernames = {}

    for teamid in all_teams:
        try:
            the_team = chpp.team(ht_id=teamid)
            dprint(1, f"Team data fetched successfully: {the_team.name}")

            # Use the actual team name from CHPP API instead of session data
            updated[teamid] = [the_team.name]

            # Update session with correct team name
            team_index = all_teams.index(teamid)
            session['all_team_names'][team_index] = the_team.name
            session.modified = True

            # REFACTOR-064: Store team competition data in database for CHPP policy compliance
            dprint(1, f"Fetching and storing competition data for team: {the_team.name}")
            try:
                # Import Team model here to avoid circular imports
                from models import Team

                # Find or create team record
                team_record = Team.get_by_ht_id(teamid)
                if not team_record:
                    team_record = Team(
                        ht_id=teamid,
                        team_name=the_team.name,
                        user_id=current_user_id
                    )
                    db.session.add(team_record)
                    dprint(1, f"Created new team record for {the_team.name}")

                # Extract competition data from CHPP team details
                competition_data = {
                    "league_name": getattr(the_team, "league_name", None),
                    "league_level": getattr(the_team, "league_level", None),
                    "power_rating": getattr(the_team, "power_rating", None),
                    "cup_still_in_cup": getattr(the_team, "still_in_cup", False),
                    "cup_cup_name": getattr(the_team, "cup_name", None),
                    "cup_cup_round": getattr(the_team, "cup_level", None),  # Using cup_level as round info
                    "cup_cup_round_index": getattr(the_team, "cup_match_rounds_left", 0),
                    "dress_uri": getattr(the_team, "dress_uri", None),
                    "logo_url": getattr(the_team, "logo_url", None),
                }

                # Update team competition data
                team_record.update_competition_data(**competition_data)
                dprint(1, f"Updated competition data for {the_team.name}: league={competition_data['league_name']}, power={competition_data['power_rating']}")

            except Exception as comp_error:
                dprint(1, f"Warning: Failed to store competition data for team {teamid}: {str(comp_error)}")
                # Continue with update process even if competition data storage fails

        except Exception as e:
            error_details = traceback.format_exc()
            dprint(1, f"ERROR: Failed to fetch team data for team {teamid}: {str(e)}")
            dprint(1, f"Team fetch error traceback: {error_details}")

            return create_page(
                template="update_error.html",
                title="Update Failed",
                error=f"Failed to fetch team data for team {teamid}: {str(e)}",
                errorinfo=error_details,
                all_teams=session["all_teams"],
                all_team_names=session["all_team_names"],
            )

        try:
            dprint(1, f"Fetching players for team: {the_team.name}")
            players_count = len(the_team.players())
            dprint(1, f"Found {players_count} players in team")
            dprint(2, the_team.players())

        except Exception as e:
            errorincode = traceback.format_exc()
            dprint(1, f"ERROR: Failed to access players for team {teamid}: {str(e)}")
            dprint(1, f"Players access error traceback: {errorincode}")

            error = "Cannot access player data. Is your team playing a match right now?"
            errorinfo = "If your team is not currently playing, please report this as a bug.\n\n"
            errorinfo += f"Technical details: {str(e)}\n\n{errorincode}"

            return render_template(
                "update_error.html",
                version=version,
                timenow=timenow,
                fullversion=fullversion,
                title="Update",
                current_user=session["current_user"],
                error=error,
                errorinfo=errorinfo,
                all_teams=session["all_teams"],
                all_team_names=session["all_team_names"],
            )

        players_fromht = []
        for p in the_team.players():
            thisplayer = {}

            the_player = chpp.player(id_=p.id)

            if the_player.transfer_details:
                dprint(2, "transfer details --- ", the_player.transfer_details.deadline)

            thisplayer["ht_id"] = p.id
            thisplayer["first_name"] = p.first_name
            thisplayer["nick_name"] = p.nick_name
            thisplayer["last_name"] = p.last_name
            thisplayer["number"] = p.number
            thisplayer["category_id"] = p.category_id
            thisplayer["owner_notes"] = p.owner_notes
            thisplayer["age_years"] = p.age
            thisplayer["age_days"] = p.age_days
            thisplayer["age"] = p.age
            # next_birthday not available
            thisplayer["next_birthday"] = None

            if p.arrival_date:
                thedate = dt(
                    p.arrival_date.year,
                    p.arrival_date.month,
                    p.arrival_date.day,
                    p.arrival_date.hour,
                    p.arrival_date.minute,
                )
                thisplayer["arrival_date"] = thedate
            else:
                thisplayer["arrival_date"] = None
            thisplayer["form"] = p.form
            thisplayer["cards"] = p.cards
            thisplayer["injury_level"] = p.injury_level
            thisplayer["statement"] = p.statement
            # language/language_id use country_id instead
            thisplayer["language"] = None
            thisplayer["language_id"] = getattr(p, 'country_id', None)
            thisplayer["agreeability"] = p.agreeability
            thisplayer["aggressiveness"] = p.aggressiveness
            thisplayer["honesty"] = p.honesty
            thisplayer["experience"] = p.experience
            thisplayer["loyalty"] = p.loyalty
            thisplayer["aggressiveness"] = p.aggressiveness
            thisplayer["specialty"] = p.specialty
            # native_country_id/native_league_id/native_league_name use country_id fallback
            country_id_value = getattr(p, 'country_id', None)
            thisplayer["native_country_id"] = country_id_value


            thisplayer["native_league_id"] = None
            thisplayer["native_league_name"] = None
            thisplayer["tsi"] = the_player.tsi
            thisplayer["salary"] = the_player.salary
            thisplayer["caps"] = the_player.caps
            thisplayer["caps_u20"] = the_player.caps_u20
            thisplayer["career_goals"] = the_player.career_goals
            thisplayer["career_hattricks"] = the_player.career_hattricks
            thisplayer["league_goals"] = the_player.league_goals
            thisplayer["cup_goals"] = the_player.cup_goals
            thisplayer["friendly_goals"] = the_player.friendlies_goals  # Custom CHPP field name
            thisplayer["current_team_matches"] = the_player.matches_current_team  # Custom CHPP field name
            thisplayer["current_team_goals"] = the_player.goals_current_team  # Custom CHPP field name
            thisplayer["national_team_id"] = the_player.national_team_id
            thisplayer["national_team_name"] = None  # Not available in Custom CHPP
            thisplayer["is_transfer_listed"] = the_player.transfer_listed  # Custom CHPP field name
            thisplayer["team_id"] = None  # Not available in Custom CHPP
            thisplayer["mother_club_bonus"] = the_player.mother_club_bonus
            thisplayer["leadership"] = the_player.leadership

            # Try to get skill values from CHPPPlayer attributes
            # If they're 0 (not provided by API), fetch old values from database

            old_player_query = (
                db.session.query(Players)
                .filter_by(ht_id=p.id, owner=teamid)
                .order_by(Players.data_date.desc())
                .first()
            )

            # Helper function to safely extract int from skill value
            def safe_skill_int(new_val, old_player, field_name):
                # If new value is non-zero, use it
                if isinstance(new_val, int) and new_val > 0:
                    return new_val
                # Otherwise, try to get old value from database
                if old_player and hasattr(old_player, field_name):
                    old_val = getattr(old_player, field_name, 0)
                    return old_val if old_val else 0
                return 0

            # Extract skills from CHPPPlayer attributes
            thisplayer["stamina"] = safe_skill_int(p.stamina, old_player_query, "stamina")
            thisplayer["keeper"] = safe_skill_int(p.keeper, old_player_query, "keeper")
            thisplayer["defender"] = safe_skill_int(p.defender, old_player_query, "defender")
            thisplayer["playmaker"] = safe_skill_int(p.playmaker, old_player_query, "playmaker")
            thisplayer["winger"] = safe_skill_int(p.winger, old_player_query, "winger")
            thisplayer["passing"] = safe_skill_int(p.passing, old_player_query, "passing")
            thisplayer["scorer"] = safe_skill_int(p.scorer, old_player_query, "scorer")
            thisplayer["set_pieces"] = safe_skill_int(p.set_pieces, old_player_query, "set_pieces")

            thisplayer["data_date"] = time.strftime("%Y-%m-%d")

            # Owner is the team ID (players are owned by teams, not users)
            thisplayer["owner"] = teamid

            playernames[p.id] = p.first_name + " " + p.last_name

            try:
                dbplayer = (
                    db.session.query(Players)
                    .filter_by(
                        ht_id=thisplayer["ht_id"], data_date=thisplayer["data_date"]
                    )
                    .first()
                )

                if dbplayer:
                    db.session.delete(dbplayer)
                    db.session.commit()

                newplayer = Players(thisplayer)
                db.session.add(newplayer)
                db.session.commit()
                dprint(
                    1,
                    f"✅ Successfully added {thisplayer['first_name']} {thisplayer['last_name']} for {thisplayer['data_date']}",
                )

            except Exception as e:
                db.session.rollback()
                error_details = traceback.format_exc()
                dprint(
                    1,
                    f"ERROR: Database operation failed for player {thisplayer['first_name']} {thisplayer['last_name']}: {str(e)}",
                )
                dprint(1, f"Database error traceback: {error_details}")

                return create_page(
                    template="update_error.html",
                    title="Update Failed",
                    error=f"Database error while saving player data: {str(e)}",
                    errorinfo=f"Failed to save {thisplayer['first_name']} {thisplayer['last_name']} to database.\n\n{error_details}",
                    all_teams=session["all_teams"],
                    all_team_names=session["all_team_names"],
                )

            players_fromht.append(thisplayer["ht_id"])

        # Get 4-week timeline using shared utility
        from app.utils import get_team_timeline
        try:
            dprint(1, f"Getting timeline for team {teamid}")
            timeline_changes[teamid] = get_team_timeline(teamid)
            dprint(1, f"Timeline retrieved successfully for team {teamid}")
        except Exception as e:
            dprint(1, f"ERROR: Failed to get timeline for team {teamid}: {str(e)}")
            timeline_changes[teamid] = {}

        updated[teamid].append("/player?id=" + str(teamid))
        updated[teamid].append("players")

        # Get the most recent player roster from database to compare
        # We need to find the latest data_date and get only those players
        from sqlalchemy import func
        try:
            dprint(1, f"Querying database for existing players for team {teamid}")
            latest_date_subquery = (
                db.session.query(func.max(Players.data_date))
                .filter_by(owner=teamid)
                .scalar_subquery()
            )

            players_data = (
                db.session.query(Players)
                .filter_by(owner=teamid)
                .filter(Players.data_date == latest_date_subquery)
                .all()
            )

            dprint(1, f"Found {len(players_data)} existing players in database")

            players_indb = []
            for p in players_data:
                players_indb.append(p.ht_id)
                playernames[p.ht_id] = p.first_name + " " + p.last_name
            players_indb = list(set(players_indb))

            # Which players are new
            players_new = diff(players_fromht, players_indb)
            dprint(1, f"Found {len(players_new)} new players")

            for p in players_new:
                # Get player name from playernames dict, with fallback for new players
                player_name = playernames.get(p, "Unknown Player")
                new_players.append([updated[teamid][0], player_name])

            # Which players are no longer in the team
            players_left = diff(players_indb, players_fromht)
            dprint(1, f"Found {len(players_left)} players who left")

            for p in players_left:
                # Get player name from playernames dict, with fallback
                player_name = playernames.get(p, "Unknown Player")
                left_players.append([updated[teamid][0], player_name])
                (
                    db.session.query(Players)
                    .filter_by(ht_id=p, owner=teamid)
                    .update({"old_owner": teamid, "owner": 0})
                )
                db.session.commit()

            dprint(1, f"Player difference calculation completed for team {teamid}")

        except Exception as e:
            error_details = traceback.format_exc()
            dprint(1, f"ERROR: Player difference calculation failed for team {teamid}: {str(e)}")
            dprint(1, f"Player difference error traceback: {error_details}")
            raise

    # End of team processing loop
    dprint(1, "=== COMPLETED PROCESSING ALL TEAMS ===")
    dprint(1, f"Processed {len(all_teams)} teams successfully")
    dprint(1, f"Timeline changes collected for teams: {list(timeline_changes.keys())}")
    dprint(1, f"Updated teams: {list(updated.keys())}")
    dprint(1, f"New players found: {len(new_players)}")
    dprint(1, f"Players who left: {len(left_players)}")

    # Download recent matches for each team as part of the update process
    dprint(1, "Importing downloadRecentMatches...")
    from app.utils import downloadRecentMatches
    dprint(1, "Import successful, initializing match download variables...")

    matches_results = {}
    total_recent_matches = 0
    total_upcoming_matches = 0
    dprint(1, "Match download variables initialized successfully")

    try:
        dprint(1, f"Starting match downloads for {len(all_teams)} teams")
        for teamid in all_teams:
            dprint(1, f"Downloading recent matches for team {teamid}")
            result = downloadRecentMatches(teamid, chpp)
            matches_results[teamid] = result

            if result["success"]:
                total_recent_matches += result["recent_count"]
                total_upcoming_matches += result["upcoming_count"]
                dprint(1, f"Team {teamid}: {result['count']} new matches added, {result['recent_count']} recent, {result['upcoming_count']} upcoming")
            else:
                dprint(1, f"Failed to download matches for team {teamid}: {result.get('error', 'Unknown error')}")

        dprint(1, f"Matches download complete: {total_recent_matches} recent, {total_upcoming_matches} upcoming")

    except Exception as e:
        error_details = traceback.format_exc()
        dprint(1, f"ERROR: Match download failed: {str(e)}")
        dprint(1, f"Match download error traceback: {error_details}")
        raise

    # Update user's last_update timestamp using model method
    try:
        dprint(1, f"Updating user timestamp for user {current_user_id}")
        User = get_user_model()
        user = db.session.query(User).filter_by(ht_id=current_user_id).first()
        if user:
            user.updatedata()  # This method sets last_update and increments c_update
            db.session.commit()
            dprint(1, f"Updated user last_update timestamp: {user.last_update}")
        else:
            dprint(1, f"Warning: User {current_user_id} not found in database")

    except Exception as e:
        error_details = traceback.format_exc()
        dprint(1, f"ERROR: User timestamp update failed: {str(e)}")
        dprint(1, f"User update error traceback: {error_details}")
        raise

    try:
        dprint(1, f"Creating update_timeline.html page with timeline_changes keys: {list(timeline_changes.keys())}")
        return create_page(
            template="update_timeline.html",
            title="Update Complete - Timeline View",
            updated=updated,
            timeline_changes=timeline_changes,
            left_players=left_players,
            new_players=new_players,
            matches_results=matches_results,
            total_recent_matches=total_recent_matches,
            total_upcoming_matches=total_upcoming_matches,
        )
    except Exception as e:
        error_details = traceback.format_exc()
        dprint(1, f"ERROR: Failed to render update_timeline.html: {str(e)}")
        dprint(1, f"Template error traceback: {error_details}")

        return create_page(
            template="update_error.html",
            title="Update Failed",
            error=f"Template rendering failed: {str(e)}",
            errorinfo=error_details,
            all_teams=session.get("all_teams", []),
            all_team_names=session.get("all_team_names", []),
        )
