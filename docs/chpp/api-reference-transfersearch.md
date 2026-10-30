# Transfer Search API Reference

## Overview
The Transfer Search API searches the transfer market.

> ⚠️ This file is **not** meant to be fetched by bots to scan the transfer market automatically, only on a manual user request. In HattrickPlanner that means an explicit user action, never page loads or Update.

## Input Parameters

**Required:**
- `file = transfersearch`
- `ageMin` - unsigned Integer - Minimum age (years)
- `ageMax` - unsigned Integer - Maximum age (years)
- `skillType1` - SkillID - Main skill to search for
- `minSkillValue1` - SkillLevel - Minimum value for the main skill
- `maxSkillValue1` - SkillLevel - Maximum value for the main skill

**Optional:**
- `version` - API version (optional)
- `ageDaysMin` - unsigned Integer (default: 0) - Minimum age (days)
- `ageDaysMax` - unsigned Integer (default: 111) - Maximum age (days)
- `skillType2` / `minSkillValue2` / `maxSkillValue2` - Secondary skill and range (default: not specified)
- `skillType3` / `minSkillValue3` / `maxSkillValue3` - Secondary skill and range (default: not specified)
- `skillType4` / `minSkillValue4` / `maxSkillValue4` - Secondary skill and range (default: not specified)
- `specialty` - SpecialtyID (default: not specified)
- `nativeCountryId` - unsigned Integer (default: not specified) - Country where the players were born
- `tsiMin` / `tsiMax` - unsigned Integer (default: not specified) - TSI range
- `priceMin` / `priceMax` - Money (default: not specified) - Price range
- `pageSize` - unsigned Integer (default: 25, max 100) - Results per page
- `pageIndex` - unsigned Integer (default: 0) - Page to show, starting from 0

**Skill range rules:**
- Min and max may differ by at most 4 levels.
- Set pieces, leadership and experience need a minimum level of 5; keeper needs 3.

## Output Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <TransferSearch>
    <ItemCount>unsigned Integer</ItemCount>
    <!-- Total items matching the search; -1 if over 100 ("many") -->

    <PageSize>unsigned Integer</PageSize>
    <!-- How many results are being shown -->

    <PageIndex>unsigned Integer</PageIndex>
    <!-- What page is being shown -->
  </TransferSearch>

  <TransferResults>
    <TransferResult>
      <PlayerId>unsigned Integer</PlayerId>
      <FirstName>String</FirstName>
      <NickName>String</NickName>
      <LastName>String</LastName>

      <NativeCountryID>unsigned Integer</NativeCountryID>
      <!-- Country where the player was born -->

      <AskingPrice>Money</AskingPrice>
      <!-- The original asking price -->

      <Deadline>DateTime</Deadline>
      <!-- The transfer deadline; can be a few hours in the past -->

      <HighestBid>Money</HighestBid>
      <!-- Highest bid so far; 0 if no bids -->

      <BidderTeam>
        <!-- Team holding the highest bid; empty if no bids -->
        <TeamID>unsigned Integer</TeamID>
        <TeamName>String</TeamName>
      </BidderTeam>

      <Details>
        <!-- Empty if the deadline has passed -->
        <Age>unsigned Integer</Age>
        <AgeDays>unsigned Integer</AgeDays>
        <!-- Days since last birthday (added in a later version) -->
        <Salary>Money</Salary>
        <TSI>unsigned Integer</TSI>
        <PlayerForm>SkillLevel</PlayerForm>
        <Experience>SkillLevel</Experience>
        <Leadership>SkillLevel</Leadership>
        <Specialty>SpecialtyID</Specialty>

        <Cards>unsigned Integer</Cards>
        <!-- Accumulated cards; 3 if suspended. Not available while a match is running -->

        <InjuryLevel>Integer</InjuryLevel>
        <!-- Weeks injured; 0 = bruised, -1 = healthy. Not available while a match is running -->

        <StaminaSkill>SkillLevel</StaminaSkill>
        <KeeperSkill>SkillLevel</KeeperSkill>
        <PlaymakerSkill>SkillLevel</PlaymakerSkill>
        <ScorerSkill>SkillLevel</ScorerSkill>
        <PassingSkill>SkillLevel</PassingSkill>
        <WingerSkill>SkillLevel</WingerSkill>
        <DefenderSkill>SkillLevel</DefenderSkill>
        <SetPiecesSkill>SkillLevel</SetPiecesSkill>

        <SellerTeam>
          <TeamID>unsigned Integer</TeamID>
          <TeamName>String</TeamName>
          <LeagueId>unsigned Integer</LeagueId>
          <!-- League where the selling team plays -->
        </SellerTeam>
      </Details>
    </TransferResult>
  </TransferResults>
</HattrickData>
```

## Notes
- Money values are in SEK, like all CHPP money.
- The CHPP docs describe `SellerTeam` with the same wording as `BidderTeam` ("team holding the highest bid"); judging by its name and the `LeagueId` field, it is the selling team.
- The CHPP docs show `TransferResults` next to `TransferSearch`; check a real response for the exact nesting before parsing.
- Not used by HattrickPlanner yet. FEAT-025 (bids on your own players) uses `playerdetails` instead, which Update already fetches.
