# REFACTOR-064: Remove CHPP API Call from Stats Blueprint

## Problem Statement
The stats blueprint (app/blueprints/stats.py) calls `get_chpp_client()` on line 190, violating the CHPP API usage policy. Stats routes should display existing database data only - they do not need live CHPP API calls.

**Detected by**: `make check-chpp` quality gate
**Policy Reference**: .github/agents/htplanner-ai-agent.md#chpp-api-usage-critical

## Current Violation
```python
# app/blueprints/stats.py:190
chpp = get_chpp_client(session)
# This triggers expensive CHPP API calls for stats display
```

## CHPP Policy (Enforced)
**ONLY call CHPP API in these scenarios**:
1. Login/Authentication (`/login`, `/callback`)
2. Explicit "Update Data" Action (`/update` route)

**NEVER call CHPP API for**:
- Page navigation (stats, feedback, any view-only page)
- Voting, commenting, or any quick user interaction
- Form submissions (use session data)
- Admin actions (check User.role from database)

## Implementation
1. **Remove**: `from app.chpp_utilities import get_chpp_client` import
2. **Remove**: `chpp = get_chpp_client(session)` call
3. **Replace with**: Session-based authentication check:
   ```python
   if "current_user_id" not in session:
       return redirect(url_for("auth.login"))
   user_id = session["current_user_id"]
   user = User.query.filter_by(ht_id=user_id).first()
   ```
4. **Use**: Database queries only for stats display
5. **Pattern**: Follow feedback.py blueprint implementation (session + database only)

## Acceptance Criteria
- [ ] `make check-chpp` passes (0 violations)
- [ ] Stats routes use session authentication only
- [ ] No CHPP client initialization in stats.py
- [ ] Stats display works correctly with database data
- [ ] All tests pass (`make test-all`)
- [ ] Quality gates pass (7/7)

## Scout Mindset Opportunities
- Audit other blueprints for similar violations
- Add inline comments marking session-only authentication pattern
- Consider adding pytest-mock tests to verify no CHPP calls
