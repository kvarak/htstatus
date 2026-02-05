# CHPP API Reference: League Levels

**Purpose**: League structure information including division levels, promotion/demotion slots, and series organization for specific leagues
**Endpoint**: `/chppxml.ashx?file=leaguelevels`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The League Levels API provides comprehensive information about the hierarchical structure of Hattrick leagues, including the number of divisions, series per level, promotion and demotion slots, and organizational details. This endpoint is essential for understanding league structures, competitive pathways, and navigating the promotion/demotion system.

## Request Parameters

### Required
- `file=leaguelevels` - Specifies the league levels endpoint

### Optional
- `version` - API version (latest recommended for full features)
- `LeagueID` - League identifier (unsigned Integer, default: logged-in user's primary team league)
  - Examples: Sverige (Sweden), USA, England, Deutschland (Germany)
  - If not specified, returns structure for user's home league

## Response Structure

### League Structure Overview
```xml
<HattrickData>
    <LeagueID>5</LeagueID>
    <Season>82</Season>
    <NrOfLeagueLevels>6</NrOfLeagueLevels>

    <LeagueLevelList>
        <LeagueLevelItem>
            <LeagueLevel>1</LeagueLevel>
            <NrOfLeagueLevelUnits>1</NrOfLeagueLevelUnits>
            <NrOfTeams>8</NrOfTeams>
            <LeagueLevelUnitIdList>12345</LeagueLevelUnitIdList>
            <NrOfSharedPromotionSlotsPerSeries>0</NrOfSharedPromotionSlotsPerSeries>
            <NrOfDirectPromotionSlotsPerSeries>0</NrOfDirectPromotionSlotsPerSeries>
            <NrOfQualificationPromotionSlotsPerSeries>0</NrOfQualificationPromotionSlotsPerSeries>
            <NrOfDirectDemotionSlotsPerSeries>2</NrOfDirectDemotionSlotsPerSeries>
            <NrOfQualificationDemotionSlotsPerSeries>1</NrOfQualificationDemotionSlotsPerSeries>
        </LeagueLevelItem>

        <LeagueLevelItem>
            <LeagueLevel>2</LeagueLevel>
            <NrOfLeagueLevelUnits>4</NrOfLeagueLevelUnits>
            <NrOfTeams>8</NrOfTeams>
            <LeagueLevelUnitIdList>12346,12347,12348,12349</LeagueLevelUnitIdList>
            <NrOfSharedPromotionSlotsPerSeries>0</NrOfSharedPromotionSlotsPerSeries>
            <NrOfDirectPromotionSlotsPerSeries>1</NrOfDirectPromotionSlotsPerSeries>
            <NrOfQualificationPromotionSlotsPerSeries>1</NrOfQualificationPromotionSlotsPerSeries>
            <NrOfDirectDemotionSlotsPerSeries>2</NrOfDirectDemotionSlotsPerSeries>
            <NrOfQualificationDemotionSlotsPerSeries>1</NrOfQualificationDemotionSlotsPerSeries>
        </LeagueLevelItem>

        <!-- Additional levels 3-6 -->
    </LeagueLevelList>
</HattrickData>
```

## Data Field Reference

### League Context
- **LeagueID**: Unique identifier for the league/country
- **Season**: Current season number for this league
- **NrOfLeagueLevels**: Total number of division levels in the league system

### League Level Details
- **LeagueLevel**: Division number (1 = top division, 2 = second tier, etc.)
- **NrOfLeagueLevelUnits**: Number of series/groups at this level
- **NrOfTeams**: Teams per series at this level (typically 8)
- **LeagueLevelUnitIdList**: Comma-separated list of series IDs at this level

### Promotion System
- **NrOfDirectPromotionSlotsPerSeries**: Automatic promotion positions per series
- **NrOfQualificationPromotionSlotsPerSeries**: Promotion playoff positions per series
- **NrOfSharedPromotionSlotsPerSeries**: Shared promotion slots across multiple series

### Demotion System
- **NrOfDirectDemotionSlotsPerSeries**: Automatic relegation positions per series
- **NrOfQualificationDemotionSlotsPerSeries**: Relegation playoff positions per series

### Common League Structures

#### Typical Top-Tier League (Level 1)
- **Teams**: 8 teams in single series
- **Promotion**: N/A (already top division)
- **Demotion**: 2-3 direct + 1 qualification spot

#### Second-Tier League (Level 2)
- **Teams**: 8 teams per series, multiple series
- **Promotion**: 1 direct + 1 qualification to Level 1
- **Demotion**: 2 direct + 1 qualification to Level 3

#### Lower Divisions (Levels 3+)
- **Teams**: 8 teams per series, increasing number of series
- **Promotion**: 1-2 spots to higher level
- **Demotion**: 1-3 spots to lower level

## Implementation Examples

### Basic League Structure Retrieval
```python
# Get league structure for user's home league
league_levels = chpp.league_levels()

print(f"League ID: {league_levels.league_id}")
print(f"Season: {league_levels.season}")
print(f"Total Levels: {league_levels.nr_of_league_levels}")
```

### Analyze League Hierarchy
```python
# Examine league structure details
for level in league_levels.league_level_list:
    print(f"Level {level.league_level}:")
    print(f"  Series: {level.nr_of_league_level_units}")
    print(f"  Teams per series: {level.nr_of_teams}")
    print(f"  Total teams: {int(level.nr_of_league_level_units) * level.nr_of_teams}")

    # Promotion opportunities
    total_promotion = (level.nr_of_direct_promotion_slots_per_series +
                      level.nr_of_qualification_promotion_slots_per_series)
    if total_promotion > 0:
        print(f"  Promotion slots: {total_promotion} per series")

    # Demotion risks
    total_demotion = (level.nr_of_direct_demotion_slots_per_series +
                     level.nr_of_qualification_demotion_slots_per_series)
    if total_demotion > 0:
        print(f"  Demotion slots: {total_demotion} per series")
```

### Calculate League Statistics
```python
# Calculate total teams and competitive structure
total_teams = 0
promotion_paths = []

for level in league_levels.league_level_list:
    level_teams = int(level.nr_of_league_level_units) * level.nr_of_teams
    total_teams += level_teams

    if level.league_level < league_levels.nr_of_league_levels:
        # Calculate promotion opportunities to next level
        promotion_per_series = (level.nr_of_direct_promotion_slots_per_series +
                               level.nr_of_qualification_promotion_slots_per_series)
        total_promotions = int(level.nr_of_league_level_units) * promotion_per_series

        promotion_paths.append({
            'from_level': level.league_level,
            'to_level': level.league_level - 1,
            'total_slots': total_promotions,
            'teams_competing': level_teams,
            'promotion_rate': (total_promotions / level_teams * 100)
        })

print(f"Total teams in league: {total_teams}")
for path in promotion_paths:
    print(f"Level {path['from_level']} → {path['to_level']}: "
          f"{path['promotion_rate']:.1f}% promotion rate")
```

### Series Navigation
```python
# Get specific series information for a level
def get_series_ids_for_level(league_levels, target_level):
    for level in league_levels.league_level_list:
        if level.league_level == target_level:
            series_ids = level.league_level_unit_id_list.split(',')
            return [int(series_id.strip()) for series_id in series_ids if series_id.strip()]
    return []

# Get all second division series
level_2_series = get_series_ids_for_level(league_levels, 2)
print(f"Second division series IDs: {level_2_series}")

# Use these IDs with leaguedetails API for specific series information
for series_id in level_2_series:
    # series_details = chpp.league_details(league_level_unit_id=series_id)
    print(f"Series {series_id} - use with leaguedetails API")
```

### International League Comparison
```python
# Compare different league structures
leagues_to_compare = {
    5: "England",
    1: "Sverige",
    7: "Deutschland",
    2: "Italia"
}

league_stats = {}
for league_id, league_name in leagues_to_compare.items():
    try:
        league_data = chpp.league_levels(league_id=league_id)

        # Calculate total teams
        total_teams = sum(
            int(level.nr_of_league_level_units) * level.nr_of_teams
            for level in league_data.league_level_list
        )

        league_stats[league_name] = {
            'levels': league_data.nr_of_league_levels,
            'total_teams': total_teams,
            'season': league_data.season
        }
    except Exception as e:
        print(f"Could not fetch data for {league_name}: {e}")

# Display comparison
for league_name, stats in league_stats.items():
    print(f"{league_name}: {stats['levels']} levels, "
          f"{stats['total_teams']} teams, season {stats['season']}")
```

## Usage Notes

### Data Characteristics
- **Static Structure**: League levels rarely change during a season
- **Season Dependency**: Structure may evolve between seasons
- **Country Specific**: Each league has unique promotion/demotion rules
- **Series Identification**: Use LeagueLevelUnitIdList for detailed series access

### Performance Considerations
- **Caching Recommended**: Structure data changes infrequently
- **League Navigation**: Use series IDs with other APIs (leaguedetails, leaguefixtures)
- **Batch Processing**: Fetch multiple league structures if comparing internationally
- **Rate Limiting**: Standard CHPP limits apply for international comparisons

### Integration Patterns
- **Series Navigation**: Use with leaguedetails API for specific series information
- **Team Context**: Understand user's team position within league hierarchy
- **Competitive Analysis**: Calculate promotion/demotion probabilities
- **Historical Tracking**: Monitor league structure changes over seasons

### Special Considerations
- **New Leagues**: Recently created leagues may have evolving structures
- **Expansion Seasons**: Some seasons feature league restructuring
- **Qualification Systems**: Complex promotion/demotion rules in some leagues
- **Regional Variations**: Different countries implement unique competitive structures

## Integration with HattrickPlanner

### Strategic Applications
- **League Navigation**: Help users understand their competitive environment
- **Promotion Planning**: Calculate requirements for advancement
- **Opponent Analysis**: Identify teams at similar competitive levels
- **Long-term Planning**: Understand promotion pathways and competitive structure

### User Experience Features
- **League Visualization**: Display hierarchical league structure
- **Promotion Tracker**: Show current standing relative to promotion/demotion
- **Competitive Context**: Explain league system to new users
- **International Comparison**: Compare league structures across countries

### Data Integration
- **Team Positioning**: Combine with league tables for competitive context
- **Match Importance**: Weight matches based on promotion/demotion implications
- **Historical Progression**: Track team advancement through league levels
- **Strategic Planning**: Inform long-term team development goals

## Related Endpoints

- **[leaguedetails](api-reference-leaguedetails.md)** - Detailed information about specific series
- **[leaguefixtures](api-reference-leaguefixtures.md)** - Fixtures and results for specific series
- **[teamdetails](api-reference-teamdetails.md)** - Team information including league position
- **[matches-basic](api-reference-matches-basic.md)** - Recent matches with league context

This endpoint provides the structural foundation for understanding Hattrick's competitive hierarchy and is essential for contextualizing team performance within the broader league system.
