# CHPP API Reference: League Details

**Purpose**: Complete league standings and division information for tactical analysis and competitive intelligence
**Endpoint**: `/chppxml.ashx?file=leaguedetails`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The League Details endpoint provides comprehensive league table information including team standings, statistics, and division context. Essential for competitive analysis, next match preparation, and understanding league dynamics within your division.

## Request Parameters

### Required
- `file=leaguedetails` - Specifies the league details endpoint

### Optional
- `version` - API version (latest recommended)
- `leagueLevelUnitID` - Target league unit ID (unsigned integer)
  - **Default**: League unit of authenticated user's primary club
  - **Usage**: Access any league unit for scouting and analysis
  - **Scope**: Can access any public league standings data

## Response Structure

### League Context Information
```xml
<HattrickData>
    <LeagueID>3</LeagueID>
    <LeagueName>Sverige</LeagueName>
    <LeagueLevel>4</LeagueLevel>
    <MaxLevel>8</MaxLevel>
    <LeagueLevelUnitID>45231</LeagueLevelUnitID>
    <LeagueLevelUnitName>IV.12</LeagueLevelUnitName>
    <CurrentMatchRound>12</CurrentMatchRound>
    <Rank>340</Rank>
</HattrickData>
```

### League Metadata
- **LeagueID** - Country/national league identifier
- **LeagueName** - Country name (Sverige, USA, England, etc.)
- **LeagueLevel** - Division tier (1 = top division, 2 = second tier, etc.)
- **MaxLevel** - Total number of divisions in country
- **LeagueLevelUnitID** - Specific division identifier
- **LeagueLevelUnitName** - Division name (e.g., "IV.12", "II.3")
- **CurrentMatchRound** - Current week/round in season
- **Rank** - Division ranking within its level

### Team Standings Data
```xml
<Team>
    <UserId>123456</UserId>
    <TeamID>789012</TeamID>
    <Position>3</Position>
    <PositionChange>1</PositionChange>
    <TeamName>Example FC</TeamName>
    <Matches>11</Matches>
    <GoalsFor>28</GoalsFor>
    <GoalsAgainst>15</GoalsAgainst>
    <Points>24</Points>
    <Won>8</Won>
    <Draws>0</Draws>
    <Lost>3</Lost>
</Team>
```

### Team Statistics
- **UserId** - Team manager's user identifier
- **TeamID** - Unique team identifier
- **Position** - Current league table position
- **PositionChange** - Movement indicator (up/down/stable)
- **TeamName** - Full team name
- **Matches** - Games played in current season
- **GoalsFor/GoalsAgainst** - Attack and defense performance
- **Points** - Total league points earned
- **Won/Draws/Lost** - Match result breakdown

## Key Implementation Notes

### Position Change Indicators
Position changes typically use:
- Positive values: Moving up the table
- Zero: No change from previous round
- Negative values: Dropping down the table

### League Table Calculations
```python
# Standard league table logic
def calculate_form_and_trends(teams_data):
    for team in teams_data:
        # Goal difference
        team['goal_difference'] = team['GoalsFor'] - team['GoalsAgainst']

        # Points per game
        if team['Matches'] > 0:
            team['points_per_game'] = team['Points'] / team['Matches']

        # Win percentage
        team['win_percentage'] = (team['Won'] / team['Matches']) * 100 if team['Matches'] > 0 else 0

        # Form trend (based on PositionChange)
        team['form_trend'] = 'improving' if team['PositionChange'] > 0 else 'declining' if team['PositionChange'] < 0 else 'stable'

    return teams_data
```

### Competitive Intelligence Features
- **Promotion/Relegation Analysis** - Identify promotion battles and relegation fights
- **Goal Difference Tracking** - Monitor attacking and defensive trends
- **Form Analysis** - Track position changes and momentum shifts

## Strategic Usage Guidelines

### Next Match Preparation
1. **Opponent Analysis** - Research upcoming opponent's league form and statistics
2. **Tactical Insights** - Understand opponent's attacking/defensive patterns from league stats
3. **Pressure Assessment** - Identify teams fighting for promotion or against relegation

### League Monitoring Features
- **Division Scouting** - Monitor multiple divisions for transfer targets or tactical patterns
- **Competitive Landscape** - Track promotion/relegation battles affecting your rivals
- **Performance Benchmarking** - Compare your team's statistics against division averages

### Feature Integration Opportunities
- **Next Game Analyzer Enhancement** - Include opponent's league form and position pressure
- **League Table Visualization** - Interactive standings with trend analysis and predictions
- **Promotion Calculator** - Project points needed for promotion based on current standings

## Data Caching Strategy
- **Frequency**: Updates after each match round completion
- **Storage**: Cache complete league tables for trend analysis across multiple rounds
- **Performance**: Essential data for multiple features (match preparation, competitive analysis)

## League System Context

### Division Structure Understanding
```python
# League system navigation
def analyze_league_context(league_data):
    level = league_data['LeagueLevel']
    max_level = league_data['MaxLevel']

    context = {
        'tier': 'top' if level == 1 else 'mid' if level <= max_level//2 else 'lower',
        'promotion_available': level > 1,
        'relegation_risk': level < max_level,
        'competitive_level': 'elite' if level <= 2 else 'competitive' if level <= 4 else 'developmental'
    }

    return context
```

## OAuth & Access Control

### Authentication Requirements
- **OAuth Scope**: Basic authentication sufficient for public league data
- **Data Access**: All league standings are publicly accessible
- **Rate Limiting**: Standard CHPP limits apply for bulk league data requests

### Error Handling
- **Invalid League Unit**: Returns error if leagueLevelUnitID doesn't exist
- **Season Transition**: May have limited data during season changeover periods
- **Match Day Updates**: Data may be updating during match processing times

## Related Endpoints
- **Team Details** (`file=teamdetails`) - Detailed team performance metrics beyond league statistics
- **Matches** (`file=matches`) - Head-to-head records and detailed match results
- **Fans** (`file=fans`) - Fan expectations and mood related to league position

---

*This comprehensive league endpoint enables sophisticated competitive analysis and tactical preparation features for strategic team management.*