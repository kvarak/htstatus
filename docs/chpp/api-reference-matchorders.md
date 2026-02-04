# CHPP API Reference: Match Orders

**Purpose**: Comprehensive match lineup management with tactical orders, substitutions, and predictive analysis
**Endpoint**: `/chppxml.ashx?file=matchorders`
**Authentication**: OAuth required (with additional "set_matchorder" scope for modifications)
**Rate Limiting**: Standard CHPP limits apply

## Overview

The Match Orders endpoint provides complete match lineup management including viewing current orders, setting new lineups, and predicting tactical ratings. This is one of the most sophisticated CHPP endpoints, enabling full tactical control and strategic planning for upcoming matches.

## Request Parameters

### Required
- `file=matchorders` - Specifies the match orders endpoint

### Optional
- `version` - API version (latest recommended for full features)
- `actionType` - Operation mode:
  - `view` (default) - Retrieve current match orders
  - `setmatchorder` - Update lineup (requires POST method and special OAuth scope)
  - `predictratings` - Calculate tactical ratings for proposed lineup
- `matchID` - Target match identifier
  - **Default**: Next scheduled match for the team
  - **Required**: When using setmatchorder or predictratings
- `teamId` - Team identifier (unsigned integer)
  - **Default**: Primary club senior team ID
  - **Restriction**: Must be a team managed by authenticated user
- `isYouth` - Youth team flag (boolean, default: false)
- `sourceSystem` - Match source (replaces isYouth parameter in newer versions)
- `lineup` - JSON-formatted match orders (POST request body)
  - **Required**: For setmatchorder action
  - **Optional**: For predictratings action

## Response Structure

### Match Context
```xml
<HattrickData>
    <MatchID>656789123</MatchID>
    <sourceSystem>Hattrick</sourceSystem>
    <MatchData Available="true">
        <HomeTeam>
            <HomeTeamID>789012</HomeTeamID>
            <HomeTeamName>Example FC</HomeTeamName>
        </HomeTeam>
        <AwayTeam>
            <AwayTeamID>345678</AwayTeamID>
            <AwayTeamName>Rival United</AwayTeamName>
        </AwayTeam>
        <Arena>
            <ArenaID>12345</ArenaID>
            <ArenaName>Example Stadium</ArenaName>
        </Arena>
        <MatchDate>2026-02-08 15:00:00</MatchDate>
        <MatchType>1</MatchType>
        <Attitude>0</Attitude>
        <TacticType>0</TacticType>
        <CoachModifier Available="true">2</CoachModifier>
    </MatchData>
</HattrickData>
```

### Tactical Settings
- **Attitude** - Team attitude/speech level (0-4 scale, owner-only visibility)
- **TacticType** - Formation tactical approach (0=Normal, 1=Pressing, 2=Counter-attacks, 3=Attack in middle, 4=Attack on wings, 5=Play creatively, 6=Long shots)
- **CoachModifier** - Playing style (-10 to +10, defensive to offensive)

### Lineup Structure
```xml
<Lineup>
    <Positions>
        <Player>
            <PlayerID>283974499</PlayerID>
            <RoleID>100</RoleID>
            <FirstName>John</FirstName>
            <NickName>Johnny</NickName>
            <LastName>Smith</LastName>
            <Behaviour>0</Behaviour>
        </Player>
    </Positions>
    <Bench>
        <Player>...</Player>
    </Bench>
    <Kickers>
        <Player>...</Player>
    </Kickers>
    <SetPieces>...</SetPieces>
    <Captain>...</Captain>
</Lineup>
```

### Player Orders System
```xml
<PlayerOrders>
    <PlayerOrder>
        <PlayerOrderID>123456</PlayerOrderID>
        <MatchMinuteCriteria>80</MatchMinuteCriteria>
        <GoalDiffCriteria>0</GoalDiffCriteria>
        <RedCardCriteria>-1</RedCardCriteria>
        <SubjectPlayerID>327875363</SubjectPlayerID>
        <ObjectPlayerID>304433518</ObjectPlayerID>
        <OrderType>1</OrderType>
        <NewPositionId>13</NewPositionId>
        <NewPositionBehaviour>0</NewPositionBehaviour>
    </PlayerOrder>
</PlayerOrders>
```

## Lineup JSON Format (Version 3.0)

