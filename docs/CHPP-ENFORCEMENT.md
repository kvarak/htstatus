# CHPP API policy and its check

CHPP (the Hattrick API) is rate-limited and slow, so the app calls it **only** at:
- `/login` and `/login/oauth` (OAuth flow, `app/blueprints/auth.py`)
- `/update`, the user's explicit "Update" (`app/blueprints/team.py`)

Everything else (page views, settings, voting, admin checks) uses the session (`current_user_id`, `all_teams`) and the database.

## The check

`make check-chpp` runs `scripts/check-chpp-usage.sh`. It is one of the `make test-all` gates and also runs in CI. It searches `app/**/*.py` for `CHPP(`, `get_chpp_client` and `from app.chpp import`, and fails on any match outside:
- `app/blueprints/auth.py` and `app/blueprints/team.py` (`ALLOWED_FILES` in the script);
- `app/chpp/` (the client itself) and docstring examples (`>>> chpp`).

If you add a route that legitimately needs CHPP (a new OAuth step or another explicit update action), add its file to `ALLOWED_FILES` and say why in the commit.

## Pattern for everything else

```python
from app.auth_utils import current_team, get_current_user, require_authentication

@stats_bp.route("/stats")
@require_authentication
def stats():
    teamid, teamname = current_team()   # from the session, validated
    user = get_current_user()           # from the database
    ...                                 # database queries only
```

Data that only CHPP has (bids, series, translations) is fetched during `/update` and stored in the database or the `instance/` JSON cache, then read from there.
