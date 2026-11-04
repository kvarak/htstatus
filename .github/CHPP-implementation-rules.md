# HT Status — CHPP implementation rules

## Authoritative source
All CHPP-related design, feature, and implementation decisions must comply with the
Hattrick CHPP Manual: https://wiki.hattrick.org/wiki/CHPP_Manual

When implementing or reviewing a feature, first classify it as:
1. Clearly allowed.
2. Clearly forbidden.
3. Ambiguous / requires explicit CHPP approval.

Do not implement category 3 without first writing a narrow functional description and
obtaining approval from Hattrick CHPP staff.

## General CHPP rules

### Access and data sources
- Use only official Hattrick CHPP XML/API endpoints.
- Never scrape, parse, download, or infer data from Hattrick HTML pages.
- Never access Hattrick data through unofficial endpoints, browser automation, or
  third-party data dumps.
- Do not redistribute raw Hattrick-derived data to other developers or applications
  unless those recipients are themselves CHPP-approved.
- Every Hattrick request must identify the application and version in the HTTP
  User-Agent string, for example: `HT Status, v1.2.3`.
- Use OAuth-based authentication. Never ask users for, store, transmit, or log their
  Hattrick password or old security code.
- Store only the minimum OAuth tokens needed for the user session. Protect them at
  rest and in transit; never expose them in URLs, logs, client-side storage, error
  messages, or analytics.
- Do not store users’ Hattrick login names or security codes in any format.
- Perform one Hattrick login per application session. Fetch multiple XML resources
  sequentially, not simultaneously. Log out or invalidate the session when finished.
- All Hattrick downloads must be initiated by an explicit user action. Do not use
  timers, cron jobs, background workers, webhooks, or automatic refresh to fetch
  Hattrick data unless Hattrick has explicitly granted an exemption.
- CHPP applications may not write to Hattrick: no automated bidding, training changes,
  lineup changes, transfers, messages, or other game actions.

### Branding, copyright, and payments
- Display the CHPP logo only after the application/function has been approved.
- Include this attribution: “This application uses information from the online game
  service Hattrick.org. This use has been approved by the developers and copyright
  owners of Hattrick.org, Extralives AB.”
- If HT Status ever charges users, clearly state that Hattrick and Extralives take no
  responsibility for payments or ongoing customer support.
- The application and any associated forum, chat, or user community must also follow
  Hattrick’s general game rules.

## Functional boundaries

### Own team
Allowed:
- Historical and current statistics for the authenticated user’s own team.
- Match analysis, training analysis, player development, finances, lineup support, and
  similar tools based on the user’s own data.
- Storage of the user’s own historical team data where needed for the feature.

### Opponents
Allowed:
- Current match-related information for an opponent: match report, ratings, stars,
  lineup where exposed by the API, and league-table context.
- Limited analysis of that current match data, provided it is not an opponent-tracking
  system.
- Data from up to one season back, i.e. 16 weeks, may be fetched and stored when
  necessary for an approved match-analysis function.
- Team logo types and press announcements for any team, but only when the end user is
  an active Hattrick Supporter and the relevant API permission/data is available.

Forbidden:
- Tracking an opponent’s players over time: form changes, injuries, new signings,
  sold players, skill changes, or similar longitudinal changes.
- “Spy” dashboards that summarize recent changes across one or more opponent teams.
- Multi-team comparative statistics, except where HT Status is explicitly approved as
  a statistics site or cup-manager site.
- Historical tracking of teams other than the authenticated user’s own team.

### Transfers
Forbidden:
- Automated transfer bidding, transfer listings, offers, or any transfer interaction.
- Features that automate or facilitate transfer actions in Hattrick.

Allowed:
- Manual copy/paste or user-supplied transfer-evaluation data stored in a separate
  HT Status database, subject to approval of the exact function.

## HT Status-specific implementation policy

### Default feature design
For every new HT Status feature:
- Define one user-visible function per approval item.
- Start from the authenticated user’s own team.
- If opponent data is needed, limit it to a single opponent and a single, explicitly
  selected match or current context.
- Do not retain opponent data beyond what the approved feature requires.
- Prefer ephemeral display over persistent opponent-history storage.
- Do not add scheduled jobs, recurring fetches, or “sync all teams” functionality.
- Do not add bulk imports, federation-wide scans, or multi-team dashboards unless
  separately approved.

### Required feature specification
Before implementation, create a feature record containing:
- Feature name.
- User story: who uses it and what action they take.
- Exact CHPP XML/API resources used.
- Data shown to the user.
- Data stored, retention period, and reason for storage.
- Whether opponent data is used; if so, which opponent and which match/context.
- Whether the feature is free, public, and available in English.
- Confirmation that all downloads are user-initiated.
- Confirmation that no Hattrick write action is performed.

Example approved-style description:
“Own-match analysis: The authenticated manager selects one of their own completed
matches. HT Status requests the match details and displays ratings, possession,
chances, goals, and player stars for that match. No opponent history is collected.”

Example forbidden-style description:
“Opponent monitoring: HT Status regularly checks selected opponents and reports new
players, injuries, form changes, and transfers.”

### Code-review checklist
Reject a pull request if it:
- Introduces HTML scraping or non-XML Hattrick access.
- Adds automatic/background Hattrick downloads.
- Stores passwords, security codes, or unnecessary OAuth material.
- Tracks opponent player or team changes over time.
- Adds multi-team statistics without explicit CHPP approval.
- Adds transfer interaction or automated game actions.
- Sends Hattrick data to an unapproved third party.
- Omits application/version identification or copyright attribution.
- Adds a feature whose scope is broader than its approved functional description.

### Approval workflow
1. Write the narrow functional description before coding.
2. Check it against the CHPP Manual.
3. If ambiguous, ask Hattrick CHPP staff before implementation.
4. Implement only the approved scope.
5. Keep the implemented behavior, UI, stored data, and API usage aligned with the
   approved description.
6. Update the functional description and obtain new approval before expanding scope.
