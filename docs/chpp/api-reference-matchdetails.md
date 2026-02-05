# CHPP API Reference: Match Details

**Purpose**: Comprehensive match information including statistics, events, possession, ratings, and match officials
**Endpoint**: `/chppxml.ashx?file=matchdetails`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The Match Details API provides comprehensive information about specific matches, including detailed statistics, possession data, team ratings, match events (goals, bookings, injuries), referee information, and attendance data. This endpoint is essential for post-match analysis and tactical insights.

## Request Parameters

### Required
- `file=matchdetails` - Specifies the match details endpoint
- `matchID` - Unique identifier for the specific match (unsigned Integer)

### Optional
- `version` - API version (latest recommended for full features)
- `matchEvents` - Include match events in response (Boolean, default: false)
  - `false` - Show no match events
  - `true` - Show match events (goals, bookings, injuries)
- `isYouth` - Youth team flag (Boolean, default: false)
- `sourceSystem` - Match source system (replaces isYouth parameter)

## Response Structure

### Match Context
```xml
<HattrickData>
    <SourceSystem>hattrick</SourceSystem>
    <UserSupporterTier>platinum</UserSupporterTier>

    <Match>
        <MatchID>656789123</MatchID>
        <MatchType>1</MatchType>
        <MatchContextId>12345</MatchContextId>
        <MatchRuleId>0</MatchRuleId>
        <CupLevel>0</CupLevel>
        <CupLevelIndex>0</CupLevelIndex>
        <MatchDate>2026-02-05 15:00:00</MatchDate>
        <FinishedDate>2026-02-05 16:47:00</FinishedDate>
        <AddedMinutes>3</AddedMinutes>
    </Match>
</HattrickData>
```

### Team Performance Data
```xml
<HomeTeam>
    <HomeTeamID>789012</HomeTeamID>
    <HomeTeamName>Example FC</HomeTeamName>
    <DressURI>http://res.hattrick.org/kits/...</DressURI>
    <Formation>4-4-2</Formation>
    <HomeGoals>2</HomeGoals>
    <TacticType>0</TacticType>
    <TacticSkill>7</TacticSkill>

    <!-- Team Ratings -->
    <RatingMidfield>15</RatingMidfield>
    <RatingRightDef>12</RatingRightDef>
    <RatingMidDef>14</RatingMidDef>
    <RatingLeftDef>13</RatingLeftDef>
    <RatingRightAtt>11</RatingRightAtt>
    <RatingMidAtt>16</RatingMidAtt>
    <RatingLeftAtt>12</RatingLeftAtt>

    <!-- Set Pieces -->
    <RatingIndirectSetPiecesDef>8</RatingIndirectSetPiecesDef>
    <RatingIndirectSetPiecesAtt>9</RatingIndirectSetPiecesAtt>

    <!-- Chances Distribution -->
    <NrOfChancesLeft>3</NrOfChancesLeft>
    <NrOfChancesCenter>5</NrOfChancesCenter>
    <NrOfChancesRight>2</NrOfChancesRight>
    <NrOfChancesSpecialEvents>1</NrOfChancesSpecialEvents>
    <NrOfChancesOther>0</NrOfChancesOther>
</HomeTeam>
```

### Match Environment
```xml
<Arena>
    <ArenaID>12345</ArenaID>
    <ArenaName>Example Stadium</ArenaName>
    <WeatherID>2</WeatherID>
    <SoldTotal>18500</SoldTotal>
    <SoldTerraces>8000</SoldTerraces>
    <SoldBasic>7000</SoldBasic>
    <SoldRoof>2500</SoldRoof>
    <SoldVIP>1000</SoldVIP>
</Arena>

<MatchOfficials>
    <Referee>
        <RefereeId>983456</RefereeId>
        <RefereeName>John Smith</RefereeName>
        <RefereeCountryId>5</RefereeCountryId>
        <RefereeCountryName>Sweden</RefereeCountryName>
        <RefereeTeamId>567890</RefereeTeamId>
        <RefereeTeamname>Historic FC</RefereeTeamname>
    </Referee>
    <RefereeAssistant1>...</RefereeAssistant1>
    <RefereeAssistant2>...</RefereeAssistant2>
</MatchOfficials>
```

