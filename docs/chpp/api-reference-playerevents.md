# CHPP API Reference: Player Events

**Purpose**: Individual player event history including goals, assists, cards, injuries, transfers, and career milestones
**Endpoint**: `/chppxml.ashx?file=playerevents`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The Player Events API provides comprehensive event history for individual players, tracking their career progression through goals, assists, bookings, injuries, transfers, and other significant milestones. This endpoint is essential for player development tracking, career statistics, and historical performance analysis.

## Request Parameters

### Required
- `file=playerevents` - Specifies the player events endpoint

### Optional
- `version` - API version (latest recommended for full features)
- `playerID` - Specific player ID to get events for (unsigned Integer)
  - If not provided, returns events for players accessible to authenticated user
  - Must be a player the authenticated user has permission to view

## Response Structure

### Player Events Data
```xml
<HattrickData>
    <UserSupporterTier>platinum</UserSupporterTier>

    <Player>
        <PlayerID>12345678</PlayerID>

        <PlayerEvents Available="true">
            <PlayerEvent>
                <EventDate>2026-02-05 15:47:00</EventDate>
                <PlayerEventTypeID>1</PlayerEventTypeID>
                <EventText>Scored a goal in the 65th minute against Example United</EventText>
            </PlayerEvent>

            <PlayerEvent>
                <EventDate>2026-01-28 16:23:00</EventDate>
                <PlayerEventTypeID>5</PlayerEventTypeID>
                <EventText>Received a yellow card for unsporting behavior</EventText>
            </PlayerEvent>

            <PlayerEvent>
                <EventDate>2026-01-15 14:15:00</EventDate>
                <PlayerEventTypeID>3</PlayerEventTypeID>
                <EventText>Made an assist in the 42nd minute</EventText>
            </PlayerEvent>

            <!-- Additional events in reverse chronological order -->
        </PlayerEvents>
    </Player>
</HattrickData>
```

### Events Not Available
```xml
<HattrickData>
    <UserSupporterTier>none</UserSupporterTier>

    <Player>
        <PlayerID>12345678</PlayerID>

        <PlayerEvents Available="false">
            <!-- No events returned -->
        </PlayerEvents>
    </Player>
</HattrickData>
```

## Data Field Reference

### Player Event Type IDs

**Note**: The CHPP documentation states that no official list of event types is provided. Each application must collect and categorize event types based on observed data. Based on common Hattrick player events, typical categories include:

#### Match Performance Events
- **Goals** - Player scored in a match
- **Assists** - Player provided an assist for a goal
- **Hat-tricks** - Player scored 3+ goals in a single match
- **Clean Sheets** - Goalkeeper kept a clean sheet
- **Man of the Match** - Player was awarded best player

#### Disciplinary Events
- **Yellow Cards** - Player received yellow card for misconduct
- **Red Cards** - Player received red card and was sent off
- **Suspensions** - Player suspended for accumulated cards or serious offenses

#### Injury & Health Events
- **Injuries** - Player suffered injury during match or training
- **Recovery** - Player returned from injury
- **Fitness Changes** - Significant stamina or form changes

#### Career Milestones
- **Transfers** - Player joined or left the team
- **Contract Extensions** - Player signed new contract
- **Position Changes** - Player position or role changed
- **Skill Improvements** - Notable skill level increases
- **International Call-ups** - Selected for national team

#### Training & Development
- **Training Achievements** - Completed specific training programs
- **Youth Promotion** - Promoted from youth to senior team
- **Specialty Assignments** - Assigned special roles (captain, set pieces)

### Event Text Formatting
- **HTML Encoded**: Event descriptions may contain HTML tags for formatting
- **Language**: Text appears in the language of the authenticated user's Hattrick account
- **Dynamic Content**: May include opponent names, match details, and contextual information

### Data Availability
- **Available**: Boolean indicating if player events are accessible
- **Supporter Dependency**: Some features may require Hattrick Supporter status
- **Permission Based**: Only players visible to authenticated user are accessible
- **Historical Depth**: Events may have retention limits based on player activity

## Implementation Examples

### Basic Player Events Retrieval
```python
# Get events for specific player
player_events = chpp.player_events(player_id=12345678)

if player_events.player_events.available:
    print(f"Found {len(player_events.player_events.events)} events for player")
    for event in player_events.player_events.events:
        print(f"{event.event_date}: {event.event_text}")
else:
    print("Player events not available")
```

### Event Type Analysis
```python
# Categorize events by type
event_types = {}
for event in player_events.player_events.events:
    event_type = event.player_event_type_id
    if event_type not in event_types:
        event_types[event_type] = []
    event_types[event_type].append(event)

# Analyze most common event types
for event_type, events in sorted(event_types.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"Event Type {event_type}: {len(events)} occurrences")
    print(f"  Latest: {events[0].event_text}")
```

