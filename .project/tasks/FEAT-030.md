# FEAT-030: Series League Table with Next Round Insights

**Dependencies**: CHPP API integration (completed), Team models (completed), Matches system (FEAT-029 recommended) | **Strategic Value**: League context awareness, competitive intelligence, strategic planning

## CHPP API Support ✅

**Fully supported by documented APIs:**
- [leaguedetails](../../docs/chpp/api-reference-leaguedetails.md) - Complete league standings
- [leaguefixtures](../../docs/chpp/api-reference-leaguefixtures.md) - Upcoming fixtures and form analysis
- [teamdetails](../../docs/chpp/api-reference-teamdetails.md) - Team information

**Could benefit from undocumented APIs:**
- `matchdetails` (not yet documented) - Detailed form analysis from recent matches

## Problem Statement

Currently, HattrickPlanner lacks a league table view that provides strategic context for the user's position in their series. Users need a comprehensive series overview that combines current league standings with tactical insights for upcoming matches. This feature would enable users to:

- View complete league table with current standings and statistics
- Understand their competitive position relative to other teams
- Analyze upcoming opponents in the context of league performance
- Identify key matches that could impact league positioning
- Plan tactical approaches based on teams' relative league standing

Without this context, users must manually navigate to Hattrick to understand their league situation, losing the strategic integration that HattrickPlanner could provide for tactical decision-making.

## Implementation

**Phase 1: League Data Integration (2-3 hours)**
- Fetch series/league table data from CHPP API
- Create Series/League model for storing league information
- Implement league position tracking and updates
- Add league data to regular team update workflows

**Phase 2: League Table Display (2-3 hours)**
- Create comprehensive league table with standings, points, goal difference
- Show team statistics: matches played, wins, draws, losses
- Highlight user's team position with visual emphasis
- Add sorting capabilities by points, goal difference, form

**Phase 3: Next Round Insights (3-4 hours)**
- Display upcoming fixtures for all teams in the series
- Highlight user's next opponent with enhanced details
- Show opponent's recent form and league trajectory
- Add tactical preparation links to opponent analysis

**Phase 4: Strategic Intelligence (2-3 hours)**
- Identify key matches that could affect user's league position
- Show promotion/relegation scenarios and key rivals
- Add league context to match importance (title race, relegation battle)
- Integrate with formation tester for opponent-specific preparation

## Acceptance Criteria

**League Table Core:**
- [ ] Complete series table showing all teams with current standings
- [ ] User's team highlighted with clear visual distinction
- [ ] Table includes: position, team name, matches played, wins, draws, losses, goals for/against, goal difference, points
- [ ] Sortable by any column (position, points, goal difference, form)
- [ ] Mobile-responsive table with essential columns visible

**Next Round Integration:**
- [ ] Upcoming fixtures displayed for all teams in the series
- [ ] User's next opponent highlighted with enhanced information
- [ ] Quick access to opponent details and recent form
- [ ] Visual indicators for match importance (relegation, promotion, derby)

**Strategic Context:**
- [ ] League position trends and recent form indicators
- [ ] Points required for promotion/avoiding relegation calculations
- [ ] Key rival tracking and head-to-head comparisons
- [ ] Integration with tactical preparation tools

**Data Management:**
- [ ] League data updated with regular team updates
- [ ] Efficient caching for league information across users
- [ ] Proper error handling for league API failures
- [ ] Historical league position tracking for trends

**Navigation & UX:**
- [ ] Series route accessible from team context (/series?id=teamid)
- [ ] Clear navigation from series to opponent analysis
- [ ] League table loads quickly with responsive design
- [ ] Intuitive sorting and filtering options

## Technical Notes

**CHPP Integration**:
- Use series/league API endpoints for complete table data
- Respect rate limits when fetching league information
- Consider caching league data as it updates less frequently than player data

**Database Design**:
- Create League/Series model for storing competition information
- Track historical league positions for trend analysis
- Optimize queries for league table display performance

**User Experience**:
- Focus on actionable intelligence rather than just data display
- Integrate with existing tactical preparation workflows
- Provide clear visual hierarchy for different types of information

**Performance Considerations**:
- Cache league table data to avoid repeated API calls
- Implement efficient database queries for league standings
- Consider pagination for large league divisions

This feature complements FEAT-008 (Next Game Analyser) by providing league context for opponent analysis, and builds upon FEAT-029 (Matches System) by adding strategic intelligence to match scheduling.
