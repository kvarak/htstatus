# CHPP API Reference: Manager Compendium

> **Source**: Hattrick CHPP Documentation (retrieved 2026-01-26)
> **Purpose**: Complete API specification for managercompendium endpoint used by custom CHPP client
> **Usage**: Reference for implementing/debugging custom CHPP parsers and data models

## Overview

The manager compendium endpoint returns comprehensive information about the logged-in user including teams, league info, and personal details.

## Input Parameters

### Required
- `file = managercompendium`

### Optional
- `version` (string) - API version
- `userId` (unsigned Integer) - Default: Your userId. What user to show the data for.

## Output Structure

```xml
HattrickData
    ├── Manager
    │   ├── UserId (unsigned Integer) - The globally unique UserID
    │   ├── Loginname (String) - The 'username' or 'nickname' used in Forums and around the site
    │   ├── SupporterTier (String) - Current Hattrick Supporter level. Empty if not a Supporter
    │   ├── LastLogins
    │   │   └── LoginTime (String) - Repeater with Login Time information
    │   ├── Language
    │   │   ├── LanguageId (unsigned Integer) - The globally unique LanguageID
    │   │   └── LanguageName (String) - The language name
    │   ├── Country
    │   │   ├── CountryId (unsigned Integer) - The globally unique CountryID
    │   │   └── CountryName (String) - The country name
    │   ├── Currency
    │   │   ├── CurrencyName (String) - The name of the currency
    │   │   └── CurrencyRate (Decimal) - Relative currency rate to SEK (swedish krona)
    │   ├── Teams
    │   │   └── Team (Container for each team)
    │   │       ├── TeamId (unsigned Integer) - The globally unique TeamID
    │   │       ├── TeamName (String) - The full team name
    │   │       ├── Arena
    │   │       │   ├── ArenaId (unsigned Integer) - The globally unique ArenaID
    │   │       │   └── ArenaName (String) - The arena name
    │   │       ├── League
    │   │       │   ├── LeagueId (unsigned Integer) - The globally unique LeagueID
    │   │       │   ├── LeagueName (String) - The League name
    │   │       │   └── Season (unsigned Integer) - The Current Season
    │   │       ├── Country
    │   │       │   ├── CountryId (unsigned Integer) - The globally unique CountryId
    │   │       │   └── CountryName (String) - The Country name
    │   │       ├── LeagueLevelUnit ('series')
    │   │       │   ├── LeagueLevelUnitId (unsigned Integer) - The globally unique LeagueLevelUnitID
    │   │       │   └── LeagueLevelUnitName (String) - The name of the LeagueLevelUnit
    │   │       ├── Region
    │   │       │   ├── RegionId (unsigned Integer) - The globally unique RegionID
    │   │       │   └── RegionName (String) - The Region name
    │   │       └── YouthTeam
    │   │           ├── YouthTeamId (unsigned Integer) - Youth academy ID (if exists)
    │   │           ├── YouthTeamName (String) - Youth academy team name (if exists)
    │   │           └── YouthLeague
    │   │               ├── YouthLeagueId (unsigned Integer) - The globally unique YouthLeagueID
    │   │               └── YouthLeagueName (String) - The name of the youth league
    │   ├── NationalTeamCoach (Empty if user is not a national team coach)
    │   │   └── NationalTeam
    │   │       ├── NationalTeamId (unsigned Integer) - The globally unique NationalTeamID
    │   │       └── NationalTeamName (String) - The name of the national team
    │   ├── NationalTeamAssistant (Empty if user is not assistant coach)
    │   │   └── NationalTeam
    │   │       ├── NationalTeamId (unsigned Integer) - The globally unique NationalTeamID
    │   │       └── NationalTeamName (String) - The name of the national team
    │   └── Avatar
    │       ├── BackgroundImage (URI) - URL to card background-image. Silhouette for non-supporter teams
    │       └── Layer (Multiple containers, each with x/y attributes)
    │           ├── x (Attribute: unsigned Integer) - x-coordinate of image layer
    │           ├── y (Attribute: unsigned Integer) - y-coordinate of image layer
    │           └── Image (URI) - URL to the bodypart item
```

## Important Notes

### YouthTeamId Handling
- **Critical**: YouthTeamId can be empty/missing if team has no Youth academy
- This is the source of the YouthTeamId bug in pychpp - our custom parser handles this gracefully
- Must check for existence before parsing to avoid exceptions

### Data Usage in HTStatus
- `UserId` and `Loginname` → CHPPUser model
- `Teams/Team/TeamId` → team selection and switching
- `YouthTeamId` → optional field (fixes pychpp compatibility bug)
- Arena, League, Country info → team context data
- Currency → potential future financial calculations

### Parser Implementation Notes
- Use `safe_find_text()` and `safe_find_int()` helper functions
- YouthTeamId requires special handling: `youth_team_id = safe_find_text(root, ".//YouthTeamId", default=None)`
- Multiple teams supported via Teams/Team containers
- Language/Country info available for localization

### Version Compatibility
- Current implementation uses version 1.6 in custom CHPP client
- All listed fields available in version 1.6+
- Backward compatible with older versions (fields may be missing)

## Related Files
- `app/chpp/parsers.py` - `parse_user()` function
- `app/chpp/models.py` - `CHPPUser` data model
- `tests/test_chpp_parsers.py` - Unit tests with real XML fixtures