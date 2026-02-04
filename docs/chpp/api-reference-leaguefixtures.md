# CHPP API Reference: League Fixtures

**Purpose**: Complete fixture schedules and match results for league divisions with historical season support
**Endpoint**: `/chppxml.ashx?file=leaguefixtures`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The League Fixtures endpoint provides complete match schedules and results for any league division, with support for historical seasons. Essential for fixture analysis, season planning, and comprehensive league monitoring across multiple divisions and time periods.

## Request Parameters

### Required
- `file=leaguefixtures` - Specifies the league fixtures endpoint

### Optional
- `version` - API version (latest recommended)
- `leagueLevelUnitID` - Target league unit ID (unsigned integer)
  - **Default**: League unit of authenticated user's primary club
  - **Usage**: Access any league unit for scouting and historical analysis
  - **Scope**: Can access any public league fixture data
- `season` - Target season (unsigned integer)
  - **Default**: Current active season
  - **Usage**: Historical analysis and season comparison
  - **Range**: Any completed or current season

## Response Structure

### League Context
```xml
<HattrickData>
    <LeagueLevelUnitID>45231</LeagueLevelUnitID>
    <LeagueLevelUnitName>IV.12</LeagueLevelUnitName>
    <Season>85</Season>
</HattrickData>
```

### League Metadata
- **LeagueLevelUnitID** - Specific division identifier
- **LeagueLevelUnitName** - Division name (e.g., "IV.12", "II.3")
- **Season** - Season number for the returned fixture data

### Match Fixture Data
```xml
<Match>
    <MatchID>656789123</MatchID>
    <MatchRound>12</MatchRound>
    <HomeTeam>
        <HomeTeamID>789012</HomeTeamID>
        <HomeTeamName>Example FC</HomeTeamName>
    </HomeTeam>
    <AwayTeam>
        <AwayTeamID>345678</AwayTeamID>
        <AwayTeamName>Rival United</AwayTeamName>
    </AwayTeam>
    <MatchDate>2026-02-08 15:00:00</MatchDate>
    <HomeGoals>2</HomeGoals>
    <AwayGoals>1</AwayGoals>
</Match>
```

### Match Information
- **MatchID** - Unique match identifier for detailed match data retrieval
- **MatchRound** - Week/round number within the season
- **HomeTeam/AwayTeam** - Team identifiers and names
- **MatchDate** - Kickoff date and time
- **HomeGoals/AwayGoals** - Final scores (only present for completed matches)

## Key Implementation Notes

### Match Status Detection
```python
def analyze_match_status(match_data):
    """Determine match status and extract relevant information"""
    has_goals = 'HomeGoals' in match_data and 'AwayGoals' in match_data
    match_date = datetime.fromisoformat(match_data['MatchDate'])
    now = datetime.now()

    if has_goals:
        return {
            'status': 'completed',
            'result': f"{match_data['HomeGoals']}-{match_data['AwayGoals']}",
            'winner': 'home' if match_data['HomeGoals'] > match_data['AwayGoals']
                     else 'away' if match_data['AwayGoals'] > match_data['HomeGoals']
                     else 'draw'
        }
    elif match_date < now:
        return {'status': 'in_progress', 'kickoff': match_date}
    else:
        return {'status': 'scheduled', 'kickoff': match_date}
```

### Fixture Analysis Features
- **Season Progress Tracking** - Monitor completion percentage and remaining fixtures
- **Head-to-Head Records** - Extract historical matchups between specific teams
- **Home/Away Balance** - Analyze venue distribution for competitive advantage assessment

## Strategic Usage Guidelines

### Fixture Planning Tools
1. **Next Fixtures Analysis** - Identify upcoming matches for tactical preparation
2. **Remaining Season Projection** - Calculate possible outcomes based on remaining fixtures
3. **Historical Performance** - Compare current season progress with previous seasons

### League Monitoring Features
- **Multi-Division Scouting** - Track fixtures across multiple leagues for player scouting
- **Promotion Battle Tracking** - Monitor key matches affecting promotion/relegation
- **Season Timeline Visualization** - Create calendar views of complete league schedules

### Feature Integration Opportunities
- **Next Game Analyzer Enhancement** - Use fixture data to prepare detailed opponent analysis
- **League Table Predictions** - Combine fixtures with current standings for projection models
- **Historical Trend Analysis** - Compare team performance patterns across multiple seasons

## Advanced Implementation Examples

### Fixture Difficulty Analysis
```python
def calculate_fixture_difficulty(fixtures, team_standings):
    """Analyze remaining fixture difficulty for teams"""
    difficulty_scores = {}

    for match in fixtures:
        home_team = match['HomeTeam']['HomeTeamID']
        away_team = match['AwayTeam']['AwayTeamID']

        # Get opponent strength from current standings
        home_opponent = away_team
        away_opponent = home_team

        # Calculate difficulty based on opponent position and home advantage
        home_difficulty = calculate_opponent_strength(away_team, team_standings)
        away_difficulty = calculate_opponent_strength(home_team, team_standings) * 1.1  # Away penalty

        difficulty_scores[home_team] = difficulty_scores.get(home_team, 0) + home_difficulty
        difficulty_scores[away_team] = difficulty_scores.get(away_team, 0) + away_difficulty

    return difficulty_scores
```

### Season Comparison Tools
```python
def compare_season_progress(current_fixtures, historical_fixtures, team_id):
    """Compare current season progress with historical performance"""
    current_progress = analyze_team_fixtures(current_fixtures, team_id)
    historical_progress = analyze_team_fixtures(historical_fixtures, team_id)

    return {
        'current_points_pace': current_progress['points_per_game'],
        'historical_points_pace': historical_progress['points_per_game'],
        'improvement': current_progress['points_per_game'] - historical_progress['points_per_game'],
        'current_position_trend': current_progress['position_trend'],
        'remaining_matches': current_progress['matches_remaining']
    }
```

## Data Caching Strategy
- **Frequency**: Cache complete season fixtures, update match results after completion
- **Historical Data**: Store completed seasons permanently for trend analysis
- **Performance**: Essential for league table predictions and fixture analysis tools

## Multi-Season Analysis

### Historical Context Integration
- **Season Progression Patterns** - Track how teams perform in different parts of seasons
- **Venue Performance Analysis** - Home vs away record analysis across seasons
- **Tactical Evolution** - Monitor scoring patterns and defensive trends over time

### Predictive Analytics Support
- **Remaining Fixture Analysis** - Project final table positions based on fixture difficulty
- **Promotion Probability Calculator** - Use fixture data for mathematical promotion chances
- **Performance Trend Projection** - Combine historical patterns with current season data

## OAuth & Access Control

### Authentication Requirements
- **OAuth Scope**: Basic authentication sufficient for public fixture data
- **Historical Access**: All seasons accessible for analysis and comparison
- **Data Privacy**: Fixture information is publicly available

### Error Handling
- **Invalid League Unit**: Returns error if leagueLevelUnitID doesn't exist
- **Invalid Season**: Returns error for non-existent season numbers
- **Season Transition**: May have incomplete data during season changeover periods

## Related Endpoints
- **League Details** (`file=leaguedetails`) - Current standings to complement fixture analysis
- **Matches** (`file=matches`) - Detailed match information for specific fixtures
- **Team Details** (`file=teamdetails`) - Team performance context for fixture analysis

---

*This comprehensive fixtures endpoint enables sophisticated season analysis, fixture planning, and multi-division monitoring for strategic team management and competitive intelligence.*