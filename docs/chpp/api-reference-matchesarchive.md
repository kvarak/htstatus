# Matches Archive API Reference

## Overview
The Matches Archive API allows you to retrieve historical match data for a team covering extended time periods.

## Input Parameters

**Required:**
- `file = matchesarchive`

**Optional:**
- `version` - API version (optional)
- `teamID` - unsigned Integer (Default: Your senior or youth teamID)
  - What team to show the matches for: Either teamID or youthTeamID depending on isYouth
- `isYouth` - Boolean (Default: false)
  - Is request for youth or not
- `FirstMatchDate` - DateTime (Default: DateTime.Now - 3 months)
  - First date to show matches in archive from
- `LastMatchDate` - DateTime (Default: DateTime.Now - 1 day)
  - Last date to show matches to. For performance reasons you may only specify an interval of 2 seasons back in time. If you specify a larger interval we'll automatically adjust it to the default which is: firstMatchDate = DateTime.Now.AddMonths(-3).Date lastMatchDate = DateTime.Now.Date
- `season` - unsigned Integer
  - Season to show matches for. (Only valid for senior teams, not for youth!)
- `includeHTO` - Boolean (Default: false)
  - If HTO matches (tournaments, ladders, preparation, and single matches) should be included

**Parameter Rules:**
- You can set FirstMatchDate and LastMatchDate OR season (which overrides FirstMatchDate and LastMatchDate when set)

## Output Structure

The API returns match archive data in the following XML structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Team>
    <TeamID>unsigned Integer</TeamID>
    <!-- The team's TeamID -->

    <TeamName>String</TeamName>
    <!-- The full name of the team -->

    <FirstMatchDate>DateTime</FirstMatchDate>
    <!-- First date to show matches in archive from -->

    <LastMatchDate>DateTime</LastMatchDate>
    <!-- Last date to show matches in archive to -->

    <MatchList>
      <Match>
        <MatchID>unsigned Integer</MatchID>
        <!-- The globally unique identifier of the match -->

        <HomeTeam>
          <HomeTeamID>Integer</HomeTeamID>
          <!-- The teamID of the Home team in the match. (Negative for street teams) -->

          <HomeTeamName>String</HomeTeamName>
          <!-- The team name of the Home team in the match -->
        </HomeTeam>

        <AwayTeam>
          <AwayTeamID>Integer</AwayTeamID>
          <!-- The teamID of the Away team in the match. (Negative for street teams) -->

          <AwayTeamName>String</AwayTeamName>
          <!-- The team name of the Away team in the match -->
        </AwayTeam>

        <MatchDate>DateTime</MatchDate>
        <!-- The start date and time (kick-off) of the match -->

        <MatchType>MatchTypeID</MatchType>
        <!-- Integer defining the type of match -->

        <MatchContextId>unsigned Integer</MatchContextId>
        <!-- This will be either LeagueLevelUnitId (for League), CupId (Cup, Hattrick Masters, World Cup and U-20 World Cup) or 0 for friendly and qualification -->

        <SourceSystem>String</SourceSystem>
        <!-- The name of the source system that plays the match -->

        <MatchRuleId>MatchRuleID</MatchRuleId>
        <!-- This will contain the rules that's in place for the ladder or tournament in question. It's provided for all matchtypes and defaults to 0 = No rules -->

        <CupId>unsigned Integer</CupId>
        <!-- Integer defining the id of the cup -->

        <CupLevel>unsigned Integer</CupLevel>
        <!-- 1 = National/Divisional cup, 2 = Challenger cup, 3 = Consolation cup. 0 if MatchType is not 3 -->

        <CupLevelIndex>unsigned Integer</CupLevelIndex>
        <!-- In Challenger cups: 1 = Emerald (start week 2), 2 = Ruby (start week 3), 3 = Sapphire (start week 4). Always 1 for National/Divisional (main cups) and Consolation cups. 0 if MatchType is not 3 -->

        <HomeGoals>unsigned Integer</HomeGoals>
        <!-- The current number of goals in the match for the home team. If the match is still upcoming or ongoing, this tag is not sent -->

        <AwayGoals>unsigned Integer</AwayGoals>
        <!-- The current number of goals in the match for the away team. If the match is still upcoming or ongoing, this tag is not sent -->
      </Match>
    </MatchList>
  </Team>
</HattrickData>
```

## Data Types

- **MatchRuleID**: Rules in place for ladder or tournament (0 = No rules)
- **SourceSystem**: Name of the source system that plays the match
- **CupId**: Integer defining the cup identifier
- **MatchTypeID**: Integer defining match type (League, Cup, Friendly, etc.)
- **DateTime**: Standard datetime format

## Notes

- Maximum interval of 2 seasons back in time for performance reasons
- HomeGoals and AwayGoals tags not sent for upcoming or ongoing matches
- Season parameter only valid for senior teams, not youth teams
- includeHTO controls whether HTO matches (tournaments, ladders, preparation, single matches) are included
- Default date range is 3 months back from current date
- Setting season parameter overrides FirstMatchDate and LastMatchDate
