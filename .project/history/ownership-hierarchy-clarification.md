# Hattrick Ownership Hierarchy Clarification

**Date**: 2026-01-26
**Issue**: Confusion between User IDs and Team IDs in session and database
**Status**: Clarified and documented

## Correct Hattrick Hierarchy

```
User (userId=182085 "kvarak")
  └─> owns Team (teamId=9838 "Dalby Stenbrotters")
       └─> owns Players (ht_id=462840653 "Malek El Beik", etc.)
```

### Database Schema
- **users.ht_id**: User ID (e.g., 182085)
- **Players.owner**: Team ID (e.g., 9838) - **NOT user ID**
- Historical data correctly uses Team ID in owner field

### Session Variables
- **session['current_user_id']**: User ID (182085)
- **session['all_teams']**: List of Team IDs owned by user ([9838, ...])
- **session['team_id']**: Currently active Team ID (9838)

## The Bug

### Root Cause
In [auth.py](../app/blueprints/auth.py), when `current_user._teams_ht_id` fails (due to YouthTeamId error or other CHPP issues), the fallback code incorrectly uses `current_user.ht_id` (user ID 182085) as the team ID:

```python
# INCORRECT FALLBACK
try:
    all_teams = current_user._teams_ht_id  # Should get [9838]
except:
    fallback_team_id = current_user.ht_id  # 182085 (user ID, not team ID!)
    session["all_teams"] = [fallback_team_id]  # Wrong!
```

### Impact
1. URL becomes `/player?id=182085` (user ID instead of team ID)
2. Query: `Players.filter_by(owner=182085)` finds nothing
3. Historical data query: `Players.filter_by(owner=9838)` finds 2138 records
4. Users see "no historical data" even though database has 483 dates

## The Fix

### Immediate Changes (✅ DONE)
1. **Reverted owner field usage**: Changed from `current_user_id` back to `teamid` in:
   - [team.py](../app/blueprints/team.py) line 294: `thisplayer["owner"] = teamid`
   - [player.py](../app/blueprints/player.py) lines 138, 146: `filter_by(owner=teamid)`

2. **Added warnings**: Auth fallback now logs when using user ID as team ID

### Remaining Work (📋 BUG-010)
Need to fix [auth.py](../app/blueprints/auth.py) session setup:
- Properly fetch team IDs when `_teams_ht_id` fails
- Consider adding user-to-team mapping table in database
- Investigate why `_teams_ht_id` fails with YouthTeamId error

## Data Verification

```bash
# Players.owner values in database:
owner=9838, records=2138      # Team ID (correct)
owner=182085, records=23      # User ID (incorrect - from buggy code)
owner=0, records=6161         # Unknown/legacy data

# Sample player for team 9838:
ht_id=462840653, name=Malek El Beik, owner=9838, dates=139 records
```

## Naming Convention

To avoid confusion:
- **user_id**: Always refers to Hattrick user ID (182085)
- **team_id** / **teamid**: Always refers to Hattrick team ID (9838)
- **Players.owner**: Team ID (9838) - never user ID
- **current_user_id**: Session variable containing user ID
- **all_teams**: Session list of team IDs owned by current user

## References

- **Issue Discovery**: User question "are you sure we save data backwards compatible way?"
- **Database Query**: `SELECT DISTINCT owner, COUNT(*) FROM players GROUP BY owner`
- **CHPP API**: `chpp.user()` returns user object with `ht_id` = user ID
- **CHPP API**: `user._teams_ht_id` should return list of team IDs owned by user
- **Bug Tracking**: [BUG-010] in backlog.md

## Testing Checklist

To verify fix works:
- [ ] Login as user 182085 (kvarak)
- [ ] Verify session['all_teams'] = [9838] (team ID, not 182085)
- [ ] Access `/player?id=9838` (team ID)
- [ ] Verify query returns 2138 historical records
- [ ] Check skill progression indicators display
- [ ] Verify training graphs populate with 483 dates
- [ ] Run update data and confirm new records use owner=9838