### Match Events (when matchEvents=true)
```xml
<Scorers>
    <Goal Index='1'>
        <ScorerPlayerID>283974499</ScorerPlayerID>
        <ScorerPlayerName>John Doe</ScorerPlayerName>
        <ScorerTeamID>789012</ScorerTeamID>
        <ScorerHomeGoals>1</ScorerHomeGoals>
        <ScorerAwayGoals>0</ScorerAwayGoals>
        <ScorerMinute>23</ScorerMinute>
        <MatchPart>firstHalf</MatchPart>
    </Goal>
</Scorers>

<Bookings>
    <Booking Index='1'>
        <BookingPlayerID>394857362</BookingPlayerID>
        <BookingPlayerName>Jane Smith</BookingPlayerName>
        <BookingTeamID>345678</BookingTeamID>
        <BookingType>1</BookingType>
        <BookingMinute>67</BookingMinute>
        <MatchPart>secondHalf</MatchPart>
    </Booking>
</Bookings>

<Injuries>
    <Injury Index='1'>
        <InjuryPlayerID>485729301</InjuryPlayerID>
        <InjuryPlayerName>Mike Johnson</InjuryPlayerName>
        <InjuryTeamID>789012</InjuryTeamID>
        <InjuryType>2</InjuryType>
        <InjuryMinute>78</InjuryMinute>
        <MatchPart>secondHalf</MatchPart>
    </Injury>
</Injuries>
```

### Possession Statistics
```xml
<PossessionFirstHalfHome>58</PossessionFirstHalfHome>
<PossessionFirstHalfAway>42</PossessionFirstHalfAway>
<PossessionSecondHalfHome>52</PossessionSecondHalfHome>
<PossessionSecondHalfAway>48</PossessionSecondHalfAway>
```

## Data Types & Values

### Match Types
- **1** - League match
- **3** - Cup match
- **4** - Friendly (normal)
- **5** - Friendly (cup rules)
- **8** - Friendly (league rules)
- **9** - Friendly (national team rules)

### Weather IDs
- **0** - Rain
- **1** - Cloudy
- **2** - Fair weather
- **3** - Sunny

### Booking Types
- **1** - Yellow card (warning)
- **2** - Red card

### Injury Types
- **1** - Bruise (minor)
- **2** - Injury (significant)

### Tactic Types
- **0** - Normal
- **1** - Pressing
- **2** - Counter-attacks
- **3** - Attack in the middle
- **4** - Attack on wings
- **5** - Play creatively
- **6** - Long shots

### Match Parts
- **firstHalf** - First 45 minutes
- **secondHalf** - Second 45 minutes
- **extraTime** - Extra time periods
- **penalties** - Penalty shootout

## Match Event Types Reference

The API supports 400+ different match event types for detailed match narrative. Here is the complete list:

### Complete Event Types Table

