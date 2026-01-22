"""Team management routes blueprint for HT Status application."""

import time
import traceback
from datetime import datetime as dt

from flask import Blueprint, render_template, session
from pychpp import CHPP
from sqlalchemy import text

from app.utils import create_page, diff, dprint, player_diff
from models import Players

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
def team():
    """Display team information."""
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

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
def update():
    """Update player data from Hattrick API."""
    dprint(1, "=== DATA UPDATE PROCESS STARTED ===")

    if session.get('current_user') is None:
        dprint(1, "ERROR: No current_user in session, redirecting to login")
        return render_template(
            '_forward.html',
            url='/login')

    # Session state validation
    dprint(1, f"Current user: {session.get('current_user')}")
    dprint(1, f"Access key available: {bool(session.get('access_key'))}")
    dprint(1, f"Access secret available: {bool(session.get('access_secret'))}")
    dprint(1, f"All teams: {session.get('all_teams')}")
    dprint(1, f"Team names: {session.get('all_team_names')}")

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
            team_players = the_team.players
            players_count = len(team_players)

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
        for p in team_players:

            thisplayer = {}

            # Get player ID - pychpp 0.5.10 uses 'ht_id' attribute
            player_id = p.ht_id
            the_player = chpp.player(ht_id=player_id)

            if the_player.transfer_details:
                pass  # Transfer details exist but not used in logging

            thisplayer['ht_id'] = p.ht_id
            thisplayer['first_name'] = p.first_name
            thisplayer['nick_name'] = p.nick_name
            thisplayer['last_name'] = p.last_name
            thisplayer['number'] = p.number
            thisplayer['category_id'] = p.category_id
            thisplayer['owner_notes'] = p.owner_notes
            thisplayer['age_years'] = p.age  # HTTeamPlayersItem uses 'age' for years
            thisplayer['age_days'] = p.age_days
            thisplayer['age'] = p.age
            # thisplayer['next_birthday'] = p.next_birthday  # Not available in HTTeamPlayersItem
            thisplayer['next_birthday'] = None  # Set default value since not available

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
            # thisplayer['language'] = p.language  # Not available in HTTeamPlayersItem
            # thisplayer['language_id'] = p.language_id  # Not available in HTTeamPlayersItem
            thisplayer['language'] = None  # Set default value since not available
            thisplayer['language_id'] = None  # Set default value since not available
            thisplayer['agreeability'] = p.agreeability
            thisplayer['aggressiveness'] = p.aggressiveness
            thisplayer['honesty'] = p.honesty
            thisplayer['experience'] = p.experience
            thisplayer['loyalty'] = p.loyalty
            thisplayer['aggressiveness'] = p.aggressiveness
            thisplayer['specialty'] = p.specialty
            # thisplayer['native_country_id'] = p.native_country_id  # Not available in HTTeamPlayersItem
            # thisplayer['native_league_id'] = p.native_league_id  # Not available in HTTeamPlayersItem
            # thisplayer['native_league_name'] = p.native_league_name  # Not available in HTTeamPlayersItem
            thisplayer['native_country_id'] = None  # Set default value since not available
            thisplayer['native_league_id'] = None  # Set default value since not available
            thisplayer['native_league_name'] = None  # Set default value since not available
            thisplayer['tsi'] = p.tsi
            thisplayer['salary'] = p.salary
            thisplayer['caps'] = p.caps
            thisplayer['caps_u20'] = p.caps_u20
            thisplayer['career_goals'] = p.career_goals
            thisplayer['career_hattricks'] = p.career_hattricks
            thisplayer['league_goals'] = the_player.league_goals
            thisplayer['cup_goals'] = the_player.cup_goals
            thisplayer['friendly_goals'] = the_player.friendlies_goals
            thisplayer['current_team_matches'] = the_player.matches_current_team
            thisplayer['current_team_goals'] = the_player.goals_current_team
            # thisplayer['national_team_id'] = p.national_team_id  # Not available in HTTeamPlayersItem
            # thisplayer['national_team_name'] = p.national_team_name  # Not available in HTTeamPlayersItem
            thisplayer['national_team_id'] = None  # Set default value since not available
            thisplayer['national_team_name'] = None  # Set default value since not available
            thisplayer['is_transfer_listed'] = the_player.transfer_listed
            thisplayer['team_id'] = teamid  # Use the teamid from session since team_ht_id not available
            thisplayer['mother_club_bonus'] = p.mother_club_bonus
            thisplayer['leadership'] = p.leadership

            thisplayer['stamina'] = p.player_skills.stamina
            thisplayer['keeper'] = p.player_skills.keeper
            thisplayer['defender'] = p.player_skills.defender
            thisplayer['playmaker'] = p.player_skills.playmaker
            thisplayer['winger'] = p.player_skills.winger
            thisplayer['passing'] = p.player_skills.passing
            thisplayer['scorer'] = p.player_skills.scorer
            thisplayer['set_pieces'] = p.player_skills.set_pieces

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

            thischanges = player_diff(thisplayer['ht_id'], 1)
            if thischanges:
                changesplayers_day.append(thischanges)

            thischanges = player_diff(thisplayer['ht_id'], 7)
            if thischanges:
                changesplayers_week.append(thischanges)

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
        template='update.html',
        title='Update Complete',
        updated=updated,
        changes_day=changesplayers_day,
        changes_week=changesplayers_week,
        left_players=left_players,
        new_players=new_players)
