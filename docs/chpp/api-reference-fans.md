# CHPP API Reference: Fans

**Purpose**: Fanclub management and supporter sentiment analysis with match-based mood tracking
**Endpoint**: `/chppxml.ashx?file=fans`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The Fans endpoint provides comprehensive fanclub information including supporter mood, expectations, and reactions to recent matches. Essential for understanding fan engagement, managing expectations, and analyzing team performance impact on supporter base.

## Request Parameters

### Required
- `file=fans` - Specifies the fanclub data endpoint

### Optional
- `version` - API version (latest recommended)
- `teamId` - Target team ID (unsigned integer)
  - **Default**: Your primary club senior team ID
  - **Restriction**: Must refer to a senior team managed by requesting user
  - **Security**: Cannot access other users' fanclub data

## Response Structure

### Fanclub Information
```xml
<Team>
    <TeamID>12345</TeamID>
    <FanClubId>67890</FanClubId>
    <FanClubName>Example FC Supporters</FanClubName>
    <FanMood>7</FanMood>
    <Members>15420</Members>
    <FanSeasonExpectation>4</FanSeasonExpectation>
</Team>
```

### Core Fanclub Metrics
- **FanClubId** - Unique identifier for the supporter organization
- **FanClubName** - Custom fanclub name (empty if not set by user)
- **FanMood** - Current supporter satisfaction level (0-11 scale)
  - **Availability**: Not available during active matches
- **Members** - Total fanclub membership size
- **FanSeasonExpectation** - Supporter expectations for current season (0-7 scale)

### Match History with Fan Reactions
```xml
<PlayedMatches>
    <Match>
        <MatchID>98765</MatchID>
        <HomeTeam>
            <HomeTeamID>12345</HomeTeamID>
            <HomeTeamName>Example FC</HomeTeamName>
        </HomeTeam>
        <AwayTeam>
            <AwayTeamID>54321</AwayTeamID>
            <AwayTeamName>Rival FC</AwayTeamName>
        </AwayTeam>
        <MatchDate>2026-02-01 15:00:00</MatchDate>
        <MatchType>1</MatchType>
        <HomeGoals>2</HomeGoals>
        <AwayGoals>1</AwayGoals>
        <FanMatchExpectation>5</FanMatchExpectation>
        <FanMoodAfterMatch>8</FanMoodAfterMatch>
        <Weather>1</Weather>
        <SoldSeats>18500</SoldSeats>
    </Match>
</PlayedMatches>
```

### Upcoming Match Expectations
```xml
<UpcomingMatches>
    <Match>
        <MatchID>98766</MatchID>
        <HomeTeam>
            <HomeTeamID>12345</HomeTeamID>
            <HomeTeamName>Example FC</HomeTeamName>
        </HomeTeam>
        <AwayTeam>
            <AwayTeamID>11111</AwayTeamID>
            <AwayTeamName>Strong FC</AwayTeamName>
        </AwayTeam>
        <MatchDate>2026-02-08 15:00:00</MatchDate>
        <MatchType>1</MatchType>
        <FanMatchExpectation>3</FanMatchExpectation>
    </Match>
</UpcomingMatches>
```

## Reference Tables

### Fan Match Expectations (0-8 Scale)
| Value | Description |
|-------|-------------|
| 8 | We will win |
| 7 | We are favourites |
| 6 | We have the edge |
| 5 | It will be a close affair |
| 4 | They have the edge |
| 3 | They are favourites |
| 2 | We will lose |
| 1 | We are outclassed |
| 0 | Better not show up |

### Fan Mood (0-11 Scale)
| Value | Description |
|-------|-------------|
| 11 | Sending love poems to you |
| 10 | dancing in the streets |
| 9 | high on life |
| 8 | delirious |
| 7 | satisfied |
| 6 | content |
| 5 | calm |
| 4 | disappointed |
| 3 | irritated |
| 2 | angry |
| 1 | furious |
| 0 | murderous |

### Fan Season Expectations (0-7 Scale)
| Value | Description |
|-------|-------------|
| 7 | We are so much better than this division! |
| 6 | We have to win this season |
| 5 | Aim for the title! |
| 4 | We belong in the top4 |
| 3 | A mid table finish is nice |
| 2 | We will have to fight to stay up |
| 1 | Every day in this division is a bonus |
| 0 | We are not worthy of this division |

## Key Implementation Notes

### Fan Mood Dynamics
- **Real-time Updates**: Fan mood changes based on match results and performance
- **Match Availability**: FanMood unavailable during active matches
- **Historical Tracking**: FanMoodAfterMatch provides post-game sentiment analysis

### Match Context Analysis
```python
# Fan expectation vs outcome analysis
def analyze_fan_reaction(match_data):
    expectation = match_data['FanMatchExpectation']
    mood_after = match_data['FanMoodAfterMatch']

    # Determine if result exceeded, met, or failed expectations
    if expectation >= 6 and mood_after >= 8:
        return "expectations_exceeded"
    elif expectation <= 3 and mood_after >= 6:
        return "surprising_success"
    elif expectation >= 6 and mood_after <= 4:
        return "disappointing_result"
    else:
        return "expectations_met"
```

### Attendance and Engagement Correlation
- **SoldSeats** - Actual attendance figures for revenue analysis
- **Weather** - Environmental factors affecting attendance
- **Member Growth Tracking** - Monitor fanclub size changes over time

## Strategic Usage Guidelines

### Fan Engagement Features
1. **Mood Tracking Dashboard** - Visualize fan sentiment trends over season
2. **Expectation Management** - Compare pre-match expectations with post-match mood
3. **Attendance Analysis** - Correlate fan mood with ticket sales performance

### Team Management Integration
- **Performance Pressure Indicator** - High expectations create pressure for results
- **Community Building Tools** - Leverage fanclub data for supporter engagement
- **Season Planning** - Understand supporter patience based on division expectations

### Feature Integration Opportunities
- **Match Preview Enhancement** - Show fan expectations alongside tactical analysis
- **Season Progress Tracking** - Monitor if team performance aligns with fan expectations
- **Social Media Integration** - Use mood data to inform community communications

## Data Caching Strategy
- **Frequency**: Updates after each match completion and weekly for baseline metrics
- **Storage**: Cache historical mood trends for sentiment analysis
- **Performance**: Lightweight data suitable for frequent dashboard updates

## OAuth & Access Control

### Authentication Requirements
- **OAuth Scope**: Team management access required for fanclub data
- **Team Ownership**: Can only access fanclub data for managed teams
- **Privacy**: Fanclub information is team-specific and not publicly accessible

### Error Handling
- **Invalid Team ID**: Returns error if teamId not managed by user
- **Match In Progress**: FanMood field unavailable during active matches
- **No Fanclub Data**: Some teams may have limited supporter information

## Related Endpoints
- **Economy** (`file=economy`) - SupportersPopularity and attendance revenue correlation
- **Team Details** (`file=teamdetails`) - Team performance metrics affecting fan mood
- **Matches** (`file=matches`) - Detailed match results for mood analysis context

---

*This fanclub endpoint enables comprehensive supporter engagement analysis and community management features for enhanced team-fan relationship building.*