| Event ID | Event Name |
|----------|------------|
| 19 | Players enter the field |
| 20 | Tactical disposition |
| 21 | Player names in lineup |
| 22 | Players from neighborhood used |
| 23 | Same formation both teams |
| 24 | Team formations (different) |
| 25 | Regional derby |
| 26 | Neutral ground |
| 27 | Away is actually home |
| 28 | Walkover lineup used |
| 30 | Spectators/venue - rain |
| 31 | Spectators/venue - cloudy |
| 32 | Spectators/venue - fair weather |
| 33 | Spectators/venue - sunny |
| 35 | Arena extended with temporary seats |
| 36 | Only venue - rain |
| 37 | Only venue - cloudy |
| 38 | Only venue - fair weather |
| 39 | Only venue - sunny |
| 40 | Dominated |
| 41 | Best player |
| 42 | Worst player |
| 43 | Double meeting first match |
| 44 | Double meeting second match |
| 45 | Half time results |
| 46 | Hat-trick comment |
| 47 | No team dominated |
| 55 | Penalty contest: Goal by Technical (no nerves) |
| 56 | Penalty contest: Goal, no nerves |
| 57 | Penalty contest: Goal in spite of nerves |
| 58 | Penalty contest: No goal because of nerves |
| 59 | Penalty contest: No goal in spite of no nerves |
| 60 | Underestimation |
| 61 | Organization breaks |
| 62 | Withdraw |
| 63 | Remove underestimation at pause |
| 64 | Reorganize |
| 65 | Nerves in important thrilling game |
| 66 | Remove underestimation at pause (goaldiff = 0) |
| 67 | Remove underestimation at pause (goaldiff = 1) |
| 68 | Successful pressing |
| 69 | Remove underestimation |
| 70 | Extension |
| 71 | Penalty contest (after extension) |
| 72 | Extension decided |
| 73 | After 22 penalties tossing coin! |
| 74 | Extension - Double meeting second match |
| 75 | Added time |
| 76 | No added time |
| 80 | New captain |
| 81 | New set pieces taker |
| 90 | Injured but keeps playing |
| 91 | Moderately injured, leaves field |
| 92 | Badly injured, leaves field |
| 93 | Injured and no replacement existed |
| 94 | Injured after foul but continues |
| 95 | Injured after foul and exits |
| 96 | Injured after foul and no replacement existed |
| 97 | Keeper injured, field player has to take his place |
| 100 | Reducing goal home team free kick |
| 101 | Reducing goal home team middle |
| 102 | Reducing goal home team left wing |
| 103 | Reducing goal home team right wing |
| 104 | Reducing goal home team penalty kick normal |
| 105 | SE: Goal Unpredictable long pass |
| 106 | SE: Goal Unpredictable scores on his own |
| 107 | Goal long shot (no tactic) |
| 108 | SE: Goal Unpredictable special action |
| 109 | SE: Goal Unpredictable mistake |
| 110 | Equalizer goal home team free kick |
| 111 | Equalizer goal home team middle |
| 112 | Equalizer goal home team left wing |
| 113 | Equalizer goal home team right wing |
| 114 | Equalizer goal home team penalty kick normal |
| 115 | SE: Quick scores after rush |
| 116 | SE: Quick rushes, passes and receiver scores |
| 117 | SE: Tired defender mistake, striker scores |
| 118 | SE Goal: Corner to anyone |
| 119 | SE: Goal Corner: Head specialist |
| 120 | Goal to take lead home team free kick |
| 121 | Goal to take lead home team middle |
| 122 | Goal to take lead home team left wing |
| 123 | Goal to take lead home team right wing |
| 124 | Goal to take lead home team penalty kick normal |
| 125 | SE: Goal: Unpredictable, own goal |
| 130 | Increase goal home team free kick |
| 131 | Increase goal home team middle |
| 132 | Increase goal home team left wing |
| 133 | Increase goal home team right wing |
| 134 | Increase goal home team penalty kick normal |
| 135 | SE: Experienced forward scores |
| 136 | SE: Inexperienced defender causes goal |
| 137 | SE: Winger to Head spec. Scores |
| 138 | SE: Winger to anyone Scores |
| 139 | SE: Technical goes around head player |
| 140 | Counter attack goal, free kick |
| 141 | Counter attack goal, middle |
| 142 | Counter attack goal, left |
| 143 | Counter attack goal, right |
| 150 | Reducing goal away team free kick |
| 151 | Reducing goal away team middle |
| 152 | Reducing goal away team left wing |
| 153 | Reducing goal away team right wing |
| 154 | Reducing goal away team penalty kick normal |
| 160 | Equalizer goal away team free kick |
| 161 | Equalizer goal away team middle |
| 162 | Equalizer goal away team left wing |
| 163 | Equalizer goal away team right wing |
| 164 | Equalizer goal away team penalty kick normal |
| 170 | Goal to take lead away team free kick |
| 171 | Goal to take lead away team middle |
| 172 | Goal to take lead away team left wing |
| 173 | Goal to take lead away team right wing |
| 174 | Goal to take lead away team penalty kick normal |
| 180 | Increase goal away team free kick |
| 181 | Increase goal away team middle |
| 182 | Increase goal away team left wing |
| 183 | Increase goal away team right wing |
| 184 | Increase goal away team penalty kick normal |
| 185 | Goal indirect free kick |
| 186 | Counter attack goal, indirect free kick |
| 187 | Goal long shot |
| 190 | SE: Goal: Powerful normal forward generates extra chance |
| 200 | No reducing goal home team free kick |
| 201 | No reducing goal home team middle |
| 202 | No reducing goal home team left wing |
| 203 | No reducing goal home team right wing |
| 204 | No reducing goal home team penalty kick normal |
| 205 | SE: No Goal Unpredictable long pass |
| 206 | SE: No Goal Unpredictable almost scores |
| 207 | No goal long shot (no tactic) |
| 208 | SE: No Goal Unpredictable special action |
| 209 | SE: No Goal Unpredictable mistake |
| 210 | No equalizer goal home team free kick |
| 211 | No equalizer goal home team middle |
| 212 | No equalizer goal home team left wing |
| 213 | No equalizer goal home team right wing |
| 214 | No equalizer goal home team penalty kick normal |
| 215 | SE: Speedy misses after rush |
| 216 | SE: Quick rushes, passes but receiver fails |
| 217 | SE: Tired defender mistake but no goal |
| 218 | SE No goal: Corner to anyone |
| 219 | SE: No Goal Corner: Head specialist |
| 220 | No goal to take lead home team free kick |
| 221 | No goal to take lead home team middle |
| 222 | No goal to take lead home team left wing |
| 223 | No goal to take lead home team right wing |
| 224 | No goal to take lead home team penalty kick normal |
| 225 | SE: No goal: Unpredictable, own goal almost |
| 230 | No increase goal home team free kick |
| 231 | No increase goal home team middle |
| 232 | No increase goal home team left wing |
| 233 | No increase goal home team right wing |
| 234 | No increase goal home team penalty kick normal |
| 235 | SE: Experienced forward fails to score |
| 236 | SE: Inexperienced defender almost causes goal |
| 237 | SE: Winger to someone: No goal |
| 239 | SE: Technical goes around head player, no goal |
| 240 | Counter attack, no goal, free kick |
| 241 | Counter attack, no goal, middle |
| 242 | Counter attack, no goal, left |
| 243 | Counter attack, no goal, right |
| 250 | No reducing goal away team free kick |
| 251 | No reducing goal away team middle |
| 252 | No reducing goal away team left wing |
| 253 | No reducing goal away team right wing |
| 254 | No reducing goal away team penalty kick normal |
| 260 | No equalizer goal away team free kick |
| 261 | No equalizer goal away team middle |
| 262 | No equalizer goal away team left wing |
| 263 | No equalizer goal away team right wing |
| 264 | No equalizer goal away team penalty kick normal |
| 270 | No goal to take lead away team free kick |
| 271 | No goal to take lead away team middle |
| 272 | No goal to take lead away team left wing |
| 273 | No goal to take lead away team right wing |
| 274 | No goal to take lead away team penalty kick normal |
| 280 | No increase goal away team free kick |
| 281 | No increase goal away team middle |
| 282 | No increase goal away team left wing |
| 283 | No increase goal away team right wing |
| 284 | No increase goal away team penalty kick normal |
| 285 | No goal indirect free kick |
| 286 | Counter attack, no goal, indirect free kick |
| 287 | No goal long shot |
| 288 | No goal long shot, defended |
| 289 | SE: Quick rushes, stopped by quick defender |
| 290 | SE: No Goal: Powerful normal forward generates extra chance |
| 301 | SE: Technical suffers from rain |
| 302 | SE: Powerful thrives in rain |
| 303 | SE: Technical thrives in sun |
| 304 | SE: Powerful suffers from sun |
| 305 | SE: Quick loses in rain |
| 306 | SE: Quick loses in sun |
| 307 | SE: Support player boost succeeded |
| 308 | SE: Support player boost failed and organization dropped |
| 309 | SE: Support player boost failed |
| 310 | SE: Powerful defensive inner presses chance |
| 311 | Counter attack triggered by technical defender |
| 331 | Tactic Type: Pressing |
| 332 | Tactic Type: Counter-attacking |
| 333 | Tactic Type: Attack in middle |
| 334 | Tactic Type: Attack on wings |
| 335 | Tactic Type: Play creatively |
| 336 | Tactic Type: Long shots |
| 343 | Tactic: Attack in middle used |
| 344 | Tactic: Attack on wings used |
| 350 | Player substitution: team is behind |
| 351 | Player substitution: team is ahead |
| 352 | Player substitution: minute |
| 360 | Change of tactic: team is behind |
| 361 | Change of tactic: team is ahead |
| 362 | Change of tactic: minute |
| 370 | Player position swap: team is behind |
| 371 | Player position swap: team is ahead |
| 372 | Player position swap: minute |
| 380 | Man marking success, short distance |
| 381 | Man marking success, long distance |
| 382 | Man marked changed from short to long distance |
| 383 | Man marked changed from long to short distance |
| 384 | Man Marker penalty, no man marked on the field |
| 385 | Man marker changed from short to long distance |
| 386 | Man marker changed from long to short distance |
| 387 | Man marker penalty, man marked not in marking position |
| 388 | Man marker penalty, man marker not in marking position |
| 389 | Man Marker penalty, no man marked in opponent team |
| 390 | Rainy weather - Many players affected |
| 391 | Sunny weather - Many players affected |
| 401 | Injury: Knee left |
| 402 | Injury: Knee right |
| 403 | Injury: Thigh left |
| 404 | Injury: Thigh right |
| 405 | Injury: Foot left |
| 406 | Injury: Foot right |
| 407 | Injury: Ankle left |
| 408 | Injury: Ankle right |
| 409 | Injury: Calf left |
| 410 | Injury: Calf right |
| 411 | Injury: Groin left |
| 412 | Injury: Groin right |
| 413 | Injury: Collarbone |
| 414 | Injury: Back |
| 415 | Injury: Hand left |
| 416 | Injury: Hand right |
| 417 | Injury: Arm left |
| 418 | Injury: Arm right |
| 419 | Injury: Shoulder left |
| 420 | Injury: Shoulder right |
| 421 | Injury: Rib |
| 422 | Injury: Head |
| 423 | Injured by foul |
| 424 | Injured player replaced |
| 425 | No replacement for injured player |
| 426 | Field player has to take injured keeper's place |
| 427 | Player injured was regainer so got bruised instead |
| 450 | Player got third yellow card misses next match |
| 451 | With this standing team x will relegate to cup y |
| 452 | Player current team matches 100s anniversary |
| 453 | Player possibly the last game in this team |
| 454 | Doctor report of injury length |
| 455 | New star player of the team |
| 456 | Player career goals multiple of 50 |
| 457 | Player league goals this season |
| 458 | Player cup goals this season |
| 459 | Bench player warming up |
| 460 | Fans shocked by losing |
| 461 | Fans upset by losing |
| 462 | Fans surprised by winning |
| 463 | Fans excited by winning |
| 464 | Exact number of spectators |
| 465 | Team should win match to secure winning the league |
| 466 | Team should win match to have chance of winning league |
| 467 | The winner of this match (if there is one) can have a chance of winning the league |
| 468 | Team should win match to make sure they don't demote |
| 469 | Team should win match to have a chance of not demoting |
| 470 | The loser of this match will demote |
| 471 | Hometeam/Awayteam has most possession in beginning of match |
| 472 | Equal possession in beginning of match |
| 473 | Career ending injury |
| 474 | Team of youngsters |
| 475 | Low attendance because of fan mood |
| 476 | Extra security because of fan mood |
| 477 | Both team's fans are angry |
| 478 | Team will have best cup run if win |
| 479 | Both teams could have best cup run if win (competing) |
| 480 | Current round is team's best cup run |
| 481 | New formation today |
| 482 | Teams using the same style of play |
| 483 | Teams using different styles of play |
| 484 | One team's style of play |
| 485 | Team of oldies |
| 486 | Team is aggressive |
| 487 | Team has only homegrown players |
| 488 | Team has all players from same country |
| 489 | Comeback after a long injury |
| 490 | Previous match (cup) similar outcome |
| 491 | Previous match (cup) different outcome |
| 492 | Previous match (league) similar outcome |
| 493 | Previous match (league) different outcome |
| 494 | Team has the ball but is not attacking |
| 495 | Team has the ball and has started attacking |
| 496 | Team is still in the cup (for league matches) |
| 497 | Both teams are still in the cup (for league matches) |
| 498 | Team is looking tired (low avg stamina) |
| 500 | Both teams walkover |
| 501 | Home team walkover |
| 502 | Away team walkover |
| 503 | Both teams break game (2 players remaining) |
| 504 | Home team breaks game (2 players remaining) |
| 505 | Away team breaks game (2 players remaining) |
| 510 | Yellow card nasty play |
| 511 | Yellow card cheating |
| 512 | Red card (2nd warning) nasty play |
| 513 | Red card (2nd warning) cheating |
| 514 | Red card without warning |
| 596 | Extra time started (third half) |
| 597 | Second half started |
| 598 | Match started |
| 599 | Match finished |
| 601 | Congratulations to the winner |
| 602 | Winner advances to next cup round (no relegation cup for loser) |
| 603 | Winner advances to next cup round and loser relegates to cup X |
| 604 | Match ended in a tie |
| 605 | End of match, congratulations team won the league |
| 606 | End of match, sad that team will demote directly |
| 650 | Hattrick Anniversary |
| 651 | Team Anniversary |
| 700 | Event-o-Matic: Manager taunts opponent |
| 701 | Event-o-Matic: Manager praises opponent |
| 702 | Event-o-Matic: Manager asks fans for support |
| 703 | Event-o-Matic: Manager expects great show |
| 704 | Event-o-Matic: Manager honours Club legacy |
| 800 | Star player missed match because of red card |
| 801 | Star player missed match because of injury |
| 802 | Team is on winning streak |
| 803 | Both teams are on winning streak |
| 804 | Team will break winning streak |
| 805 | Weakest team (HTRating) is winning |
| 806 | Possession shift because of red card |
| 807 | Possession shift because of substitution (lost) |
| 808 | Possession shift because of substitution (gained) |
| 809 | Possession shift (other reason) |
| 810 | Previous match winner |
| 811 | Previous match was a tie |
| 812 | Player birthday |
| 813 | New match kit |
| 814 | Team underperforming compared to last league match (HT Rating) |
| 815 | Team overperforming compared to last league match (HT Rating) |
| 816 | Possession shift because of team confusion |
| 817 | Possession shift because of team nerves |
| 818 | Brothers play for same team |
| 819 | Father/son play for same team |
| 820 | Family members play against each other |
| 821 | Family members assist + goal |
| 822 | Family members facing each other in a penalty |
| 880 | Assist end to a goal |

