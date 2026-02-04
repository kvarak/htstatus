# Current Bids API Reference

## Overview
The Current Bids API shows transfer market activity for a team, including active bids, recently finished transfers, and hotlisted players. Provides functionality to track and manage transfer market participation.

## Input Parameters

**Required:**
- `file = currentbids`

**Optional:**
- `version` - API version (optional)
- `actionType` - Indicates what type of action the page should perform
  - `view` (default) - Shows all active, recently finished or hotlisted transfers for the specified team
  - `ignoreTransfer` - Removes tracking of a specific transfer (Supporters only, requires "place_bid" scope)
  - `deleteAllFinished` - Removes tracking of all finished transfers in one go (Supporters only, requires "place_bid" scope)
- `teamId` - unsigned Integer (Default: Your primary club senior teamId)
  - Team id to show the transfers for. Must refer to a senior team managed by requesting user

**Action-Specific Parameters:**

**For actionType=ignoreTransfer:**
- `transferId` - unsigned Integer (REQUIRED)
  - Id of the transfer to be ignored
- `trackingTypeId` - trackingTypeId (REQUIRED)
  - Tracking type (category) of the transfer to be ignored. Only values 5, 8 and 9 are allowed

## Output Structure

The API returns current bids data in the following XML structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <TeamId>unsigned Integer</TeamId>
  <!-- Globally unique identifier of the team whose bids are shown -->

  <BidItems TrackingTypeId='trackingTypeId'>
    <BidItem>
      <TransferId>unsigned Integer</TransferId>
      <!-- Unique id for the transfer. Only needed for the ignore functionality -->

      <PlayerId>unsigned Integer</PlayerId>
      <!-- The globally unique playerID for the transferlisted player -->

      <PlayerName>String</PlayerName>
      <!-- The name for the transferlisted player -->

      <HighestBid>
        <Amount>Money</Amount>
        <!-- Amount of the highest bid -->

        <TeamId>unsigned Integer</TeamId>
        <!-- Id of the team holding the highest bid -->

        <TeamName>String</TeamName>
        <!-- Name of the team holding the highest bid -->
      </HighestBid>

      <Deadline>DateTime</Deadline>
      <!-- The transfer deadline -->
    </BidItem>
  </BidItems>
</HattrickData>
```

## Tracking Types

The `trackingTypeId` attribute on BidItems indicates the category of transfer tracking:

### Common Tracking Types
- **Type 5**: Losing bids (can be ignored)
- **Type 8**: Hotlisted transfers (can be ignored)
- **Type 9**: Finished transfers (can be ignored)
- **Other values**: Active bids and ongoing transfers

### Management Rules
- Only tracking types 5, 8, and 9 can be ignored
- Ignore functionality requires Hattrick Supporter status
- "place_bid" OAuth scope required for ignore and delete operations

## Action Types

### view (Default)
- **Purpose**: Display all transfer activity for the team
- **Returns**: Active bids, recent finished transfers, hotlisted players
- **Access**: Available to all users
- **Usage**: Primary interface for reviewing transfer market participation

### ignoreTransfer
- **Purpose**: Remove tracking for a specific transfer
- **Requirements**:
  - Hattrick Supporter status
  - "place_bid" OAuth scope
  - Valid transferId and trackingTypeId (5, 8, or 9 only)
- **Usage**: Clean up transfer history by removing unwanted items
- **Limitations**: Only works for losing bids, hotlisted, and finished transfers

### deleteAllFinished
- **Purpose**: Remove tracking for all finished transfers at once
- **Requirements**:
  - Hattrick Supporter status
  - "place_bid" OAuth scope
- **Usage**: Bulk cleanup of transfer history
- **Effect**: Clears all completed transfer tracking

## Data Types

- **Money**: Monetary amount for bid values
- **DateTime**: Standard datetime format for transfer deadlines
- **trackingTypeId**: Transfer category identifier
- **unsigned Integer**: Positive integer identifiers
- **String**: Text data for player and team names

## Usage Guidelines

### Transfer Market Monitoring
- Use `view` action to monitor ongoing transfer activity
- Check `Deadline` field to track transfer timing
- Monitor `HighestBid` changes to assess competition levels

### Transfer History Management
- Use `ignoreTransfer` for selective cleanup of unwanted items
- Use `deleteAllFinished` for bulk cleanup of completed transfers
- Supporter status required for all management operations

### Bidding Strategy
- Track competitive bidding patterns through highest bid information
- Monitor deadlines to time bid submissions effectively
- Use hotlist functionality to track interesting players without bidding

## Access Control

### Authentication Requirements
- Must be authenticated as team manager
- Can only access data for teams you manage
- Defaults to primary senior team if no teamId specified

### Supporter Features
- Transfer tracking management requires Hattrick Supporter status
- Ignore and delete operations restricted to supporters
- "place_bid" OAuth scope required for management actions

## Integration Notes

### Related APIs
- **Players**: Get detailed information about transferlisted players
- **Team Details**: Context about bidding teams
- **Transfers**: Broader transfer market data

### Rate Limiting Considerations
- Transfer data changes frequently during active bidding
- Consider caching strategies for frequently accessed data
- Respect CHPP rate limits for real-time monitoring

## Implementation Examples

### Monitor Active Transfers
```
file=currentbids&actionType=view&teamId=123456
```

### Remove Specific Transfer Tracking
```
file=currentbids&actionType=ignoreTransfer&transferId=789012&trackingTypeId=5
```

### Clean All Finished Transfers
```
file=currentbids&actionType=deleteAllFinished
```

## Notes

- Transfer deadlines are critical for bidding strategy
- Highest bid information updates in real-time during active transfers
- Tracking type determines what management actions are available
- Supporter-only features enhance transfer market workflow
- OAuth scopes must be properly configured for management operations
- Transfer IDs are required for selective ignore functionality
- Bulk delete affects all finished transfers regardless of tracking type