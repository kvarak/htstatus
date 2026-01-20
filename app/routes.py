import inspect
import math
import re
import subprocess  # noqa: B404 - Used only for git version detection (static commands)
import time
import traceback
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta
from flask import render_template, request, session
from pychpp import CHPP
from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from models import Group, Match, MatchPlay, Players, PlayerSetting, User

# Initialize these after app is created
app = None
db = None

# Global variables set during initialization
bootstrap = None
consumer_key = None
consumer_secret = None
versionstr = None
fullversion = None
version = None
timenow = None
debug_level = None

def initialize_routes():
    """Initialize routes module with app and db instances."""
    global bootstrap, consumer_key, consumer_secret, versionstr, fullversion, version, timenow, debug_level

    # --------------------------------------------------------------------------------
    # --------------------------------------------------------------------------------
    # Bootstrap already initialized in routes_bp.py, just reference it
    from app.routes_bp import bootstrap as bp_bootstrap
    bootstrap = bp_bootstrap

    # Set consumer_key and consumer_secret provided for your app by Hattrick
    consumer_key = app.config['CONSUMER_KEY']
    consumer_secret = app.config['CONSUMER_SECRETS']

    # Security Note: Git version detection for UI display only
    # - Static command with no user input injection vectors
    # - Development/operations utility, not user-facing security context
    # - Risk is theoretical (partial path warning) rather than practical
    # - Acceptable for development tooling purposes
    versionstr = subprocess.check_output(["git", "describe", "--tags"]).strip()  # noqa: B607,B603
    versionstr = versionstr.decode("utf-8").split('-')
    fullversion = versionstr[0] + "." + versionstr[1] + "-" + versionstr[2]
    version = versionstr[0] + "." + versionstr[1]

    timenow = time.strftime('%Y-%m-%d %H:%M:%S')
    debug_level = app.config['DEBUG_LEVEL']

# Module constants
default_group_order = 99
logfile = "htplanner.log"

# --------------------------------------------------------------------------------
# HT definitions
# --------------------------------------------------------------------------------


HTmatchtype = {}
HTmatchtype[1] = "League match"
HTmatchtype[2] = "Qualification match"
HTmatchtype[3] = "Cup match (standard league match)"
HTmatchtype[4] = "Friendly (normal rules)"
HTmatchtype[5] = "Friendly (cup rules)"
HTmatchtype[6] = "Not currently in use, but reserved for international \
                  competition matches with normal rules (may or may not \
                  be implemented at some future point)."
HTmatchtype[7] = "Hattrick Masters"
HTmatchtype[8] = "International friendly (normal rules)"
HTmatchtype[9] = "International friendly (cup rules)"
HTmatchtype[10] = "National teams competition match (normal rules)"
HTmatchtype[11] = "National teams competition match (cup rules)"
HTmatchtype[12] = "National teams friendly"
HTmatchtype[50] = "Tournament League match"
HTmatchtype[51] = "Tournament Playoff match"
HTmatchtype[61] = "Single match"
HTmatchtype[62] = "Ladder match"
HTmatchtype[80] = "Preparation match"
HTmatchtype[100] = "Youth league match"
HTmatchtype[101] = "Youth friendly match"
HTmatchtype[102] = "RESERVED"
HTmatchtype[103] = "Youth friendly match (cup rules)"
HTmatchtype[104] = "RESERVED"
HTmatchtype[105] = "Youth international friendly match"
HTmatchtype[106] = "Youth international friendly match (Cup rules)"
HTmatchtype[107] = "RESERVED"

HTmatchrole = {}
HTmatchrole[100] = "Keeper"
HTmatchrole[101] = "Right back"
HTmatchrole[102] = "Right central defender"
HTmatchrole[103] = "Middle central defender"
HTmatchrole[104] = "Left central defender"
HTmatchrole[105] = "Left back"
HTmatchrole[106] = "Right winger"
HTmatchrole[107] = "Right inner midfield"
HTmatchrole[108] = "Middle inner midfield"
HTmatchrole[109] = "Left inner midfield"
HTmatchrole[110] = "Left winger"
HTmatchrole[111] = "Right forward"
HTmatchrole[112] = "Middle forward"
HTmatchrole[113] = "Left forward"
HTmatchrole[114] = "Substitution (Keeper)"
HTmatchrole[115] = "Substitution (Defender)"
HTmatchrole[116] = "Substitution (Inner midfield)"
HTmatchrole[117] = "Substitution (Winger)"
HTmatchrole[118] = "Substitution (Forward)"
HTmatchrole[200] = "Substitution (Keeper)"
HTmatchrole[201] = "Substitution (Central defender)"
HTmatchrole[202] = "Substitution (Wing back)"
HTmatchrole[203] = "Substitution (Inner midfielder)"
HTmatchrole[204] = "Substitution (Forward)"
HTmatchrole[205] = "Substitution (Winger)"
HTmatchrole[206] = "Substitution (Extra)"
HTmatchrole[207] = "Backup (Keeper)"
HTmatchrole[208] = "Backup (Central defender)"
HTmatchrole[209] = "Backup (Wing back)"
HTmatchrole[210] = "Backup (Inner midfielder)"
HTmatchrole[211] = "Backup (Forward)"
HTmatchrole[212] = "Backup (Winger)"
HTmatchrole[213] = "Backup (Extra)"
HTmatchrole[17] = "Set pieces"
HTmatchrole[18] = "Captain"
HTmatchrole[19] = "Replaced Player #1"
HTmatchrole[20] = "Replaced Player #2"
HTmatchrole[21] = "Replaced Player #3"
HTmatchrole[22] = "Penalty taker (1)"
HTmatchrole[23] = "Penalty taker (2)"
HTmatchrole[24] = "Penalty taker (3)"
HTmatchrole[25] = "Penalty taker (4)"
HTmatchrole[26] = "Penalty taker (5)"
HTmatchrole[27] = "Penalty taker (6)"
HTmatchrole[28] = "Penalty taker (7)"
HTmatchrole[29] = "Penalty taker (8)"
HTmatchrole[30] = "Penalty taker (9)"
HTmatchrole[31] = "Penalty taker (10)"
HTmatchrole[32] = "Penalty taker (11)"

HTmatchbehaviour = {}
HTmatchbehaviour[-1] = "No change"
HTmatchbehaviour[0] = "Normal"
HTmatchbehaviour[1] = "Offensive"
HTmatchbehaviour[2] = "Defensive"
HTmatchbehaviour[3] = "Towards middle"
HTmatchbehaviour[4] = "Towards wing"
HTmatchbehaviour[5] = "Extra forward"
HTmatchbehaviour[6] = "Extra inner midfield"
HTmatchbehaviour[7] = "Extra defender"

# --------------------------------------------------------------------------------