### Career Timeline Creation
```python
# Create chronological career timeline
career_timeline = []
for event in player_events.player_events.events:
    timeline_entry = {
        'date': event.event_date,
        'type': event.player_event_type_id,
        'description': event.event_text,
        'season': determine_season_from_date(event.event_date)
    }
    career_timeline.append(timeline_entry)

# Sort by date (most recent first)
career_timeline.sort(key=lambda x: x['date'], reverse=True)

# Group by season for analysis
seasons = {}
for entry in career_timeline:
    season = entry['season']
    if season not in seasons:
        seasons[season] = []
    seasons[season].append(entry)
```

### Match Performance Tracking
```python
# Track match-related events
def categorize_match_events(events):
    match_performance = {
        'goals': [],
        'assists': [],
        'cards': [],
        'injuries': [],
        'other': []
    }

    for event in events:
        text = event.event_text.lower()
        if 'goal' in text or 'scored' in text:
            match_performance['goals'].append(event)
        elif 'assist' in text:
            match_performance['assists'].append(event)
        elif 'card' in text or 'yellow' in text or 'red' in text:
            match_performance['cards'].append(event)
        elif 'injury' in text or 'injured' in text:
            match_performance['injuries'].append(event)
        else:
            match_performance['other'].append(event)

    return match_performance

performance = categorize_match_events(player_events.player_events.events)
print(f"Goals: {len(performance['goals'])}, Assists: {len(performance['assists'])}")
```

### Event Type Discovery
```python
# Discover and catalog event types from event text patterns
def discover_event_patterns(events):
    patterns = {}

    for event in events:
        event_type = event.player_event_type_id
        if event_type not in patterns:
            patterns[event_type] = {
                'count': 0,
                'examples': [],
                'keywords': set()
            }

        patterns[event_type]['count'] += 1
        if len(patterns[event_type]['examples']) < 3:
            patterns[event_type]['examples'].append(event.event_text)

        # Extract keywords for pattern recognition
        words = event.event_text.lower().split()
        key_words = [w for w in words if len(w) > 3 and w.isalpha()]
        patterns[event_type]['keywords'].update(key_words[:3])

    return patterns

# Build event type catalog for your application
event_catalog = discover_event_patterns(player_events.player_events.events)
for event_type, data in event_catalog.items():
    print(f"Type {event_type}: {data['count']} events")
    print(f"  Keywords: {list(data['keywords'])[:5]}")
    print(f"  Example: {data['examples'][0] if data['examples'] else 'None'}")
```

## Usage Notes

### Data Availability Constraints
- **Player Visibility**: Only accessible for players the authenticated user can view
- **Supporter Features**: Some functionality may require Hattrick Supporter status
- **Historical Limits**: Event history may have retention limits
- **Performance Impact**: Large event histories may result in substantial response sizes

### Event Type Management
- **No Official List**: Event types must be discovered and categorized by each application
- **Dynamic Nature**: New event types may be introduced over time
- **Language Dependency**: Event text varies by user language settings
- **Pattern Recognition**: Use text analysis to categorize and filter events

### Implementation Considerations
- **Rate Limiting**: Consider batching requests for multiple players
- **Caching Strategy**: Cache player events to reduce API calls
- **Error Handling**: Handle cases where events are not available
- **Data Processing**: Parse HTML content in event text appropriately

### Performance Optimization
- **Selective Loading**: Request specific players rather than bulk data
- **Progressive Enhancement**: Load events on-demand for active players
- **Event Filtering**: Filter events client-side to reduce processing
- **Historical Analysis**: Cache aggregated statistics to improve performance

## Integration with HattrickPlanner

### Player Development Tracking
- **Career Progression**: Track skill development and milestone achievements
- **Performance Trends**: Identify patterns in player performance over time
- **Injury History**: Monitor player fitness and injury patterns
- **Match Contributions**: Quantify player impact through goals and assists

### Team Analytics
- **Squad Performance**: Aggregate player events for team-wide insights
- **Transfer Analysis**: Track player performance before and after transfers
- **Tactical Analysis**: Correlate events with tactical changes and formations
- **Historical Comparison**: Compare current performance with historical data

### Strategic Planning
- **Player Valuation**: Use career events to assess player value and potential
- **Squad Management**: Identify players at risk or showing improvement
- **Match Preparation**: Review opponent player histories for tactical planning
- **Development Focus**: Target training based on player event patterns

## Related Endpoints

- **[playerdetails](api-reference-playerdetails.md)** - Current player information and statistics
- **[matchdetails](api-reference-matchdetails.md)** - Match-specific events and performance data
- **[matchlineup](api-reference-matchlineup.md)** - Match lineup with individual player ratings
- **[training](api-reference-training.md)** - Player training and development history

This endpoint provides the historical context and event tracking necessary for comprehensive player development analysis and career progression monitoring in HattrickPlanner.
