# Translations API Reference

## Overview
The Translations API provides localized text for various game denominations and terms. This endpoint should be cached rather than fetched frequently - recommended to update weekly or monthly rather than per user session.

## Input Parameters

**Required:**
- `file = translations`
- `languageId` - unsigned Integer
  - The id of the language to get the translations for

**Optional:**
- `version` - API version (optional)

## Output Structure

The API returns translation data in the following XML structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Language Id='unsigned Integer'>String</Language>
  <!-- The language sent in -->

  <Texts>
    <SkillNames>
      <Skill Type='String'>String</Skill>
      <!-- The name of the skill -->
    </SkillNames>

    <SkillLevels>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the skill -->
    </SkillLevels>

    <SkillSubLevels>
      <SubLevel Value='Float'>String</SubLevel>
      <!-- The sub-level of the skill -->
    </SkillSubLevels>

    <PlayerSpecialties>
      <Item Value='unsigned Integer'>String</Item>
      <!-- The player specialty -->
    </PlayerSpecialties>

    <PlayerAgreeability>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the player agreeability -->
    </PlayerAgreeability>

    <PlayerAgressiveness>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the player aggressiveness -->
    </PlayerAgressiveness>

    <PlayerHonesty>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the player honesty -->
    </PlayerHonesty>

    <TacticTypes>
      <Item Value='unsigned Integer'>String</Item>
      <!-- The tactic type -->
    </TacticTypes>

    <MatchPositions>
      <Item Value='unsigned Integer'>String</Item>
      <!-- The match position -->
    </MatchPositions>

    <RatingSectors>
      <Item Value='unsigned Integer'>String</Item>
      <!-- The rating sector -->
    </RatingSectors>

    <TeamAttitude>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the team attitude -->
    </TeamAttitude>

    <TeamSpirit>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the team spirit -->
    </TeamSpirit>

    <Confidence>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the confidence -->
    </Confidence>

    <TrainingTypes>
      <Item Value='unsigned Integer'>String</Item>
      <!-- The training type -->
    </TrainingTypes>

    <Sponsors>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the sponsors -->
    </Sponsors>

    <FanMood>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the fan mood -->
    </FanMood>

    <FanMatchExpectations>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the fan match expectation -->
    </FanMatchExpectations>

    <FanSeasonExpectations>
      <Level Value='unsigned Integer'>String</Level>
      <!-- The level of the fan season expectation -->
    </FanSeasonExpectations>

    <LeagueNames>
      <League>
        <LeagueId>unsigned Integer</LeagueId>
        <!-- The globally unique LeagueID -->

        <LocalLeagueName>String</LocalLeagueName>
        <!-- The name of the league in the league's local language -->

        <LanguageLeagueName>String</LanguageLeagueName>
        <!-- The name of the league in the chosen language -->
      </League>
    </LeagueNames>
  </Texts>
</HattrickData>
```

## Translation Categories

### Player Attributes
- **SkillNames**: Core player skills (keeping, defending, playmaking, winger, passing, scoring, set pieces)
- **SkillLevels**: Skill level descriptions (disastrous, wretched, poor, weak, inadequate, passable, solid, excellent, formidable, outstanding, brilliant, magnificent, world class, supernatural, titanic, extra-terrestrial, mythical, magical, utopian, divine)
- **SkillSubLevels**: Skill sub-level refinements (very low, low, high, very high)
- **PlayerSpecialties**: Special abilities (technical, quick, powerful, unpredictable, head specialist, regainer)
- **PlayerAgreeability**: Personality trait levels
- **PlayerAgressiveness**: Personality trait levels
- **PlayerHonesty**: Personality trait levels

### Tactical Elements
- **TacticTypes**: Match tactics (normal, pressing, counter-attacks, attack in the middle, attack on wings, play creatively, long shots)
- **MatchPositions**: Field positions (goalkeeper, right back, central defender, left back, right wingback, etc.)
- **RatingSectors**: Team rating areas (right defense, central defense, left defense, midfield, right attack, central attack, left attack)

### Team Management
- **TeamAttitude**: Team attitude levels (play it cool, normal, match of the season)
- **TeamSpirit**: Team spirit levels (wretched, poor, decent, good, excellent)
- **Confidence**: Self-confidence levels (non-existent, disastrous, poor, weak, decent, strong, wonderful, slightly exaggerated, exaggerated, completely exaggerated, divine)
- **TrainingTypes**: Training focus areas (goalkeeping, defending, playmaking, winger, passing, scoring, set pieces, stamina)

### Club Management
- **Sponsors**: Sponsorship levels and descriptions
- **FanMood**: Fan satisfaction levels (furious, disappointed, calm, content, delighted, dancing in the streets)
- **FanMatchExpectations**: Fan expectations for individual matches
- **FanSeasonExpectations**: Fan expectations for the season

### Geographic Data
- **LeagueNames**: League names in both local and requested languages

## Data Types

- **String**: Localized text in the requested language
- **unsigned Integer**: Numeric identifiers and values
- **Float**: Decimal values for skill sub-levels

## Usage Guidelines

### Caching Strategy
- **Update Frequency**: Weekly or monthly, NOT per user session
- **Storage**: Cache all translations locally in application database
- **Performance**: Reduces API calls and improves response times

### Implementation Notes
- Use languageId to match user's Hattrick language preference
- Store translations in normalized database tables with language keys
- Consider fallback to default language if requested language unavailable
- Update translations when new skills or game elements are added

## Common Language IDs

- English: 1
- Swedish: 4
- German: 3
- Spanish: 5
- French: 6
- Italian: 7
- Portuguese: 9
- Dutch: 10

*(Check current CHPP documentation for complete language ID list)*

## Notes

- NOT intended for per-session fetching - implement proper caching
- Translations change infrequently, weekly/monthly updates sufficient
- Essential for proper localization of player skills, tactics, and game elements
- League names provided in both local and requested languages for international context
- Skill sub-levels use float values for precise skill descriptions
- Player personality traits include agreeability, aggressiveness, and honesty
- Fan expectations separate match-level and season-level anticipations