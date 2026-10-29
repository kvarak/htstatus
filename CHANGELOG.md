# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Levels as numbers or words** - choose in Settings whether skill and personality levels show as both Hattrick's word and the number (solid (7), the default), just numbers (7) or just words (solid); with one form, the other is shown on hover, the player table still sorts by number, and its headers are only rotated 90° in numbers mode
- **Hattrick terms in your language** (FEAT-027) - skill names, skill levels, specialties and personality traits now use the words Hattrick uses in the language you play in; pick another language in Settings
- **Dark mode** (UI-014) - 🌙/☀️ toggle in the navbar, same look and behaviour as the other kvarak projects: follows the system setting until you pick a mode, remembers the choice, no light flash on load; charts switch colours too
- **Debug Charts Date Range Selection** - Enhanced admin debugging with time-based filtering (FEAT-033)
  - Date range controls in debug page Chart Controls section with 6-month default
  - HTML5 date inputs with validation for start/end date relationships
  - Client-side filtering for immediate responsiveness with filtered datasets
  - Integration with existing AdminPreferences model for date range persistence
  - Compatible with existing admin user filter for combined filtering
  - Improved chart performance and focus on recent activity trends
- **Interactive Tutorial System** - Comprehensive user onboarding and feature discovery
  - Welcome tour for new users introducing key navigation and features
  - Context-aware feature tours for Players, Training, and Data Updates
  - Progressive disclosure: tours appear automatically based on page visits and user progress
  - Persistent progress tracking with localStorage and version-aware feature alerts
  - Floating help button for easy access to tutorials and help menu
  - Full accessibility support with keyboard navigation and screen reader compatibility
  - Built with Intro.js for professional guided tour experience
- **Default Player Groups for New Users** - Automatically create 7 sensible player groups when users first sign up
  - Groups: Goalkeepers, Defenders, Midfielders, Wingers, Forwards, Youth/Development, Veterans
  - Football-themed color scheme with proper spacing for user customization (order 10, 20, 30, etc.)
  - Integrated into both auth flow and player page fallback for comprehensive coverage
  - Comprehensive test coverage for group creation, existing user handling, and error scenarios
- Integration test resolution task (TEST-002) in project backlog

### Changed
- Enhanced navbar with tutorial target IDs for guided tours
- Player table includes tutorial integration with ID targeting
- App version meta tag added for tutorial feature detection
- Project documentation updated with completion status and metrics
- Backlog dependencies updated to reflect infrastructure readiness
- Feature ideas moved from `.project/backlog.md` to new `.project/features.md`; backlog now holds improvements, bug fixes, refactoring, tests and infra only
- Stats, formation, training, compare and player pages load the current roster with shared database-side queries (`app/roster.py`) instead of per-page history scans and per-player queries
- `make lint` uses ruff + black (flake8/isort were not installed); CI also runs file-format, CHPP-policy and the full test suite against PostgreSQL

- Page-visit tracking uses one `@track_activity` decorator; the logged-in user is loaded once per request (`get_current_user`) instead of up to four times
- Admin debug charts: date-range logic moved to `app/static/js/debug-date-filter.js` with Node unit tests; inline error messages instead of pop-up alerts
- Formation tester: players on the pitch show the same hover tooltip as the player list, and positions are coloured green/yellow/red by effectiveness
- Changelog page markup lives in `changes.html` (Jinja escaping) instead of HTML built in Python
- `/update` split into small helpers (team refresh, archive download, player record building, snapshot saving, match download); previous player records are loaded once per team instead of once per player
- Login and OAuth callback split into small helpers; team fetching (incl. the "no youth team" CHPP workaround) lives in one place, `fetch_user_teams`
- Skill-change timeline loads player history in a few queries instead of ~4 per player per week
- Model registry removed; models are imported directly
- Flask-Bootstrap removed (templates already used Bootstrap 4); `base.html` extends a small local `_skeleton.html`, and the error page now uses the normal app layout
- Debug charts share one `renderChart` helper instead of 18 copies of the create/destroy code
- Tooling trimmed for hobby scale: `make test-all` runs the gates (tests, file format, lint, template lint, bandit, CHPP policy) and prints a pass/fail summary; the quality-intelligence JSON reporting, coverage-report script and test-file-per-module gate are gone
- Docs trimmed: DEPLOYMENT.md describes the real Pi/systemd deployment; TECHNICAL.md debugging guide replaced by a short troubleshooting list; progress.md shows current status only
- Admin debug charts accessibility: labelled date range fieldset, screen-reader chart descriptions, labelled shrink/expand buttons, keyboard chart reordering (Arrow Up/Down) with announcements

### Removed
- Redis (never used by the app), the `configs/` docker-compose overrides (one `docker-compose.yml` remains, pgAdmin via `make pgadmin`), broken `services-staging` target
- Unused dev dependencies (safety, pre-commit, pytest-json-report) and one-off scripts (old user cleanup, historical match cleanup, unknown-country check, match data query)
- Unused code: `/api/players/filter`, admin `/debug/chpp_teams` and `/debug/chpp_raw` (violated CHPP policy), `logout.html`, unused helpers in `utils.py`, `auth_utils.py`, `error_handlers.py`, `chpp_utilities.py`, `hattrick_countries.py`, XML debug printing in the player parser
- One-off debugging scripts and committed match backup data files
- 21 permanently skipped, broken tests; TODO-only test stubs replaced with real tests

