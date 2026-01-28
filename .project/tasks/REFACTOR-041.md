# REFACTOR-041: Consolidate Debug Scripts

## Problem Statement
Multiple country investigation scripts were created that serve similar purposes, adding project noise. These should be consolidated into a single parameterized utility.

## Implementation
- Keep check_unknown_countries.py as the primary utility
- Remove redundant scripts: check_owner_9838.py, check_teams.py, simple_country_check.py, etc.
- Enhance primary script with additional options if needed
- Move to a dedicated utilities folder or remove entirely after data fix

## Acceptance Criteria
- [ ] Single country investigation utility remains
- [ ] Redundant debug scripts removed
- [ ] Project scripts directory cleaned up
- [ ] Documentation updated if utility is kept

## Priority
P2 - Reduce waste and project noise