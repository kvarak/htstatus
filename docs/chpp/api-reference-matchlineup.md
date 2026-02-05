# CHPP API Reference: Match Lineup

**Purpose**: Detailed lineup information for finished matches including starting lineup, substitutions, and post-match player ratings
**Endpoint**: `/chppxml.ashx?file=matchlineup`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The Match Lineup API provides comprehensive lineup information for completed matches, including starting formations, substitutions made during the match, player ratings, and tactical changes. This endpoint is essential for post-match analysis, tactical review, and understanding team performance at the individual player level.

## Request Parameters

### Required
- `file=matchlineup` - Specifies the match lineup endpoint
- `matchID` - Unique identifier for the specific match (unsigned Integer, default: last match)
- `teamID` - Team ID to get lineup data for (unsigned Integer, default: logged-in user's team)

### Optional
- `version` - API version (1.2, 1.3, 1.5, 1.6, 1.7 available)
- `isYouth` - Youth team flag (Boolean, default: false) *(Available in versions 1.2, 1.3, 1.5, 1.6, 1.7)*
- `sourceSystem` - Match source system (replaces isYouth parameter, default: Hattrick)

### Version Support
Different versions provide varying levels of functionality:
- **1.2-1.7**: Support isYouth parameter for youth matches
- **Latest**: Recommended for full feature support and sourceSystem parameter

## Response Structure

### Match Context
```xml
<HattrickData>
    <MatchID>656789123</MatchID>
    <SourceSystem>hattrick</SourceSystem>

    <HomeTeam>
        <HomeTeamID>123456</HomeTeamID>
        <HomeTeamName>Example FC</HomeTeamName>
    </HomeTeam>

    <AwayTeam>
        <AwayTeamID>789012</AwayTeamID>
        <AwayTeamName>Rival United</AwayTeamName>
    </AwayTeam>

    <MatchType>1</MatchType>
    <MatchContextId>12345</MatchContextId>

    <Arena>
        <ArenaID>98765</ArenaID>
        <ArenaName>Stadium Name</ArenaName>
    </Arena>
</HattrickData>
```

### Team Lineup Data
```xml
<Team>
    <TeamID>123456</TeamID>
    <TeamName>Example FC</TeamName>
    <ExperienceLevel>7.2</ExperienceLevel>
    <StyleOfPlay>1</StyleOfPlay>

    <StartingLineup>
        <Player>
            <PlayerID>1001</PlayerID>
            <RoleID>100</RoleID>
            <FirstName>John</FirstName>
            <LastName>Goalkeeper</LastName>
            <NickName>Johnny</NickName>
            <Behaviour>0</Behaviour>
        </Player>
        <Player>
            <PlayerID>1002</PlayerID>
            <RoleID>101</RoleID>
            <FirstName>Mike</FirstName>
            <LastName>Defender</LastName>
            <NickName>Micky</NickName>
            <Behaviour>1</Behaviour>
        </Player>
        <!-- Additional starting lineup players -->
    </StartingLineup>

    <Substitutions>
        <Substitution>
            <TeamID>123456</TeamID>
            <SubjectPlayerID>1008</SubjectPlayerID>
            <ObjectPlayerID>1012</ObjectPlayerID>
            <OrderType>1</OrderType>
            <NewPositionId>109</NewPositionId>
            <NewPositionBehaviour>0</NewPositionBehaviour>
            <MatchMinute>65</MatchMinute>
            <MatchPart>2</MatchPart>
        </Substitution>
    </Substitutions>

    <Lineup>
        <Player>
            <PlayerID>1001</PlayerID>
            <RoleID>100</RoleID>
            <FirstName>John</FirstName>
            <LastName>Goalkeeper</LastName>
            <NickName>Johnny</NickName>
            <RatingStars>6.5</RatingStars>
            <RatingStarsEndOfMatch>6.2</RatingStarsEndOfMatch>
            <Behaviour>0</Behaviour>
        </Player>
        <!-- All players who participated in match -->
    </Lineup>
</Team>
```

## Data Field Reference

### Player Role IDs (RoleID)
Standard 11v11 positions in 553-based formation system:
- **100** - Goalkeeper
- **101** - Right Back
- **102** - Right Center Back
- **103** - Center Back
- **104** - Left Center Back
- **105** - Left Back
- **106** - Right Wingback
- **107** - Left Wingback
- **108** - Right Midfielder
- **109** - Central Midfielder
- **110** - Left Midfielder
- **111** - Right Winger
- **112** - Left Winger
- **113** - Forward
- **114** - Right Forward
- **115** - Left Forward

### Player Behaviours (Behaviour)
Individual tactical instructions:
- **0** - Normal
- **1** - Offensive
- **2** - Defensive
- **3** - Towards Middle
- **4** - Towards Wing
- **5** - Play Maker (only for some positions)
- **6** - Captain (leadership role)
- **7** - Set Pieces (free kicks/corners)

### Match Order Types (OrderType)
Types of tactical changes during match:
- **1** - Substitution (player replacement)
- **2** - Position swap (players change positions)
- **3** - Behaviour change (tactical instruction change)

### Match Parts (MatchPart)
When tactical changes occurred:
- **1** - First Half (0-45 minutes)
- **2** - Second Half (46-90 minutes)
- **3** - Extra Time (91+ minutes)

### Style of Play (StyleOfPlay)
Team's overall tactical approach:
- **0** - Neutral
- **1** - Pressing
- **2** - Counter-attacks
- **3** - Attack in middle
- **4** - Attack on wings
- **5** - Play creatively
- **6** - Long shots

## Implementation Examples

### Basic Lineup Retrieval
```python
# Get lineup for specific match and team
lineup = chpp.match_lineup(match_id=656789123, team_id=123456)

print(f"Team: {lineup.team.team_name}")
print(f"Experience Level: {lineup.team.experience_level}")
print(f"Style of Play: {lineup.team.style_of_play}")
```

### Starting Formation Analysis
```python
# Analyze starting formation
starting_eleven = []
for player in lineup.team.starting_lineup:
    starting_eleven.append({
        'name': f"{player.first_name} {player.last_name}",
        'position': player.role_id,
        'behaviour': player.behaviour
    })

# Group by position type
defenders = [p for p in starting_eleven if 101 <= p['position'] <= 107]
midfielders = [p for p in starting_eleven if 108 <= p['position'] <= 112]
forwards = [p for p in starting_eleven if p['position'] >= 113]

print(f"Formation: {len(defenders)}-{len(midfielders)}-{len(forwards)}")
```

### Substitution Pattern Analysis
```python
# Track substitutions throughout match
substitutions = []
for sub in lineup.team.substitutions:
    sub_info = {
        'minute': sub.match_minute,
        'part': sub.match_part,
        'type': sub.order_type,
        'player_out': sub.subject_player_id,
        'player_in': sub.object_player_id,
        'new_position': sub.new_position_id
    }
    substitutions.append(sub_info)

print(f"Total substitutions: {len(substitutions)}")
for sub in sorted(substitutions, key=lambda x: x['minute']):
    print(f"{sub['minute']}': Substitution - Position {sub['new_position']}")
```

### Player Performance Analysis
```python
# Compare player ratings throughout match
for player in lineup.team.lineup:
    if hasattr(player, 'rating_stars_end_of_match'):
        rating_change = player.rating_stars_end_of_match - player.rating_stars
        change_text = "↑" if rating_change > 0 else "↓" if rating_change < 0 else "="

        print(f"{player.first_name} {player.last_name}: "
              f"{player.rating_stars} → {player.rating_stars_end_of_match} {change_text}")
```

### Youth Match Handling
```python
# Get youth team lineup (versions 1.2+)
youth_lineup = chpp.match_lineup(
    match_id=456789012,
    team_id=123456,
    is_youth=True
)

# Note: Youth matches don't have RatingStarsEndOfMatch
for player in youth_lineup.team.lineup:
    print(f"{player.first_name} {player.last_name}: {player.rating_stars} stars")
```

## Usage Notes

### Data Availability
- **Finished Matches Only**: Lineup data only available for completed matches
- **Team Restriction**: Can only access lineup data for teams you have permission to view
- **Historical Access**: No time limits on historical match data
- **Youth Matches**: Require specific isYouth=true parameter in supported versions

### Performance Considerations
- **Response Size**: Moderate - contains detailed player and tactical data
- **Caching**: Recommended for frequently accessed matches as data doesn't change
- **Rate Limiting**: Consider batching multiple match requests
- **Version Selection**: Use latest version for optimal feature support

### Special Cases
- **Street Teams**: Team IDs may be negative for informal/street teams
- **Youth Limitations**: Youth matches don't include end-of-match ratings
- **Missing Players**: Some data fields may be empty for incomplete records
- **Tactical Changes**: Position swaps and behaviour changes tracked separately

## Related Endpoints

- **matchdetails** - Complete match information including events and statistics
- **matches** - Recent/upcoming matches list
- **matchesarchive** - Historical match collections
- **matchorders** - Pre-match tactical setup and planned orders

## Integration with HattrickPlanner

This endpoint provides essential data for:

### Tactical Analysis
- Formation effectiveness analysis
- Substitution pattern optimization
- Player role performance tracking
- Tactical flexibility measurement

### Player Performance
- Individual match ratings tracking
- Position-specific performance analysis
- Fitness and form progression
- Development tracking for youth players

### Team Strategy
- Opponent formation analysis
- Successful tactical combinations
- Substitution timing optimization
- Style of play effectiveness

The Match Lineup API is fundamental for post-match analysis and strategic planning in HattrickPlanner, providing the detailed player and tactical data needed for comprehensive match review and team development.