### Fixed
- Players sold some time ago remained listed in the team; the update now releases every departed player
- Changelog page escapes commit messages (they were rendered as raw HTML)
- Test isolation: tests no longer drop shared tables or leave the model registry mocked
- `User.is_admin()` ignored role-based admins (compared against lowercase "admin")
- Stats age-distribution charts used Chart.js v2 axis options (ignored by v4, console errors); the axis title and integer ticks now apply
- Debug chart date range end date is now inclusive (users active later on the end day were excluded)
- A failed team competition-data save no longer breaks the rest of the update (rollback); today's player snapshot is replaced in one commit
- Sessions pointing to a user that no longer exists are logged out instead of browsing with a missing user
- Error log: identical errors within an hour are stored once, rows older than 90 days are deleted, and logging works after a failed DB transaction
- Position contributions: tactical variants (e.g. IMD/IMO, WBO, WO, DF) used their own skill weights in name only and silently fell back to the base position; they now differ as intended. Formation tester side midfielders/forwards use the IMN/FW weights
- Formation tester: the overall rating counts empty positions as 0 (it averaged only the assigned players)
- OAuth callback: the fallback for users without a youth team crashed (it parsed an already-parsed XML element); login no longer logs the password length

## [2.0.0] - 2026-01-01

### Added
- **Professional Development Infrastructure** - Complete modernization of local development environment
  - UV dependency management with comprehensive error handling and cross-platform support
  - Enhanced Makefile with dependency checking and helpful installation guidance
  - Fallback support for systems without UV installed
- **Comprehensive Testing Infrastructure** - Professional-grade testing foundation
  - Modern SQLAlchemy fixtures compatible with current Flask-SQLAlchemy
  - pytest integration with coverage reporting and CI/CD support
  - 94% test success rate (32 of 34 tests passing)
  - Integration test identification and isolation
- **Code Quality Framework** - Enterprise-level quality assurance tools
  - ruff linting with automatic fixes (91 issues identified, 56 auto-fixed)
  - black code formatting integration
  - mypy type checking capabilities
  - Comprehensive quality gates in Makefile
- **Configuration Management** - Professional configuration architecture
  - Environment-based config.py with Development/Test/Production classes
  - config.py.example template following best practices
  - Comprehensive environment variable support with sensible defaults
  - Production configuration validation
- **Project Management Enhancement** - Structured development workflows
  - Comprehensive .project/ documentation structure
  - Advanced prompts.json with systematic development workflows
  - Typed task IDs (DOC, INFRA, TEST, SEC) for better organization
  - Strategic progress tracking with measurable metrics

### Changed
- **Testing Infrastructure Modernization** - Updated deprecated SQLAlchemy patterns
  - Replaced deprecated create_scoped_session with sessionmaker
  - Fixed Flask app context compatibility issues
  - Updated database tests to use modern text() for raw SQL
- **Code Organization** - Improved import ordering and code structure
  - Fixed E402 module-level import ordering issues
  - Enhanced factory pattern with better error handling
  - Improved argument usage and code quality compliance
- **Documentation Enhancement** - Comprehensive project documentation updates
  - README.md enhanced with config.py setup instructions
  - Architecture.md updated with configuration structure details
  - Goals.md updated with achieved strategic milestones
  - Progress.md enhanced with detailed accomplishments and metrics

### Fixed
- **New Machine Setup** - Resolved critical development environment barriers
  - Fixed "make test" failures on fresh installations due to missing UV
  - Added comprehensive dependency checking with clear error messages
  - Implemented cross-platform installation guidance (Linux/macOS)
- **Test Suite Stability** - Addressed compatibility and reliability issues
  - Fixed SQLAlchemy session fixture compatibility problems
  - Resolved Flask application context test assertion issues
  - Updated database connection tests for modern API patterns
  - Improved test isolation and transaction handling

### Infrastructure
- **Cross-Platform Support** - Linux and macOS development parity achieved
- **Professional Quality Gates** - Comprehensive linting, testing, and security tools operational
- **Strategic Milestone Achievement** - Project transitioned to implementation-ready status with multiple high-priority tasks unblocked

### Security
- **Configuration Security** - config.py properly excluded from version control
- **Environment Management** - Sensitive configuration via environment variables
- **Quality Scanning** - Security tools integrated for ongoing vulnerability assessment

## [Legacy Versions]

### [Pre-2.0] - Historical Development
- Original HT Status application development
- Flask application with Hattrick CHPP API integration
- Basic PostgreSQL schema and player data management
- Initial React frontend development (modern UI direction)
- Docker Compose orchestration setup
- Legacy shell scripts for development (deprecated in 2.0)

---

## Change Categories

This changelog follows these categories:
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
- **Infrastructure** for development environment improvements

## Contributing to Changelog

When making changes to the project:
1. Add entries to the [Unreleased] section
2. Follow the established format and categories
3. Reference relevant task IDs from .project/backlog.md when applicable
4. Focus on changes that affect users, developers, or deployment
