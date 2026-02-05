# CHPP API Policy Enforcement

**Status**: ✅ ACTIVE - Integrated into `make test-all` quality gates
**Created**: January 30, 2026 (INFRA-038)
**Purpose**: Enforce CHPP API usage policy through automated static analysis

## Quick Start

```bash
# Check CHPP policy compliance
make check-chpp

# Full quality gates (includes CHPP check)
make test-all
```

## Policy Summary

**CHPP API calls are EXPENSIVE and RATE-LIMITED.**

### ✅ ALLOWED Routes
- `/login` - OAuth authentication
- `/callback` - OAuth callback
- `/update` - Explicit user-triggered data sync

### ❌ FORBIDDEN Routes
- Page navigation (stats, feedback, player lists, etc.)
- Voting, commenting, quick interactions
- Form submissions
- Admin actions

**Alternative**: Use `session["current_user_id"]` + database queries

## How It Works

### Static Analysis Script
`scripts/check-chpp-usage.sh` scans all Python files in `app/**/*.py` for:

1. **`CHPP(`** - Direct CHPP client initialization
2. **`get_chpp_client`** - Helper function that wraps CHPP
3. **`from app.chpp import`** - CHPP module imports

**Exceptions**:
- `app/blueprints/auth.py` - Login/OAuth flows
- `app/blueprints/team.py` - Update route only
- `app/chpp/` directory - CHPP client implementation
- Docstring examples (lines with `>>> chpp`)

### Integration Points

1. **Makefile Quality Gate** (Primary)
   ```makefile
   GATES = fileformat lint security-bandit security-deps test-coverage-files check-chpp
   ```

2. **Manual Check**
   ```bash
   ./scripts/check-chpp-usage.sh
   ```

3. **Pre-Commit Hook** (Recommended - not yet implemented)
   ```bash
   # .git/hooks/pre-commit
   ./scripts/check-chpp-usage.sh || exit 1
   ```

## Output Format

**Success** (0 violations):
```
✅ CHPP API usage policy: PASSED
   All CHPP calls are in approved routes (login, OAuth, update)
```

**Failure** (violations found):
```
❌ CHPP API usage policy: FAILED

Found 1 unauthorized CHPP API calls

app/blueprints/stats.py:190:        chpp = get_chpp_client(session)

Fix: Remove CHPP calls from unauthorized routes
See: .github/agents/htplanner-ai-agent.md#chpp-api-usage-critical
```

## Current Status

**Quality Gates**: 7/7 (pending REFACTOR-064)
- ✅ File Format
- ✅ Code Quality (lint)
- ✅ Bandit Security
- ⚠️ Dependency Analysis (13 warnings)
- ✅ Test Coverage (files)
- ⚠️ Test Coverage (39.5% - below 50% target)
- ❌ **CHPP Policy** (1 violation in stats.py)

**Known Violations**:
1. **REFACTOR-064**: `app/blueprints/stats.py:190` - Remove get_chpp_client() call

## Implementation Pattern

### ❌ Before (CHPP API call)
```python
from app.chpp_utilities import get_chpp_client

@stats_bp.route("/")
def stats():
    chpp = get_chpp_client(session)  # ❌ Expensive CHPP call
    user_context = get_current_user_context(chpp)
    # ... stats logic
```

### ✅ After (Session + Database)
```python
from models import User

@stats_bp.route("/")
def stats():
    # ✅ Session-only authentication
    if "current_user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["current_user_id"]
    user = User.query.filter_by(ht_id=user_id).first()
    if not user:
        return redirect(url_for("auth.login"))

    # ✅ Minimal user context from session
    user_context = {
        "user": user,
        "teams": session.get("all_teams", []),
        "team_names": session.get("all_team_names", [])
    }
    # ... stats logic using database only
```

## Documentation

**Full Policy**: [.github/agents/htplanner-ai-agent.md](.github/agents/htplanner-ai-agent.md#chpp-api-usage-critical)

**Implementation Examples**:
- ✅ `app/blueprints/feedback.py` - Correct pattern (session + database)
- ✅ `app/blueprints/auth.py` - Allowed CHPP usage (OAuth)
- ❌ `app/blueprints/stats.py` - Current violation (needs fix)

## Maintenance

**When to Update Allowed Files**:
1. New OAuth-related route added
2. Additional explicit update endpoint created
3. Migration of functionality to different blueprint

**Edit**: `scripts/check-chpp-usage.sh` line 20-23:
```bash
declare -a ALLOWED_FILES=(
    "app/blueprints/auth.py"
    "app/blueprints/team.py"  # Contains /update route
    # Add new allowed files here
)
```

## Future Enhancements

1. **Pre-Commit Hook** - Block commits with violations (INFRA-039)
2. **Route Testing with Mocks** - pytest-mock spy to detect runtime CHPP calls (TEST-037)
3. **CI/CD Integration** - GitHub Actions quality gate
4. **Decorator Enforcement** - `@chpp_required` decorator to whitelist allowed routes

## Recent Improvements

### Historical Data Filtering (February 4, 2026)
**Problem**: CHPP `matchesarchive` endpoint with season parameters was returning confusing historical data from inactive team periods (e.g., 2005 "Root Brothers FC" data mixed with current "Dalby Stenbrotters FC" data).

**Solution**: Modified `downloadMatches()` function in `app/utils.py` to:
- Use date-based filtering instead of season numbers
- Limit archive downloads to last 12 months only
- Prevent retrieval of historical data from team ID reuse scenarios

**Result**: Clean match history aligned with CHPP's performance limits and current team activity.
