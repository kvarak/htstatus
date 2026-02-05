# Matches API Reference

## Overview
The Matches API allows you to retrieve match information for a team including recent matches and upcoming fixtures.

## Input Parameters

**Required:**
- `file = matches`

**Optional:**
- `version` - API version (optional)
- `teamID` - unsigned Integer (Default: Your senior or youth teamID)
  - What team to show the matches for: Either teamID or youthTeamID depending on isYouth
- `isYouth` - Boolean (Default: false)
  - Is request for youth or not
- `LastMatchDate` - DateTime (Default: DateTime.Now + 28 days)
  - Last date to show matches to. If more than 50 matches are affected, only the 50 first will be returned

## Output Structure

The API returns match data in the following XML structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Team>
    <TeamID>unsigned Integer</TeamID>
    <!-- The team's TeamID -->

    <TeamName>String</TeamName>
    <!-- The full name of the team -->

    <ShortTeamName>String</ShortTeamName>
    <!-- The short team name. Only available when isYouth is false -->

    <League>
      <LeagueID>unsigned Integer</LeagueID>
      <!-- The globally unique LeagueID -->

      <LeagueName>String</LeagueName>
      <!-- The league name -->

      <LeagueLevelUnit>
        <LeagueLevelUnitID>unsigned Integer</LeagueLevelUnitID>
        <!-- The globally unique LeagueLevelUnitID -->

        <LeagueLevelUnitName>String</LeagueLevelUnitName>
        <!-- The name of the LeagueLevelUnit -->

        <LeagueLevel>unsigned Integer</LeagueLevel>
        <!-- Integer value stating the relative level of the LeagueLevelUnit, with 1 indicating the league's top series -->
      </LeagueLevelUnit>
    </League>

    <MatchList>
      <Match>
        <MatchID>unsigned Integer</MatchID>
        <!-- The globally unique identifier of the match -->

        <HomeTeam>
          <HomeTeamID>Integer</HomeTeamID>
          <!-- The teamID of the Home team in the match. (Negative for street teams) -->

          <HomeTeamName>String</HomeTeamName>
          <!-- The team name of the Home team in the match -->

          <HomeTeamShortName>String</HomeTeamShortName>
          <!-- The short team name of the Home team in the match -->
        </HomeTeam>

        <AwayTeam>
          <AwayTeamID>Integer</AwayTeamID>
          <!-- The teamID of the Away team in the match. (Negative for street teams) -->

          <AwayTeamName>String</AwayTeamName>
          <!-- The team name of the Away team in the match -->

          <AwayTeamShortName>String</AwayTeamShortName>
          <!-- The short team name of the Away team in the match -->
        </AwayTeam>

        <MatchDate>DateTime</MatchDate>
        <!-- The start date and time (kick-off) of the match -->

        <SourceSystem>sourceSystem</SourceSystem>
        <!-- SourceSystem tells from which system the match is ex: hattrick, youth, htointegrated -->

        <MatchType>MatchTypeID</MatchType>
        <!-- Integer defining the type of match -->

        <MatchContextId>unsigned Integer</MatchContextId>
        <!-- This will be either LeagueLevelUnitId (for League), CupId (Cup, Hattrick Masters, World Cup and U-20 World Cup), LadderId, TournamentId, or 0 for friendly, qualification, single matches and preparation matches -->

        <CupLevel>unsigned Integer</CupLevel>
        <!-- 1 = National/Divisional cup, 2 = Challenger cup, 3 = Consolation cup. 0 if MatchType is not 3 -->

        <CupLevelIndex>unsigned Integer</CupLevelIndex>
        <!-- In Challenger cups: 1 = Emerald (start week 2), 2 = Ruby (start week 3), 3 = Sapphire (start week 4). Always 1 for National/Divisional (main cups) and Consolation cups. 0 if MatchType is not 3 -->

        <HomeGoals>unsigned Integer</HomeGoals>
        <!-- The current number of goals in the match for the home team -->

        <AwayGoals>unsigned Integer</AwayGoals>
        <!-- The current number of goals in the match for the away team -->

        <Status>MatchStatus</Status>
        <!-- Specifying whether the match is FINISHED, ONGOING or UPCOMING -->

        <OrdersGiven>Boolean</OrdersGiven>
        <!-- A boolean value only supplied for upcoming matches (haven't started yet) of your own team that signifies whether you have given orders or not. If the request is for another team than your own (even if it is for your opponent), this data is not sent -->
      </Match>
    </MatchList>
  </Team>
</HattrickData>
```

## Data Types

- **MatchStatus**: FINISHED, ONGOING, UPCOMING
- **MatchTypeID**: Integer defining match type (League, Cup, Friendly, etc.)
- **sourceSystem**: hattrick, youth, htointegrated
- **DateTime**: Standard datetime format

## Notes

- Maximum of 50 matches returned per request
- OrdersGiven field only appears for your own team's upcoming matches
- Negative team IDs indicate street teams
- CupLevel and CupLevelIndex are only relevant for cup matches (MatchType = 3)
