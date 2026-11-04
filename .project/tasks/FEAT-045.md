# FEAT-045: Team mood

Show the mood around the user's own team: team spirit, self-confidence, fan mood, the fans' expectations (season and next matches) and sponsor popularity, in Hattrick's own words (the cached translations already have TeamSpirit, Confidence, FanMood, FanMatchExpectations, FanSeasonExpectations and Sponsors).

## Feature record (`.github/CHPP-implementation-rules.md`)

- **Feature name:** Team mood
- **User story:** a manager clicks "Update data" and then sees on the team page how the team spirit, confidence, fans and sponsors stand now, and how they changed since earlier updates. On the matches page, each upcoming match shows what the fans expect.
- **CHPP resources:**
  - `training`: `Morale` (TeamSpiritID) and `SelfConfidence` (SelfConfidenceID). This file is already fetched every Update; only the two fields are new.
  - `fans`: `FanMood`, `FanSeasonExpectation`, `FanMatchExpectation` per upcoming match.
  - `economy`: `SponsorsPopularity` and `SupportersPopularity` only. Ignore the money fields.
- **Data shown:** current values as Hattrick words (`ht_term` with English fallback), the change since the previous Update, and a simple trend per season. The fans' expectation goes next to each upcoming match on the matches page.
- **Data stored:** one row per own team per Update (date, team spirit, confidence, fan mood, season expectation, sponsor and supporter popularity), kept like the player snapshots, so the trend can be shown. Match expectations are stored on the upcoming match.
- **Opponent data:** none. Only the user's own team(s).
- **Free, public, English:** yes, same as the rest of the site. Words follow the user's Hattrick language.
- **User-initiated downloads:** yes, only during "Update data" (`app/blueprints/team.py`). No timers or background jobs.
- **Hattrick write actions:** none.
- **CHPP category:** 1 (own-team data, read only). Fans and Economy are still new files for the product, so update the functional description first.

## Functional description (submit before coding)

Title: **Team mood**

> Team spirit, self-confidence, fan mood, the fans' expectations for the season and coming matches, and sponsor popularity for the user's own team(s), shown in Hattrick's words with the change since the user's previous update. Read only, and fetched only when the user clicks "Update data".

Xml files: **Training, Fans, Economy**

Training is part of the denied "Training log" function (DOC-035). Either get DOC-035 approved first and add Fans and Economy here, or list Training in this function too.

## Gotchas

- `Morale` and `SelfConfidence` have an `Available` attribute. Treat "not available" as unknown, not as 0.
- Check the scales against the cached translations: team spirit 0–10, confidence 0–9, fan mood 0–11, season expectation 0–7.
- One Update already makes many calls. Fans and Economy are one call each per team, which is fine.

## Good enough

A small "Team mood" tile on the team page with the six values in words and arrows for changes. The fans' expectation goes on each upcoming match. Then the trend chart, if it's cheap to add.
