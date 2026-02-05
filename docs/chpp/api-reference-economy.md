# CHPP API Reference: Economy

**Purpose**: Team financial management and budget planning with comprehensive income/expense tracking
**Endpoint**: `/chppxml.ashx?file=economy`
**Authentication**: OAuth required
**Rate Limiting**: Standard CHPP limits apply

## Overview

The Economy endpoint provides comprehensive financial data for Hattrick teams, including current budget projections, historical performance, and popularity metrics. Essential for financial planning and team sustainability analysis.

## Request Parameters

### Required
- `file=economy` - Specifies the economy data endpoint

### Optional
- `version` - API version (latest recommended)
- `teamId` - Target team ID (unsigned integer)
  - **Default**: Your primary club senior team ID
  - **Restriction**: Must refer to a senior team managed by requesting user
  - **Security**: Cannot access other users' financial data

## Response Structure

### Team Financial Overview
```xml
<Team>
    <TeamID>12345</TeamID>
    <TeamName>Example FC</TeamName>
    <Cash>2500000</Cash>
    <ExpectedCash>2750000</ExpectedCash>
</Team>
```

### Popularity Metrics
- **SponsorsPopularity** - Sponsor relationship strength (affects sponsor income)
- **SupportersPopularity** - Fan satisfaction level (affects attendance)
- **FanClubSize** - Core supporter base size

### Current Week Budget Projections

#### Income Sources
- **IncomeSpectators** - Gate receipts from match attendance
- **IncomeSponsors** - Base sponsor contract payments
- **IncomeSponsorBonuses** - Performance-based sponsor rewards
- **IncomeFinancial** - Interest and investment returns
- **IncomeSoldPlayers** - Transfer market sales revenue
- **IncomeSoldPlayersCommission** - Commission from developed player sales
- **IncomeSum** - Total projected weekly income

#### Expense Categories
- **CostsArena** - Stadium maintenance and operations
- **CostsPlayer** - Player salaries and bonuses
- **CostsFinancial** - Interest payments and fees
- **CostsBoughtPlayers** - Transfer market purchases
- **CostsArenaBuilding** - Stadium expansion costs
- **CostsStaff** - Coaching and support staff wages
- **CostsYouth** - Youth academy investment
- **CostsSum** - Total projected weekly expenses

#### Financial Summary
- **ExpectedWeeksTotal** - Net budget result (Income - Costs)

### Historical Comparison (Last Week)
Complete mirror of current week data with `Last` prefix:
- `LastIncomeSpectators`, `LastIncomeSponsors`, etc.
- `LastCostsArena`, `LastCostsPlayer`, etc.
- `LastWeeksTotal` - Previous week's actual financial result

## Key Implementation Notes

### Financial Data Accuracy
- **Budget vs Actual**: Current week shows projections, last week shows actual results
- **Timing**: Data updates after weekly economic processing
- **Currency**: All monetary values in Hattrick currency units

### Team Management Integration
```python
# Financial health assessment
def assess_financial_status(economy_data):
    cash = economy_data['Cash']
    expected_result = economy_data['ExpectedWeeksTotal']

    # Calculate weeks of sustainability
    if expected_result < 0:
        weeks_sustainable = cash / abs(expected_result)
        return {'status': 'declining', 'weeks': weeks_sustainable}
    else:
        return {'status': 'growing', 'weekly_profit': expected_result}
```

### Budget Planning Features
- **Cash Flow Analysis**: Compare current vs historical performance
- **Trend Detection**: Multi-week financial trajectory
- **Alert System**: Warn when cash/expenses approach critical levels

## Strategic Usage Guidelines

### Financial Planning Tools
1. **Budget Forecasting** - Project future financial position based on trends
2. **Investment Planning** - Determine affordable player purchases or stadium upgrades
3. **Performance Tracking** - Monitor sponsor/supporter satisfaction trends

### Feature Integration Opportunities
- **Training Cost Calculator** - Factor staff costs into training planning
- **Transfer Budget Advisor** - Recommend safe spending limits based on cash flow
- **Arena Investment ROI** - Calculate attendance income vs expansion costs

### Data Caching Strategy
- **Frequency**: Weekly updates align with Hattrick economic cycle
- **Storage**: Cache full economy data for trend analysis
- **Performance**: Essential data for multiple features (transfer planning, team overview)

## OAuth & Access Control

### Authentication Requirements
- **OAuth Scope**: Full team management access required
- **Team Ownership**: Can only access teams managed by authenticated user
- **Security**: Financial data is highly sensitive, implement appropriate access logging

### Error Handling
- **Invalid Team ID**: Returns error if teamId not managed by user
- **No Economic Rights**: Some team types may have limited economic data access

## Related Endpoints
- **Team Details** (`file=teamdetails`) - Basic team information and performance metrics
- **Club** (`file=club`) - Staff costs and youth academy investment details
- **Current Bids** (`file=currentbids`) - Transfer market financial commitments

---

*This comprehensive financial endpoint supports robust team management features with both current planning and historical analysis capabilities.*
