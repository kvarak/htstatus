# Achievements API Reference

## Overview
The Achievements API lists the achievements of a specific user.

## Input Parameters

**Required:**
- `file = achievements`

**Optional:**
- `version` - API version (optional)
- `userID` - unsigned Integer (default: your own userID)
  - What user to show achievements for

## Output Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <MaxPoints>unsigned Integer</MaxPoints>
  <!-- The maximum number of points a user currently can achieve -->

  <AchievementList>
    <Achievement>
      <AchievementTypeID>unsigned Integer</AchievementTypeID>
      <!-- The AchievementTypeID. NOTE: there is no published list of available achievements -->

      <AchievementTitle>String</AchievementTitle>
      <!-- The title for the achievement -->

      <AchievementText>String</AchievementText>
      <!-- The text describing the achievement -->

      <CategoryID>AchievementCategoryID</CategoryID>
      <!-- The category (integer) the achievement belongs to -->

      <EventDate>DateTime</EventDate>
      <!-- The date when the achievement was awarded -->

      <Points>unsigned Integer</Points>
      <!-- Points awarded for the achievement -->

      <Multilevel>Boolean</Multilevel>
      <!-- True if the AchievementTypeID has multiple levels -->

      <Rank>unsigned Integer</Rank>
      <!-- The user's current rank in this achievement, 1 = best rank possible -->

      <NumberOfEvents>unsigned Integer</NumberOfEvents>
      <!-- Global number of users that have been awarded this achievement -->
    </Achievement>
  </AchievementList>
</HattrickData>
```

## Notes
- Not used by HattrickPlanner yet.
