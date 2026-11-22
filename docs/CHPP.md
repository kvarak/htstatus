# CHPP: rules and how we follow them

HattrickPlanner is an approved CHPP product. Everything that touches Hattrick data follows this page. Sources: the [CHPP Manual](https://wiki.hattrick.org/wiki/CHPP_Manual), the [CHPP Product License Agreement](CHPPProductLicenseAgreement.md) and the [OAuth Guide](OAuthGuide.md). What we may use is listed in our functional description ([.project/FunctionalDescription.md](../.project/FunctionalDescription.md), a copy of the product page on Hattrick). Ids in the XML: [datatypes.md](datatypes.md), [MatchEventTypes.md](MatchEventTypes.md), endpoints: [chpp/](chpp/README.md).

## When we call CHPP

Only when the user asks for it (license 5.3, no automated access):
- `/login` and `/login/oauth` (OAuth, `app/blueprints/auth.py`)
- `/update`, the "Update data" button (`app/blueprints/team.py`)

Page views, settings, voting and admin pages use the session and the database. No cron jobs, timers or background workers call CHPP; the server cron only deploys and backs up. Requests run one after another, never in parallel.

`make check-chpp` (part of `make test-all` and CI) runs `scripts/check-chpp-usage.sh`: `CHPP(`, `get_chpp_client` and `from app.chpp import` may only appear in `auth.py`, `team.py` and `app/chpp/`. Helpers that receive a `chpp` client (`app/utils.py`, `app/opponents.py`, `app/translations.py`) may only be called from those routes. A new route that really needs CHPP goes into `ALLOWED_FILES` with the reason in the commit.

```python
@stats_bp.route("/stats")
@require_authentication
def stats():
    teamid, teamname = current_team()   # session, validated
    user = get_current_user()           # database
    ...                                 # database queries only
```

## Rules

**Access**
- Only the CHPP XML files (`chppxml.ashx`); never scrape Hattrick pages or use other sources.
- OAuth only (`app/chpp/auth.py`). Never ask for, store or log the Hattrick password. The password on `/login` is the user's own HattrickPlanner password.
- Read only: no scopes are requested (`scope=""`), so no bids, training, lineups or other game actions.
- Every request identifies the app in the User-Agent (`HattrickPlanner, v<version>`, set in `app/chpp/`).

**Data**
- Download only what a feature needs, and reuse what is stored (license 5.4).
- OAuth tokens stay on the server: never in URLs, logs, error messages or client-side storage. They live in the database (the `User` row); the cookie session only holds the user id, and CHPP clients read the tokens from the database.
- No sharing with other apps or sites (license 5.2). Public pages and share tags never contain team or player data (`app/seo.py`).
- Open questions in DOC-037: storing the Hattrick login name, invalidating the token at logout.

**Own team and opponents**
- Own team: statistics, history, training, matches and player development are fine, and may be stored.
- Opponents: only what helps with one upcoming or played match (results, ratings, lineup, league table), at most one season back, and kept only as long as the feature needs it. Update prunes scouting matches to the current opponents' last 10 finished matches (`prune_opponent_matches` in `app/opponents.py`); the "Next game scouting" function still needs submitting to Hattrick (INFRA-094, [.project/tasks/INFRA-094.md](../.project/tasks/INFRA-094.md)).
- Not allowed: following other teams over time (their players' skills, form, injuries, transfers), "spy" overviews, or statistics comparing many teams without approval (the admin training speed overview: DOC-037).

**Branding and privacy**
- Show this sentence (in the "Thanks to" box on the home page, `app/templates/main.html`): "This app uses information from the online game service Hattrick.org. This use has been approved by the developers and copyright owners of Hattrick.org, Extralives AB."
- Only the CHPP logo, never the Hattrick logo or site graphics (license 7.2).
- A published privacy policy (license 8.1): the public `/privacy` page, linked from the footer. Keep it true when storing new data; users delete their account themselves in Settings (`app/account.py`).
- Don't copy Hattrick Supporter features without approval (license 9.1).

## A new feature that uses CHPP

1. Write the function for the product page first: title, one or two sentences (whose data, what is shown, "read only, fetched only when the user clicks Update data") and the XML files. One function per user-visible feature.
2. If it's unclear whether it's allowed (opponent data, data from many teams), ask CHPP staff before building it.
3. Fetch during Update, store, and read from the database on page views. Skip what is already stored.
4. Note in the todo item or its task file which XML files it uses, what is stored and for how long, and whether opponent data is involved.
5. Run `make check-chpp`. Keep the feature within what the approved text says; a bigger feature needs an updated text first.