### Event Categories Summary
- **19-99**: Match setup, weather, basic events, injuries
- **100-199**: Home team goals and special events
- **200-299**: Failed attempts and missed chances
- **300-399**: Weather effects, special conditions, tactical information
- **400-499**: Specific injuries, cards, and extensive match context
- **500-599**: Walkover situations, cards, and match flow events
- **600-699**: Match endings, results, and anniversaries
- **700-899**: Event-o-Matic messages and additional match events
- **880**: Assist information

## Implementation Examples

### Basic Match Details
```python
# Get comprehensive match information
match_details = chpp.match_details(match_id=656789123)
print(f"Final Score: {match_details.home_goals}-{match_details.away_goals}")
print(f"Possession: {match_details.possession_home}%-{match_details.possession_away}%")
```

### Match Events Analysis
```python
# Get match with detailed events
match_with_events = chpp.match_details(match_id=656789123, match_events=True)

for goal in match_with_events.goals:
    print(f"{goal.minute}': {goal.scorer_name} ({goal.team_name})")

for booking in match_with_events.bookings:
    card_type = "Yellow" if booking.type == 1 else "Red"
    print(f"{booking.minute}': {card_type} card - {booking.player_name}")
```

### Team Performance Analysis
```python
# Analyze team ratings and tactical effectiveness
home_attack = (
    match_details.home_team.rating_left_att +
    match_details.home_team.rating_mid_att +
    match_details.home_team.rating_right_att
) / 3

print(f"Average attack rating: {home_attack}")
print(f"Formation: {match_details.home_team.formation}")
print(f"Tactic: {match_details.home_team.tactic_type}")
```

