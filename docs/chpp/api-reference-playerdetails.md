# CHPP API Reference: Player Details

**Purpose**: Individual player analysis with comprehensive details, transfer market integration, and bid placement
**Endpoint**: `/chppxml.ashx?file=playerdetails`
**Authentication**: OAuth required (with "place_bid" scope for transfer actions)
**Rate Limiting**: Standard CHPP limits apply

## Overview

The Player Details endpoint provides comprehensive information for individual players, including detailed transfer market data and bid placement capabilities. This endpoint offers deeper analysis than the general Players endpoint, with enhanced transfer market integration and supporter-specific features.

## Request Parameters

### Required
- `file=playerdetails` - Specifies the player details endpoint
- `playerID` - Target player identifier (unsigned integer)

### Optional
- `version` - API version (latest recommended for full features)
- `actionType` - Operation mode:
  - `view` (default) - Retrieve detailed player information
  - `placeBid` - Place transfer market bid (requires special OAuth scope and additional parameters)
- `includeMatchInfo` - Include LastMatch performance data (default: false)

### Transfer Bid Parameters (actionType=placeBid)
- `teamId` - Bidding team identifier (required, must be managed by authenticated user)
- `bidAmount` - Bid amount in SEK (required for version 2.5+)
- `maxBidAmount` - Maximum autobid amount in SEK (optional)

## Response Structure

### Player Identity & Context
```xml
<HattrickData>
    <UserSupporterTier>platinum</UserSupporterTier>
    <Player>
        <PlayerID>283974499</PlayerID>
        <FirstName>John</FirstName>
        <NickName>Johnny</NickName>
        <LastName>Smith</LastName>
        <PlayerNumber>7</PlayerNumber>
        <PlayerCategoryID>2</PlayerCategoryID>
        <OwnerNotes>Star player potential - focus on PM training</OwnerNotes>
        <Age>23</Age>
        <AgeDays>45</AgeDays>
        <NextBirthDay>2026-03-15 12:00:00</NextBirthDay>
        <ArrivalDate>2024-07-15 12:00:00</ArrivalDate>
    </Player>
</HattrickData>
```

## Enhanced Player Information

### Personal Development
- **Age/AgeDays** - Precise age tracking for skill development optimization
- **NextBirthDay** - Skill development timing for training planning
- **ArrivalDate** - Team tenure and adaptation analysis
- **PlayerForm** - Current form level (1-8 scale)
- **PlayerCategoryID** - User-defined categorization (owner-only)
- **OwnerNotes** - Private management notes (owner-only)

### Player Status & Availability
```xml
<Cards>1</Cards>
<InjuryLevel>-1</InjuryLevel>
<PlayerForm>7</PlayerForm>
```

### Supporter Features
```xml
<Statement>Ready to give everything for the team!</Statement>
<PlayerLanguage>English</PlayerLanguage>
<PlayerLanguageID>2</PlayerLanguageID>
```

## Origin & Background Information

### Mother Club Details
```xml
<MotherClub>
    <TeamID>123456</TeamID>
    <TeamName>Youth Academy FC</TeamName>
</MotherClub>
<MotherClubBonus>true</MotherClubBonus>
```

### Geographic Origin
```xml
<NativeCountryID>1</NativeCountryID>
<NativeLeagueID>1</NativeLeagueID>
<NativeLeagueName>Sweden</NativeLeagueName>
```

### Current Team Context
```xml
<OwningTeam>
    <TeamID>789012</TeamID>
    <TeamName>Example FC</TeamName>
    <LeagueID>1</LeagueID>
</OwningTeam>
<Salary>15680</Salary>
<IsAbroad>false</IsAbroad>
```

## Complete Skills Profile

### All Eight Skills
```xml
<PlayerSkills>
    <StaminaSkill>8</StaminaSkill>
    <KeeperSkill>1</KeeperSkill>
    <PlaymakerSkill>7</PlaymakerSkill>
    <ScorerSkill>9</ScorerSkill>
    <PassingSkill>6</PassingSkill>
    <WingerSkill>4</WingerSkill>
    <DefenderSkill>5</DefenderSkill>
    <SetPiecesSkill>3</SetPiecesSkill>
</PlayerSkills>
```

### Special Attributes
- **Experience/Loyalty/Leadership** - Character and team dynamics
- **Agreeability/Aggressiveness/Honesty** - Personality traits affecting behavior
- **Specialty** - Special abilities (Technical, Quick, Head, Unpredictable, etc.)
- **TSI** - Total Skill Index for market valuation

## Transfer Market Integration

### Transfer Listing Details
```xml
<TransferListed>true</TransferListed>
<TransferDetails>
    <AskingPrice>2500000</AskingPrice>
    <Deadline>2026-02-10 14:30:00</Deadline>
    <HighestBid>2200000</HighestBid>
    <MaxBid>2300000</MaxBid>
    <BidderTeam>
        <TeamID>456789</TeamID>
        <TeamName>Rival FC</TeamName>
    </BidderTeam>
</TransferDetails>
```

### Transfer Market Features
- **AskingPrice** - Seller's initial price target
- **Deadline** - Transfer deadline (may be in past for recently completed transfers)
- **HighestBid** - Current highest bid amount
- **MaxBid** - User's autobid limit (if applicable)
- **BidderTeam** - Information about highest bidding team

