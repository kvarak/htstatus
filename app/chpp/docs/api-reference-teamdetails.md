# CHPP API Reference: Team Details

> **Source**: Hattrick CHPP Documentation (retrieved 2026-01-26)
> **Purpose**: Complete API specification for teamdetails endpoint used by custom CHPP client
> **Usage**: Reference for implementing INFRA-028 data parity fixes and debugging parsers

## Overview

The teamdetails endpoint returns comprehensive team information including owner details, league status, power ratings, cup information, trophies, and other team metadata.

## Input Parameters

### Required
- `file = teamdetails`

### One Required (either/or)
- `teamID` (unsigned Integer) - What team to show data for. Default: Your senior teamID
- `userID` (unsigned Integer) - What team/user to show data for. Default: Your userID if teamID not set

### Optional
- `version` (string) - API version
- `includeDomesticFlags` (Boolean, Default: false) - Include team's own country in flag collections
- `includeFlags` (Boolean, Default: false) - Include flag collection
- `includeSupporters` (Boolean, Default: false) - Include supported teams and supporters

**Note**: teamID and userID generate same result, except ownerless teams require teamID, users without teams require userID.

## Output Structure

```xml
HattrickData
    ├── User (Container for team owner data)
    │   ├── UserID (unsigned Integer) - Globally unique UserID (0 for ownerless teams)
    │   ├── Language
    │   │   ├── LanguageID (unsigned Integer) - Globally unique LanguageID
    │   │   └── LanguageName (String) - Language name
    │   ├── SupporterTier (supporterTier) - Hattrick Supporter level (empty if not supporter)
    │   ├── Loginname (String) - Username/nickname (not supplied if ownerless)
    │   ├── Name (String) - Personal name or 'HIDDEN' (not supplied if ownerless)
    │   ├── ICQ (unsigned Integer) - ICQ number if any (not supplied if ownerless)
    │   ├── SignupDate (DateTime) - User signup date (not supplied if ownerless)
    │   ├── ActivationDate (DateTime) - When user gained team control (not supplied if ownerless)
    │   ├── LastLoginDate (DateTime) - Last login (not supplied if ownerless)
    │   ├── HasManagerLicense (Boolean) - Whether user has manager license
    │   └── NationalTeams
    │       └── NationalTeam
    │           ├── NationalTeamStaffType (NationalTeamStaffType) - Position in national team
    │           ├── NationalTeamID (unsigned Integer) - Globally unique identifier
    │           └── NationalTeamName (String) - National team name
    └── Teams
        └── Team (Not supplied for users without team)
            ├── TeamID (unsigned Integer) - Globally unique TeamID
            ├── TeamName (String) - Full team name
            ├── ShortTeamName (String) - Short team name
            ├── IsPrimaryClub (Boolean) - If this is user's primary team
            ├── FoundedDate (DateTime) - Club founding date
            ├── IsDeactivated (Boolean) - Whether team is deactivated from league
            ├── Arena
            │   ├── ArenaID (unsigned Integer) - Globally unique ArenaID
            │   └── ArenaName (String) - Arena name
            ├── League
            │   ├── LeagueID (unsigned Integer) - Globally unique LeagueID
            │   └── LeagueName (String) - League name
            ├── Country
            │   ├── CountryID (unsigned Integer) - Globally unique CountryID
            │   └── CountryName (String) - Country name
            ├── Region
            │   ├── RegionID (unsigned Integer) - Globally unique RegionID
            │   └── RegionName (String) - Region name
            ├── Trainer
            │   └── PlayerID (unsigned Integer) - Player who is team trainer/coach
            ├── HomePage (URI) - Team's home page URL
            ├── Cup (Empty if team playing match)
            │   ├── StillInCup (Boolean) - If team still in cup
            │   ├── CupID (unsigned Integer) - Globally unique CupID (only if still in cup)
            │   ├── CupName (String) - Cup name (only if still in cup)
            │   ├── CupLeagueLevel (unsigned Integer) - 0=National(1-6), 7-9=Divisional (only if still in cup)
            │   ├── CupLevel (unsigned Integer) - 1=National/Divisional, 2=Challenger, 3=Consolation (only if still in cup)
            │   ├── CupLevelIndex (unsigned Integer) - Always 1 for National/Consolation, Challenger: 1=Emerald, 2=Ruby, 3=Sapphire (only if still in cup)
            │   ├── MatchRound (unsigned Integer) - Next/current round (only if still in cup)
            │   └── MatchRoundsLeft (unsigned Integer) - Remaining rounds (only if still in cup)
            ├── PowerRating ⭐ CRITICAL FOR INFRA-028
            │   ├── GlobalRanking (unsigned Integer) - Global power rating rank
            │   ├── LeagueRanking (unsigned Integer) - League power rating rank
            │   ├── RegionRanking (unsigned Integer) - Regional power rating rank
            │   └── PowerRating (unsigned Integer) - Team's power rating value
            ├── FriendlyTeamID (unsigned Integer) - Booked friendly opponent teamID (0 if none, empty if playing match)
            ├── LeagueLevelUnit (Empty if league playing qualification)
            │   ├── LeagueLevelUnitID (unsigned Integer) - Globally unique LeagueLevelUnitID
            │   ├── LeagueLevelUnitName (String) - Series name
            │   └── LeagueLevel (unsigned Integer) - Relative level (1=top series) ⭐ CRITICAL FOR INFRA-028
            ├── NumberOfVictories (unsigned Integer) - Current winning streak (≥2 matches, empty if playing)
            ├── NumberOfUndefeated (unsigned Integer) - Current undefeated streak (≥2 matches, empty if playing)
            ├── Fanclub
            │   ├── FanclubID (unsigned Integer) - Globally unique FanclubID
            │   ├── FanclubName (String) - Fanclub name
            │   └── FanclubSize (unsigned Integer) - Number of fanclub members
            ├── LogoURL (URI) - Team logo URL ⭐ CRITICAL FOR INFRA-028
            ├── Guestbook (Only shown if user has supporter)
            │   └── NumberOfGuestbookItems (unsigned Integer) - Number of guestbook postings
            ├── PressAnnouncement (Only shown if user has supporter)
            │   ├── Subject (String) - Press announcement subject
            │   ├── Body (String) - Press announcement body
            │   └── SendDate (DateTime) - When press announcement was submitted
            ├── TeamColors (Only shown if user has supporter, empty if no theme set)
            │   ├── BackgroundColor (String) - Club theme background color
            │   └── Color (String) - Matching text color to background
            ├── DressURI (URI) - Team kit image URI
            ├── DressAlternateURI (URI) - Alternate team kit image URI
            ├── BotStatus
            │   ├── IsBot (Boolean) - Whether team is currently a bot
            │   └── BotSince (DateTime) - When team became bot (only if IsBot=true)
            ├── TeamRank (unsigned Integer) - League rank based on level/position (empty if playing match)
            ├── YouthTeamID (unsigned Integer) - Youth academy ID (0 if none)
            ├── YouthTeamName (String) - Youth academy name (empty if none)
            ├── NumberOfVisits (unsigned Integer) - Team visits in latest day with visits
            ├── Flags (Acquired team flags)
            │   ├── HomeFlags
            │   │   └── Flag
            │   │       ├── LeagueID (unsigned Integer) - League a flag belongs to
            │   │       ├── LeagueName (String) - League name for flag
            │   │       └── CountryCode (String) - Country code for flag
            │   └── AwayFlags
            │       └── Flag
            │           ├── LeagueID (unsigned Integer) - League a flag belongs to
            │           ├── LeagueName (String) - League name for flag
            │           └── CountryCode (String) - Country code for flag
            ├── TrophyList (Empty if no trophies)
            │   └── Trophy (May be several elements)
            │       ├── TrophyTypeId (trophyID) - Type ID for trophy
            │       ├── TrophySeason (unsigned Integer) - Season trophy was won
            │       ├── LeagueLevel (unsigned Integer) - League level won (tournaments: acts as type)
            │       ├── LeagueLevelUnitId (String) - LeagueLevelUnit ID won (tournaments: tournament ID)
            │       ├── LeagueLevelUnitName (String) - LeagueLevelUnit name won (tournaments: tournament name)
            │       ├── GainedDate (DateTime) - Date trophy was gained
            │       ├── ImageUrl (URI) - Trophy image URL
            │       ├── CupLeagueLevel (unsigned Integer) - Cup league level, 0=main cups, 1-6=division (empty if not cup)
            │       ├── CupLevel (CupLevel) - Cup level (empty if not cup trophy)
            │       └── CupLevelIndex (CupLevelIndex) - Challenger cup type, 1=National/Consolation (empty if not cup)
            ├── SupportedTeams (Only if includeSupporters=true, empty if no supporters)
            │   └── SupportedTeam
            │       ├── UserId (unsigned Integer) - Supported team owner's UserID
            │       ├── LoginName (String) - Supported team owner's username
            │       ├── TeamId (unsigned Integer) - Supported team's TeamID
            │       ├── TeamName (String) - Supported team name
            │       ├── LeagueID (unsigned Integer) - Supported team's LeagueID
            │       ├── LeagueName (String) - Supported team's league name
            │       ├── LeagueLevelUnitID (unsigned Integer) - Supported team's series ID
            │       ├── LeagueLevelUnitName (String) - Supported team's series name
            │       ├── LastMatch
            │       │   ├── LastMatchId (unsigned Integer) - Globally unique match ID
            │       │   ├── LastMatchDate (DateTime) - Last match date
            │       │   ├── LastMatchHomeTeamId (unsigned Integer) - Home team ID
            │       │   ├── LastMatchHomeTeamName (String) - Home team name
            │       │   ├── LastMatchHomeGoals (unsigned Integer) - Home team goals
            │       │   ├── LastMatchAwayTeamId (unsigned Integer) - Away team ID
            │       │   ├── LastMatchAwayTeamName (String) - Away team name
            │       │   └── LastMatchAwayGoals (unsigned Integer) - Away team goals
            │       ├── NextMatch
            │       │   ├── NextMatchId (unsigned Integer) - Globally unique match ID
            │       │   ├── NextMatchDate (DateTime) - Next match date
            │       │   ├── NextMatchHomeTeamId (unsigned Integer) - Home team ID
            │       │   ├── NextMatchHomeTeamName (String) - Home team name
            │       │   ├── NextMatchAwayTeamId (unsigned Integer) - Away team ID
            │       │   └── NextMatchAwayTeamName (String) - Away team name
            │       └── PressAnnouncement
            │           ├── PressAnnouncementSendDate (DateTime) - When announcement was sent
            │           ├── PressAnnouncementSubject (String) - Announcement subject
            │           └── PressAnnouncementBody (String) - Announcement body
            ├── MySupporters (Only if includeSupporters=true, empty if no supporters)
            │   └── SupporterTeam
            │       ├── UserId (unsigned Integer) - Supporter team owner's UserID
            │       ├── LoginName (String) - Supporter team owner's username
            │       ├── TeamId (unsigned Integer) - Supporter team's TeamID
            │       ├── TeamName (String) - Supporter team name
            │       ├── LeagueID (unsigned Integer) - Supporter team's LeagueID
            │       ├── LeagueName (String) - Supporter team's league name
            │       ├── LeagueLevelUnitID (unsigned Integer) - Supporter team's series ID
            │       └── LeagueLevelUnitName (String) - Supporter team's series name
            ├── PossibleToChallengeMidweek (Boolean) - If team can be challenged for mid-week friendly
            └── PossibleToChallengeWeekend (Boolean) - If team can be challenged for weekend friendly
```