allcolumns = [
    ('Group', 'group'), ('Number', 'number'),
    ('Specialty', 'specialty'), ('Name', 'name'),
    ('Age', 'age_years'), ('Keeper', 'keeper'),
    ('Defence', 'defender'), ('Playmaking', 'playmaker'),
    ('Winger', 'winger'), ('Passing', 'passing'),
    ('Scorer', 'scorer'), ('Set pieces', 'set_pieces'),
    ('Max stars', 'max_stars'), ('Last stars', 'last_stars'),
    ('Status', 'status'), ('First seen', 'firstseen'),
    ('Player notes', 'owner_notes'),
    ('Leadership', 'leadership'), ('Agreeability', 'agreeability'),
    ('Aggressiveness', 'aggressiveness'), ('Honesty', 'honesty'),
    ('Experience', 'experience'), ('Loyalty', 'loyalty'), ('TSI', 'tsi'),
    ('Form', 'form'), ('Stamina', 'stamina'),
    ('Career goals', 'career_goals'), ('Statement', 'statement'),
    ('Salary', 'salary'),
    ('Goalkeeper contribution (GC)', 'GC'),
    ("Central Defender Normal (CD)", "CD"),
    ("Central Defender Offensive (CDO)", "CDO"),
    ("Side Central Defender Towards Wing (CDTW)", "CDTW"),
    ("Wing Back Defensive (WBD)", "WBD"),
    ("Wingback Normal (WBN)", "WBN"),
    ("Wing Back Offensive (WBO)", "WBO"),
    ("Wingback Towards Middle (WBTM)", "WBTM"),
    ("Winger Offensive (WO)", "WO"),
    ("Winger Towards Middle (WTM)", "WTM"),
    ("Winger Normal (WN)", "WN"),
    ("Winger Defensive (WD)", "WD"),
    ("Inner Midfielder Normal (IMN)", "IMN"),
    ("Inner Midfielder Defensive (IMD)", "IMD"),
    ("Inner Midfielder Offensive (IMO)", "IMO"),
    ("Inner Midfielder Towards Wing (IMTW)", "IMTW"),
    ("Forward Normal (FW)", "FW"),
    ("Forward Towards Wing (FTW) ", "FTW"),
    ("Defensive Forward (DF)", "DF"),
    ("Best position", "bestposition"),
    ("Man marking capability", "MMC")
]

defaultcolumns = [
    ('Group', 'group'), ('Number', 'number'),
    ('Specialty', 'specialty'), ('Name', 'name'),
    ('Age', 'age_years'), ('Keeper', 'keeper'),
    ('Defence', 'defender'), ('Playmaking', 'playmaker'),
    ('Winger', 'winger'), ('Passing', 'passing'),
    ('Scorer', 'scorer'), ('Set pieces', 'set_pieces'),
    ('Max stars', 'max_stars'), ('Last stars', 'last_stars'),
    ('Status', 'status'), ('First seen', 'firstseen'),
    ("Best position", "bestposition")
]

tracecolumns = [
    'keeper', 'defender', 'playmaker',
    'winger', 'passing', 'scorer', 'set_pieces'
]

calccolumns = [
    'GC',
    'CD', 'CDO', 'CDTW',
    'WBD', 'WBN', 'WBO', 'WBTM',
    'WO', 'WTM', 'WN', 'WD',
    'IMN', 'IMD', 'IMO', 'IMTW',
    'FW',
    'FTW', 'DF'
]

# --------------------------------------------------------------------------------
# Contribution functions
# --------------------------------------------------------------------------------


def calculateManmark(player):
    xp = math.log(player['experience']) * 4 / 3 if player['experience'] > 0 else 0
    loy = player['loyalty'] / 20
    formfactor = round(math.pow(((player['form'] - 0.5) / 7), 0.45), 2)
    defending = player['defender'] + xp + loy

    manmarkco = (math.pow(defending, 3.5) /
                 (math.pow(defending, 3.5) +
                  math.pow(10, 3.5)))
    manmarkco = manmarkco * formfactor

    # powerful
    if player['specialty'] == 3:
        manmarkco = manmarkco * 1.1
    # no speciality
    elif player['specialty'] == 0:
        manmarkco = manmarkco * 1.05

    return round(manmarkco, 2)


def calculateContribution(position, player):
    contr = 0

    # XP adds to skills
    xp = 0 if player['experience'] == 0 else math.log(player['experience']) * 4 / 3

    # Loyalty adds to skills (good enough approximation)
    loy = player['loyalty'] / 20

    # Form multiplies to skills
    formfactor = round(math.pow(((player['form'] - 0.5) / 7), 0.45), 2)

    # Goalkeeper
    if position == "GC":
        contr += 0.61 * (player['keeper'] + xp + loy)
        contr += 0.87 * (player['keeper'] + xp + loy)
        contr += 0.61 * (player['keeper'] + xp + loy)
        contr += 0.25 * (player['defender'] + xp + loy)
        contr += 0.35 * (player['defender'] + xp + loy)
        contr += 0.25 * (player['defender'] + xp + loy)
    # Central Defender
    elif position == "CD":
        contr += 0.26 * (player['defender'] + xp + loy)
        contr += 1.00 * (player['defender'] + xp + loy)
        contr += 0.26 * (player['defender'] + xp + loy)
        contr += 0.25 * (player['playmaker'] + xp + loy)
    elif position == "CDO":
        contr += 0.20 * (player['defender'] + xp + loy)
        contr += 0.73 * (player['defender'] + xp + loy)
        contr += 0.20 * (player['defender'] + xp + loy)
        contr += 0.40 * (player['playmaker'] + xp + loy)
    elif position == "CDTW":
        contr += 0.81 * (player['defender'] + xp + loy)
        contr += 0.67 * (player['defender'] + xp + loy)
        contr += 0.00 * (player['defender'] + xp + loy)
        contr += 0.15 * (player['playmaker'] + xp + loy)
        contr += 0.26 * (player['winger'] + xp + loy)
    # Wingback
    elif position == "WBN":
        contr += 0.92 * (player['defender'] + xp + loy)
        contr += 0.38 * (player['defender'] + xp + loy)
        contr += 0.00 * (player['defender'] + xp + loy)
        contr += 0.15 * (player['playmaker'] + xp + loy)
        contr += 0.59 * (player['winger'] + xp + loy)
    elif position == "WBD":
        contr += 1.00 * (player['defender'] + xp + loy)
        contr += 0.43 * (player['defender'] + xp + loy)
        contr += 0.00 * (player['defender'] + xp + loy)
        contr += 0.10 * (player['playmaker'] + xp + loy)
        contr += 0.45 * (player['winger'] + xp + loy)
    elif position == "WBO":
        contr += 0.74 * (player['defender'] + xp + loy)
        contr += 0.35 * (player['defender'] + xp + loy)
        contr += 0.00 * (player['defender'] + xp + loy)
        contr += 0.20 * (player['playmaker'] + xp + loy)
        contr += 0.69 * (player['winger'] + xp + loy)
    elif position == "WBTM":
        contr += 0.75 * (player['defender'] + xp + loy)
        contr += 0.70 * (player['defender'] + xp + loy)
        contr += 0.00 * (player['defender'] + xp + loy)
        contr += 0.20 * (player['playmaker'] + xp + loy)
        contr += 0.35 * (player['winger'] + xp + loy)
    # Winger
    elif position == "WN":
        contr += 0.86 * (player['winger'] + xp + loy)
        contr += 0.35 * (player['defender'] + xp + loy)
        contr += 0.20 * (player['defender'] + xp + loy)
        contr += 0.45 * (player['playmaker'] + xp + loy)
        contr += 0.26 * (player['passing'] + xp + loy)
        contr += 0.11 * (player['passing'] + xp + loy)
    elif position == "WD":
        contr += 0.69 * (player['winger'] + xp + loy)
        contr += 0.61 * (player['defender'] + xp + loy)
        contr += 0.25 * (player['defender'] + xp + loy)
        contr += 0.30 * (player['playmaker'] + xp + loy)
        contr += 0.21 * (player['passing'] + xp + loy)
        contr += 0.05 * (player['passing'] + xp + loy)
    elif position == "WO":
        contr += 1.00 * (player['winger'] + xp + loy)
        contr += 0.22 * (player['defender'] + xp + loy)
        contr += 0.13 * (player['defender'] + xp + loy)
        contr += 0.30 * (player['playmaker'] + xp + loy)
        contr += 0.29 * (player['passing'] + xp + loy)
        contr += 0.13 * (player['passing'] + xp + loy)
    elif position == "WTM":
        contr += 0.74 * (player['winger'] + xp + loy)
        contr += 0.29 * (player['defender'] + xp + loy)
        contr += 0.25 * (player['defender'] + xp + loy)
        contr += 0.55 * (player['playmaker'] + xp + loy)
        contr += 0.15 * (player['passing'] + xp + loy)
        contr += 0.16 * (player['passing'] + xp + loy)
    # Inner Midfielder
    elif position == "IMN":
        contr += 1.00 * (player['playmaker'] + xp + loy)
        contr += 0.09 * (player['defender'] + xp + loy)
        contr += 0.40 * (player['defender'] + xp + loy)
        contr += 0.09 * (player['defender'] + xp + loy)
        contr += 0.13 * (player['passing'] + xp + loy)
        contr += 0.33 * (player['passing'] + xp + loy)
        contr += 0.13 * (player['passing'] + xp + loy)
        contr += 0.22 * (player['scorer'] + xp + loy)
    elif position == "IMD":
        contr += 0.95 * (player['playmaker'] + xp + loy)
        contr += 0.14 * (player['defender'] + xp + loy)
        contr += 0.58 * (player['defender'] + xp + loy)
        contr += 0.14 * (player['defender'] + xp + loy)
        contr += 0.07 * (player['passing'] + xp + loy)
        contr += 0.18 * (player['passing'] + xp + loy)
        contr += 0.07 * (player['passing'] + xp + loy)
        contr += 0.13 * (player['scorer'] + xp + loy)
    elif position == "IMO":
        contr += 0.95 * (player['playmaker'] + xp + loy)
        contr += 0.04 * (player['defender'] + xp + loy)
        contr += 0.16 * (player['defender'] + xp + loy)
        contr += 0.04 * (player['defender'] + xp + loy)
        contr += 0.18 * (player['passing'] + xp + loy)
        contr += 0.49 * (player['passing'] + xp + loy)
        contr += 0.18 * (player['passing'] + xp + loy)
        contr += 0.31 * (player['scorer'] + xp + loy)
    elif position == "IMTW":
        contr += 0.90 * (player['playmaker'] + xp + loy)
        contr += 0.24 * (player['defender'] + xp + loy)
        contr += 0.33 * (player['defender'] + xp + loy)
        contr += 0.00 * (player['defender'] + xp + loy)
        contr += 0.31 * (player['passing'] + xp + loy)
        contr += 0.23 * (player['passing'] + xp + loy)
        contr += 0.00 * (player['passing'] + xp + loy)
        contr += 0.59 * (player['winger'] + xp + loy)
    # Forward
    elif position == "FW":
        contr += 0.27 * (player['scorer'] + xp + loy)
        contr += 1.00 * (player['scorer'] + xp + loy)
        contr += 0.27 * (player['scorer'] + xp + loy)
        contr += 0.14 * (player['passing'] + xp + loy)
        contr += 0.33 * (player['passing'] + xp + loy)
        contr += 0.14 * (player['passing'] + xp + loy)
        contr += 0.24 * (player['winger'] + xp + loy)
        contr += 0.24 * (player['winger'] + xp + loy)
        contr += 0.25 * (player['playmaker'] + xp + loy)
    elif position == "DF":
        contr += 0.13 * (player['scorer'] + xp + loy)
        contr += 0.56 * (player['scorer'] + xp + loy)
        contr += 0.13 * (player['scorer'] + xp + loy)
        # technical defensive forward
        if player['specialty'] == 1:
            contr += 0.41 * (player['passing'] + xp + loy)
            contr += 0.53 * (player['passing'] + xp + loy)
            contr += 0.41 * (player['passing'] + xp + loy)
        else:
            contr += 0.31 * (player['passing'] + xp + loy)
            contr += 0.53 * (player['passing'] + xp + loy)
            contr += 0.31 * (player['passing'] + xp + loy)
        contr += 0.13 * (player['winger'] + xp + loy)
        contr += 0.13 * (player['winger'] + xp + loy)
        contr += 0.35 * (player['playmaker'] + xp + loy)
    elif position == "FTW":
        contr += 0.51 * (player['scorer'] + xp + loy)
        contr += 0.66 * (player['scorer'] + xp + loy)
        contr += 0.19 * (player['scorer'] + xp + loy)
        contr += 0.21 * (player['passing'] + xp + loy)
        contr += 0.23 * (player['passing'] + xp + loy)
        contr += 0.21 * (player['passing'] + xp + loy)
        contr += 0.64 * (player['winger'] + xp + loy)
        contr += 0.21 * (player['winger'] + xp + loy)
        contr += 0.15 * (player['playmaker'] + xp + loy)
    return round(contr * formfactor, 2)


