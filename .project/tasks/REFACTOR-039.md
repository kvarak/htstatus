# REFACTOR-039: Consolidate Country Data Migration Script

## Problem Statement
The CHPP country ID fix prevents future issues but leaves historical incorrect data in database. Need migration script to correct existing wrong country mappings (40→46, 180→151, 191→163).

## Implementation
- Create migration script to update historical country data
- Map wrong IDs to correct ones based on investigation findings
- Verify data integrity before and after migration
- Remove obsolete debugging scripts created during investigation

## Acceptance Criteria
- [ ] Migration script updates all historical country ID data
- [ ] Country IDs 40, 180, 191 corrected to 46, 151, 163 respectively
- [ ] Stats page pie charts show proper country names
- [ ] Remove debugging scripts: check_owner_9838.py, check_teams.py, etc.
- [ ] Database consistency verified

## Priority
P2 - Data integrity and cleanup