## Critical Fields for INFRA-028 Data Parity

### Missing in Custom CHPP (High Priority)
1. **LogoURL** - Team logo URL (explains missing team logos)
2. **PowerRating container** - GlobalRanking, LeagueRanking, RegionRanking, PowerRating values
3. **LeagueLevelUnit/LeagueLevel** - Proper league level information (explains "None" displays)
4. **Cup information** - CupName, CupLevel, StillInCup status
5. **NumberOfVictories/NumberOfUndefeated** - Team streaks

### Available but May Need Verification
1. **DressURI/DressAlternateURI** - Team kit images (should already work)
2. **Arena information** - ArenaID, ArenaName
3. **Fanclub data** - FanclubName, FanclubSize
4. **Region information** - RegionID, RegionName

### Supporter-Only Features (Lower Priority)
1. **TeamColors** - Background/text colors for themes
2. **PressAnnouncement** - Press release information
3. **Guestbook** - Guestbook statistics

## Parser Implementation Notes

### Current CHPPTeam Model Gaps
```python
# Missing fields to add to CHPPTeam dataclass:
logo_url: str | None = None
power_rating: int | None = None
power_rating_global_ranking: int | None = None
power_rating_league_ranking: int | None = None
power_rating_region_ranking: int | None = None
league_level: int | None = None
league_level_unit_id: int | None = None
league_level_unit_name: str | None = None
cup_name: str | None = None
cup_level: int | None = None
still_in_cup: bool = False
number_of_victories: int | None = None
number_of_undefeated: int | None = None
arena_id: int | None = None
arena_name: str | None = None
```

