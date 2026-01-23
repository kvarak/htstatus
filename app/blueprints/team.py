"""Team management routes blueprint for HT Status application."""

import time
import traceback
from datetime import datetime as dt

from flask import Blueprint, render_template, session
from sqlalchemy import text

from app.auth_utils import get_current_user_id, get_user_teams, require_authentication
from app.utils import create_page, diff, dprint, get_player_changes
from models import Players
from pychpp import CHPP

# Create Blueprint for team routes
team_bp = Blueprint('team', __name__)

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


@team_bp.route('/team')
@require_authentication
def team():
    """Display team information."""
    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'])

    current_user = chpp.user()
    all_teams = current_user._teams_ht_id

    teams = []
    for teamid in all_teams:
        dprint(1, teamid)
        this_team = chpp.team(ht_id=teamid)
        dprint(2, vars(this_team))
        teams.append(this_team.name)

    return create_page(
        template='team.html',
        title='Team')


@team_bp.route('/update')
@require_authentication
def update():
    """Update player data from Hattrick API."""
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
        chpp = CHPP(consumer_key,
                    consumer_secret,
                    session['access_key'],
                    session['access_secret'])
        dprint(1, "CHPP client initialized successfully")

        # Test basic API connectivity with YouthTeamId error handling
        dprint(1, "Testing CHPP API connectivity...")
        try:
            test_user = chpp.user()
            dprint(1, f"API connectivity test successful, user ID: {test_user.ht_id}")
        except Exception as chpp_user_error:
            if "YouthTeamId" in str(chpp_user_error):
                dprint(1, f"YouthTeamId error encountered, continuing with limited functionality: {chpp_user_error}")
                # We can still proceed with team data updates despite user() failing
                test_user = None
            else:
                raise chpp_user_error

    except Exception as e:
        error_details = traceback.format_exc()
        dprint(1, f"CRITICAL ERROR: CHPP initialization failed: {str(e)}")
        dprint(1, f"Full error traceback: {error_details}")

        return create_page(
            template='update.html',
            title='Update Failed',
            error=f"Cannot connect to Hattrick API: {str(e)}",
            errorinfo="Please check your internet connection and try again. If the problem persists, Hattrick servers may be unavailable.",
            all_teams=session.get('all_teams', []),
            all_team_names=session.get('all_team_names', []))

    all_teams = session['all_teams']
    all_team_names = session['all_team_names']

    updated = {}
    changesplayers_day = []
    changesplayers_week = []

    for i in range(len(all_teams)):
        updated[all_teams[i]] = [all_team_names[i]]

    new_players = []
    left_players = []
    playernames = {}

    for teamid in all_teams:

        try:
            the_team = chpp.team(ht_id=teamid)
            dprint(1, f"Team data fetched successfully: {the_team.name}")

        except Exception as e:
            error_details = traceback.format_exc()
            dprint(1, f"ERROR: Failed to fetch team data for team {teamid}: {str(e)}")
            dprint(1, f"Team fetch error traceback: {error_details}")

            return create_page(
                template='update.html',
                title='Update Failed',
                error=f"Failed to fetch team data for team {teamid}: {str(e)}",
                errorinfo=error_details,
                all_teams=session['all_teams'],
                all_team_names=session['all_team_names'])

        try:
            dprint(1, f"Fetching players for team: {the_team.name}")
            players_count = len(the_team.players)
            dprint(1, f"Found {players_count} players in team")
            dprint(2, the_team.players)

        except Exception as e:
            errorincode = traceback.format_exc()
            dprint(1, f"ERROR: Failed to access players for team {teamid}: {str(e)}")
            dprint(1, f"Players access error traceback: {errorincode}")

            error = "Cannot access player data. Is your team playing a match right now?"
            errorinfo = "If your team is not currently playing, please report this as a bug.\n\n"
            errorinfo += f"Technical details: {str(e)}\n\n{errorincode}"

            return render_template(
                'update.html',
                version=version,
                timenow=timenow,
                fullversion=fullversion,
                title='Update',
                current_user=session['current_user'],
                error=error,
                errorinfo=errorinfo,
                all_teams=session['all_teams'],
                all_team_names=session['all_team_names'])

        players_fromht = []
        for p in the_team.players:

            thisplayer = {}

            the_player = chpp.player(ht_id=p.ht_id)

            if the_player.transfer_details:
                dprint(2,
                       "transfer details --- ",
                       the_player.transfer_details.deadline)

            thisplayer['ht_id'] = p.ht_id
            thisplayer['first_name'] = p.first_name
            thisplayer['nick_name'] = p.nick_name
            thisplayer['last_name'] = p.last_name
            thisplayer['number'] = p.number
            thisplayer['category_id'] = p.category_id
            thisplayer['owner_notes'] = p.owner_notes
            thisplayer['age_years'] = p.age_years
            thisplayer['age_days'] = p.age_days
            thisplayer['age'] = p.age
            thisplayer['next_birthday'] = p.next_birthday

            thedate = dt(
                p.arrival_date.year,
                p.arrival_date.month,
                p.arrival_date.day,
                p.arrival_date.hour,
                p.arrival_date.minute)

            thisplayer['arrival_date'] = thedate
            thisplayer['form'] = p.form
            thisplayer['cards'] = p.cards
            thisplayer['injury_level'] = p.injury_level
            thisplayer['statement'] = p.statement
            thisplayer['language'] = p.language
            thisplayer['language_id'] = p.language_id
            thisplayer['agreeability'] = p.agreeability
            thisplayer['aggressiveness'] = p.aggressiveness
            thisplayer['honesty'] = p.honesty
            thisplayer['experience'] = p.experience
            thisplayer['loyalty'] = p.loyalty
            thisplayer['aggressiveness'] = p.aggressiveness
            thisplayer['specialty'] = p.specialty
            thisplayer['native_country_id'] = p.native_country_id
            thisplayer['native_league_id'] = p.native_league_id
            thisplayer['native_league_name'] = p.native_league_name
            thisplayer['tsi'] = p.tsi
            thisplayer['salary'] = p.salary
            thisplayer['caps'] = p.caps
            thisplayer['caps_u20'] = p.caps_u20
            thisplayer['career_goals'] = p.career_goals
            thisplayer['career_hattricks'] = p.career_hattricks
            thisplayer['league_goals'] = p.league_goals
            thisplayer['cup_goals'] = p.cup_goals
            thisplayer['friendly_goals'] = p.friendly_goals
            thisplayer['current_team_matches'] = p.current_team_matches
            thisplayer['current_team_goals'] = p.current_team_goals
            thisplayer['national_team_id'] = p.national_team_id
            thisplayer['national_team_name'] = p.national_team_name
            thisplayer['is_transfer_listed'] = the_player.is_transfer_listed
            thisplayer['team_id'] = p.team_ht_id
            thisplayer['mother_club_bonus'] = p.mother_club_bonus
            thisplayer['leadership'] = p.leadership

            # Debug: Check which object has skills
            # Use the_player.skills instead of p.skills for pychpp 0.3.12
            skills_source = the_player.skills if hasattr(the_player, 'skills') and the_player.skills else p.skills

            # Helper function to safely extract int from skill value
            def safe_skill_int(skill_val):
                if skill_val is None:
                    return 0
                if isinstance(skill_val, int):
                    return skill_val
                try:
                    result = int(skill_val)
                    return result if result is not None else 0
                except (TypeError, ValueError):
                    return 0

            thisplayer['stamina'] = safe_skill_int(skills_source.get('stamina') if skills_source else None)
            thisplayer['keeper'] = safe_skill_int(skills_source.get('keeper') if skills_source else None)
            thisplayer['defender'] = safe_skill_int(skills_source.get('defender') if skills_source else None)
            thisplayer['playmaker'] = safe_skill_int(skills_source.get('playmaker') if skills_source else None)
            thisplayer['winger'] = safe_skill_int(skills_source.get('winger') if skills_source else None)
            thisplayer['passing'] = safe_skill_int(skills_source.get('passing') if skills_source else None)
            thisplayer['scorer'] = safe_skill_int(skills_source.get('scorer') if skills_source else None)
            thisplayer['set_pieces'] = safe_skill_int(skills_source.get('set_pieces') if skills_source else None)

            thisplayer['data_date'] = time.strftime('%Y-%m-%d')

            thisplayer['owner'] = teamid

            playernames[p.ht_id] = p.first_name + " " + p.last_name

            try:
                dbplayer = db.session.query(Players).filter_by(
                    ht_id=thisplayer['ht_id'],
                    data_date=thisplayer['data_date']).first()

                if dbplayer:
                    db.session.delete(dbplayer)
                    db.session.commit()

                newplayer = Players(thisplayer)
                db.session.add(newplayer)
                db.session.commit()
                dprint(
                    1,
                    f"✅ Successfully added {thisplayer['first_name']} {thisplayer['last_name']} for {thisplayer['data_date']}")

            except Exception as e:
                db.session.rollback()
                error_details = traceback.format_exc()
                dprint(1, f"ERROR: Database operation failed for player {thisplayer['first_name']} {thisplayer['last_name']}: {str(e)}")
                dprint(1, f"Database error traceback: {error_details}")

                return create_page(
                    template='update.html',
                    title='Update Failed',
                    error=f"Database error while saving player data: {str(e)}",
                    errorinfo=f"Failed to save {thisplayer['first_name']} {thisplayer['last_name']} to database.\n\n{error_details}",
                    all_teams=session['all_teams'],
                    all_team_names=session['all_team_names'])

            players_fromht.append(thisplayer['ht_id'])

        # Collect changes for 4-week timeline - simplified
        timeline_changes = {}

        for week_num in range(1, 5):  # Weeks 1-4
            week_start_days = week_num * 7       # Start of week (older)
            week_end_days = (week_num - 1) * 7   # End of week (newer)

            timeline_changes[f'week_{week_num}'] = {
                'week_label': f"Week {week_num}",
                'is_current': week_num == 1,
                'days_ago_start': week_start_days,
                'days_ago_end': week_end_days,
                'changes': []
            }

            # Get all changes for all players in this week period
            for player_id in players_fromht:
                player_changes = get_player_changes(player_id, week_start_days, week_end_days, the_team.name)

                for change in player_changes:
                    timeline_changes[f'week_{week_num}']['changes'].append(change)

        updated[teamid].append('/player?id=' + str(teamid))
        updated[teamid].append('players')

        # Of each of the players you ever have owned, get the last download
        players_data = (db.session.query(Players)
                        .filter_by(owner=teamid)
                        .order_by(text("number"))
                        .order_by(text("data_date"))
                        .all())
        players_indb = []
        for p in players_data:
            players_indb.append(p.ht_id)
            playernames[p.ht_id] = p.first_name + " " + p.last_name
        players_indb = list(set(players_indb))

        # Which players are new
        players_new = diff(players_fromht, players_indb)

        for p in players_new:
            new_players.append([updated[teamid][0], playernames[p]])

        # Which players are no longer in the team
        players_left = diff(players_indb, players_fromht)

        for p in players_left:
            left_players.append([updated[teamid][0], playernames[p]])
            (db.session
             .query(Players)
             .filter_by(ht_id=p,
                        owner=teamid)
             .update({"old_owner": teamid, "owner": 0}))
            db.session.commit()

    return create_page(
        template='update_timeline.html',
        title='Update Complete - Timeline View',
        updated=updated,
        timeline_changes=timeline_changes,
        left_players=left_players,
        new_players=new_players)
