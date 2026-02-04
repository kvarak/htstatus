# Manager Compendium API Reference

## Overview
The Manager Compendium API provides comprehensive information about a manager including personal details, teams, language settings, national team roles, and avatar information.

## Input Parameters

**Required:**
- `file = managercompendium`

**Optional:**
- `version` - API version (optional)
- `userId` - unsigned Integer (Default: Your userId)
  - What user to show the data for

## Output Structure

The API returns manager data in the following XML structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Manager>
    <UserId>unsigned Integer</UserId>
    <!-- The globally unique UserID -->

    <Loginname>String</Loginname>
    <!-- The 'username' or 'nickname' used in Forums and around the site -->

    <SupporterTier>String</SupporterTier>
    <!-- The current level of Hattrick Supporter that the user has. Empty if not a Supporter -->

    <LastLogins>
      <LoginTime>String</LoginTime>
      <!-- Repeater with Login Time information -->
    </LastLogins>

    <Language>
      <LanguageId>unsigned Integer</LanguageId>
      <!-- The globally unique LanguageID -->

      <LanguageName>String</LanguageName>
      <!-- The language name -->
    </Language>

    <Country>
      <CountryId>unsigned Integer</CountryId>
      <!-- The globally unique CountryID -->

      <CountryName>String</CountryName>
      <!-- The country name -->
    </Country>

    <Currency>
      <CurrencyName>String</CurrencyName>
      <!-- The name of the currency -->

      <CurrencyRate>Decimal</CurrencyRate>
      <!-- Decimal value specifying the relative currency rate to SEK (Swedish krona) -->
    </Currency>

    <Teams>
      <Team>
        <TeamId>unsigned Integer</TeamId>
        <!-- The globally unique TeamID -->

        <TeamName>String</TeamName>
        <!-- The full team name -->

        <Arena>
          <ArenaId>unsigned Integer</ArenaId>
          <!-- The globally unique ArenaID -->

          <ArenaName>String</ArenaName>
          <!-- The arena name -->
        </Arena>

        <League>
          <LeagueId>unsigned Integer</LeagueId>
          <!-- The globally unique LeagueID -->

          <LeagueName>String</LeagueName>
          <!-- The League name -->

          <Season>unsigned Integer</Season>
          <!-- The Current Season -->
        </League>

        <Country>
          <CountryId>unsigned Integer</CountryId>
          <!-- The globally unique CountryId -->

          <CountryName>String</CountryName>
          <!-- The Country name -->
        </Country>

        <LeagueLevelUnit>
          <LeagueLevelUnitId>unsigned Integer</LeagueLevelUnitId>
          <!-- The globally unique LeagueLevelUnitID -->

          <LeagueLevelUnitName>String</LeagueLevelUnitName>
          <!-- The name of the LeagueLevelUnit -->
        </LeagueLevelUnit>

        <Region>
          <RegionId>unsigned Integer</RegionId>
          <!-- The globally unique RegionID -->

          <RegionName>String</RegionName>
          <!-- The Region name -->
        </Region>

        <YouthTeam>
          <YouthTeamId>unsigned Integer</YouthTeamId>
          <!-- If the Team has a Youth academy the ID is represented here -->

          <YouthTeamName>String</YouthTeamName>
          <!-- If the Team has a Youth academy the team name is represented here -->

          <YouthLeague>
            <YouthLeagueId>unsigned Integer</YouthLeagueId>
            <!-- The globally unique YouthLeagueID -->

            <YouthLeagueName>String</YouthLeagueName>
            <!-- The name of the youth league -->
          </YouthLeague>
        </YouthTeam>
      </Team>
    </Teams>

    <NationalTeamCoach>
      <NationalTeam>
        <NationalTeamId>unsigned Integer</NationalTeamId>
        <!-- The globally unique NationalTeamID -->

        <NationalTeamName>String</NationalTeamName>
        <!-- The name of the national team -->
      </NationalTeam>
    </NationalTeamCoach>

    <NationalTeamAssistant>
      <NationalTeam>
        <NationalTeamId>unsigned Integer</NationalTeamId>
        <!-- The globally unique NationalTeamID -->

        <NationalTeamName>String</NationalTeamName>
        <!-- The name of the national team -->
      </NationalTeam>
    </NationalTeamAssistant>

    <Avatar>
      <BackgroundImage>URI</BackgroundImage>
      <!-- The URL to the card background-image. This will show a silhouette for non-supporter teams -->

      <Layer x='unsigned Integer' y='unsigned Integer'>
        <Image>URI</Image>
        <!-- The URL to the bodypart item -->
      </Layer>
    </Avatar>
  </Manager>
</HattrickData>
```

## Data Types

- **URI**: URL to image resource
- **Decimal**: Currency exchange rate relative to Swedish krona (SEK)
- **String**: Text data including names, login information
- **unsigned Integer**: Positive integer identifiers

## Notes

- Default userId parameter shows data for the logged-in user
- Currency rates are relative to Swedish krona (SEK) as base currency
- LastLogins contains repeating LoginTime elements for login history
- YouthTeam section is empty if no Youth academy exists
- NationalTeamCoach and NationalTeamAssistant sections are empty if user has no national team roles
- Avatar BackgroundImage shows silhouette for non-supporter teams
- Multiple Layer elements can exist for avatar composition with x,y positioning
- Teams section can contain multiple teams if user manages multiple clubs
- YouthLeague section is empty if youth team is not currently in a league