# --------------------------------------------------------------------------------
# Help functions
# --------------------------------------------------------------------------------


def get_training(players_data):

    allplayerids = []
    allplayers = {}
    playernames = {}
    for entry in players_data:
        allplayers[entry.ht_id] = []
        if entry.number == 100:
            playernames[entry.ht_id] = entry.first_name + " " + entry.last_name
        else:
            playernames[entry.ht_id] = str(entry.number) + ". " + \
                entry.first_name + " " + entry.last_name
        if entry.ht_id not in allplayerids:
            allplayerids.append(entry.ht_id)

    for player in players_data:
        allplayers[player.ht_id].append(
            [
                datetime.date(player.data_date),
                (
                    player.keeper,
                    player.defender,
                    player.playmaker,
                    player.winger,
                    player.passing,
                    player.scorer,
                    player.set_pieces
                )
            ])

    increases = {}
    for i in allplayers:
        increases[i] = \
            allplayers[i][len(allplayers[i])-1][1][0] - \
            allplayers[i][0][1][0]
        for s in range(6):
            increases[i] = increases[i] + \
                allplayers[i][len(allplayers[i])-1][1][s] - \
                allplayers[i][0][1][s]

    # Sort player list based on increases
    allplayerids = sorted(
        allplayerids,
        key=lambda ele: increases[ele],
        reverse=True)

    for i in allplayers:
        # Date filler
        (firstdate, previousskill) = allplayers[i][0]
        (lastdate, x) = allplayers[i][len(allplayers[i])-1]

        friday = firstdate - \
            timedelta(days=firstdate.weekday()) + timedelta(days=4, weeks=-1)

        date_modified = friday
        datelist = [friday]

        while date_modified < lastdate:
            date_modified += timedelta(days=1)
            datelist.append(date_modified)

        newy = []
        for d in datelist:
            for (da, y) in allplayers[i]:
                if (d == da):
                    previousskill = y
            newy.append([d, previousskill])

        # Just take every 7th
        weekly = newy[0::7]
        # add the last day if it's not the last day already
        (lastweekday, x) = weekly[len(weekly)-1]
        if lastdate != lastweekday:
            weekly.append(allplayers[i][len(allplayers[i])-1])

        allplayers[i] = weekly

    return (allplayerids, allplayers, playernames)

# --------------------------------------------------------------------------------


def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month

# --------------------------------------------------------------------------------


def diff(first, second):
    second = set(second)
    return [item for item in first if item not in second]

# --------------------------------------------------------------------------------


def dprint(lvl, *args):
    if lvl <= debug_level:
        # 0 represents this line, 1 represents line at caller
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        pstr = ""
        for a in args:
            pstr = pstr + str(a)
        print(now + " " + info.function + ":" + str(info.lineno) + " " + pstr)

# --------------------------------------------------------------------------------


def debug_print(route, function, *args):
    for arg in args:
        towrite = route + " [" + function + "]: " + arg
        dprint(2, towrite)
    if debug_level >= 3:
        with open(logfile, "a") as file:
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            for arg in args:
                towrite = now + " " + route + " [" + function + "]: " + arg + "\n"
                file.write(towrite)

# --------------------------------------------------------------------------------


