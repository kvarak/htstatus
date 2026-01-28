# [CLEANUP-002] Debug Script Consolidation

**Status**: 🎯 Ready to Execute | **Effort**: 1 hour | **Priority**: P3 | **Impact**: Code cleanup, repository hygiene
**Dependencies**: None | **Strategic Value**: Eliminate temporary debugging waste

## Problem Statement
During Custom CHPP debugging, 10+ temporary scripts were created in root and scripts directories for investigation. These debugging scripts represent code waste and reduce repository clarity. Need to consolidate useful debugging functionality and remove temporary files.

## Implementation
1. **Audit Debug Scripts** (15 min):
   - Identify all check_*.py, debug_*.py, test_*.py files created during investigation
   - Review functionality to determine which utilities should be preserved
   - List files: check_goals.py, check_historical.py, debug_stats.py, debug_team_fetch.py, test_parser.py, etc.

2. **Create Consolidated Debug Module** (30 min):
   - Create `scripts/debug_utils.py` with common debugging functions
   - Extract useful functions: goal data analysis, XML inspection, historical data queries
   - Provide command-line interface: `python scripts/debug_utils.py --goals --xml --history`

3. **Clean Repository** (15 min):
   - Remove temporary debug scripts from root directory
   - Remove duplicate debugging approaches
   - Update .gitignore if needed to prevent future debug script commits

## Success Criteria
- Repository cleaned of 10+ temporary debugging scripts
- Single consolidated debug utility module created
- Common debugging workflows preserved and accessible
- Zero loss of useful debugging functionality

## Expected Outcomes
Eliminate temporary debugging waste, improve repository clarity, consolidated debugging toolkit