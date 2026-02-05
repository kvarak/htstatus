# CHPP API Reference: Players

**Purpose**: Comprehensive player management with detailed skills, statistics, and performance data
**Endpoint**: `/chppxml.ashx?file=players`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The Players endpoint provides complete player roster information including detailed skills, performance statistics, personality traits, and match data. This is the foundation endpoint for player management, analysis, and comparison features.

## Request Parameters

### Required
- `file=players` - Specifies the players endpoint

### Optional
- `version` - API version (latest recommended for full feature support)
- `actionType` - Data scope selection:
  - `view` (default) - Current team roster
  - `viewOldies` - Former players from youth academy or startup squad
  - `viewOldCoaches` - Ex-players now working as coaches
- `orderBy` - Sort field (default: "PlayerNumber")
  - Available fields: PlayerNumber, FirstName, LastName, Age, TSI, etc.
- `teamID` - Target team identifier
  - **Default**: Authenticated user's primary team
  - **Restriction**: Must be team managed by user or publicly accessible
- `includeMatchInfo` - Include LastMatch performance data (default: false)
  - **Performance Impact**: Increases response size significantly
  - **Use Case**: Essential for performance analysis features

## Response Structure

### Team Context
```xml
<HattrickData>
    <UserSupporterTier>platinum</UserSupporterTier>
    <IsYouth>false</IsYouth>
    <ActionType>view</ActionType>
    <IsPlayingMatch>false</IsPlayingMatch>
    <Team>
        <TeamID>789012</TeamID>
        <TeamName>Example FC</TeamName>
    </Team>
</HattrickData>
```

### Player Information Structure
```xml
<Player>
    <PlayerID>283974499</PlayerID>
    <FirstName>John</FirstName>
    <NickName>Johnny</NickName>
    <LastName>Smith</LastName>
    <PlayerNumber>7</PlayerNumber>
    <Age>23</Age>
    <AgeDays>45</AgeDays>
    <ArrivalDate>2024-07-15 12:00:00</ArrivalDate>
    <OwnerNotes>Star player potential</OwnerNotes>
    <TSI>3250</TSI>
    <PlayerForm>7</PlayerForm>
    <Statement>Ready to give 110% for the team!</Statement>
    <Experience>5</Experience>
    <Loyalty>6</Loyalty>
    <MotherClubBonus>true</MotherClubBonus>
    <Leadership>4</Leadership>
    <Salary>15680</Salary>
    <IsAbroad>false</IsAbroad>
</Player>
```

## Core Player Data

### Basic Information
- **PlayerID** - Unique identifier for all CHPP operations
- **Names** - FirstName, NickName (optional), LastName
- **PlayerNumber** - Jersey number (1-99)
- **Age/AgeDays** - Precise age tracking for skill development timing
- **ArrivalDate** - Transfer history and team tenure tracking

### Management Data
- **OwnerNotes** - Private notes (owner-only visibility)
- **Statement** - Player statement (Supporter feature)
- **TSI** - Total Skill Index for market value estimation
- **PlayerForm** - Current form level (1-8 scale)
- **Salary** - Weekly wage costs

## Player Skills System

### Core Skills (1-20 scale)
```xml
<StaminaSkill>8</StaminaSkill>
<KeeperSkill>1</KeeperSkill>
<PlaymakerSkill>7</PlaymakerSkill>
<ScorerSkill>9</ScorerSkill>
<PassingSkill>6</PassingSkill>
<WingerSkill>4</WingerSkill>
<DefenderSkill>5</DefenderSkill>
<SetPiecesSkill>3</SetPiecesSkill>
```

### Special Skills
- **Experience** - Match experience accumulation (affects performance consistency)
- **Loyalty** - Club attachment (affects transfer behavior)
- **Leadership** - Team leadership capability (affects team dynamics)

### Personality Traits
- **Agreeability** - Contract negotiation behavior
- **Aggressiveness** - Match behavior and card tendency
- **Honesty** - Fair play tendency and referee relations

## Performance Statistics

### Season Statistics
```xml
<LeagueGoals>12</LeagueGoals>
<CupGoals>3</CupGoals>
<FriendliesGoals>2</FriendliesGoals>
<AssistsCurrentTeam>8</AssistsCurrentTeam>
```

### Career Statistics
```xml
<CareerGoals>87</CareerGoals>
<CareerHattricks>4</CareerHattricks>
<CareerAssists>34</CareerAssists>
<MatchesCurrentTeam>156</MatchesCurrentTeam>
<GoalsCurrentTeam>45</GoalsCurrentTeam>
```

### Match Availability
- **Cards** - Suspension tracking (3 = suspended)
- **InjuryLevel** - Weeks injured (-1 = healthy, 0 = bruised)
- **IsPlayingMatch** - Currently in active match

## Advanced Features

