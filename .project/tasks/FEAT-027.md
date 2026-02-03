# FEAT-027: Hattrick Language Localization

**GitHub Issue**: [#13](https://github.com/kvarak/htstatus/issues/13) - "Translate to the language in hattrick"
**Dependencies**: UI framework (completed), user preferences system (FEAT-017) | **Strategic Value**: International user accessibility, authentic Hattrick experience

## Problem Statement

Currently, HattrickPlanner is only available in English, while Hattrick itself supports multiple languages including Swedish, German, Spanish, French, and others. Users who play Hattrick in their native language experience a disconnect when using HattrickPlanner in English.

The original request from kvarak (June 2020) suggested translating the application to match the user's Hattrick language setting, creating a more seamless and authentic experience for international Hattrick managers.

## Implementation

**Phase 1: Internationalization Infrastructure**
- Set up Flask-Babel for i18n/l10n support
- Create translation message extraction workflow
- Implement language detection from user's Hattrick profile
- Add language preference storage to user models

**Phase 2: Core Translation Support**
- Extract all user-facing strings into translation templates
- Create translation files for primary Hattrick languages (Swedish, German, Spanish)
- Implement dynamic language switching
- Add language preference to user settings

**Phase 3: Hattrick-Specific Terminology**
- Align football/soccer terminology with Hattrick's language versions
- Translate skill names, position names, and game concepts consistently
- Use official Hattrick translations where available
- Create glossary for Hattrick-specific terms

**Phase 4: Advanced Localization**
- Format numbers, dates, and currency according to locale
- Support for right-to-left languages (future consideration)
- Implement fallback to English for missing translations
- Add translation contribution workflow for community

## Acceptance Criteria

- [ ] Application detects user's Hattrick language automatically
- [ ] UI elements display in user's preferred language
- [ ] Hattrick terminology matches official game translations
- [ ] Language switching works without page reload
- [ ] All user-facing text is translatable
- [ ] Numbers and dates formatted according to locale
- [ ] Graceful fallback to English for missing translations
- [ ] Translation files are maintainable and well-structured
- [ ] Core languages supported: English, Swedish, German
- [ ] Translation extraction workflow documented

**Technical Notes**:
- Consider using CHPP API to detect user's Hattrick language setting
- Prioritize Swedish translation first (original requester's language)
- Implement lazy loading for translation files to optimize performance
- Focus on hobby project simplicity - avoid over-engineering localization system
