# FEAT-019: Player Skill Changes - 4 Week Timeline on Player Details Page

## Problem Statement
Currently, users can only view the "Player Skill Changes - 4 Week Timeline" on the update page after performing an update. This timeline is not available on the individual player details page (`/player?id=XXX`), making it difficult for users to review recent skill changes for a specific player without running a full update.

Hattrick managers frequently need to track skill progression for individual players when making training decisions, transfer evaluations, and tactical planning. Having this timeline available directly on the player page would significantly improve the user experience for these core Hattrick geek workflows.

## Implementation
1. **Data Source**: Reuse the existing timeline logic from the update page
2. **Scope**: Display timeline only for the selected team/player (respect team isolation)
3. **Location**: Place under the existing players table on the player details page
4. **UI Framework**: Use Flask templates with `.card-custom` styling
5. **Data Flow**: Query skill changes for the specific player from the database
6. **Performance**: Limit to 4-week window as per existing implementation

### Technical Details
- Route: `/player?id=XXX` (existing route)
- Template: Extend existing player template
- Data: Query `PlayerSkillChange` model for the specific player
- Styling: Football green theme with responsive design
- Accessibility: Ensure screen reader compatibility

## Acceptance Criteria
- [ ] Timeline appears under the players table on `/player?id=XXX`
- [ ] Timeline shows only data for the selected team/player (no cross-team data)
- [ ] Timeline matches the 4-week period from the update page implementation
- [ ] UI follows design system (football green theme, `.card-custom` classes)
- [ ] Timeline is responsive across different screen sizes
- [ ] Timeline meets accessibility standards (WCAG 2.1 AA)
- [ ] No performance regression on player page load
- [ ] Timeline gracefully handles cases with no skill changes
- [ ] Implementation follows existing CHPP and Flask patterns
- [ ] Test coverage for new functionality