### National Team Integration
```xml
<NationalTeamID>5047</NationalTeamID>
<CountryID>1</CountryID>
<Caps>12</Caps>
<CapsU20>8</CapsU20>
```

### Transfer Market Data
- **TransferListed** - Currently on transfer list
- **Specialty** - Special abilities (Technical, Quick, etc.)
- **PlayerCategoryId** - User-defined categorization

### Coach Information (Former Players)
```xml
<TrainerData>
    <TrainerType>1</TrainerType>
    <TrainerSkillLevel>3</TrainerSkillLevel>
</TrainerData>
```

### Last Match Performance (Optional)
```xml
<LastMatch>
    <Date>2026-02-01 15:00:00</Date>
    <MatchId>656789123</MatchId>
    <PositionCode>109</PositionCode>
    <PlayedMinutes>90</PlayedMinutes>
    <Rating>7.5</Rating>
    <RatingEndOfGame>8.0</RatingEndOfGame>
</LastMatch>
```

## Strategic Implementation Examples

### Player Analysis System
```python
def analyze_player_profile(player_data):
    """Comprehensive player analysis for team management"""
    skills = {
        'keeper': player_data['KeeperSkill'],
        'defender': player_data['DefenderSkill'],
        'playmaker': player_data['PlaymakerSkill'],
        'winger': player_data['WingerSkill'],
        'passing': player_data['PassingSkill'],
        'scorer': player_data['ScorerSkill'],
        'set_pieces': player_data['SetPiecesSkill'],
        'stamina': player_data['StaminaSkill']
    }

    # Determine best position based on skills
    position_suitability = calculate_position_ratings(skills)

    # Market value estimation
    estimated_value = calculate_market_value(
        player_data['TSI'],
        player_data['Age'],
        skills,
        player_data['Specialty']
    )

    # Development potential
    development_potential = assess_development_potential(
        player_data['Age'],
        player_data['AgeDays'],
        skills,
        player_data['PlayerForm']
    )

    return {
        'best_positions': position_suitability,
        'estimated_value': estimated_value,
        'development_potential': development_potential,
        'availability_status': check_availability(player_data),
        'performance_trend': analyze_recent_performance(player_data)
    }
```

### Team Composition Analysis
```python
def analyze_team_composition(players_list):
    """Analyze team balance and identify gaps"""
    position_coverage = {}
    age_distribution = {}
    skill_averages = {}

    for player in players_list:
        # Position strength analysis
        for position in calculate_viable_positions(player):
            position_coverage[position] = position_coverage.get(position, 0) + 1

        # Age profile tracking
        age_group = categorize_age(player['Age'])
        age_distribution[age_group] = age_distribution.get(age_group, 0) + 1

    return {
        'position_gaps': identify_weak_positions(position_coverage),
        'age_balance': assess_age_distribution(age_distribution),
        'skill_benchmarks': calculate_team_benchmarks(players_list),
        'transfer_priorities': suggest_transfer_targets(position_coverage)
    }
```

## Feature Integration Guidelines

### Player Comparison Tool (FEAT-010)
- **Multi-Player Analysis**: Side-by-side skill comparisons
- **Position Suitability**: Best role recommendations for each player
- **Development Tracking**: Age-based potential analysis
- **Market Value Assessment**: TSI and skill-based valuations

### Batch Group Management (FEAT-026)
- **Filtering Capabilities**: Age, skill level, position, form-based selection
- **Bulk Operations**: Group assignments and management actions
- **Category Management**: PlayerCategoryId utilization

### Training Integration
- **Skill Development Planning**: Age and current skill level optimization
- **Position Training**: Targeted skill improvement for specific roles
- **Form Management**: Training intensity based on current form

## Data Caching Strategy
- **Frequency**: Cache player data for session duration, refresh on explicit update
- **Differential Updates**: Track only changed statistics and skills
- **Performance**: Essential for comparison tools and frequent access patterns

## OAuth & Access Control

### Authentication Requirements
- **Team Ownership**: Full access to own team players
- **Public Access**: Basic information for other teams (skills, stats)
- **Private Data**: OwnerNotes, Salary visible only to team owner

### Supporter Features
- **Enhanced Data**: Player statements and advanced statistics
- **Historical Access**: Extended career statistics and performance data

### Error Handling
- **Invalid Team Access**: Returns error for unauthorized team access
- **Match In Progress**: Some statistics unavailable during active matches
- **Player Privacy**: Restricted data fields for non-owned teams

## Related Endpoints
- **Match Orders** (`file=matchorders`) - Lineup integration and tactical planning
- **Training** (`file=training`) - Skill development and training planning
- **Transfers** (`file=transfersplayer`) - Transfer market integration

---

*This comprehensive players endpoint enables sophisticated team management, player analysis, and strategic planning features for advanced Hattrick team management.*
