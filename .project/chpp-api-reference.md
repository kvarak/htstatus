# CHPP API Reference

> **Purpose**: Essential field mappings and XML structures for Hattrick CHPP API integration
> **Source**: Real Hattrick API documentation analysis (Jan 2026)

## Key Field Name Corrections

### Manager/User Data (managercompendium)
- `UserId` (not ManagerId)
- `Loginname` (not LoginName)
- `YouthTeamId` nested under `<YouthTeam>` (optional field)
- Team IDs under `<Teams><Team><TeamId>` structure

### Team Data (teamdetails)
- `TeamID` (not TeamId)
- `TeamName`, `ShortTeamName` (consistent)
- `PlayerID` for player references (not PlayerId)

### Player Data (players)
- `PlayerID` (not PlayerId)
- Skills without "Skill" suffix: `Keeper`, `Defender`, `Playmaker`, `Winger`, `Passing`, `Scorer`, `SetPieces`
- `PlayerForm`, `Stamina` (not PlayerForm, StaminaSkill)
- Players nested under `<PlayerList><Player>` structure

## Critical XML Patterns

**Manager with optional YouthTeam:**
```xml
<Manager>
    <UserId>123456</UserId>
    <Loginname>testuser</Loginname>
    <Teams>
        <Team>
            <TeamId>456789</TeamId>
            <YouthTeam>
                <YouthTeamId>789012</YouthTeamId> <!-- Optional -->
            </YouthTeam>
        </Team>
    </Teams>
</Manager>
```

**Player List Structure:**
```xml
<Team>
    <TeamID>456789</TeamID>
    <PlayerList>
        <Player>
            <PlayerID>1001</PlayerID>
            <Keeper>5</Keeper>
            <!-- Other fields -->
        </Player>
    </PlayerList>
</Team>
```

## Implementation Notes

- **YouthTeamId Fix**: Handled as optional field (eliminates 27-line workaround)
- **Field Case Sensitivity**: XML field names follow Hattrick's exact casing
- **Parser Updates**: See `app/chpp/parsers.py` for correct XPath expressions
- **Test Coverage**: Parser tests validate real API structure compatibility