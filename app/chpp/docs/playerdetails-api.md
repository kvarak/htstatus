# CHPP PlayerDetails API Documentation

> **Source**: Hattrick CHPP API documentation (playerdetails endpoint)
> **Date Saved**: January 26, 2026
> **Purpose**: Complete API reference for player data extraction in custom CHPP client

## API Endpoint: `playerdetails`

**Description**: Detailed information for a player

### Input Parameters

**Required:**
- `file=playerdetails`
- `playerID` (unsigned Integer) - The player to get information for

**Optional:**
- `version` - API version
- `actionType` - Action to perform (view, placeBid)
- `includeMatchInfo` (Boolean, default: false) - Include LastMatch container
- `teamId` (unsigned Integer) - Required for placeBid actions
- `bidAmount` (Money) - Bid amount in SEK
- `maxBidAmount` (Money) - Maximum autobid amount in SEK

### Key Data Fields Available

#### Basic Player Info
- `PlayerID` - Globally unique player ID
- `FirstName` - Player's first name
- `NickName` - Player's nickname
- `LastName` - Player's last name
- `PlayerNumber` - Jersey number (1-99)
- `Age` - Age in years
- `AgeDays` - Days since last birthday
- `TSI` - Total Skill Index

#### **Goal Statistics** 🎯
- `CareerGoals` - Total goals throughout player's career
- `LeagueGoals` - Goals in league this season
- `CupGoals` - Goals in cup this season
- `FriendliesGoals` - Goals in friendlies this season
- `GoalsCurrentTeam` - Goals for current team
- `MatchesCurrentTeam` - Total matches for current team
- `AssistsCurrentTeam` - Assists for current team
- `CareerAssists` - Career assists total

#### Skills
```xml
<PlayerSkills>
  <StaminaSkill>SkillLevel</StaminaSkill>
  <KeeperSkill>SkillLevel</KeeperSkill>
  <PlaymakerSkill>SkillLevel</PlaymakerSkill>
  <ScorerSkill>SkillLevel</ScorerSkill>
  <PassingSkill>SkillLevel</PassingSkill>
  <WingerSkill>SkillLevel</WingerSkill>
  <DefenderSkill>SkillLevel</DefenderSkill>
  <SetPiecesSkill>SkillLevel</SetPiecesSkill>
</PlayerSkills>
```

#### Team & Transfer Info
- `Salary` - Player salary
- `TransferListed` - On transfer list status
- `TransferDetails` - Transfer information if listed

#### Match Data (with includeMatchInfo=true)
- `LastMatch` - Information about last played match
  - `Date` - Match date
  - `MatchId` - Match ID
  - `PositionCode` - Position played
  - `PlayedMinutes` - Minutes played
  - `Rating` - Average match rating
  - `RatingEndOfGame` - End-of-match rating

## Implementation Notes for Custom CHPP Client

### Current CHPPPlayer Model Fields
Our `CHPPPlayer` model should extract these goal-related fields:
- `career_goals` ← `CareerGoals`
- `league_goals` ← `LeagueGoals`
- `cup_goals` ← `CupGoals`
- `friendlies_goals` ← `FriendliesGoals`
- `goals_current_team` ← `GoalsCurrentTeam`
- `current_team_matches` ← `MatchesCurrentTeam`
- `assists_current_team` ← `AssistsCurrentTeam`
- `career_assists` ← `CareerAssists`

### Parser Implementation
The `parse_player()` function should extract:
```python
career_goals = safe_find_int(player_node, "CareerGoals", 0)
league_goals = safe_find_int(player_node, "LeagueGoals", 0)
cup_goals = safe_find_int(player_node, "CupGoals", 0)
friendlies_goals = safe_find_int(player_node, "FriendliesGoals", 0)
goals_current_team = safe_find_int(player_node, "GoalsCurrentTeam", 0)
current_team_matches = safe_find_int(player_node, "MatchesCurrentTeam", 0)
```

### Stats Page Integration
For `get_top_scorers()` function:
- Primary: `goals_current_team` (GoalsCurrentTeam)
- Fallback: `career_goals` (CareerGoals)
- Match data: `current_team_matches` (MatchesCurrentTeam)

## XML Response Example Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Player>
    <PlayerID>12345</PlayerID>
    <FirstName>John</FirstName>
    <NickName>Johnny</NickName>
    <LastName>Smith</LastName>
    <!-- ... other fields ... -->
    <CareerGoals>25</CareerGoals>
    <LeagueGoals>8</LeagueGoals>
    <CupGoals>2</CupGoals>
    <FriendliesGoals>3</FriendliesGoals>
    <GoalsCurrentTeam>15</GoalsCurrentTeam>
    <MatchesCurrentTeam>45</MatchesCurrentTeam>
    <!-- ... -->
  </Player>
</HattrickData>
```

## Related Files
- `/app/chpp/models.py` - CHPPPlayer data model
- `/app/chpp/parsers.py` - XML parsing functions
- `/app/utils.py` - get_top_scorers() function
- `/app/templates/stats.html` - Stats display template