## Performance Statistics & Career Data

### Career Statistics
```xml
<CareerGoals>87</CareerGoals>
<CareerHattricks>4</CareerHattricks>
<CareerAssists>34</CareerAssists>
<MatchesCurrentTeam>156</MatchesCurrentTeam>
<GoalsCurrentTeam>45</GoalsCurrentTeam>
<AssistsCurrentTeam>18</AssistsCurrentTeam>
```

### Current Season Performance
```xml
<LeagueGoals>12</LeagueGoals>
<CupGoals Available="true">3</CupGoals>
<FriendliesGoals>2</FriendliesGoals>
```

### National Team Career
```xml
<NationalTeamID>5047</NationalTeamID>
<NationalTeamName>Sweden</NationalTeamName>
<Caps>12</Caps>
<CapsU20>8</CapsU20>
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

### Complete Player Analysis
```python
def comprehensive_player_analysis(player_data):
    """Generate complete player profile for strategic decision-making"""
    analysis = {
        'identity': {
            'name': f"{player_data['FirstName']} {player_data['LastName']}",
            'nickname': player_data.get('NickName'),
            'age_profile': calculate_age_profile(player_data['Age'], player_data['AgeDays']),
            'origin': {
                'mother_club': player_data.get('MotherClub', {}).get('TeamName'),
                'native_league': player_data['NativeLeagueName'],
                'mother_club_bonus': player_data['MotherClubBonus']
            }
        },
        'skills': extract_skill_profile(player_data['PlayerSkills']),
        'performance': {
            'current_season': {
                'league_goals': player_data['LeagueGoals'],
                'cup_goals': player_data.get('CupGoals'),
                'assists': player_data['AssistsCurrentTeam']
            },
            'career_totals': {
                'goals': player_data['CareerGoals'],
                'assists': player_data['CareerAssists'],
                'hattricks': player_data['CareerHattricks']
            }
        },
        'market_status': analyze_transfer_status(player_data),
        'availability': {
            'injury_status': interpret_injury_level(player_data['InjuryLevel']),
            'suspension_status': interpret_cards(player_data['Cards']),
            'form_level': player_data['PlayerForm']
        }
    }

    return analysis
```

### Transfer Market Analysis
```python
def analyze_transfer_opportunity(player_data):
    """Evaluate transfer market opportunity and bidding strategy"""
    if not player_data.get('TransferListed'):
        return {'status': 'not_available'}

    transfer_details = player_data['TransferDetails']

    analysis = {
        'market_position': {
            'asking_price': transfer_details['AskingPrice'],
            'current_bid': transfer_details['HighestBid'],
            'competition_level': assess_bidding_competition(transfer_details),
            'time_remaining': calculate_time_to_deadline(transfer_details['Deadline'])
        },
        'value_assessment': {
            'estimated_value': calculate_market_value(player_data),
            'price_vs_value': compare_price_to_value(transfer_details, player_data),
            'bidding_recommendation': suggest_bid_strategy(transfer_details, player_data)
        },
        'strategic_fit': {
            'team_need_match': assess_team_fit(player_data),
            'development_potential': calculate_development_upside(player_data),
            'roi_projection': project_return_on_investment(player_data)
        }
    }

    return analysis
```

## Feature Integration Guidelines

### Transfer Bid Display (FEAT-025)
- **Current Bid Monitoring** - Real-time highest bid tracking
- **Competitive Intelligence** - Bidding team information and competition analysis
- **Deadline Management** - Transfer deadline tracking and urgency indicators
- **Bid Strategy Tools** - Optimal bidding recommendations based on market analysis

### Player Comparison Tool (FEAT-010)
- **Enhanced Comparison Data** - Comprehensive skill profiles and career statistics
- **Transfer Market Context** - Include market value and transfer status in comparisons
- **Performance Analytics** - Career trajectory and current form analysis
- **Origin Analysis** - Mother club bonus and geographic context comparison

### Individual Player Analysis
- **Development Planning** - Age-based skill development optimization
- **Position Suitability** - Comprehensive skill analysis for tactical planning
- **Market Value Tracking** - TSI and skill-based valuation monitoring

## OAuth & Transfer Market Security

### Authentication Requirements
- **Basic Access**: View player details for any player
- **Enhanced Data**: Supporter features require appropriate tier
- **Transfer Actions**: "place_bid" scope required for bid placement

### Bid Placement Security
- **Team Ownership Validation** - Can only bid with managed teams
- **Financial Verification** - Bid amount validation against team finances
- **Rate Limiting** - Prevents bid manipulation and spam

### Error Handling
- **Invalid Player ID** - Returns error for non-existent players
- **Transfer Restrictions** - Validates bid eligibility and market access
- **Match In Progress** - Some statistics unavailable during active matches

## Related Endpoints
- **Players** (`file=players`) - Team roster overview and basic player lists
- **Current Bids** (`file=currentbids`) - Transfer market activity monitoring
- **Transfers Player** (`file=transfersplayer`) - Transfer market search and discovery

---

*This detailed player endpoint enables sophisticated individual player analysis, transfer market intelligence, and comprehensive player evaluation for strategic team management decisions.*
