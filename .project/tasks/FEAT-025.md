# FEAT-025: Transfer Current Bid Display

**GitHub Issue**: [#27](https://github.com/kvarak/htstatus/issues/27) - "Spelare - transfer - aktuellt bud"
**Dependencies**: Player statistics (completed), CHPP API integration (completed) | **Strategic Value**: Transfer market management, real-time bidding insights

## Problem Statement

Currently, players being sold through the Hattrick transfer system do not display the current bid amount in the player overview. Users need to manually navigate to Hattrick to check bid status, creating a fragmented workflow for transfer market management.

The original request from VilijamRigo (June 2020) asked for an additional column showing current bids on players being sold. This feature was previously blocked due to CHPP API limitations but was unblocked in January 2021 when pychpp 0.2.11 added the necessary transfer data support.

## Implementation

**Phase 1: CHPP Transfer Data Integration**
- Add CHPP transfer API calls to fetch current transfer/bid data
- Create transfer data models for bid tracking
- Implement caching strategy for transfer data (refreshed on player data updates)

**Phase 2: UI Integration**
- Add "Current Bid" column to player overview tables
- Display bid amount with currency formatting
- Show bid status indicators (active, expired, sold)
- Add visual indicators for urgent transfers (ending soon)

**Phase 3: Data Management**
- Integrate transfer data fetching with existing player update workflows
- Add error handling for transfer API failures
- Implement fallback display when transfer data unavailable

## Acceptance Criteria

- [ ] Players on transfer market display current bid amounts
- [ ] Bid data updates when player data is refreshed
- [ ] Transfer status clearly indicated (active, sold, expired)
- [ ] Currency amounts properly formatted
- [ ] Transfer data fetching does not impact page load performance
- [ ] Graceful handling when transfer API unavailable
- [ ] Mobile-responsive bid display in player tables

**Technical Notes**:
- Requires CHPP transfer API integration (available since pychpp 0.2.11)
- Consider rate limiting for transfer data to avoid CHPP API abuse
- Transfer data should be cached and updated with regular player updates
