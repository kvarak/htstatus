# Transfers Team API Reference

## Overview
The Transfers Team API returns the transfer history of a team: totals for buys and sales, and a paged list of finished transfers.

## Input Parameters

**Required:**
- `file = transfersteam`

**Optional:**
- `version` - API version (optional)
- `teamID` - unsigned Integer (default: your own teamID)
  - What team to show the transfers for
- `pageIndex` - unsigned Integer (default: 1)
  - What page to retrieve. Each page has 25 records (the last page may have fewer). Use 0 for the last page.

## Output Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Team>
    <TeamID>unsigned Integer</TeamID>
    <!-- Globally unique identifier of the team -->

    <TeamName>String</TeamName>
    <!-- The full name of the team -->

    <ActivatedDate>DateTime</ActivatedDate>
    <!-- The date when the user got this team -->
  </Team>

  <Stats>
    <TotalSumOfBuys>Money</TotalSumOfBuys>
    <!-- Total sum in SEK of all players bought by this team -->

    <TotalSumOfSales>Money</TotalSumOfSales>
    <!-- Total sum in SEK of all players sold by this team -->

    <NumberOfBuys>unsigned Integer</NumberOfBuys>
    <!-- Total number of bought players -->

    <NumberOfSales>unsigned Integer</NumberOfSales>
    <!-- Total number of sold players -->
  </Stats>

  <Transfers>
    <PageIndex>unsigned Integer</PageIndex>
    <!-- The pageIndex retrieved -->

    <Pages>unsigned Integer</Pages>
    <!-- Total number of pages available -->

    <StartDate>DateTime</StartDate>
    <!-- Oldest date in the selected transfers list -->

    <EndDate>DateTime</EndDate>
    <!-- Latest date in the selected transfers list -->

    <Transfer>
      <TransferID>unsigned Integer</TransferID>
      <!-- Globally unique identifier of the transfer -->

      <Deadline>DateTime</Deadline>
      <!-- When bidding closed for the transfer -->

      <Player>
        <PlayerID>unsigned Integer</PlayerID>
        <PlayerName>String</PlayerName>
      </Player>

      <TSI>unsigned Integer</TSI>
      <!-- The player's TSI when he was put on the transfer list -->

      <TransferType>Char</TransferType>
      <!-- 'S' = Sale or 'B' = Buy, seen from the requested team's point of view -->

      <Buyer>
        <BuyerTeamID>unsigned Integer</BuyerTeamID>
        <BuyerTeamName>String</BuyerTeamName>
      </Buyer>

      <Seller>
        <SellerTeamID>unsigned Integer</SellerTeamID>
        <SellerTeamName>String</SellerTeamName>
      </Seller>

      <Price>Money</Price>
      <!-- The final price the buyer paid -->
    </Transfer>
  </Transfers>
</HattrickData>
```

## Notes
- Money values are in SEK.
- Only finished transfers are listed. Current bids on your own players come from `playerdetails` (`TransferDetails`).
- The CHPP docs page lists the fields flat; check a real response for the exact placement of `TSI`, `TransferType` and `Price` (inside `Player` or directly in `Transfer`) before parsing.
- Not used by HattrickPlanner yet. It could later show a "sold for" price when a player leaves the roster at Update.
