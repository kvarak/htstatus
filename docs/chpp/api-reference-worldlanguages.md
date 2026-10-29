# World Languages API Reference

## Overview
The World Languages API lists the languages available in Hattrick. Use the `LanguageID` values with the [translations](api-reference-translations.md) endpoint. The list rarely changes, so cache it.

## Input Parameters

**Required:**
- `file = worldlanguages`

**Optional:**
- `version` - API version (optional)

## Output Structure

```xml
<?xml version="1.0" encoding="utf-8"?>
<HattrickData>
  <LanguageList>
    <Language>
      <LanguageID>unsigned Integer</LanguageID>
      <!-- The globally unique LanguageID -->

      <LanguageName>String</LanguageName>
      <!-- The Language name -->
    </Language>
  </LanguageList>
</HattrickData>
```

## Notes
- Example IDs (version 1.2): Svenska = 1, English (UK) = 2, Italiano = 4, Français = 5.
- The user's own language is in managercompendium `Manager/Language/LanguageId`.