### Parser Updates Required
```python
# In app/chpp/parsers.py parse_team() function:
logo_url = safe_find_text(root, ".//LogoURL")
power_rating = safe_find_int(root, ".//PowerRating/PowerRating", None)
power_rating_global_ranking = safe_find_int(root, ".//PowerRating/GlobalRanking", None)
power_rating_league_ranking = safe_find_int(root, ".//PowerRating/LeagueRanking", None)
league_level = safe_find_int(root, ".//LeagueLevelUnit/LeagueLevel", None)
cup_name = safe_find_text(root, ".//Cup/CupName")
still_in_cup = safe_find_bool(root, ".//Cup/StillInCup", False)
arena_id = safe_find_int(root, ".//Arena/ArenaID", None)
arena_name = safe_find_text(root, ".//Arena/ArenaName")
```

## Template Integration for INFRA-028

### Stats Template Updates
```html
<!-- Team logo display -->
{% if competition_info and competition_info.logo_url %}
<div class="col-md-4">
  <p><strong>Team Logo</strong></p>
  <img src="{{ competition_info.logo_url }}" alt="Team Logo" class="img-fluid" style="max-height: 80px;">
</div>
{% endif %}

<!-- Power rating section -->
{% if competition_info and competition_info.power_rating %}
<div class="card border-warning">
  <div class="card-body">
    <h6 class="card-title">📊 Power Rating</h6>
    <p class="card-text">
      <strong>Rating:</strong> {{ competition_info.power_rating }}<br>
      {% if competition_info.power_rating_global_ranking %}
      <strong>Global Rank:</strong> #{{ competition_info.power_rating_global_ranking }}<br>
      {% endif %}
      {% if competition_info.power_rating_league_ranking %}
      <strong>League Rank:</strong> #{{ competition_info.power_rating_league_ranking }}<br>
      {% endif %}
    </p>
  </div>
</div>
{% endif %}

<!-- League information -->
{% if competition_info.league_level %}
<strong>Level:</strong> {{ competition_info.league_level }}<br>
{% endif %}
```

## Version Compatibility
- Current implementation uses version 3.6 in custom CHPP client
- All critical fields available in version 3.6+
- PowerRating container available since early API versions
- LogoURL available since team customization features added

## Usage in HTStatus
- **Primary endpoint** for team information in stats page
- **Data source** for competition_info object in matches blueprint
- **Foundation** for team context throughout application
- **Integration point** with managercompendium data for complete user context

## Related Files
- `app/chpp/parsers.py` - `parse_team()` function (needs INFRA-028 updates)
- `app/chpp/models.py` - `CHPPTeam` data model (needs field additions)
- `app/blueprints/matches.py` - stats() route (competition_info extraction)
- `app/templates/stats.html` - Display template (logo, power rating sections)