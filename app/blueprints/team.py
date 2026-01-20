"""Team management routes blueprint for HT Status application."""

import traceback
import time
import datetime
from datetime import datetime as dt
from flask import Blueprint, render_template, request, session
from sqlalchemy import text
from pychpp import CHPP

from models import Players
from app.routes_bp import create_page, dprint, debug_print, player_diff, diff

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
    debug_print("team", "chpp.user", current_user._SOURCE_FILE)
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

        # Test basic API connectivity
        dprint(1, "Testing CHPP API connectivity...")
        test_user = chpp.user()
        dprint(1, f"API connectivity test successful, user ID: {test_user.ht_id}")

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

    dprint(1, f"Processing {len(all_teams)} teams for data update")

    for teamid in all_teams:
        dprint(1, f"Processing team ID: {teamid}")

        try:
            dprint(1, f"Fetching team data for team ID: {teamid}")
            the_team = chpp.team(ht_id=teamid)
            debug_print("update", "chpp.team", the_team._SOURCE_FILE)
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

            thisplayer['stamina'] = p.skills['stamina']
            thisplayer['keeper'] = p.skills['keeper']
            thisplayer['defender'] = p.skills['defender']
            thisplayer['playmaker'] = p.skills['playmaker']
            thisplayer['winger'] = p.skills['winger']
            thisplayer['passing'] = p.skills['passing']
            thisplayer['scorer'] = p.skills['scorer']
            thisplayer['set_pieces'] = p.skills['set_pieces']

            thisplayer['data_date'] = time.strftime('%Y-%m-%d')

            thisplayer['owner'] = teamid

            playernames[p.ht_id] = p.first_name + " " + p.last_name

            try:
                dprint(2, f"Checking for existing player {p.first_name} {p.last_name} (ID: {p.ht_id}) in database")
                dbplayer = db.session.query(Players).filter_by(
                    ht_id=thisplayer['ht_id'],
                    data_date=thisplayer['data_date']).first()

                if dbplayer:
                    dprint(
                        1,
                        f"Updating existing player: {thisplayer['first_name']} {thisplayer['last_name']}")
                    db.session.delete(dbplayer)
                    db.session.commit()

                dprint(2, f"Adding new player data to database: {thisplayer['first_name']} {thisplayer['last_name']}")
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
                dprint(2, thischanges)

            thischanges = player_diff(thisplayer['ht_id'], 7)
            if thischanges:
                changesplayers_week.append(thischanges)
                dprint(2, thischanges)

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
        dprint(2, "New: ", players_new)

        for p in players_new:
            new_players.append([updated[teamid][0], playernames[p]])

        # Which players are no longer in the team
        players_left = diff(players_indb, players_fromht)
        dprint(2, "Left: ", players_left)

        for p in players_left:
            left_players.append([updated[teamid][0], playernames[p]])
            (db.session
             .query(Players)
             .filter_by(ht_id=p,
                        owner=teamid)
             .update({"old_owner": teamid, "owner": 0}))
            db.session.commit()

    dprint(1, "=== DATA UPDATE PROCESS COMPLETED SUCCESSFULLY ===")
    dprint(1, f"Teams processed: {len(all_teams)}")
    dprint(1, f"Total new players: {len(new_players)}")
    dprint(1, f"Total departed players: {len(left_players)}")
    dprint(1, f"Daily changes tracked: {len(changesplayers_day)}")
    dprint(1, f"Weekly changes tracked: {len(changesplayers_week)}")

    return create_page(
        template='update.html',
        title='Update Complete',
        updated=updated,
        changes_day=changesplayers_day,
        changes_week=changesplayers_week,
        left_players=left_players,
        new_players=new_players)
