# [REFACTOR-036] Consolidate Activity Tracking Pattern

**Status**: 🔮 Future | **Effort**: 2-3 hours | **Priority**: P3 | **Impact**: Code maintainability and consistency
**Dependencies**: None | **Strategic Value**: Reduce code duplication and improve maintainability

## Problem Statement
Activity tracking is currently implemented with repeated database query patterns across all routes (`db.session.query(User).filter_by(ht_id=session["current_user_id"]).first()`). This creates code duplication, potential performance overhead, and maintenance burden.

## Implementation
1. **Create Activity Tracking Decorator** (1-2 hours):
   - Implement `@track_activity('activity_type')` decorator pattern
   - Centralize user lookup and database commit logic
   - Add proper error handling for missing users

2. **Migrate Existing Routes** (1 hour):
   - Replace manual activity tracking calls with decorator usage
   - Remove duplicated database queries from route implementations
   - Test all activity types still function correctly

## Acceptance Criteria
- Single decorator handles all activity tracking logic
- All routes use consistent pattern without code duplication
- Performance improvement from reduced database queries
- No functional regressions in activity counter behavior
- Clear documentation for future route development

## Expected Outcomes
Reduced code duplication, improved maintainability, consistent error handling, potential performance improvements from optimized database access patterns