def count_clicks(page):
    try:
        user = (db.session.query(User)
                .filter_by(ht_id=session['current_user_id'])
                .first())
    except Exception:
        return 1

    if page == "login.html":
        User.login(user)
    elif page == "player.html":
        User.player(user)
    elif page == "matches.html":
        User.matches(user)
    elif page == "team.html":
        User.team(user)
    elif page == "training.html":
        User.training(user)
    elif page == "update.html":
        User.updatedata(user)
    else:
        return 2

    db.session.commit()

    return 0

# --------------------------------------------------------------------------------


def create_page(template, title, **kwargs):
    last_update = ""
    if 'current_user' in session:
        current_user = session['current_user']
        all_teams = session['all_teams']
        all_team_names = session['all_team_names']
        try:
            user = (db.session.query(User)
                    .filter_by(ht_id=session['current_user_id'])
                    .first())
            role = User.getRole(user)
            if role == "None":
                role = False
            last_update = user.last_update
        except Exception:
            role = False
    else:
        current_user = False
        all_teams = False
        all_team_names = False
        role = False

    with open('app/static/changelog.txt') as f:
        changelog = f.readlines()
    with open('app/static/changelog-full.txt') as f:
        changelogfull = f.readlines()

    count_clicks(template)

    return render_template(
        template,
        title=title,
        version=version,
        timenow=timenow,
        fullversion=fullversion,
        apptitle=app.config['APP_NAME'],
        current_user=current_user,
        all_teams=all_teams,
        all_team_names=all_team_names,
        role=role,
        changelog=changelog,
        changelogfull=changelogfull,
        last_update=last_update,
        **kwargs)


# --------------------------------------------------------------------------------


def player_diff(playerid, daysago):
    # Prints the changes since <date>
    datetime_object = (datetime.now() - timedelta(days=daysago)).date()

    all_teams = session['all_teams']
    all_team_names = session['all_team_names']
    for owner in all_teams:
        foundit = db.session.query(Players).filter_by(
            ht_id=playerid,
            owner=owner).order_by(text("data_date desc")).first()
        if foundit:
            theteam = owner
            latest = foundit
            oldest = (db.session
                      .query(Players)
                      .filter_by(
                          ht_id=playerid,
                          owner=owner)
                      .filter(Players.data_date >= datetime_object)
                      .order_by("data_date")
                      .first())

    if not (oldest):
        return False

    teamname = all_team_names[all_teams.index(theteam)]

    ignore_list = [
        "age",
        "age_days",
        "caps",
        "career_goals",
        "career_hattricks",
        "category_id",
        "cup_goals",
        "current_team_goals",
        "current_team_matches",
        "data_date",
        "form",
        "friendly_goals",
        "injury_level",
        "league_goals",
        "loyalty",
        "national_team_id",
        "national_team_name",
        "number",
        "salary",
        "stamina",
        "tsi",
        "owner",
        "owner_notes",
        "old_owner",
        "leadership",
        "mother_club_bonus"
    ]

    ret = []
    thediff = {}
    for key, elem in latest:
        thediff[key] = elem
    for key, elem in oldest:
        if key not in ignore_list and elem != thediff[key]:
            retstr = [teamname]
            retstr.append(oldest.first_name)
            retstr.append(oldest.last_name)
            retstr.append(key)
            retstr.append(elem)
            retstr.append(thediff[key])
            ret.append(retstr)

    return ret


def player_diff_v2(playerid, daysago):
    # Prints the changes since <date>
    datetime_object = (datetime.now() - timedelta(days=daysago)).date()

    all_teams = session['all_teams']
    all_team_names = session['all_team_names']
    for owner in all_teams:
        foundit = db.session.query(Players).filter_by(
            ht_id=playerid,
            owner=owner).order_by(text("data_date desc")).first()
        if foundit:
            theteam = owner
            latest = foundit
            oldest = (db.session
                      .query(Players)
                      .filter_by(
                          ht_id=playerid,
                          owner=owner)
                      .filter(Players.data_date >= datetime_object)
                      .order_by("data_date")
                      .first())

    if not (oldest):
        return False

    teamname = all_team_names[all_teams.index(theteam)]

    ignore_list = [
        "age",
        "age_days",
        "caps",
        "career_goals",
        "career_hattricks",
        "category_id",
        "cup_goals",
        "current_team_goals",
        "current_team_matches",
        "data_date",
        "form",
        "friendly_goals",
        "injury_level",
        "league_goals",
        "loyalty",
        "national_team_id",
        "national_team_name",
        "number",
        "salary",
        "stamina",
        "tsi",
        "owner",
        "owner_notes",
        "old_owner",
        "leadership",
        "mother_club_bonus"
    ]

    ret = []
    thediff = {}
    for key, elem in latest:
        thediff[key] = elem
    for key, elem in oldest:
        if key not in ignore_list and elem != thediff[key]:
            retstr = [teamname]
            retstr.append(oldest.first_name)
            retstr.append(oldest.last_name)
            retstr.append(key)
            retstr.append(elem)
            retstr.append(thediff[key])
            ret.append(retstr)

    return ret

# --------------------------------------------------------------------------------
# Talk to CHPP functions
# --------------------------------------------------------------------------------


def downloadMatches(teamid):
    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'])

    the_matches = chpp.matches_archive(ht_id=teamid, youth=False)

    for match in the_matches:
        dprint(2, "---------------")

        # TODO: get more details about the match like below
        # the_match = chpp.match(ht_id=match.ht_id)

        thedate = datetime(
            match.datetime.year,
            match.datetime.month,
            match.datetime.day,
            match.datetime.hour,
            match.datetime.minute)

        dprint(2, "Adding match ", match.ht_id, " to database.")

        dbmatch = (db.session.query(Match)
                   .filter_by(ht_id=match.ht_id)
                   .first())

        if dbmatch:
            dprint(1, "WARNING: This match already exists.")
        else:
            thismatch = {}
            thismatch['ht_id'] = match.ht_id
            thismatch['home_team_id'] = match.home_team_id
            thismatch['home_team_name'] = match.home_team_name
            thismatch['away_team_id'] = match.away_team_id
            thismatch['away_team_name'] = match.away_team_name
            thismatch['datetime'] = thedate
            thismatch['matchtype'] = match.type
            thismatch['context_id'] = match.context_id
            thismatch['rule_id'] = match.rule_id
            thismatch['cup_level'] = match.cup_level
            thismatch['cup_level_index'] = match.cup_level_index
            thismatch['home_goals'] = match.home_goals
            thismatch['away_goals'] = match.away_goals

            newmatch = Match(thismatch)
            db.session.add(newmatch)
            db.session.commit()

            matchlineup = chpp.match_lineup(ht_id=match.ht_id,
                                            team_id=teamid)
            for p in matchlineup.lineup_players:
                dprint(2, " - Adding ", p.first_name, " ",
                       p.last_name, " to database")
                thismatchlineup = {}
                thismatchlineup['match_id'] = match.ht_id
                thismatchlineup['player_id'] = p.ht_id
                thismatchlineup['datetime'] = thedate
                thismatchlineup['role_id'] = p.role_id
                thismatchlineup['first_name'] = p.first_name
                thismatchlineup['nick_name'] = p.nick_name
                thismatchlineup['last_name'] = p.last_name
                thismatchlineup['rating_stars'] = p.rating_stars
                thismatchlineup['rating_stars_eom'] = p.rating_stars_eom
                thismatchlineup['behaviour'] = p.behaviour

                newmatchlineup = MatchPlay(thismatchlineup)
                db.session.add(newmatchlineup)
                db.session.commit()


# --------------------------------------------------------------------------------
# Route functions
# --------------------------------------------------------------------------------


