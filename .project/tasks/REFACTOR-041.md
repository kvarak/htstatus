# REFACTOR-041: Consolidate Debug Scripts & Country Data Migration (Consolidates REFACTOR-039)

**Status**: 🎯 Ready to Execute | **Effort**: 2 hours | **Priority**: P4 | **Impact**: Code cleanup and data integrity

## Problem Statement
Multiple country investigation scripts were created that serve similar purposes, adding project noise. Additionally, the CHPP country ID fix prevents future issues but leaves historical incorrect data in database requiring migration.

**Consolidates**: This task combines REFACTOR-039 (country data migration) since both address cleanup of country debugging scripts.

## Implementation
### Phase 1: Data Migration (1 hour)
- Create migration script to update historical country data
- Map wrong IDs to correct ones: 40→46, 180→151, 191→163
- Verify data integrity before and after migration
- Ensure Stats page pie charts show proper country names

### Phase 2: Script Cleanup (1 hour)
- Keep check_unknown_countries.py as the primary utility
- Remove redundant scripts: check_owner_9838.py, check_teams.py, simple_country_check.py, etc.
- Enhance primary script with additional options if needed
- Clean up scripts/ directory structure

## Acceptance Criteria
- [ ] Migration script updates all historical country ID data
- [ ] Country IDs 40, 180, 191 corrected to 46, 151, 163 respectively
- [ ] Stats page pie charts show proper country names
- [ ] Single country investigation utility remains
- [ ] Redundant debug scripts removed
- [ ] Project scripts directory cleaned up
- [ ] Database consistency verified

## Priority
P4 - Code cleanup and data integrity
