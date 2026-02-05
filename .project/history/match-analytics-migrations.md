# Match Analytics Migration Evolution

**Date**: February 5, 2026
**Task**: REFACTOR-107
**Status**: Documentation Only (Migrations Already in Production)

## Migration Sequence Analysis

The match analytics feature evolved through 4 sequential migrations due to iterative API discovery and schema alignment with CHPP structure:

### 1. 5dfd6c919450 - Initial Enhanced Analytics
**Date**: 2026-02-05 07:38:10
**Added**: 20 fields
- `home/away_team_possession` (Float) - Later removed
- `home/away_team_shots` - Later removed
- `home/away_team_shots_on_target` - Later removed
- `home/away_team_tackles` - Later removed
- `home/away_team_passes` - Later removed
- `home/away_team_rating` (Float) - Kept
- `attendance` (Integer) - Kept
- `weather` (String) - Replaced with weather_id
- `referee_name/country` (String) - Kept, expanded
- `home/away_team_formation` (String) - Kept
- `home/away_team_tactic` (String) - Kept

**Rationale**: Initial implementation based on expected CHPP API structure before full API exploration.

### 2. 75ec6d294370 - Align with CHPP Structure
**Date**: 2026-02-05 13:47:12
**Added**: 14 fields | **Removed**: 10 fields
- Added possession by halves (4 fields): `possession_first_half_home/away`, `possession_second_half_home/away`
- Added chance breakdown (10 fields): `home/away_team_chances_left/center/right/special/other`
- Removed aggregate fields: shots, shots_on_target, tackles, passes, possession averages

**Rationale**: CHPP API returns possession by halves, not averages. Chances are broken down by position, not total shots. Removed unsupported fields.

### 3. f03b862df0b3 - Comprehensive Match Details
**Date**: 2026-02-05 15:13:17
**Added**: 34 fields | **Modified**: 1 field (weather → weather_id)
- Positional ratings (12 fields): `home/away_team_rating_left/mid/right_def/att`
- Set pieces ratings (4 fields): `home/away_team_rating_set_pieces_def/att`
- Arena capacity (4 fields): `arena_capacity_terraces/basic/roof/vip`
- Weather ID (1 field): `weather_id` (Integer, replacing String weather)
- Match metadata (2 fields): `added_minutes`, `referee_id`
- Officials details (3 fields): `referee_country_id`, `referee_team_id/name`
- Team presentation (4 fields): `home/away_team_dress_uri`, `home/away_team_attitude`
- Tactical details (4 fields): `home/away_team_tactic_type/skill`

**Rationale**: Full CHPP matchdetails and matchlineup API exploration revealed extensive analytics available. Added all discoverable fields for comprehensive match analysis.

### 4. 831d57cb541f - User Activity Tracking
**Date**: 2026-02-05 16:32:54
**Table**: users (not match)
**Added**: 2 fields
- `c_matches_archive` (Integer) - Counter for archive downloads
- `last_matches_archive` (DateTime) - Timestamp of last archive download

**Rationale**: Separate concern - user activity tracking for feature usage analytics, not match data.

## Net Schema Impact

**Match Table**: +68 fields (20 added, 10 removed, +24 added, +34 added = 78 - 10 = 68)
**Users Table**: +2 fields

## Why Not Consolidate?

**Database Protection Rule**: These migrations are already applied in production. Consolidating would require:
1. Creating new migration that duplicates final state
2. Manually marking old migrations as applied without running them
3. Risk of schema drift between dev/staging/production environments
4. Potential data loss if rollback needed

**Hobby Project Principle**: Production database integrity > cleaner version history

## Lessons Learned

1. **API Exploration First**: Should have fully explored CHPP matchdetails/matchlineup APIs before first migration
2. **Schema Planning**: Could have avoided add/remove cycle with upfront API documentation review
3. **Migration Batching**: Non-urgent schema additions could be batched into single migration window
4. **Separation of Concerns**: Migration 4 (user tracking) correctly separated from match analytics migrations

## Recommendation for Future

- Complete CHPP API exploration BEFORE creating migrations
- Use `docs/chpp/` documentation to validate schema design
- Batch non-critical fields into scheduled migration windows
- Keep separate concerns in separate migrations (match analytics vs user tracking)

## Task Conclusion

**REFACTOR-107 Status**: Cannot be executed as originally scoped due to production database protection rules.
**Alternative Completed**: Documented migration evolution rationale for future reference.
**Action Required**: Mark task as OBSOLETE in backlog - migrations are working, consolidation would risk production data.
