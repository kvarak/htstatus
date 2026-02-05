# CHPP API Reference Documentation

## Overview

This directory contains comprehensive documentation for Hattrick Community Premier Program (CHPP) APIs used by HattrickPlanner. The CHPP provides official access to Hattrick data through XML APIs with OAuth authentication.

## Important CHPP Developer Guidelines

**⚠️ CRITICAL**: As a CHPP developer you may ONLY access interfaces documented here, nothing else. It's strictly forbidden to develop products that work with any other part of the site. Violation of these rules might render you to lose your team.

## Documentation Status

### ✅ Documented APIs (21/79 total)
These APIs have comprehensive documentation with implementation examples, authentication patterns, and strategic usage guidelines:

- **[avatars](api-reference-avatars.md)** - Avatars for all players of user's team
- **[club](api-reference-club.md)** - Information about specialists and youth
- **[currentbids](api-reference-currentbids.md)** - Shows the current transfer activity for a team
- **[economy](api-reference-economy.md)** - Economy information
- **[fans](api-reference-fans.md)** - Fanclub information
- **[leaguedetails](api-reference-leaguedetails.md)** - Information about a League Level Unit (series)
- **[leaguefixtures](api-reference-leaguefixtures.md)** - Fixtures for a League Level Unit (series)
- **[leaguelevels](api-reference-leaguelevels.md)** - League structure information including division levels, promotion/demotion slots, and series organization
- **[managercompendium](api-reference-managercompendium.md)** - The manager compendium of the logged in user
- **[matches-basic](api-reference-matches-basic.md)** - The most recent and upcoming matches for a particular team
- **[matchdetails](api-reference-matchdetails.md)** - Detailed match information including statistics, events, possession, and analytics
- **[matchesarchive](api-reference-matchesarchive.md)** - Matches Archive
- **[matchlineup](api-reference-matchlineup.md)** - Detailed lineup information for finished matches including starting lineup, substitutions, and player ratings
- **[matchorders](api-reference-matchorders.md)** - Match orders for upcoming matches
- **[playerdetails](api-reference-playerdetails.md)** - Detailed information for a player
- **[playerevents](api-reference-playerevents.md)** - Individual player event history including goals, assists, cards, injuries, and career milestones
- **[players](api-reference-players.md)** - Players roster information
- **[staffavatars](api-reference-staffavatars.md)** - Avatars for all staff members
- **[stafflist](api-reference-stafflist.md)** - A list of all staff members
- **[teamdetails](api-reference-teamdetails.md)** - Team information
- **[training](api-reference-training.md)** - Training information
- **[translations](api-reference-translations.md)** - Translations for the denominations in the game

### 🔮 Available But Not Yet Documented (58/79 remaining)
These APIs are available on request for future features:

#### Core Team Management
- **achievements** - The achievements of a specific user
- **arenadetails** - Information about specific arenas, supporter statistics and the largest arenas
- **bookmarks** - User bookmarks
- **challenges** - Challenges system
- **hofplayers** - Hall of Fame Players
- **supporters** - Information about teams supported and teams supporting

#### Match & Competition Data
- **cupmatches** - Information about cup matches
- **live** - Get (live) match ticker
- **trainingevents** - Get training events for a player

#### League & Tournament System
- **ladderdetails** - Information about teams in the ladder and positions in it
- **ladderlist** - Information about ladder that the user is currently playing in
- **tournamentdetails** - Information about a tournament
- **tournamentfixtures** - Information about matches for a tournament
- **tournamentleaguetables** - League tables for a tournament
- **tournamentlist** - Information about tournaments that the user is currently playing in

#### Transfer Market
- **transfersearch** - Search the transfer market (manual user request only)
- **transfersteam** - Get the transfer history of a team
- **transfersplayer** - Get all transfers of a player

#### National Teams & International
- **nationalteams** - National teams
- **nationalteamdetails** - National Team information
- **nationalteammatches** - National team matches
- **nationalplayers** - National team players
- **worldcup** - World cup groups and matches
- **worlddetails** - General Information about all countries in HT World
- **worldlanguages** - Available languages

#### Youth System
- **youthavatars** - Avatars for all players of user's youthteam
- **youthleaguedetails** - The youth league information
- **youthleaguefixtures** - Fixtures for a Youth League (series)
- **youthplayerdetails** - Detailed information for a youth player
- **youthplayerlist** - Youth Players
- **youthteamdetails** - Youth team information

