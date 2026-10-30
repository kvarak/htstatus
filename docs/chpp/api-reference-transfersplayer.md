# Transfers Player API Reference

## Overview
The Transfers Player API returns all finished transfers of one player.

## Input Parameters

**Required:**
- `file = transfersplayer`
- `playerID` - unsigned Integer
  - The player to get the transfers for

**Optional:**
- `version` - API version (optional)

## Output Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Transfers>
    <StartDate>DateTime</StartDate>
    <!-- Oldest date in the selected transfers list -->

    <EndDate>DateTime</EndDate>
    <!-- Latest date in the selected transfers list -->

    <Player>
      <PlayerID>unsigned Integer</PlayerID>
      <!-- Globally unique identifier of the player -->

      <PlayerName>String</PlayerName>
      <!-- The full name of the player -->
    </Player>

    <Transfer>
      <!-- One per transfer; there can be several -->
      <TransferID>unsigned Integer</TransferID>
      <!-- Globally unique identifier of the transfer -->

      <Deadline>DateTime</Deadline>
      <!-- When bidding closed for the transfer -->

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

      <TSI>unsigned Integer</TSI>
      <!-- The player's TSI when he was put on the transfer list -->
    </Transfer>
  </Transfers>
</HattrickData>
```

## Notes
- Money values are in SEK.
- Only finished transfers are listed. Current bids on your own players come from `playerdetails` (`TransferDetails`).
- The CHPP docs page lists the fields flat; check a real response for the exact nesting before parsing.
- Not used by HattrickPlanner yet. For "sold for" prices of a whole team, `transfersteam` needs one call instead of one per player.
