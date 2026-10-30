# Arena Details API Reference

## Overview
The Arena Details API gives information about specific arenas, supporter statistics and the largest arenas in Hattrick.

## Input Parameters

**Required:**
- `file = arenadetails`

**Optional:**
- `version` - API version (optional)
- `StatsType` - Statistics type to show (versions 1.3, 1.4):
  - *(empty)* - **Default view** (default)
  - `MyArena` - Supporter statistics for the user's own arena
  - `OtherArenas` - Supporter statistics for the biggest arenas

### Default view (`StatsType` empty)
- `arenaID` - unsigned Integer (default: your own arenaID, if no teamId supplied)
  - Which arena to show details for
- `teamId` - unsigned Integer (default: your own primary team's team id)
  - Which of your own teams' arena to show details for; only used when no arenaID is supplied

### `StatsType = MyArena`
- `arenaID` - unsigned Integer (default: your own arenaID, if no teamId supplied)
- `teamId` - unsigned Integer (default: your own primary team's team id); only used when no arenaID is supplied
- `MatchType` - ArenaMatchType (default: All)
  - Which type of matches to include in the statistics
- `FirstDate` - DateTime (default: date of the first match in the arena)
  - The first date the statistics should cover
- `LastDate` - DateTime (default: now)
  - The last date the statistics should cover

### `StatsType = OtherArenas`
- `StatsLeagueID` - unsigned Integer, **required** (default: 0)
  - Which league to show statistics for; 0 = global statistics

## Output Structure (default view)

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Arena>
    <ArenaID>unsigned Integer</ArenaID>
    <!-- The globally unique arenaID -->

    <ArenaName>String</ArenaName>
    <!-- The name of the arena -->

    <ArenaImage>String</ArenaImage>
    <!-- URL to an image of the arena -->

    <ArenaFallbackImage>String</ArenaFallbackImage>
    <!-- Default image for an arena of this size; use only when ArenaImage fails to load -->

    <Team>
      <TeamID>unsigned Integer</TeamID>
      <!-- The globally unique teamID of the team owning this arena -->

      <TeamName>String</TeamName>
      <!-- The name of the team -->
    </Team>

    <League>
      <LeagueID>unsigned Integer</LeagueID>
      <!-- The globally unique leagueID of the arena's team -->

      <LeagueName>String</LeagueName>
      <!-- The name of the league -->
    </League>

    <Region>
      <RegionID>unsigned Integer</RegionID>
      <!-- The globally unique regionID of the arena -->

      <RegionName>String</RegionName>
      <!-- The name of the region -->
    </Region>

    <CurrentCapacity Available="Boolean">
      <!-- Available=false and empty while the arena is under construction -->

      <RebuiltDate>DateTime</RebuiltDate>
      <!-- The date when the current capacity was reached -->

      <Terraces>unsigned Integer</Terraces>
      <!-- Current capacity on the terraces -->

      <Basic>unsigned Integer</Basic>
      <!-- Current capacity on the basic seats -->

      <Roof>unsigned Integer</Roof>
      <!-- Current capacity on the seats under roof -->

      <VIP>unsigned Integer</VIP>
      <!-- Current capacity in the VIP lounge -->

      <Total>unsigned Integer</Total>
      <!-- The arena's current total capacity -->
    </CurrentCapacity>

    <ExpandedCapacity Available="Boolean">
      <!-- Available=true while the arena is under construction, otherwise false and empty -->

      <ExpansionDate>DateTime</ExpansionDate>
      <!-- Preliminary date when the expansion is finished -->

      <Terraces>unsigned Integer</Terraces>
      <Basic>unsigned Integer</Basic>
      <Roof>unsigned Integer</Roof>
      <VIP>unsigned Integer</VIP>
      <Total>unsigned Integer</Total>
      <!-- Expanded capacity per seat type, and in total -->
    </ExpandedCapacity>
  </Arena>
</HattrickData>
```

## Notes
- Only the default view's output was captured from the CHPP docs; the `MyArena` and `OtherArenas` outputs (supporter statistics) are not documented here yet.
- Not used by HattrickPlanner yet.