# @app.route('/')  # Registered manually in factory.py
# @app.route('/index')  # Registered manually in factory.py
def index():

    allusers = db.session.query(User).all()
    # time2m = date.today() - relativedelta(months=2)
    time1m = date.today() - relativedelta(months=1)
    activeusers = db.session.query(User).filter(User.last_usage > time1m).all()

    if ('current_user') not in session:
        return create_page(
            template='main.html',
            title='Home',
            usercount=len(allusers),
            activeusers=len(activeusers))

    all_teams = session['all_teams']
    all_team_names = session['all_team_names']
    updated = {}

    for i in range(len(all_teams)):
        updated[all_teams[i]] = all_team_names[i]

    dprint(2, updated)

    # changesplayers_week = []
    # changesteams = {}
    # changesteams_v2 = {}

    # for teamid in all_teams:

    #     changesplayers = []
    #     changesplayers_v2 = []

    #     # Of each of the players you ever have owned, get the last download
    #     players_data = (db.session.query(Players)
    #                     .filter_by(owner=teamid)
    #                     .order_by("data_date")
    #                     .all())
    #     newlst = {}
    #     for thislist in players_data:
    #         newlst[thislist.ht_id] = dict(iter(thislist))
    #     players_now = []
    #     for _k, val in newlst.items():
    #         players_now.append(val)

    #     for thisplayer in players_now:

    #         thischanges = player_diff(thisplayer['ht_id'], 7)
    #         thischanges_v2 = player_diff_v2(thisplayer['ht_id'], 7)
    #         if thischanges:
    #             changesplayers.append(thischanges)
    #             changesplayers_v2.append(thischanges_v2)
    #             dprint(2, thischanges)

    #     changesteams[teamid] = changesplayers
    #     changesteams_v2[teamid] = changesplayers_v2

    thisuserdata = (db.session.query(User)
                    .filter_by(ht_id=session['current_user_id'])
                    .first())
    thisuser = {
        'id': thisuserdata.ht_id,
        'name': thisuserdata.ht_user,
        'role': thisuserdata.role,
        'c_team': thisuserdata.c_team,
        'c_training': thisuserdata.c_training,
        'c_player': thisuserdata.c_player,
        'c_matches': thisuserdata.c_matches,
        'c_login': thisuserdata.c_login,
        'c_update': thisuserdata.c_update,
        'last_update': thisuserdata.last_update,
        'last_usage': thisuserdata.last_usage,
        'last_login': thisuserdata.last_login,
        'created': thisuserdata.created}

    dprint(2, thisuser)

    return create_page(
        template='main.html',
        title='Home',
        # changesteams=changesteams,
        # changesteams_v2=changesteams_v2,
        thisuser=thisuser,
        usercount=len(allusers),
        activeusers=len(activeusers),
        updated=updated)

# --------------------------------------------------------------------------------


# @app.route('/settings', methods=['GET', 'POST'])  # Registered manually in factory.py
def settings():
    error = ""
    if ('current_user') not in session:
        return render_template(
            '_forward.html',
            url='/')

    groupname = request.form.get('groupname')
    grouporder = request.form.get('grouporder')
    addgroup = request.form.get('addgroup')
    updategroup = request.form.get('updategroup')
    deletegroup = request.form.get('deletegroup')
    groupid = request.form.get('groupid')
    textcolor = request.form.get('textcolor')
    bgcolor = request.form.get('bgcolor')
    if not textcolor:
        textcolor = "#000000"
    if not bgcolor:
        bgcolor = "#FFFFFF"

    user = (db.session.query(User)
            .filter_by(ht_id=session['current_user_id'])
            .first())
    columns = User.getColumns(user)
    if len(columns) == 0:
        columns = defaultcolumns

    columnsorder = request.form.get('columnsorder')
    setcolumnsdefault = request.form.get('defaultcolumns')
    showdefaultcolumns = False
    if columnsorder and columnsorder != "empty":
        columns = []
        columngroups = columnsorder.split('Hidden columns')
        # Columns to show
        for r in columngroups[0].split('<div'):
            r = r.strip()
            if r == "":
                continue
            key = re.search('id="(.+?)"', r)
            text = re.search('>(.+?)</div>', r)
            if key:
                columns.append((text.group(1), key.group(1)))
        User.updateColumns(user, columns)
        db.session.commit()
    elif setcolumnsdefault == "defaultcolumns":
        columns = defaultcolumns
        showdefaultcolumns = True

    hiddencolumns = [item for item in allcolumns if item not in columns]

    if addgroup:
        if groupname and grouporder:
            newgroup = Group(
                user_id=session['current_user_id'],
                name=groupname,
                order=grouporder,
                textcolor=textcolor,
                bgcolor=bgcolor)
            db.session.add(newgroup)
            db.session.commit()
        else:
            error = "Groups need both name and order."

    elif updategroup and groupid:
        if groupname and grouporder:
            (db.session
             .query(Group)
             .filter_by(id=groupid)
             .update({"name": groupname,
                      "order": grouporder,
                      "textcolor": textcolor,
                      "bgcolor": bgcolor}))
            db.session.commit()
        else:
            error = "Groups need both name and order."

    elif deletegroup and groupid:
        try:
            thegroup = (db.session
                        .query(Group)
                        .filter_by(id=groupid)
                        .first())
            db.session.delete(thegroup)
            db.session.commit()
        except Exception:

            error = "The group wasn't empty, \
                removed all players from that group."
            db.session.rollback()

            # remove all connected players
            connections = (db.session.query(PlayerSetting)
                           .filter_by(group_id=groupid,
                                      user_id=session['current_user_id'])
                           .all())
            dprint(2, connections)

            for playersetting in connections:
                connection = (db.session
                              .query(PlayerSetting)
                              .filter_by(player_id=playersetting.player_id,
                                         user_id=session['current_user_id'])
                              .first())
                db.session.delete(connection)
                db.session.commit()

            thegroup = (db.session
                        .query(Group)
                        .filter_by(id=groupid)
                        .first())
            db.session.delete(thegroup)
            db.session.commit()

    group_data = (db.session.query(Group)
                  .filter_by(user_id=session['current_user_id'])
                  .order_by(Group.order)
                  .all())

    # Add a default group
    default_group = Group(
        user_id=0,
        name="<default>",
        order=default_group_order,
        textcolor="#000000",
        bgcolor="#FFFFFF")
    before_default = [g for g in group_data if g.order < default_group_order]
    after_default = [g for g in group_data if g.order >= default_group_order]
    before_default.append(default_group)

    group_data = before_default + after_default

    return create_page(
        template='settings.html',
        title='Settings',
        columns=columns,
        hiddencolumns=hiddencolumns,
        showdefaultcolumns=showdefaultcolumns,
        group_data=group_data,
        error=error)

# --------------------------------------------------------------------------------