### Complete Lineup Structure
```json
{
  "positions": [
    {"id": 283974499, "behaviour": 0},
    {"id": 227622136, "behaviour": 1},
    {"id": 0, "behaviour": 0},
    {"id": 226747085, "behaviour": 0},
    ...
  ],
  "bench": [
    {"id": 319107771, "behaviour": 0},
    {"id": 0, "behaviour": 0},
    ...
  ],
  "kickers": [
    {"id": 226747085, "behaviour": 0},
    ...
  ],
  "captain": "190611685",
  "setPieces": "226747085",
  "settings": {
    "tactic": "0",
    "speechLevel": "0",
    "newLineup": "",
    "coachModifier": "0",
    "manMarkerPlayerId": "0",
    "manMarkingPlayerId": "0"
  },
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

## Reference Tables

### Match Minute Criteria
| Value | Description |
|-------|-------------|
| -1 | Anytime |
| 0-119 | After x minutes |
| 46 | Halftime |
| 91 | Before extratime |

### Goal Difference Criteria
| Value | Description |
|-------|-------------|
| -1 | Any standing |
| 0 | Match is tied |
| 1 | In the lead |
| 2 | Down |
| 3 | In the lead by more than one |
| 4 | Down by more than one |
| 5 | Not down |
| 6 | Not in the lead |
| 7 | In the lead by more than two |
| 8 | Down by more than two |
| 9 | Match is not tied |

### Red Card Criteria
| Value | Description |
|-------|-------------|
| -1 | Ignore red card status |
| 1 | My player red-carded |
| 2 | Opponent red-carded |
| 11-15 | My specific position red-carded |
| 21-25 | Opponent specific position red-carded |

## Key Implementation Features

### Tactical Management System
```python
def create_match_orders(lineup_data, tactical_settings):
    """Build comprehensive match orders with tactical intelligence"""
    return {
        'formation': analyze_formation_from_positions(lineup_data['positions']),
        'tactical_approach': tactical_settings['tactic'],
        'playing_style': tactical_settings['coachModifier'],
        'substitution_strategy': analyze_substitution_patterns(lineup_data['substitutions']),
        'special_roles': {
            'captain': lineup_data['captain'],
            'set_pieces': lineup_data['setPieces'],
            'penalty_takers': lineup_data['kickers']
        }
    }
```

### Conditional Order Management
```python
def build_conditional_substitution(player_in, player_out, conditions):
    """Create intelligent conditional substitutions"""
    return {
        'playerin': player_in,
        'playerout': player_out,
        'orderType': '1',  # Substitution
        'min': str(conditions.get('minute', 80)),
        'standing': str(conditions.get('goal_difference', -1)),
        'card': str(conditions.get('red_card_situation', -1)),
        'pos': str(conditions.get('new_position', -1)),
        'beh': str(conditions.get('new_behaviour', -1))
    }
```

### Rating Prediction Analysis
The `predictratings` action enables tactical analysis:
- **Sector Strength Calculation** - Predict defense, midfield, attack ratings
- **Tactical Effectiveness** - Analyze formation suitability for opponent
- **Player Role Optimization** - Test different position/behaviour combinations

## Strategic Usage Guidelines

### Match Preparation Tools
1. **Formation Optimizer** - Test different lineups with rating predictions
2. **Conditional Strategy Builder** - Create game-state responsive substitutions
3. **Tactical Analysis** - Compare tactical approaches against specific opponents

### Advanced Features Implementation
- **AI-Powered Lineup Suggestions** - Use player skills and opponent analysis
- **Historical Performance Integration** - Combine with past match results
- **Injury/Suspension Management** - Automatic backup player selection

### Integration Opportunities
- **Next Game Analyzer Enhancement** - Include tactical preparation interface
- **Training Integration** - Optimize lineups based on player development
- **Opposition Analysis** - Adjust tactics based on opponent's typical formation

## OAuth & Authentication

### Required Scopes
- **Basic Access**: View match orders for managed teams
- **set_matchorder**: Modify lineups and tactical settings (special permission required)

### Security Considerations
- **Team Ownership Validation**: Can only access/modify teams managed by authenticated user
- **Match Timing Restrictions**: Orders can only be set for upcoming matches
- **Rate Limiting**: Strict limits on lineup modifications to prevent abuse

### Error Handling
- **Invalid Formation**: Returns validation errors for illegal player positions
- **Player Availability**: Checks for injured/suspended players
- **Timing Restrictions**: Prevents orders for started/completed matches

## Technical Implementation Notes

### Position Management
- **Field Positions**: 0-13 (Goalkeeper to Left Forward)
- **Bench Organization**: Primary substitutes (7 slots) + Backup substitutes (7 slots)
- **Special Roles**: Captain, Set Pieces, Penalty Takers (11 kickers required)

### Data Validation
- **Required Fields**: All position slots must be specified (use ID "0" for empty)
- **Behaviour Consistency**: Valid behaviour codes for each position type
- **Substitution Logic**: Proper order type and criteria validation

## Related Endpoints
- **Players** (`file=players`) - Player skill data for tactical decisions
- **Matches** (`file=matches`) - Match results for tactical analysis
- **Team Details** (`file=teamdetails`) - Team context and tactical assistant level

---

*This comprehensive match orders endpoint enables sophisticated tactical management with full lineup control, conditional strategies, and predictive analysis for advanced team management.*