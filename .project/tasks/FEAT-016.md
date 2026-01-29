# [FEAT-016] Alternative Leadership Indicators

**Status**: 🎯 Ready to Execute | **Effort**: 30 min | **Priority**: P2 | **Impact**: User value without complexity
**Dependencies**: None | **Strategic Value**: Replace rejected complex visualizations

## Problem Statement
User rejected complex leadership visualizations (radar charts, bubble charts, timelines) but may still want basic leadership insights. Need simple, text-based leadership indicators that provide value without visual complexity.

## Implementation Plan
1. Calculate simple leadership metrics from existing player data:
   - Team Captain indicator (highest leadership skill)
   - Leadership Distribution: Count of High/Medium/Low leadership players
   - Leadership Average: Team average leadership level
   - Leadership Potential: Players with leadership growth opportunity
2. Display as simple text cards on stats page, not charts
3. Use existing Bootstrap card components for consistency

## Acceptance Criteria
- [ ] Replace leadership chart space with simple text metrics
- [ ] Show leadership insights without complex visualizations
- [ ] Use consistent card styling with other stats components
- [ ] Calculate metrics from live player data
- [ ] Fast rendering with no Chart.js dependencies

## Strategic Benefits
- Provides leadership value user might actually want
- No complex charts to maintain or remove later
- Builds foundation for understanding simple vs complex feature preferences
- Quick implementation with immediate user value