# @app.route('/login', methods=['GET', 'POST'])  # Registered manually in factory.py
def login():

    # this comes from form
    username = request.form.get('username')
    password = request.form.get('password')
    # this comes from CHPP
    oauth_verifier = request.values.get('oauth_verifier')
    oa = oauth_verifier

    if not (oa) and not (username) and session.get('current_user') is None:
        return create_page(
            template='login.html',
            title='Login / Signup')

    # Initialize CHPP instance
    chpp = CHPP(consumer_key, consumer_secret)

    # if this returns a user, then the user already exists in database
    user = db.session.query(User).filter_by(username=username).first()

    if username and user:
        if check_password_hash(user.password, password):
            dprint(1, "Login success")
            # get stuff and add in session
            session['access_key'] = user.access_key
            session['access_secret'] = user.access_secret
            session['current_user'] = user.ht_user
            session['current_user_id'] = user.ht_id
        else:
            error = "Login failed"
            return create_page(
                template='login.html',
                title='Login / Signup',
                error=error)

    else:
        if not (oauth_verifier):
            # New user, connect to CHPP to be able to create user
            dprint(1, "New user, connect to CHPP to be able to create user")

            if len(password) < 8:
                # Password too short
                error = "Password too short"
                return create_page(
                    template='login.html',
                    title='Login / Signup',
                    error=error)

            auth = chpp.get_auth(callback_url=app.config['CALLBACK_URL'],
                                 scope="")
            # debug_print("login", "chpp.get_auth", auth._SOURCE_FILE)
            session['request_token'] = auth["request_token"]
            session['req_secret'] = auth["request_token_secret"]
            session['username'] = username
            session['password'] = generate_password_hash(password,
                                                         method='sha256')
            return render_template(
                '_forward.html',
                url=auth['url'])

        else:
            # New access permissions from Hattrick
            dprint(1, "New access permissions from Hattrick")
            access_token = chpp.get_access_token(
                           request_token=session['request_token'],
                           request_token_secret=session['req_secret'],
                           code=oauth_verifier)

            # debug_print(
            #     "login",
            #     "chpp.get_access_token",
            #     access_token._SOURCE_FILE)

            session['access_key'] = access_token['key']
            session['access_secret'] = access_token['secret']

            chpp = CHPP(consumer_key,
                        consumer_secret,
                        session['access_key'],
                        session['access_secret'])

            current_user = chpp.user()
            debug_print("login", "chpp.user", current_user._SOURCE_FILE)
            session['current_user'] = current_user.username
            session['current_user_id'] = current_user.ht_id

            # check if the user exists already in the database
            ht_id = (db.session.query(User)
                     .filter_by(ht_id=current_user.ht_id)
                     .first())

            if ht_id:
                # existing ht_id in db
                # then reassign the ownership
                dprint(1, "existing ht_id in db")
                User.claimUser(
                    ht_id,
                    username=session['username'],
                    password=session['password'],
                    access_key=session['access_key'],
                    access_secret=session['access_secret'])
                db.session.commit()

            else:
                # create new user with the form data.
                dprint(1, "create new user")
                new_user = User(
                    ht_id=current_user.ht_id,
                    ht_user=current_user.username,
                    username=session['username'],
                    password=session['password'],
                    access_key=access_token['key'],
                    access_secret=access_token['secret'])
                # add the new user to the database
                db.session.add(new_user)
                db.session.commit()

    dprint(1, "UserID: ", session['current_user_id'])

    chpp = CHPP(consumer_key,
                consumer_secret,
                session['access_key'],
                session['access_secret'])

    current_user = chpp.user()
    debug_print("login", "chpp.user", current_user._SOURCE_FILE)
    all_teams = current_user._teams_ht_id
    all_team_names = []
    for id in all_teams:
        all_team_names.append(chpp.team(ht_id=id).name)
    session['all_teams'] = all_teams
    session['all_team_names'] = all_team_names

    session['team_id'] = all_teams[0]

    return create_page(
        template='main.html',
        title='Logged in')

# --------------------------------------------------------------------------------


# @app.route('/logout')  # Registered manually in factory.py
def logout():
    print("LOGOUT FUNCTION CALLED - DEBUGGING")  # Force console output
    dprint(1, f"Logging out user: {session.get('current_user', 'Unknown')}")

    # Clear session first
    user_before = session.get('current_user', 'No user')
    session.clear()
    print(f"Session cleared for user: {user_before}")

    # Force explicit redirect
    print("Attempting redirect to /login")
    from flask import make_response
    response = make_response()
    response.status_code = 302
    response.headers['Location'] = '/login'
    return response

# --------------------------------------------------------------------------------


