# Club API Reference

## Overview
The Club API provides information about team specialists (staff) and youth squad details for a senior team.

## Input Parameters

**Required:**
- `file = club`

**Optional:**
- `version` - API version (optional)
- `teamId` - unsigned Integer (Default: Your primary club senior teamId)
  - Team id to get data for. Must refer to a senior team managed by requesting user

## Output Structure

The API returns club information in the following XML structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Team>
    <TeamID>unsigned Integer</TeamID>
    <!-- The globally unique TeamID -->

    <TeamName>String</TeamName>
    <!-- The name of the team -->

    <Staff>
      <AssistantTrainerLevels>unsigned Integer</AssistantTrainerLevels>
      <!-- The level of the Assistant Trainers -->

      <FinancialDirectorLevels>unsigned Integer</FinancialDirectorLevels>
      <!-- The level of the Financial Director -->

      <FormCoachLevels>unsigned Integer</FormCoachLevels>
      <!-- The level of the Form Coach -->

      <MedicLevels>unsigned Integer</MedicLevels>
      <!-- The level of the Medic -->

      <SpokespersonLevels>unsigned Integer</SpokespersonLevels>
      <!-- The level of the Spokesperson -->

      <SportPsychologistLevels>unsigned Integer</SportPsychologistLevels>
      <!-- The level of the Sport Psychologist -->

      <TacticalAssistantLevels>unsigned Integer</TacticalAssistantLevels>
      <!-- The level of the Tactical Assistant -->
    </Staff>

    <YouthSquad>
      <Investment>Money</Investment>
      <!-- The weekly youth squad investment -->

      <HasPromoted>Boolean</HasPromoted>
      <!-- Boolean value indicating if the team has promoted a youth player this week -->

      <YouthLevel>unsigned Integer</YouthLevel>
      <!-- The current level of the youth squad -->
    </YouthSquad>
  </Team>
</HattrickData>
```

## Staff Specialists

### Available Staff Types
- **Assistant Trainers**: Support training activities and player development
- **Financial Director**: Manages club finances and economic efficiency
- **Form Coach**: Helps maintain and improve player form
- **Medic**: Reduces injury risk and recovery time
- **Spokesperson**: Manages fan relations and public image
- **Sport Psychologist**: Improves player mental attributes and team spirit
- **Tactical Assistant**: Provides tactical insights and match preparation support

### Staff Levels
- Staff levels typically range from 0 (none hired) to 10+ (maximum level)
- Higher levels provide greater benefits but cost more in weekly salary
- Each specialist type has specific benefits for team performance

## Youth Squad Information

### Investment
- **Type**: Money (weekly amount)
- **Purpose**: Determines youth player quality and development speed
- **Range**: Varies by league and team financial capability
- **Impact**: Higher investment leads to better youth prospects

### Promotion Status
- **HasPromoted**: Boolean indicating if a youth player was promoted this week
- **Timing**: Updates weekly during youth promotion phase
- **Limitation**: Teams can only promote one youth player per week

### Youth Level
- **Range**: Typically 1-10+ levels
- **Function**: Determines overall youth academy quality and capacity
- **Development**: Can be improved through sustained investment
- **Benefits**: Higher levels produce better youth players more frequently

## Data Types

- **unsigned Integer**: Positive integer values for levels and identifiers
- **String**: Text data for team name
- **Money**: Monetary amount for weekly youth investment
- **Boolean**: True/false value for promotion status

## Usage Notes

### Access Control
- Must be authenticated as team manager
- Can only access data for teams you manage
- Defaults to primary senior team if no teamId specified

### Update Frequency
- Staff levels change only when hiring/firing specialists
- Youth investment can be changed weekly
- HasPromoted updates weekly during promotion cycles
- YouthLevel changes gradually based on investment and time

### Strategic Implications
- Staff specialists provide various team benefits
- Youth squad investment is key to long-term player development
- Balancing staff costs vs. benefits is crucial for team economics
- Youth academy development requires sustained investment commitment

## Related APIs
- **Team Details**: Provides broader team information context
- **Training**: Shows how staff affects training effectiveness
- **Players**: Youth players appear in player listings after promotion

## Notes

- Staff levels directly impact team performance in various areas
- Youth squad data is essential for long-term team planning
- Investment amounts vary significantly between different leagues
- HasPromoted status resets weekly during youth promotion cycles
- Higher staff levels require increased weekly salary commitments
- Youth level progression is gradual and requires consistent investment
- Some staff benefits are visible immediately, others accumulate over time