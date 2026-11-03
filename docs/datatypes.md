# CHPP Data Types

The value types and enumerations used by the CHPP XML files, from the official CHPP documentation. The endpoint references in [chpp/](chpp/README.md) use these names for fields such as `MatchTypeID` or `SkillLevel`.

## Contents

- [Basic types](#basic-types)
- **Matches**: [MatchTypeID](#matchtypeid), [MatchStatus](#matchstatus), [MatchRuleID](#matchruleid), [ArenaMatchType](#arenamatchtype), [MatchTacticType](#matchtactictype), [MatchTeamAttitude](#matchteamattitude), [coachModifier](#coachmodifier), [MatchRating](#matchrating), [MatchPositionID](#matchpositionid), [MatchRoleID](#matchroleid), [MatchRoleOldID](#matchroleoldid), [MatchBehaviourID](#matchbehaviourid), [matchOrderTypeID](#matchordertypeid), [matchPart](#matchpart), [WeatherID](#weatherid)
- **Players**: [SkillID](#skillid), [SkillLevel](#skilllevel), [SpecialtyID](#specialtyid), [PlayerCategoryID](#playercategoryid), [PlayerAgreeability](#playeragreeability), [PlayerAggressiveness](#playeraggressiveness), [PlayerHonesty](#playerhonesty), [positionChange](#positionchange)
- **Team and club**: [TeamSpiritID](#teamspiritid), [SelfConfidenceID](#selfconfidenceid), [SupportersPopularityID](#supporterspopularityid), [trainingType](#trainingtype), [StaffType](#stafftype), [NationalTeamStaffType](#nationalteamstafftype), [supporterTier](#supportertier), [trackingTypeId](#trackingtypeid)
- **Competitions**: [CupID](#cupid), [CupLevel](#cuplevel), [CupLevelIndex](#cuplevelindex), [WorldCupID](#worldcupid), [TournamentType](#tournamenttype), [trophyID](#trophyid), [AchievementCategoryID](#achievementcategoryid), [GenderID](#genderid), [LeagueSystemID](#leaguesystemid)
- **Youth and scouting**: [YouthLeagueStatusID](#youthleaguestatusid), [YouthLeagueType](#youthleaguetype), [ScoutSearchTypeID](#scoutsearchtypeid), [ScoutTravelTypeID](#scouttraveltypeid), [ScoutCommentTypeID](#scoutcommenttypeid), [ScoutCommentSkillTypeID](#scoutcommentskilltypeid)
- **Other**: [BookmarkTypeID](#bookmarktypeid), [sourceSystem](#sourcesystem)
- **Match orders**: [lineup](#lineup)

## Basic types

A `*` after a type means the value may be empty.

| Type | Values |
| --- | --- |
| Boolean | `true` or `false` |
| Boolean\* | `true`, `false` or empty (not given) |
| Bit | `0` (false) or `1` (true) |
| Char | One character, `a-Z` or `0-9` |
| DateTime | `YYYY-MM-DD HH:MM:SS` in Swedish time (CET/CEST), see RFC 3339 section 5.6 / ISO 8601 |
| DateTime\* | As DateTime; `0001-01-01 00:00:00` means empty |
| Decimal | Decimal number: more precise than Float but with a smaller range, used for money-like values |
| Float | Floating-point number |
| Integer | Signed integer |
| unsigned Integer | Integer from `0` |
| unsigned Integer\* | As unsigned Integer, or empty |
| String | Text |
| String\* | Text, or empty |
| String (HTML encoded) | HTML-encoded text |
| URI | Uniform Resource Identifier |
| Money | Integer amount in SEK (Swedish krona) |

## Matches

### MatchTypeID

Stored as `Match.matchtype`; the matches page and scouting treat `1` as league and `3` as cup.

| Value | Description |
| --- | --- |
| `1` | League match |
| `2` | Qualification match |
| `3` | Cup match (standard league match) |
| `4` | Friendly (normal rules) |
| `5` | Friendly (cup rules) |
| `6` | Not currently in use, but reserved for international competition matches with normal rules (may or may not be implemented at some future point). |
| `7` | Hattrick Masters |
| `8` | International friendly (normal rules) |
| `9` | International friendly (cup rules) |
| `10` | National teams competition match (normal rules) |
| `11` | National teams competition match (cup rules) |
| `12` | National teams friendly |
| `50` | Tournament League match |
| `51` | Tournament Playoff match |
| `61` | Duel |
| `62` | Ladder match |
| `80` | Preparation match |
| `100` | Youth league match |
| `101` | Youth friendly match |
| `102` | RESERVED |
| `103` | Youth friendly match (cup rules) |
| `104` | RESERVED |
| `105` | Youth international friendly match |
| `106` | Youth international friendly match (Cup rules) |
| `107` | RESERVED |

### MatchStatus

The matches XML sends the status as text (`UPCOMING`, `ONGOING`, `FINISHED`), stored in `Match.status`.

| Value | Description |
| --- | --- |
| `0` | Not Started |
| `1` | Ongoing |
| `2` | Finished |

### MatchRuleID

| Value | Description |
| --- | --- |
| `0` | No rules |
| `1` | Homegrown players |
| `2` | Under 20 (incl. 20) |
| `3` | Over 33 (incl. 33) |

### ArenaMatchType

| Value | Description |
| --- | --- |
| `All` | Show statistics for all types of games. |
| `CompOnly` | Shows statistics for all competition games. |
| `LeagueOnly` | Shows statistics only for series games. |
| `FriendlyOnly` | Shows statistics only for friendly games. |

### MatchTacticType

Stored as `home_team_tactic_type` / `away_team_tactic_type` on `Match` and named in `TACTIC_NAMES` in `app/opponents.py`. There are no values 5 and 6.

| Value | Description |
| --- | --- |
| `0` | Normal |
| `1` | Pressing |
| `2` | Counter-attacks |
| `3` | Attack in the middle |
| `4` | Attack in wings |
| `7` | Play creatively |
| `8` | Long shots |

### MatchTeamAttitude

| Value | Description |
| --- | --- |
| `-1` | Play it cool |
| `0` | Normal |
| `1` | Match of the season |

### coachModifier

| Value | Description |
| --- | --- |
| `-10` | 100% defensive |
| `-9` | 90% defensive |
| `-8` | 80% defensive |
| `-7` | 70% defensive |
| `-6` | 60% defensive |
| `-5` | 50% defensive |
| `-4` | 40% defensive |
| `-3` | 30% defensive |
| `-2` | 20% defensive |
| `-1` | 10% defensive |
| `0` | Neutral |
| `1` | 10% offensive |
| `2` | 20% offensive |
| `3` | 30% offensive |
| `4` | 40% offensive |
| `5` | 50% offensive |
| `6` | 60% offensive |
| `7` | 70% offensive |
| `8` | 80% offensive |
| `9` | 90% offensive |
| `10` | 100% offensive |

### MatchRating

Each `SkillLevel` split into four sub-levels (very low, low, high, very high).

| Value | Description |
| --- | --- |
| `1` | very low disastrous |
| `2` | low disastrous |
| … | … |
| `80` | very high divine |

### MatchPositionID

| Value | Description |
| --- | --- |
| `1` | Keeper |
| `2` | Right back |
| `3` | Central defender #1 |
| `4` | Central defender #2 |
| `5` | Left back |
| `6` | Right winger |
| `7` | Inner midfield #1 |
| `8` | Inner midfield #2 |
| `9` | Left winger |
| `10` | Forward #1 |
| `11` | Forward #2 |

### MatchRoleID

Values 17–35 are the same as in `MatchRoleOldID`.

| Value | Description |
| --- | --- |
| `100` | Keeper |
| `101` | Right back |
| `102` | Right central defender |
| `103` | Middle central defender |
| `104` | Left central defender |
| `105` | Left back |
| `106` | Right winger |
| `107` | Right inner midfield |
| `108` | Middle inner midfield |
| `109` | Left inner midfield |
| `110` | Left winger |
| `111` | Right forward |
| `112` | Middle forward |
| `113` | Left forward |
| `114` | Substitution (Keeper) |
| `115` | Substitution (Defender) |
| `116` | Substitution (Inner midfield) |
| `117` | Substitution (Winger) |
| `118` | Substitution (Forward) |
| `119` | Substitution (Wing back) |
| `120` | Substitution (Extra) |
| `200` | Substitution (Keeper) |
| `201` | Substitution (Central defender) |
| `202` | Substitution (Wing back) |
| `203` | Substitution (Inner midfielder) |
| `204` | Substitution (Forward) |
| `205` | Substitution (Winger) |
| `206` | Substitution (Extra) |
| `207` | Backup (Keeper) |
| `208` | Backup (Central defender) |
| `209` | Backup (Wing back) |
| `210` | Backup (Inner midfielder) |
| `211` | Backup (Forward) |
| `212` | Backup (Winger) |
| `213` | Backup (Extra) |
| `17` | Set pieces |
| `18` | Captain |
| `19` | Replaced Player #1 |
| `20` | Replaced Player #2 |
| `21` | Replaced Player #3 |
| `22` | Penalty taker (1) |
| `23` | Penalty taker (2) |
| `24` | Penalty taker (3) |
| `25` | Penalty taker (4) |
| `26` | Penalty taker (5) |
| `27` | Penalty taker (6) |
| `28` | Penalty taker (7) |
| `29` | Penalty taker (8) |
| `30` | Penalty taker (9) |
| `31` | Penalty taker (10) |
| `32` | Penalty taker (11) |
| `33` | Red Carded Player #1 |
| `34` | Red Carded Player #2 |
| `35` | Red Carded Player #3 |

### MatchRoleOldID

Old numbering, replaced by `MatchRoleID`.

| Value | Description |
| --- | --- |
| `1` | Keeper |
| `2` | Right back |
| `3` | Central defender #1 |
| `4` | Central defender #2 |
| `5` | Left back |
| `6` | Right winger |
| `7` | Inner midfield #1 |
| `8` | Inner midfield #2 |
| `9` | Left winger |
| `10` | Forward #1 |
| `11` | Forward #2 |
| `12` | Substitution (Keeper) |
| `13` | Substitution (Defender) |
| `14` | Substitution (Inner midfield) |
| `15` | Substitution (Winger) |
| `16` | Substitution (Forward) |
| `17` | Set pieces |
| `18` | Captain |
| `19` | Replaced Player #1 |
| `20` | Replaced Player #2 |
| `21` | Replaced Player #3 |

### MatchBehaviourID

| Value | Description |
| --- | --- |
| `-1` | No change |
| `0` | Normal |
| `1` | Offensive |
| `2` | Defensive |
| `3` | Towards middle |
| `4` | Towards wing |
| `5` | Extra forward |
| `6` | Extra inner midfield |
| `7` | Extra defender |

### matchOrderTypeID

| Value | Description |
| --- | --- |
| `1` | Normal substitution / Behaviour change |
| `3` | Player swap |

### matchPart

| Value | Description |
| --- | --- |
| `0` | Before the match started |
| `1` | First half |
| `2` | Second half (incl. added time) |
| `3` | Overtime |
| `4` | Penalty contest |

### WeatherID

| Value | Description |
| --- | --- |
| `0` | Rain |
| `1` | Overcast |
| `2` | Partially cloudy |
| `3` | Sunny |

## Players

### SkillID

| Value | Description |
| --- | --- |
| `1` | Goaltending |
| `2` | Stamina |
| `3` | Set pieces |
| `4` | Defending |
| `5` | Scoring |
| `6` | Winger |
| `7` | Passing |
| `8` | Playmaking |
| `9` | Trainer |
| `10` | Leadership |
| `11` | Experience |

### SkillLevel

The level names in the user's language come from the `translations` file; the app shows them with `level_text`.

| Value | Description |
| --- | --- |
| `0` | non-existent |
| `1` | disastrous |
| `2` | wretched |
| … | … |
| `19` | utopian |
| `20` | divine |

### SpecialtyID

| Value | Description |
| --- | --- |
| `0` | No specialty |
| `1` | Technical |
| `2` | Quick |
| `3` | Powerful |
| `4` | Unpredictable |
| `5` | Head specialist |
| `6` | Resilient |
| `8` | Support |

### PlayerCategoryID

| Value | Description |
| --- | --- |
| `1` | Keeper |
| `2` | Wing back |
| `3` | Central defender |
| `4` | Winger |
| `5` | Inner midfielder |
| `6` | Forward |
| `7` | Substitute |
| `8` | Reserve |
| `9` | Extra 1 |
| `10` | Extra 2 |
| `0` | No category set |

### PlayerAgreeability

| Value | Description |
| --- | --- |
| `5` | Beloved team member |
| `4` | Popular guy |
| `3` | Sympathetic guy |
| `2` | Pleasant guy |
| `1` | Controversial person |
| `0` | Nasty fellow |

### PlayerAggressiveness

| Value | Description |
| --- | --- |
| `5` | Unstable |
| `4` | Fiery |
| `3` | Temperamental |
| `2` | Balanced |
| `1` | Calm |
| `0` | Tranquil |

### PlayerHonesty

| Value | Description |
| --- | --- |
| `5` | Saintly |
| `4` | Righteous |
| `3` | Upright |
| `2` | Honest |
| `1` | Dishonest |
| `0` | Infamous |

### positionChange

| Value | Description |
| --- | --- |
| `0` | No change |
| `1` | Up |
| `2` | Down |

## Team and club

### TeamSpiritID

| Value | Description |
| --- | --- |
| `10` | Paradise on Earth! |
| `9` | walking on clouds |
| `8` | delirious |
| `7` | satisfied |
| `6` | content |
| `5` | calm |
| `4` | composed |
| `3` | irritated |
| `2` | furious |
| `1` | murderous |
| `0` | like the Cold War |

### SelfConfidenceID

| Value | Description |
| --- | --- |
| `9` | completely exaggerated |
| `8` | exaggerated |
| `7` | slightly exaggerated |
| `6` | wonderful |
| `5` | strong |
| `4` | decent |
| `3` | poor |
| `2` | wretched |
| `1` | disastrous |
| `0` | non-existent |

### SupportersPopularityID

| Value | Description |
| --- | --- |
| `9` | sending you love poems |
| `8` | dancing in the streets |
| `7` | high on life |
| `6` | delirious |
| `5` | satisfied |
| `4` | content |
| `3` | calm |
| `2` | irritated |
| `1` | furious |
| `0` | murderous |

### trainingType

| Value | Description |
| --- | --- |
| `0` | General (Deprecated) |
| `1` | Stamina (Deprecated) |
| `2` | Set Pieces |
| `3` | Defending |
| `4` | Scoring |
| `5` | Winger |
| `6` | Scoring and Set Pieces |
| `7` | Passing |
| `8` | Playmaking |
| `9` | Keeper |
| `10` | Passing (Defenders + Midfielders) |
| `11` | Defending (Defenders + Midfielders) |
| `12` | Winger (Winger + Attackers) |

### StaffType

| Value | Description |
| --- | --- |
| `1` | Assistant Trainer |
| `2` | Medic |
| `3` | Spokesperson |
| `4` | Sport Psychologist |
| `5` | Form coach |
| `6` | Financial Director |
| `7` | Tactical Assistant |

### NationalTeamStaffType

| Value | Description |
| --- | --- |
| `0` | National Team Coach |
| `1` | Assistant Coach |
| `2` | Scout |

### supporterTier

| Value | Description |
| --- | --- |
| `silver` | Supporter Silver |
| `gold` | Supporter Gold |
| `platinum` | Supporter Platinum |
| `diamond` | Supporter Diamond |

### trackingTypeId

| Value | Description |
| --- | --- |
| `1` | Selling |
| `2` | Buying |
| `3` | Mother club |
| `4` | Previous team |
| `5` | Hotlisted (Supporter only) |
| `8` | Losing bids (Supporter only) |
| `9` | Finished (Supporter only) |
| `10` | Transfer prospects (Supporter only) |

## Competitions

### CupID

Other cup ids are listed in the `worlddetails` file.

| Value | Description |
| --- | --- |
| `183` | Hattrick Masters |
| `x` | See worlddetails file for IDs |

### CupLevel

| Value | Description |
| --- | --- |
| `1` | National cup |
| `2` | Challenger cup |
| `3` | Consolation cup |

### CupLevelIndex

| Value | Description |
| --- | --- |
| `1` | Emerald |
| `2` | Ruby |
| `3` | Sapphire |

### WorldCupID

| Value | Description |
| --- | --- |
| `39` | World Cup (old format) |
| `45` | U-20 World Cup (old format) |
| `137` | World Cup (new format) |
| `149` | U-20 World Cup (new format) |

### TournamentType

| Value | Description |
| --- | --- |
| `1` | Single match |
| `2` | League |
| `3` | League with playoffs |
| `4` | Cup |
| `5` | Double elimination cup |
| `6` | Ladder |
| `8` | Swiss tournament |
| `10` | Division battle |
| `11` | Wildcards |
| `12` | World Cup |

### trophyID

| Value | Description |
| --- | --- |
| `16` | Cup win |
| `17` | Series win |
| `18` | League win |
| `78` | World cup Gold |
| `79` | World cup Silver |
| `80` | World cup Bronze |
| `91` | Hattrick masters win |
| `93` | Hattrick Masters top scorer |
| `103` | Tournament winner |
| `203` | Tutorial Tournament |
| `204` | Trial Winner |

### AchievementCategoryID

| Value | Description |
| --- | --- |
| `1` | Ranking |
| `2` | Team |
| `3` | Matches |
| `4` | Manager |
| `5` | Special Awards |
| `6` | Supporter |

### GenderID

| Value | Description |
| --- | --- |
| `1` | Male |
| `2` | Female |

### LeagueSystemID

Listed like this in the CHPP documentation (the same values as `GenderID`).

| Value | Description |
| --- | --- |
| `1` | Male |
| `2` | Female |

## Youth and scouting

### YouthLeagueStatusID

| Value | Description |
| --- | --- |
| `0` | Not full |
| `1` | About to create matches |
| `3` | Matches created, league is running |
| `10` | League is finished |

### YouthLeagueType

| Value | Description |
| --- | --- |
| `1` | Regional |
| `2` | National |
| `3` | International |

### ScoutSearchTypeID

| Value | Description |
| --- | --- |
| `0` | Any |
| `1` | Keeper |
| `2` | Defender |
| `3` | Wingback |
| `4` | Midfielder |
| `5` | Winger |
| `6` | Forward |

### ScoutTravelTypeID

| Value | Description |
| --- | --- |
| `1` | Plane |
| `2` | Car |

### ScoutCommentTypeID

| Value | Description |
| --- | --- |
| `0` | Hello |
| `1` | Found player |
| `2` | (not in use) |
| `3` | Talented in one skill |
| `4` | Current skill level |
| `5` | Potential skill level |
| `6` | Average skill level |
| `7` | Sign player to team |
| `8` | (not in use) |
| `9` | Player has speciality |

### ScoutCommentSkillTypeID

| Value | Description |
| --- | --- |
| `1` | Keeper |
| `2` | (not in use) |
| `3` | Defending |
| `4` | Playmaker |
| `5` | Winger |
| `6` | Scorer |
| `7` | Set Pieces |
| `8` | Passing |

## Other

### BookmarkTypeID

| Value | Description |
| --- | --- |
| `1` | Teams and Users |
| `2` | Players |
| `3` | Matches |
| `4` | Forum Users |
| `5` | League Units |
| `6` | Youth Teams |
| `7` | Youth Players |
| `8` | Youth Matches |
| `9` | Youth Leagues |
| `10` | Forum Posts |
| `11` | Forum Threads |

### sourceSystem

| Value | Description |
| --- | --- |
| `hattrick` | Hattrick main system |
| `youth` | Youth system |
| `htointegrated` | Hattrick integrated used for e.g. tournaments |

## Match orders

### lineup

The lineup sent to `matchorders` is a JSON string with three parts:

```json
{
  "positions": [
    {"id": "283974499", "behaviour": "0"},
    {"id": "227622136", "behaviour": "1"},
    {"id": "0", "behaviour": "0"}
  ],
  "settings": {"tactic": "0", "speechLevel": "0", "newLineup": ""},
  "substitutions": [
    {
      "playerin": "304433518",
      "playerout": "327875363",
      "orderType": "1",
      "min": "80",
      "pos": "-1",
      "beh": "-1",
      "card": "-1",
      "standing": "0"
    }
  ]
}
```

**positions** (shortened above): all 32 slots in this order. Send `"id": "0"` for an empty slot; the order matters.

| Slots | Content |
| --- | --- |
| 0–13 | Players on the field: keeper (0), right back (1), right central defender (2), … up to left forward (13); the same order as `MatchRoleID` 100–113 |
| 14–18 | Substitutes: keeper, defender, midfielder, forward, winger |
| 19–20 | Captain and set pieces taker |
| 21–31 | Penalty takers (11) |

`id` is the player id, `behaviour` a [MatchBehaviourID](#matchbehaviourid).

**settings**

| Field | Content |
| --- | --- |
| `tactic` | [MatchTacticType](#matchtactictype) |
| `speechLevel` | [MatchTeamAttitude](#matchteamattitude) |
| `newLineup` | Always empty |

**substitutions**: 0–5 orders (send `[]` for none).

| Field | Content |
| --- | --- |
| `playerin` | Player id in the "in" box |
| `playerout` | Player id in the "out" box; the same as `playerin` for a behaviour change |
| `orderType` | [matchOrderTypeID](#matchordertypeid): 1 = substitution or behaviour change, 3 = position swap |
| `min` | Match minute (MatchMinuteCriteria) |
| `pos` | Slot 0–13 to move to (`-1` = no change) |
| `beh` | [MatchBehaviourID](#matchbehaviourid) after the order (`-1` = no change) |
| `card` | Red card condition (RedCardCriteria) |
| `standing` | Goal difference condition (GoalDiffCriteria) |