# @app.route('/update')  # Registered manually in factory.py
def update():
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

        # downloadMatches(teamid)

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

            thedate = datetime(
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

        # updated[teamid] = ['/player?id=' + str(teamid), 'players']
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

# --------------------------------------------------------------------------------


# @app.route('/debug', methods=['GET', 'POST'])  # Registered manually in factory.py
def admin():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/')

    error = ""

    try:
        user = (db.session.query(User)
                .filter_by(ht_id=session['current_user_id'])
                .first())
        role = User.getRole(user)
        if role != "Admin":
            return render_template(
                '_forward.html',
                url='/')
    except Exception:
        return render_template(
            '_forward.html',
            url='/')

    adminchecked = request.form.get('admin')
    userid = request.form.get('userid')

    dprint(2, "Checkbox: ", adminchecked)
    dprint(2, userid)

    if userid:
        try:
            user = (db.session.query(User)
                    .filter_by(ht_id=userid)
                    .first())
            updateto = "Admin" if adminchecked else "User"

            dprint(2, updateto)

            User.setRole(user, updateto)
            db.session.commit()

        except Exception:
            error = "couldn't change user"

    allusers = db.session.query(User).order_by(text('last_usage desc')).all()
    users = []
    for user in allusers:
        if (user.last_update - user.created).days < 1:
            active_time = "< 1 day"
        elif (user.last_update - user.created).days == 1:
            active_time = "1 day"
        elif diff_month(user.last_update, user.created) < 2:
            active_time = str((user.last_update - user.created).days) + " days"
        else:
            active_time = (str(diff_month(user.last_update, user.created)) +
                           " months")

        thisuser = {
            'id': user.ht_id,
            'name': user.ht_user,
            'role': user.role,
            'c_team': user.c_team,
            'c_training': user.c_training,
            'c_player': user.c_player,
            'c_matches': user.c_matches,
            'c_login': user.c_login,
            'c_update': user.c_update,
            'last_update': user.last_update,
            'last_usage': user.last_usage,
            'last_login': user.last_login,
            'created': user.created,
            'active_time': active_time}
        users.append(thisuser)

    return create_page(
        template='debug.html',
        title='Debug',
        users=users,
        error=error)

# --------------------------------------------------------------------------------


# @app.route('/team')  # Registered manually in factory.py
def team():
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

# --------------------------------------------------------------------------------


# @app.route('/player', methods=['GET', 'POST'])  # Registered manually in factory.py
def player():
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    updategroup = request.form.get('updategroup')
    playerid = request.form.get('playerid')
    groupid = request.form.get('groupid')

    teamid = request.values.get('id')

    teamid = int(teamid) if teamid else request.form.get('id')

    dprint(1, teamid)

    all_teams = session['all_teams']

    if teamid not in all_teams:
        error = "Wrong teamid, try the links."
        return create_page(
            template='player.html',
            title='Players',
            error=error)

    all_team_names = session['all_team_names']
    teamname = all_team_names[all_teams.index(teamid)]

    if updategroup and playerid and groupid:
        if int(groupid) < 0:
            theconnection = (db.session
                             .query(PlayerSetting)
                             .filter_by(player_id=playerid,
                                        user_id=session['current_user_id'])
                             .first())
            db.session.delete(theconnection)
            db.session.commit()
        else:
            connection = (db.session
                          .query(PlayerSetting)
                          .filter_by(player_id=playerid,
                                     user_id=session['current_user_id'])
                          .first())
            if connection:
                (db.session
                 .query(PlayerSetting)
                 .filter_by(player_id=playerid,
                            user_id=session['current_user_id'])
                 .update({"group_id": groupid}))
                db.session.commit()
            else:
                newconnection = PlayerSetting(
                    player_id=playerid,
                    user_id=session['current_user_id'],
                    group_id=groupid)
                db.session.add(newconnection)
                db.session.commit()

    group_data = (db.session.query(Group)
                  .filter_by(user_id=session['current_user_id'])
                  .order_by(Group.order)
                  .all())

    into_groups = (db.session
                   .query(PlayerSetting)
                   .filter_by(user_id=session['current_user_id'])
                   .all())

    # dprint(3, group_data)
    # dprint(3, into_groups)

    # Of each of the players you ever have owned, get the last download
    players_data = (db.session.query(Players)
                    .filter_by(owner=teamid)
                    .order_by(text("data_date"))
                    .order_by(text("number"))
                    .all())

    (allplayerids, allplayers, playernames) = get_training(players_data)

    newlst = {}
    for thislist in players_data:
        newlst[thislist.ht_id] = dict(iter(thislist))
    players_now = []
    for _k, val in newlst.items():
        players_now.append(val)

    # Of each of the players you ever have owned, get the first download
    players_data = (db.session.query(Players)
                    .filter_by(owner=teamid)
                    .order_by(text("data_date desc"))
                    .all())
    newlst = {}
    for thislist in players_data:
        newlst[thislist.ht_id] = dict(iter(thislist))
    players_oldest_dict = {}
    for _k, val in newlst.items():
        players_oldest_dict[val['ht_id']] = val

    # Add stars to the list of players
    for p in players_now:
        dbmatch = (db.session.query(MatchPlay)
                   .filter_by(player_id=p['ht_id'])
                   .order_by(text("rating_stars desc"))
                   .all())
        p['max_stars'] = "-"
        for m in dbmatch:
            if m.rating_stars is not None:
                p['max_stars'] = m.rating_stars
                p['max_stars_match_id'] = m.match_id
                break
        dbmatch = (db.session.query(MatchPlay)
                   .filter_by(player_id=p['ht_id'])
                   .order_by(text("datetime desc"))
                   .all())
        p['last_stars'] = "-"
        for m in dbmatch:
            if m.rating_stars is not None and m.rating_stars != 0:
                p['last_stars'] = m.rating_stars
                p['last_stars_match_id'] = m.match_id
                break

    # Get the columns
    user = (db.session.query(User)
            .filter_by(ht_id=session['current_user_id'])
            .first())
    columns = User.getColumns(user)
    if len(columns) == 0:
        columns = defaultcolumns

    # Calculate contributions
    for _x, c in columns:
        if c in calccolumns:
            for p in players_now:
                p[c] = calculateContribution(c, p)
                p['MMC'] = calculateManmark(p)

    for _x, c in columns:
        for p in players_now:
            bestposition = "-"
            bestval = 0
            for c in calccolumns:
                tmp = calculateContribution(c, p)
                if tmp > bestval:
                    bestposition = c
                    bestval = tmp
            p['bestposition'] = bestposition
            # Form multiplies to skills
            p['formfactor'] = round(math.pow(((p['form'] - 0.5) / 7), 0.45), 2)

    # Group the players into groups
    tmp_player = players_now
    grouped_players_now = {}
    for group in group_data:
        in_this_group = (
            [elem.player_id
             for elem in into_groups
             if elem.group_id == group.id])
        grouped_players_now[group.id] = (
            [player
             for player in tmp_player
             if player['ht_id'] in in_this_group])
        players_now = (
            [player
             for player in players_now
             if player['ht_id'] not in in_this_group])

    # Add a default group
    default_group = Group(
        user_id=0,
        name="",
        order=default_group_order,
        textcolor="#000000",
        bgcolor="#FFFFFF")
    before_default = [g for g in group_data if g.order < default_group_order]
    after_default = [g for g in group_data if g.order >= default_group_order]
    before_default.append(default_group)

    group_data = before_default + after_default

    grouped_players_now[default_group.id] = players_now

    return create_page(
        template='player.html',
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
        allplayers=allplayers,)

# --------------------------------------------------------------------------------


# @app.route('/matches', methods=['GET', 'POST'])  # Registered manually in factory.py
def matches():
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

# --------------------------------------------------------------------------------


# @app.route('/stats')  # Registered manually in factory.py
def stats():
    print("\n*** STATS ROUTE CALLED ***")
    if session.get('current_user') is None:
        return render_template(
            '_forward.html',
            url='/login')

    teamid = request.values.get('id')

    teamid = int(teamid) if teamid else request.form.get('id')
    print(f"*** STATS FOR TEAM ID: {teamid} ***")
    all_teams = session['all_teams']

    error = ""
    if teamid not in all_teams:
        error = "Wrong teamid, try the links."
        return create_page(
            template='stats.html',
            title='Stats')

    all_team_names = session['all_team_names']
    teamname = all_team_names[all_teams.index(teamid)]

    # Get all current players for the team
    current_players = (db.session.query(Players)
                       .filter_by(owner=teamid)
                       .order_by(Players.data_date.desc())
                       .all())

    # Filter to get the most recent data for each player
    latest_players = {}
    for player in current_players:
        if player.ht_id not in latest_players:
            latest_players[player.ht_id] = player

    current_players_list = list(latest_players.values())

    # Calculate team statistics
    team_stats = calculate_team_statistics(current_players_list)

    # Get top performers
    top_scorers = get_top_scorers(current_players_list)
    top_performers = get_top_performers(current_players_list)

    # Get match statistics for the team
    match_stats = get_team_match_statistics(teamid)

    # Get trophy data from CHPP
    trophies = []
    try:
        print(f"\n=== FETCHING TROPHY DATA FOR TEAM {teamid} ===")
        chpp = CHPP(consumer_key,
                    consumer_secret,
                    session['access_key'],
                    session['access_secret'])
        team_details = chpp.team(ht_id=teamid)

        print(f"Team details fetched: {team_details.name}")
        print(f"Team has trophies attribute: {hasattr(team_details, 'trophies')}")

        if hasattr(team_details, 'trophies'):
            print(f"Trophies object: {team_details.trophies}")
            print(f"Trophies type: {type(team_details.trophies)}")
            print(f"Trophies length: {len(team_details.trophies) if team_details.trophies else 0}")
            if team_details.trophies:
                print(f"Processing {len(team_details.trophies)} trophies")
                for i, trophy in enumerate(team_details.trophies):
                    print(f"Trophy {i}: {vars(trophy)}")
                    trophies.append({
                        'type_id': getattr(trophy, 'type_id', None),
                        'season': getattr(trophy, 'season', None),
                        'league_level': getattr(trophy, 'league_level', None),
                        'league_level_unit_name': getattr(trophy, 'league_level_unit_name', 'Unknown'),
                        'gained_date': getattr(trophy, 'gained_date', None),
                        'cup_league_level': getattr(trophy, 'cup_league_level', None)
                    })
            else:
                print("Trophies list is empty or None")
        else:
            print("No trophies attribute found on team object")
    except Exception as e:
        print(f"Error fetching trophies: {e}")
        import traceback
        print(traceback.format_exc())
        trophies = []

    print(f"=== TROPHY FETCH COMPLETE: {len(trophies)} trophies found ===\n")

    return create_page(
        template='stats.html',
        error=error,
        teamname=teamname,
        teamid=teamid,
        team_stats=team_stats,
        top_scorers=top_scorers,
        top_performers=top_performers,
        match_stats=match_stats,
        trophies=trophies,
        title='Stats')

# --------------------------------------------------------------------------------

def calculate_team_statistics(players):
    """Calculate comprehensive team statistics from current players"""
    if not players:
        return {}

    def safe_int(value):
        """Safely convert value to int, handling None and strings"""
        if value is None:
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def safe_float(value):
        """Safely convert value to float, handling None and strings"""
        if value is None:
            return 0.0
        try:
            if isinstance(value, str):
                # Handle comma-separated numbers and extract numeric part
                import re
                value_clean = value.replace(',', '')
                # Extract just the numeric part (e.g., "25.234" -> 25.234)
                match = re.search(r'\d+\.?\d*', value_clean)
                if match:
                    return float(match.group())
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    total_players = len(players)
    total_career_goals = sum(safe_int(p.career_goals) for p in players)
    total_team_goals = sum(safe_int(p.current_team_goals) for p in players)
    total_matches = sum(safe_int(p.current_team_matches) for p in players)
    total_league_goals = sum(safe_int(p.league_goals) for p in players)
    total_cup_goals = sum(safe_int(p.cup_goals) for p in players)
    total_friendly_goals = sum(safe_int(p.friendly_goals) for p in players)

    # Calculate average age
    avg_age = sum(safe_float(p.age) for p in players) / total_players if total_players > 0 else 0

    # Calculate average TSI (Total Skill Index)
    avg_tsi = sum(safe_int(p.tsi) for p in players) / total_players if total_players > 0 else 0

    # Calculate average salary
    avg_salary = sum(safe_int(p.salary) for p in players) / total_players if total_players > 0 else 0

    # Goals per match ratio
    goals_per_match = total_team_goals / total_matches if total_matches > 0 else 0

    return {
        'total_players': total_players,
        'total_career_goals': total_career_goals,
        'total_team_goals': total_team_goals,
        'total_matches': total_matches,
        'total_league_goals': total_league_goals,
        'total_cup_goals': total_cup_goals,
        'total_friendly_goals': total_friendly_goals,
        'avg_age': round(avg_age, 1),
        'avg_tsi': f"{int(avg_tsi):,}",
        'avg_wage': int(avg_salary),
        'goals_per_match': round(goals_per_match, 2)
    }

def get_top_scorers(players, limit=5):
    """Get top goal scorers from current players"""
    def safe_int(value):
        try:
            return int(value) if value else 0
        except (ValueError, TypeError):
            return 0

    scorers = [(f"{p.first_name} {p.last_name}", safe_int(p.current_team_goals), safe_int(p.current_team_matches))
               for p in players if safe_int(p.current_team_goals) > 0]
    scorers.sort(key=lambda x: x[1], reverse=True)
    return scorers[:limit]

def get_top_performers(players, limit=5):
    """Get top performers based on TSI"""
    def safe_int(value):
        try:
            return int(value) if value else 0
        except (ValueError, TypeError):
            return 0

    def safe_float(value):
        """Extract numeric value from age string"""
        if value is None:
            return 0.0
        try:
            if isinstance(value, str):
                # Handle age strings like "25.234" by extracting numeric part
                import re
                value_clean = value.replace(',', '')
                match = re.search(r'\d+\.?\d*', value_clean)
                if match:
                    return float(match.group())
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    performers = [(f"{p.first_name} {p.last_name}", f"{safe_int(p.tsi):,}", round(safe_float(p.age), 1))
                  for p in players if safe_int(p.tsi) > 0]
    performers.sort(key=lambda x: int(x[1].replace(',', '')), reverse=True)
    return performers[:limit]

def get_team_match_statistics(teamid):
    """Get team's match statistics from Match and MatchPlay tables"""
    try:
        # Get recent matches for the team
        matches = (db.session.query(Match)
                   .filter_by(home_team_id=teamid)
                   .order_by(Match.datetime.desc())
                   .limit(10)
                   .all())

        if not matches:
            # Try as away team
            matches = (db.session.query(Match)
                       .filter_by(away_team_id=teamid)
                       .order_by(Match.datetime.desc())
                       .limit(10)
                       .all())

        wins = losses = draws = 0
        goals_for = goals_against = 0

        for match in matches:
            if match.home_team_id == teamid:
                goals_for += match.home_goals or 0
                goals_against += match.away_goals or 0
                if match.home_goals > match.away_goals:
                    wins += 1
                elif match.home_goals < match.away_goals:
                    losses += 1
                else:
                    draws += 1
            else:
                goals_for += match.away_goals or 0
                goals_against += match.home_goals or 0
                if match.away_goals > match.home_goals:
                    wins += 1
                elif match.away_goals < match.home_goals:
                    losses += 1
                else:
                    draws += 1

        return {
            'total_matches': len(matches),
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'goals_for': goals_for,
            'goals_against': goals_against,
            'goal_difference': goals_for - goals_against,
            'win_percentage': round(wins / len(matches) * 100, 1) if matches else 0
        }
    except Exception as e:
        dprint(1, f"Error getting match statistics: {e}")
        return {
            'total_matches': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'goals_for': 0,
            'goals_against': 0,
            'goal_difference': 0,
            'win_percentage': 0
        }

# --------------------------------------------------------------------------------


# @app.route('/training')  # Registered manually in factory.py
def training():
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
            template='training.html',
            title='Training')

    all_team_names = session['all_team_names']
    teamname = all_team_names[all_teams.index(teamid)]

    # Get all players you have ever owned
    players_data = (db.session.query(Players)
                    .filter_by(owner=teamid)
                    .order_by(text("data_date"))
                    .order_by(text("ht_id"))
                    .all())

    allplayerids = []
    allplayers = {}
    playernames = {}
    for entry in players_data:
        allplayers[entry.ht_id] = []
        if entry.number == 100:
            playernames[entry.ht_id] = entry.first_name + " " + entry.last_name
        else:
            playernames[entry.ht_id] = str(entry.number) + ". " + \
                entry.first_name + " " + entry.last_name
        if entry.ht_id not in allplayerids:
            allplayerids.append(entry.ht_id)

    for player in players_data:
        allplayers[player.ht_id].append(
            [
                datetime.date(player.data_date),
                (
                    player.keeper,
                    player.defender,
                    player.playmaker,
                    player.winger,
                    player.passing,
                    player.scorer,
                    player.set_pieces
                )
            ])

    increases = {}
    for i in allplayers:
        increases[i] = \
            allplayers[i][len(allplayers[i])-1][1][0] - \
            allplayers[i][0][1][0]
        for s in range(6):
            increases[i] = increases[i] + \
                allplayers[i][len(allplayers[i])-1][1][s] - \
                allplayers[i][0][1][s]

    # Sort player list based on increases
    allplayerids = sorted(
        allplayerids,
        key=lambda ele: increases[ele],
        reverse=True)

    for i in allplayers:
        # Date filler
        (firstdate, previousskill) = allplayers[i][0]
        (lastdate, x) = allplayers[i][len(allplayers[i])-1]

        friday = firstdate - \
            timedelta(days=firstdate.weekday()) + timedelta(days=4, weeks=-1)

        date_modified = friday
        datelist = [friday]

        while date_modified < lastdate:
            date_modified += timedelta(days=1)
            datelist.append(date_modified)

        newy = []
        for d in datelist:
            for (da, y) in allplayers[i]:
                if (d == da):
                    previousskill = y
            newy.append([d, previousskill])

        # Just take every 7th
        weekly = newy[0::7]
        # add the last day if it's not the last day already
        (lastweekday, x) = weekly[len(weekly)-1]
        if lastdate != lastweekday:
            weekly.append(allplayers[i][len(allplayers[i])-1])

        allplayers[i] = weekly

    # Deduplicate consecutive rows with identical skill values
    for player_id in allplayers:
        deduped = []
        prev_skills = None
        for entry in allplayers[player_id]:
            date, skills = entry
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
        for i, (date, skills) in enumerate(reversed(player_data)):
            if i == len(player_data) - 1:
                # Oldest row has no previous to compare with
                changes = [0] * 7
            else:
                # Compare current skills with chronologically older skills
                older_date, older_skills = list(reversed(player_data))[i+1]
                # Positive change = improvement (show green ↑)
                changes = [skills[j] - older_skills[j] for j in range(7)]
            skill_changes[player_id].append((date, skills, changes))

    return create_page(
        template='training.html',
        teamname=teamname,
        error=error,
        skills=tracecolumns,
        teamid=teamid,
        increases=increases,
        playernames=playernames,
        allplayerids=allplayerids,
        allplayers=allplayers,
        skill_changes=skill_changes,
        title='Training')
