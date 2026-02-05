# Team Details API Reference

## Overview
The Team Details API provides comprehensive information about a team and its owner, including team statistics, arena details, league information, trophies, supporters, and various optional data collections.

## Input Parameters

**Required:**
- `file = teamdetails`

**Either/Or Required:**
- `teamID` - unsigned Integer (Default: Your senior teamID)
  - What team to show the data for. Ownerless teams can only be accessed via teamID
- `userID` - unsigned Integer (Default: Your userID, if teamID not set)
  - What user to show the data for. Users without teams can only be accessed via userID

**Optional:**
- `version` - API version (optional)
- `includeDomesticFlags` - Boolean (Default: false)
  - Whether the team's own country should be included in flag collections
- `includeFlags` - Boolean (Default: false)
  - Whether flag collection should be provided
- `includeSupporters` - Boolean (Default: false)
  - Whether supported teams and team supporters should be included

**Parameter Rules:**
- Either teamID or userID is required
- If neither is supplied, defaults to logged-in user's userID

## Output Structure

The API returns team details in the following XML structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <User>
    <UserID>unsigned Integer</UserID>
    <!-- The globally unique UserID for the owner of the team. Teams without an owner have UserID = 0 -->

    <Language>
      <LanguageID>unsigned Integer</LanguageID>
      <!-- The globally unique LanguageID -->

      <LanguageName>String</LanguageName>
      <!-- The language name -->
    </Language>

    <SupporterTier>supporterTier</SupporterTier>
    <!-- The current level of Hattrick Supporter that the user has (including Diamond). Empty if not a Supporter -->

    <Loginname>String</Loginname>
    <!-- The 'username' or 'nickname' used in Forums and around the site. Not supplied if the team is ownerless -->

    <Name>String</Name>
    <!-- The user's personal name or the value 'HIDDEN' to indicate that the user has chosen to hide it. Not supplied if the team is ownerless -->

    <ICQ>unsigned Integer</ICQ>
    <!-- The user's ICQ number (if any). Not supplied if the team is ownerless -->

    <SignupDate>DateTime</SignupDate>
    <!-- The date and time when the user signed up for Hattrick. Not supplied if the team is ownerless -->

    <ActivationDate>DateTime</ActivationDate>
    <!-- The date and time when the user gained control of this team. Not supplied if the team is ownerless -->

    <LastLoginDate>DateTime</LastLoginDate>
    <!-- The date and time when the user last logged on. Not supplied if the team is ownerless -->

    <HasManagerLicense>Boolean</HasManagerLicense>
    <!-- Whether or not the user has received the manager license -->

    <NationalTeams>
      <NationalTeam>
        <NationalTeamStaffType>NationalTeamStaffType</NationalTeamStaffType>
        <!-- The staff type id from the position the user has in the national team -->

        <NationalTeamID>unsigned Integer</NationalTeamID>
        <!-- The globally unique identifier of the national team -->

        <NationalTeamName>String</NationalTeamName>
        <!-- The name of the national team -->
      </NationalTeam>
    </NationalTeams>
  </User>

  <Teams>
    <Team>
      <TeamID>unsigned Integer</TeamID>
      <!-- The globally unique TeamID -->

      <TeamName>String</TeamName>
      <!-- The full team name -->

      <ShortTeamName>String</ShortTeamName>
      <!-- The short team name -->

      <IsPrimaryClub>Boolean</IsPrimaryClub>
      <!-- True/false indicating if this team is the user's primary team -->

      <FoundedDate>DateTime</FoundedDate>
      <!-- Date when club was founded -->

      <IsDeactivated>Boolean</IsDeactivated>
      <!-- Whether or not the team is deactivated and not part of the league system -->

      <Arena>
        <ArenaID>unsigned Integer</ArenaID>
        <!-- The globally unique ArenaID -->

        <ArenaName>String</ArenaName>
        <!-- The arena name -->
      </Arena>

      <League>
        <LeagueID>unsigned Integer</LeagueID>
        <!-- The globally unique LeagueID -->

        <LeagueName>String</LeagueName>
        <!-- The League name -->
      </League>

      <Country>
        <CountryID>unsigned Integer</CountryID>
        <!-- The globally unique CountryID -->

        <CountryName>String</CountryName>
        <!-- The Country name -->
      </Country>

      <Region>
        <RegionID>unsigned Integer</RegionID>
        <!-- The globally unique RegionID -->

        <RegionName>String</RegionName>
        <!-- The Region name -->
      </Region>

      <Trainer>
        <PlayerID>unsigned Integer</PlayerID>
        <!-- The globally unique PlayerID of the player that has the job as trainer of the team -->
      </Trainer>

      <HomePage>URI</HomePage>
      <!-- The home page URL that the team has specified -->

      <Cup>
        <StillInCup>Boolean</StillInCup>
        <!-- Boolean value stating if the team is still in the cup -->

        <CupID>unsigned Integer</CupID>
        <!-- The globally unique CupID of the cup that the team is still in. Only provided if team is still in cup -->

        <CupName>String</CupName>
        <!-- The name of the cup that the team is still in. Only provided if team is still in cup -->

        <CupLeagueLevel>unsigned Integer</CupLeagueLevel>
        <!-- LeagueLevel for the cup. 0 = National (LeagueLevel 1-6), 7-9 = Divisional. Only provided if team is still in cup -->

        <CupLevel>unsigned Integer</CupLevel>
        <!-- Level of the cup. 1 = National/Divisional, 2 = Challenger, 3 = Consolation. Only provided if team is still in cup -->

        <CupLevelIndex>unsigned Integer</CupLevelIndex>
        <!-- Index of the cup. Always 1 for National and Consolation cups, for Challenger cup: 1 = Emerald, 2 = Ruby, 3 = Sapphire. Only provided if team is still in cup -->

        <MatchRound>unsigned Integer</MatchRound>
        <!-- Next round (or current if matches are ongoing). Only provided if team is still in cup -->

        <MatchRoundsLeft>unsigned Integer</MatchRoundsLeft>
        <!-- How many rounds are left of this cup. Only provided if team is still in cup -->
      </Cup>

      <PowerRating>
        <GlobalRanking>unsigned Integer</GlobalRanking>
        <!-- The Power Rating team ranking in Global -->

        <LeagueRanking>unsigned Integer</LeagueRanking>
        <!-- The Power Rating team ranking in the same league -->

        <RegionRanking>unsigned Integer</RegionRanking>
        <!-- The Power Rating team ranking in the same region -->

        <PowerRating>unsigned Integer</PowerRating>
        <!-- The Power Rating value of the team -->
      </PowerRating>

      <FriendlyTeamID>unsigned Integer</FriendlyTeamID>
      <!-- The team's status about if a friendly is booked. The value is the opponents globally unique teamID if the team has booked a friendly, 0 if not. If the team is playing a match the tag will be empty -->

      <LeagueLevelUnit>
        <LeagueLevelUnitID>unsigned Integer</LeagueLevelUnitID>
        <!-- The globally unique LeagueLevelUnitID -->

        <LeagueLevelUnitName>String</LeagueLevelUnitName>
        <!-- The name of the LeagueLevelUnit -->

        <LeagueLevel>unsigned Integer</LeagueLevel>
        <!-- Integer value stating the relative level of the LeagueLevelUnit, with 1 indicating the league's top series -->
      </LeagueLevelUnit>

      <NumberOfVictories>unsigned Integer</NumberOfVictories>
      <!-- If the team is in a winning streak of at least 2 matches, this integer indicates how many victories in a row it currently has. If the team is playing a match the tag will be empty -->

      <NumberOfUndefeated>unsigned Integer</NumberOfUndefeated>
      <!-- If the team is in a streak of at least 2 matches as undefeated, this integer indicates how many matches in a row it is undefeated. If the team is playing a match the tag will be empty -->

      <Fanclub>
        <FanclubID>unsigned Integer</FanclubID>
        <!-- The globally unique FanclubID -->

        <FanclubName>String</FanclubName>
        <!-- The name of the fanclub -->

        <FanclubSize>unsigned Integer</FanclubSize>
        <!-- The amount of members in the fanclub -->
      </Fanclub>

      <LogoURL>URI</LogoURL>
      <!-- The logo URL that the team has specified -->

      <Guestbook>
        <!-- This container and its elements is only shown if the user has supporter -->
        <NumberOfGuestbookItems>unsigned Integer</NumberOfGuestbookItems>
        <!-- The number of postings in the team's guestbook -->
      </Guestbook>

      <PressAnnouncement>
        <!-- This container and its elements is only shown if the user has supporter -->
        <Subject>String</Subject>
        <!-- The subject text specified for the PressAnnouncement -->

        <Body>String</Body>
        <!-- The body of the PressAnnouncement -->

        <SendDate>DateTime</SendDate>
        <!-- The time and date when the PressAnnouncement was submitted -->
      </PressAnnouncement>

      <TeamColors>
        <!-- This container and its elements is only shown if the user has supporter -->
        <BackgroundColor>String</BackgroundColor>
        <!-- The defined background color from the club theme -->

        <Color>String</Color>
        <!-- The matching text color to the defined background color -->
      </TeamColors>

      <DressURI>URI</DressURI>
      <!-- URI to an image representing the dress of the team -->

      <DressAlternateURI>URI</DressAlternateURI>
      <!-- Same as DressURI, except that it shows the alternate dress -->

      <BotStatus>
        <IsBot>Boolean</IsBot>
        <!-- Specifies whether a team is currently a bot or not -->

        <BotSince>DateTime</BotSince>
        <!-- The date when the team was made a bot, only available if team is a bot -->
      </BotStatus>

      <TeamRank>unsigned Integer</TeamRank>
      <!-- If the team has an owner, last is the League Rank, a number based on LeagueLevel, position etc, only counting teams with an owner. If the team is playing a match the tag will be empty -->

      <YouthTeamID>unsigned Integer</YouthTeamID>
      <!-- If the Team has a Youth academy the ID is represented here. If not it will be 0 -->

      <YouthTeamName>String</YouthTeamName>
      <!-- If the Team has a Youth academy the team name is represented here. If not it will be an empty string -->

      <NumberOfVisits>unsigned Integer</NumberOfVisits>
      <!-- The number of visits the team had in the latest day with at least one visit -->

      <Flags>
        <!-- Only included if includeFlags parameter is true -->
        <HomeFlags>
          <Flag>
            <LeagueID>unsigned Integer</LeagueID>
            <!-- The LeagueId for the league a flag belongs to -->

            <LeagueName>String</LeagueName>
            <!-- The LeagueName for the league a flag belongs to -->

            <CountryCode>String</CountryCode>
            <!-- The CountryCode for the league a flag belongs to -->
          </Flag>
        </HomeFlags>

        <AwayFlags>
          <Flag>
            <LeagueID>unsigned Integer</LeagueID>
            <!-- The LeagueId for the league a flag belongs to -->

            <LeagueName>String</LeagueName>
            <!-- The LeagueName for the league a flag belongs to -->

            <CountryCode>String</CountryCode>
            <!-- The CountryCode for the league a flag belongs to -->
          </Flag>
        </AwayFlags>
      </Flags>

      <TrophyList>
        <Trophy>
          <TrophyTypeId>trophyID</TrophyTypeId>
          <!-- TypeId for the trophy -->

          <TrophySeason>unsigned Integer</TrophySeason>
          <!-- The season the trophy was won -->

          <LeagueLevel>unsigned Integer</LeagueLevel>
          <!-- The level the league the user won. For tournament trophies, this act as a "type" -->

          <LeagueLevelUnitId>String</LeagueLevelUnitId>
          <!-- The LeagueLevelUnitId of the leaguelevelunit that the user won. For tournaments this is the id of the tournament -->

          <LeagueLevelUnitName>String</LeagueLevelUnitName>
          <!-- The name of the leaguelevelunit that the user won. For tournaments this is the name of the tournament -->

          <GainedDate>DateTime</GainedDate>
          <!-- The date when the user gained the trophy -->

          <ImageUrl>URI</ImageUrl>
          <!-- The url to the trophy image -->

          <CupLeagueLevel>unsigned Integer</CupLeagueLevel>
          <!-- The league level of the cup. 0 for the main cups, division 1-6. Empty when not a cup trophy (16) -->

          <CupLevel>CupLevel</CupLevel>
          <!-- The level of the cup. Empty when not a cup trophy (16) -->

          <CupLevelIndex>CupLevelIndex</CupLevelIndex>
          <!-- Which type of challenger cup. Always 1 for national and consolation cups. Empty when not a cup trophy (16) -->
        </Trophy>
      </TrophyList>

      <!-- The following sections only included if includeSupporters parameter is true -->
      <SupportedTeams TotalItems='unsigned Integer' MaxItems='unsigned Integer'>
        <SupportedTeam>
          <UserId>unsigned Integer</UserId>
          <!-- The globally unique UserID for the owner of the supported team -->

          <LoginName>String</LoginName>
          <!-- The 'username' or 'nickname' used in Forums and around the site -->

          <TeamId>unsigned Integer</TeamId>
          <!-- The globally unique TeamID for the supported team -->

          <TeamName>String</TeamName>
          <!-- The teamname of the supported team -->

          <LeagueID>unsigned Integer</LeagueID>
          <!-- The globally unique LeagueID for the supported team -->

          <LeagueName>String</LeagueName>
          <!-- The League name -->

          <LeagueLevelUnitID>unsigned Integer</LeagueLevelUnitID>
          <!-- The globally unique LeagueLevelUnitID for the supported team -->

          <LeagueLevelUnitName>String</LeagueLevelUnitName>
          <!-- The name of the LeagueLevelUnit -->

          <LastMatch>
            <LastMatchId>unsigned Integer</LastMatchId>
            <!-- The globally unique matchID -->

            <LastMatchDate>DateTime</LastMatchDate>
            <!-- The matchdate of the last match -->

            <LastMatchHomeTeamId>unsigned Integer</LastMatchHomeTeamId>
            <!-- The globally unique TeamID for the home team -->

            <LastMatchHomeTeamName>String</LastMatchHomeTeamName>
            <!-- The team name of the home team in the match -->

            <LastMatchHomeGoals>unsigned Integer</LastMatchHomeGoals>
            <!-- The number of goals scored in the match by the hometeam -->

            <LastMatchAwayTeamId>unsigned Integer</LastMatchAwayTeamId>
            <!-- The globally unique TeamID for the away team -->

            <LastMatchAwayTeamName>String</LastMatchAwayTeamName>
            <!-- The team name of the away team in the match -->

            <LastMatchAwayGoals>unsigned Integer</LastMatchAwayGoals>
            <!-- The number of goals scored in the match by the awayteam -->
          </LastMatch>

          <NextMatch>
            <NextMatchId>unsigned Integer</NextMatchId>
            <!-- The globally unique matchID -->

            <NextMatchDate>DateTime</NextMatchDate>
            <!-- The matchdate of the next match -->

            <NextMatchHomeTeamId>unsigned Integer</NextMatchHomeTeamId>
            <!-- The globally unique TeamID for the home team -->

            <NextMatchHomeTeamName>String</NextMatchHomeTeamName>
            <!-- The team name of the home team in the match -->

            <NextMatchAwayTeamId>unsigned Integer</NextMatchAwayTeamId>
            <!-- The globally unique TeamID for the away team -->

            <NextMatchAwayTeamName>String</NextMatchAwayTeamName>
            <!-- The team name of the away team in the match -->
          </NextMatch>

          <PressAnnouncement>
            <PressAnnouncementSendDate>DateTime</PressAnnouncementSendDate>
            <!-- The time and date when the PressAnnouncement was submitted -->

            <PressAnnouncementSubject>String</PressAnnouncementSubject>
            <!-- The subject text specified for the PressAnnouncement -->

            <PressAnnouncementBody>String</PressAnnouncementBody>
            <!-- The body of the PressAnnouncement -->
          </PressAnnouncement>
        </SupportedTeam>
      </SupportedTeams>

      <MySupporters TotalItems='unsigned Integer' MaxItems='unsigned Integer'>
        <SupporterTeam>
          <UserId>unsigned Integer</UserId>
          <!-- The globally unique UserID for the owner of the supporter team -->

          <LoginName>String</LoginName>
          <!-- The 'username' or 'nickname' used in Forums and around the site -->

          <TeamId>unsigned Integer</TeamId>
          <!-- The globally unique TeamID for the supporter team -->

          <TeamName>String</TeamName>
          <!-- The teamname of the supporter team -->

          <LeagueID>unsigned Integer</LeagueID>
          <!-- The globally unique LeagueID for the supporter team -->

          <LeagueName>String</LeagueName>
          <!-- The League name -->

          <LeagueLevelUnitID>unsigned Integer</LeagueLevelUnitID>
          <!-- The globally unique LeagueLevelUnitID for the supported team -->

          <LeagueLevelUnitName>String</LeagueLevelUnitName>
          <!-- The name of the LeagueLevelUnit -->
        </SupporterTeam>
      </MySupporters>

      <PossibleToChallengeMidweek>Boolean</PossibleToChallengeMidweek>
      <!-- Whether or not the team is possible to challenge for a mid-week friendly -->

      <PossibleToChallengeWeekend>Boolean</PossibleToChallengeWeekend>
      <!-- Whether or not the team is possible to challenge for a weekend friendly -->
    </Team>
  </Teams>
</HattrickData>
```

## Data Types

- **supporterTier**: Supporter package level (including Diamond)
- **NationalTeamStaffType**: Staff position type in national team
- **trophyID**: Trophy type identifier
- **CupLevel**: Cup level identifier
- **CupLevelIndex**: Cup level index identifier
- **URI**: URL to web resource
- **DateTime**: Standard datetime format
- **Boolean**: True/false value

## Notes

- Either teamID or userID is required, but not both
- Ownerless teams (UserID = 0) can only be accessed via teamID
- Users without teams can only be accessed via userID
- Many user-specific fields are not supplied for ownerless teams
- Guestbook, PressAnnouncement, and TeamColors require supporter status
- Flags collection requires includeFlags parameter set to true
- Supporters data requires includeSupporters parameter set to true
- Some fields are empty when team is currently playing a match
- Trophy list includes league, cup, and tournament achievements
- Power Rating provides global, league, and regional rankings
- Cup information only provided if team is currently in a cup
- Youth team fields show 0 or empty string if no youth academy exists
