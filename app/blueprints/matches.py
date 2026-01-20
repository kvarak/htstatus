"""Matches and stats routes blueprint for HT Status application."""

from flask import Blueprint, render_template, request, session
from sqlalchemy import text

from app.routes_bp import create_page
from models import Match, MatchPlay

# Create Blueprint for match and stats routes
matches_bp = Blueprint('matches', __name__)

# These will be set by setup_matches_blueprint()
db = None
HTmatchtype = {}
HTmatchrole = {}
HTmatchbehaviour = {}


def setup_matches_blueprint(db_instance, match_types, match_roles, match_behaviours):
    """Initialize matches blueprint with db instance and Hattrick constants."""
    global db, HTmatchtype, HTmatchrole, HTmatchbehaviour
    db = db_instance
    HTmatchtype = match_types
    HTmatchrole = match_roles
    HTmatchbehaviour = match_behaviours


def matches():
    """Display team matches and match details."""
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    teamid = request.values.get('id')
    matchid = request.values.get('m')

    teamid = int(teamid) if teamid else request.form.get('id')
    matchid = int(matchid) if matchid else request.form.get('m')
    all_teams = session['all_teams']

    error = ""
    if teamid not in all_teams:
        error = "Wrong teamid, try the links."
        return create_page(
            template='matches.html',
            error=error,
            title='Matches')

    all_team_names = session['all_team_names']
    teamname = all_team_names[all_teams.index(teamid)]

    # Get all registered matches
    dbmatches = db.session.query(Match).filter(
        (Match.away_team_id == teamid) |
        (Match.home_team_id == teamid)).order_by(text("datetime desc")).all()
    dbmatchplays = {}
    for m in dbmatches:
        dbmatch = db.session.query(MatchPlay).filter_by(match_id=m.ht_id).all()
        dbmatchplays[m.ht_id] = dbmatch

    return create_page(
        template='matches.html',
        error=error,
        matches=dbmatches,
        matchplays=dbmatchplays,
        matchidtoshow=matchid,
        teamname=teamname,
        teamid=teamid,
        HTmatchtype=HTmatchtype,
        HTmatchrole=HTmatchrole,
        HTmatchbehaviour=HTmatchbehaviour,
        title='Matches')


def stats():
    """Display team statistics."""
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    teamid = request.values.get('id')

    teamid = int(teamid) if teamid else request.form.get('id')
    all_teams = session['all_teams']

    error = ""
    if teamid not in all_teams:
        error = "Wrong teamid, try the links."
        return create_page(
            template='stats.html',
            title='Stats')

    all_team_names = session['all_team_names']
    teamname = all_team_names[all_teams.index(teamid)]

    return create_page(
        template='stats.html',
        error=error,
        teamname=teamname,
        teamid=teamid,
        title='Stats')
