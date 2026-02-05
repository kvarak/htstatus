# Avatars API Reference

## Overview
The Avatars API allows you to retrieve avatar/player image information for all players of a user's team, including current players and Hall of Fame players.

## Input Parameters

**Required:**
- `file = avatars`

**Optional:**
- `version` - API version (optional)
- `actionType` - Indicates what type of action the page should perform
  - `players` (default) - View the avatars of players for the team of the currently logged in user
  - `hof` - View the avatars of Hall of Fame players for the team of the currently logged in user
- `teamId` - unsigned Integer (Default: Your senior teamId)
  - What team/user to show the avatars for. Defaults to logged in teamId

## Output Structure

The API returns avatar data in the following XML structure:

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <Team>
    <TeamId>unsigned Integer</TeamId>
    <!-- The globally unique TeamID -->

    <Players>
      <Player>
        <PlayerID>unsigned Integer</PlayerID>
        <!-- The globally unique PlayerID -->

        <Avatar>
          <BackgroundImage>URI</BackgroundImage>
          <!-- The URL to the card background-image. This will show a silhouette for non-supporter teams -->

          <Layer x='unsigned Integer' y='unsigned Integer'>
            <Image>URI</Image>
            <!-- The URL to the bodypart item -->
          </Layer>
        </Avatar>
      </Player>
    </Players>
  </Team>
</HattrickData>
```

## Data Types

- **URI**: URL to image resource
- **Layer**: Positioned image layer with x,y coordinates
- **PlayerID**: Globally unique player identifier
- **TeamId**: Globally unique team identifier

## Notes

- BackgroundImage shows silhouette for non-supporter teams
- Multiple Layer elements can exist for different bodypart items
- Each Layer has x,y positioning coordinates for proper avatar composition
- Hall of Fame players accessible via `actionType=hof`
- Default action shows current team players