## Usage Notes

- **Event Details**: Use `matchEvents=true` to get comprehensive match narrative
- **Performance Impact**: Including events increases response size significantly
- **Historical Data**: Available for all completed matches (no time limit)
- **Team Privacy**: Some data (TeamAttitude) only visible to team owners
- **Rate Limiting**: Consider caching for frequently accessed matches
- **Data Completeness**: Not all matches have complete statistical data

## Event Data Mapping

In general, `SubjectTeamId` is the team that the event belongs to, `SubjectPlayerId` is the main (and sometimes only) player in the event and `ObjectPlayerId` is, if exists, the other player.

However, there are specific events that use these fields differently:

| EventTypeID | SubjectPlayerId | ObjectPlayerId | SubjectTeamId |
|-------------|-----------------|----------------|---------------|
| 23 | Home lineup | Away lineup | |
| 24 | Home lineup | Away lineup | |
| 25 | | Region ID | |
| 27 | Home team ID | Away team ID | |
| 30-33 | Arena ID | Sold seats | Seats in total |
| 35 | Arena ID | Temporary seats | |
| 40 | | Midfield possession | |
| 61 | Organisation level | | |
| 64 | Trainer ID | Organisation level | |
| 68 | Pressing tactic level | | |
| 75 | | Added minutes | |
| 331-336 | Tactic level | | |
| 451 | | Cup ID | |
| 454 | | Injury weeks | |
| 456 | | Goals ever | |
| 457 | | Goals this league | |
| 458 | | Goals this cup | |
| 464 | | Sold seats | |
| 465 | 1st place league team ID | | |
| 466 | | 2nd place league team ID | |
| 468 | 6th place league team ID | | |
| 469 | | 7th place league team ID | |

## Related Endpoints

- **matches-basic** - Recent/upcoming matches list
- **matchesarchive** - Historical match collections
- **matchorders** - Tactical setup and lineups
- **matchlineup** - Post-match lineup with ratings

This endpoint provides the foundation for comprehensive match analysis, tactical preparation, and performance tracking in HattrickPlanner.
