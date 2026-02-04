# Training API Reference

## Overview
The Training API allows you to retrieve and manage training information for teams, including current training settings, trainer details, and team formation experience.

## Input Parameters

**Required:**
- `file = training`

**Optional:**
- `version` - API version (optional)
- `actionType` - Indicates what type of action the page should perform
  - `view` (default) - Training information for the logged-in user's team
  - `stats` - Shows distribution among training types for all leagues or specific league (Requires Hattrick Supporter)
  - `setTraining` - Set training settings for the logged-in user's team (Requires "set_training" scope)

**Action-Specific Parameters:**

**For actionType=stats:**
- `leagueID` - unsigned Integer (Default: Your leagueID)
  - What LeagueID to retrieve statistics for (empty for global stats in version 1.7 or above)

**For actionType=view:**
- `teamId` - unsigned Integer (Default: Your primary club senior teamId)
  - Team id to view training information for. Must refer to a senior team managed by requesting user

**For actionType=setTraining:**
- `teamId` - unsigned Integer (REQUIRED, no default)
  - Team id to set training for. Must refer to a senior team managed by requesting user
- `trainingType` - trainingType
  - Type of training to be set for the specified team
- `trainingLevel` - unsigned Integer
  - Training level to be set for the specified team (0-100)
- `trainingLevelStamina` - unsigned Integer
  - Stamina level to be set for the specified team (5-100)

## Output Structure

The API returns training data in the following XML structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <UserSupporterTier>supporterTier</UserSupporterTier>
  <!-- Indicates which Supporter package the fetching user has, or empty if not a Supporter -->

  <Team>
    <TeamID>unsigned Integer</TeamID>
    <!-- The globally unique TeamID -->

    <TeamName>String</TeamName>
    <!-- The name of the team -->

    <TrainingLevel>unsigned Integer</TrainingLevel>
    <!-- The current training level for the team in percent -->

    <NewTrainingLevel Available='Boolean'>unsigned Integer</NewTrainingLevel>
    <!-- The goal training level for the team in percent -->

    <TrainingType>trainingType</TrainingType>
    <!-- Integer defining the type of training -->

    <StaminaTrainingPart>unsigned Integer</StaminaTrainingPart>
    <!-- The current part of training level, in percent, used on stamina training -->

    <LastTrainingTrainingType>trainingType</LastTrainingTrainingType>
    <!-- The training type that took place last training -->

    <LastTrainingTrainingLevel>unsigned Integer</LastTrainingTrainingLevel>
    <!-- The training intensity that was used the last training -->

    <LastTrainingStaminaTrainingPart>unsigned Integer</LastTrainingStaminaTrainingPart>
    <!-- The stamina share that was used the last training -->

    <Trainer>
      <TrainerID>unsigned Integer</TrainerID>
      <!-- The globally unique PlayerID for the trainer -->

      <TrainerName>String</TrainerName>
      <!-- The name of the trainer -->

      <ArrivalDate>DateTime</ArrivalDate>
      <!-- The date the trainer became trainer of the team -->
    </Trainer>

    <SpecialTraining>
      <Player>
        <PlayerID>unsigned Integer</PlayerID>
        <!-- The globally unique PlayerID for the player with special training instructions -->

        <SpecialTrainingTypeID>unsigned Integer</SpecialTrainingTypeID>
        <!-- The type of special training is always 1 = Stamina -->
      </Player>
    </SpecialTraining>

    <Morale Available='Boolean'>TeamSpiritID</Morale>
    <!-- The morale/team spirit of the team -->

    <SelfConfidence Available='Boolean'>SelfConfidenceID</SelfConfidence>
    <!-- The self confidence of the team -->

    <!-- Formation Experience -->
    <Experience442>SkillLevel</Experience442>
    <!-- The team's experience of playing 4-4-2 -->

    <Experience433>SkillLevel</Experience433>
    <!-- The team's experience of playing 4-3-3 -->

    <Experience451>SkillLevel</Experience451>
    <!-- The team's experience of playing 4-5-1 -->

    <Experience352>SkillLevel</Experience352>
    <!-- The team's experience of playing 3-5-2 -->

    <Experience532>SkillLevel</Experience532>
    <!-- The team's experience of playing 5-3-2 -->

    <Experience343>SkillLevel</Experience343>
    <!-- The team's experience of playing 3-4-3 -->

    <Experience541>SkillLevel</Experience541>
    <!-- The team's experience of playing 5-4-1 -->

    <Experience523>SkillLevel</Experience523>
    <!-- The team's experience of playing 5-2-3 -->

    <Experience550>SkillLevel</Experience550>
    <!-- The team's experience of playing 5-5-0 -->

    <Experience253>SkillLevel</Experience253>
    <!-- The team's experience of playing 2-5-3 -->
  </Team>
</HattrickData>
```

## Data Types

- **trainingType**: Integer defining the type of training
- **supporterTier**: Supporter package level indicator
- **TeamSpiritID**: Team morale/spirit level identifier
- **SelfConfidenceID**: Team self confidence level identifier
- **SkillLevel**: Formation experience skill level
- **DateTime**: Standard datetime format

## Notes

- `stats` action requires Hattrick Supporter account
- `setTraining` action requires "set_training" scope in OAuth
- TeamId is required (no default) for `setTraining` action
- Training levels range from 0-100%, stamina training levels from 5-100%
- Special training is currently only available for Stamina (SpecialTrainingTypeID = 1)
- Formation experience is tracked for 10 different tactical formations
- Morale and SelfConfidence fields have "Available" attribute indicating data availability