#### Alliance/Federation System
- **alliances** - Alliance / Federation search
- **alliancedetails** - Alliance / Federation information

#### Utility APIs
- **regiondetails** - Detailed information about a region
- **search** - Search functionality

## CHPP System Information

### Standard Response Structure
The output container 'HattrickData' always contains:

| Element | Description |
|---------|-------------|
| FileName | The name of the file that your request was sent to |
| Version | The delivered version of the XML output |
| UserID | The logged on User's UserID (not TeamID). Defaults to 0 if not logged on |
| FetchedDate | Date and time when the XML file was fetched (DateTime format) |

### Error Handling
Any internal error is caught and returns XML with error information instead of requested file.

#### Common Error Codes
| Code | Description |
|------|-------------|
| 0 | Not logged in |
| 1 | Access Denied |
| 2 | File Not Specified |
| 3 | File not supported |
| 6 | Only for Supporters |
| 7 | Not supported version |
| 10 | Invalid parameter |
| 50 | Unknown TeamID |
| 51 | Unknown MatchID |
| 56 | Unknown PlayerID |
| 57 | Unknown LeagueID |
| 58 | Unknown LeagueLevelUnitID |
| 59 | This request is only allowed for teams owned by the requesting user |
| 90 | Hattrick is down for maintenance |
| 99 | Other undefined error |

### Testing Support
For testing purposes, you can override supporter status with `overrideIsSupporter=X`:
- X=-1: Off
- X=0: Silver
- X=1: Gold
- X=2: Platinum
- X=3: Diamond

*Note: Does not work for 'teamdetails' file*

## World Cup Tournament IDs
The new World Cup format (after January 2021) uses the Tournament system:

| Cup | Tournament ID |
|-----|---------------|
| U21 Europe Cup | 4878483 |
| U21 America Cup | 4878490 |
| U21 Africa Cup | 4878492 |
| U21 Asia-Oceania Cup | 4878493 |
| U21 Wildcard Rounds | 4891573 |
| U21 World Cup | 4892549 |
| U21 Nations Cup | 4892615 |
| U21 Friendlies | 4894807 |

## Recent CHPP Changelog
- **2025-09-17**: tournamentfixtures v1.1 - Added Input: matchRound
- **2025-02-25**: Major updates to players and playerdetails APIs
- **2024-09-16**: Updates to teamdetails
- **2024-08-26**: New leaguelevels API added
- **2023-09-07**: Multiple API updates across players, playerdetails, staffavatars, stafflist

## Implementation Guidelines for HattrickPlanner

### Authentication Pattern
```python
from app.chpp import CHPP

chpp = CHPP(
    consumer_key=config.CONSUMER_KEY,
    consumer_secret=config.CONSUMER_SECRETS,
    access_key=session['access_key'],
    access_secret=session['access_secret']
)
```

### Rate Limiting & Performance
**CHPP API calls are EXPENSIVE and RATE-LIMITED**. Only call CHPP APIs for:
1. Login/Authentication - Initial OAuth flow and user/team data fetch
2. Explicit "Update Data" actions - When user clicks "Update" to sync with Hattrick

**Never call CHPP APIs for**:
- Page navigation or view-only operations
- Form submissions (use session data)
- Quick user interactions (voting, commenting)

### Strategic Usage Guidelines
Each documented API includes specific guidance on:
- **Primary Use Cases**: Main HattrickPlanner features supported
- **Data Refresh Strategy**: When and how often to fetch data
- **Session Integration**: How to combine with Flask session data
- **Performance Considerations**: Optimization patterns for hobby project context

### Security Requirements
- OAuth tokens stored in Flask sessions
- Never commit CHPP credentials to version control
- Use environment variables for API configuration
- Validate user ownership for team-specific data requests

## Contributing

When adding new API documentation:

1. Follow the established format pattern from existing docs
2. Include comprehensive implementation examples
3. Document strategic usage guidelines for HattrickPlanner features
4. Update this README to move the API from "Available" to "Documented"
5. Link to specific HattrickPlanner features that benefit from the API

## Resources

- [Official CHPP Documentation](http://hattrick.org/goto.ashx?path=/Help/Rules/CHPP.aspx)
- [HattrickPlanner Technical Documentation](../../TECHNICAL.md)
- [OAuth Implementation Guide](../CHPP-ENFORCEMENT.md)
