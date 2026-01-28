# [FEAT-009] Display Player Group Names in Update Timeline

**Status**: 🎯 Ready to Execute | **Effort**: 1-2 hours | **Priority**: P1 | **Impact**: Enhanced player identification
**Dependencies**: None | **Strategic Value**: Improved user experience for custom groups

## Problem Statement
When viewing the update timeline, players are displayed by name only. Users who have organized their players into custom groups (e.g., \"Ytterback\", \"Formation 1\", \"Reserves\") cannot easily identify which group a player belongs to when viewing skill changes and updates.

## User Request Example
```
Current:
Jalal Allaoui
📈 Winger: 4 → 5

Desired:
Jalal Allaoui (Ytterback)
📈 Winger: 4 → 5
```

## Database Structure
- `PlayerSetting` table links `player_id` to `group_id` for a given `user_id`
- `Group` table contains group `name`, `textcolor`, `bgcolor` for display
- Relationship: player_id → PlayerSetting → Group.name

## Implementation
1. **Update get_player_changes() Function** (30-45 min):
   - Add group name lookup to player change detection logic
   - Query PlayerSetting and Group tables to find player's group name
   - Include group name in change data structure for template use
   - Handle players without group assignments gracefully

2. **Enhance Template Display Logic** (30-45 min):
   - Update `update_timeline.html` to display group names after player names
   - Format as \"Player Name (Group Name)\" when group exists
   - Maintain existing styling while adding group information
   - Consider group text color for visual consistency

3. **Testing & Validation** (15-30 min):
   - Test with players assigned to different groups
   - Test with players not assigned to any group
   - Verify display works with various group name lengths
   - Ensure responsive design maintained

## Acceptance Criteria
- Players with group assignments show \"Player Name (Group Name)\"
- Players without groups show \"Player Name\" (no change)
- Group names display consistently throughout timeline
- No impact on timeline loading performance
- Visual styling remains consistent with UI guidelines

## Technical Notes
- Requires JOIN between Players → PlayerSetting → Group tables
- Consider caching group lookups for performance if needed
- Group colors could be used for future enhancement

## Expected Outcomes
Users can easily identify which tactical group or formation players belong to when reviewing skill changes and updates