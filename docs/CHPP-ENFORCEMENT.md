# CHPP API policy and its check

HattrickPlanner is a licensed CHPP product. The rules come from the [CHPP Product License Agreement](CHPPProductLicenseAgreement.md) and the [OAuth Guide](OAuthGuide.md); the ids in the XML are explained in [CHPP Data Types](datatypes.md) and [Match event types](MatchEventTypes.md).

CHPP (the Hattrick API) is rate-limited and slow, and the license forbids automated access (5.3), so the app calls it **only** at:
- `/login` and `/login/oauth` (OAuth flow, `app/blueprints/auth.py`)
- `/update`, the user's explicit "Update" (`app/blueprints/team.py`)

Everything else (page views, settings, voting, admin checks) uses the session (`current_user_id`, `all_teams`) and the database.

## The check

`make check-chpp` runs `scripts/check-chpp-usage.sh`. It is one of the `make test-all` gates and also runs in CI. It searches `app/**/*.py` for `CHPP(`, `get_chpp_client` and `from app.chpp import`, and fails on any match outside:
- `app/blueprints/auth.py` and `app/blueprints/team.py` (`ALLOWED_FILES` in the script);
- `app/chpp/` (the client itself) and docstring examples (`>>> chpp`).

If you add a route that legitimately needs CHPP (a new OAuth step or another explicit update action), add its file to `ALLOWED_FILES` and say why in the commit.

The check only sees where a client is created. Helpers that receive a `chpp` client as an argument (`app/utils.py`, `app/opponents.py`, `app/translations.py`, ...) are fine, as long as they are only called from the allowed routes.

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

Data that only CHPP has (bids, series, translations, training) is fetched during `/update` and stored in the database or the `instance/` JSON cache, then read from there.

## What the license requires, and how the app follows it

| License rule | In HattrickPlanner |
| --- | --- |
| 5.1 Never ask for the Hattrick login or password; use OAuth | Login goes through OAuth (`app/chpp/auth.py`: OAuth 1.0a, GET, HMAC-SHA1, always an `oauth_callback`). The username/password on `/login` is the user's own HattrickPlanner account, never the Hattrick one. |
| 5.2 Don't share data with other apps or sites | No exports to other services, no public API. `app/seo.py` keeps team and player data out of public pages and share tags. |
| 5.3 No automated access without consent | No cron jobs, schedulers or background tasks call CHPP. Server cron (`deploy/`) only deploys images and makes backups. Every CHPP call starts with the user clicking login or Update. |
| 5.4 Only CHPP XML, minimum data, automated downloads at most once a day | Data comes only from `chppxml.ashx`, and only when the user starts it. Stored data is reused: pages read the database, and opponent setups are only fetched for matches that don't have one yet. |
| 4.1 Keep the functional description up to date | When a feature uses a new CHPP file or new data (e.g. other teams' matches), update the description on the product page on Hattrick. |
| 6.1 No exploiting bugs or cheating | Analysis only; the app never sends orders to Hattrick. |
| 6.2 / 9.1 Supporter-only data; don't replace Hattrick Supporter | Don't build features that copy Supporter functions without approval in the functional description. |
| 7.2 No Hattrick logo or site graphics | Only the CHPP logo may be used; the app has its own icons. |
| 8.1 A published privacy policy, followed | See "Needs action" below. |
| OAuth scopes (write permissions) | The app asks for no scopes (`scope=""` in `app/blueprints/auth.py`), so it can only read. Asking for `set_matchorder`, `set_training`, `place_bid`, ... would need a new functional description and user consent. |

## Checklist for a new feature that uses CHPP

1. Fetch the data during `/update` (or login), store it, and read it from the database on page views.
2. Download only what the feature needs, and skip what is already stored.
3. Only read data the user may see in Hattrick (e.g. `matchorders` and `matchlineup` are limited to the user's own teams).
4. Update the functional description on Hattrick if the feature uses new CHPP files or new kinds of data.
5. Run `make check-chpp` (part of `make test-all`).
