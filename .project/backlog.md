# HTStatus Development Backlog

> **Purpose**: Prioritized active task tracking with 7-level priority system for HTStatus development
> **Audience**: Developers and AI agents selecting and executing tasks
> **Update Frequency**: Continuously - update status when starting/completing tasks, add new tasks as discovered
> **Standards**: Follow [rules.md](rules.md) for editing guidelines

## Management Rules

**For AI Agents**:
1. ALWAYS read this entire backlog before selecting tasks
2. Choose tasks marked 🎯 Ready to Execute with no blockers
3. Update task status when starting (🚀 ACTIVE) and completing (✅ COMPLETED)
4. Follow priority order: P0 Critical Bugs → P1 Testing → P2 Deployment → P3 Stability → P4 Functionality → P5 DevOps → P6 Documentation → P7 Future
5. Move completed tasks to history/backlog-done.md with completion notes and REMOVE them from here.

**For Humans**:
- Tasks organized by 8 priority levels based on project maturity and risk
- P0 tasks are critical bugs blocking core functionality
- P1 tasks ensure application reliability and testing confidence
- P2-P3 tasks build stability and maintainability
- P4-P6 tasks enhance operations, developer experience, and documentation
- Choose based on available time, skills, and project needs

---

## Current Focus

**Priority 1: Testing & App Reliability**
- 🚀 [TEST-012-A] Fix 6 Player Group Fixture Issues (2-3 hours) - Complete test suite reliability **ACTIVE**
- 🎯 [TEST-013] Add CHPP Integration Testing (3-4 hours) - Prevent team ID vs user ID bugs, test multi-team scenarios **READY**

**Priority 2: Deployment & Operations**
- 🎯 [INFRA-021] Environment Parity Enforcement (4-6 hours) - Pin Python versions and dependencies across dev/test/prod **HIGH PRIORITY**
- 🎯 [INFRA-018] CHPP Config Test Reliability (45-60 min) - Fix configuration test environment isolation issues

**Priority 3: Stability & Maintainability** (It stays working) - Major foundation complete, focus on test coverage and security
- 🎯 [UI-008] Implement UI Guidelines Across Existing Pages (8-12 hours) - Apply unified design system to Flask templates and React components **NEXT IN LINE**
- 🎯 [TEST-004] Blueprint Test Coverage (3-4 hours) - Achieve 80% coverage for blueprint modules **READY TO EXECUTE**
- 🎯 [TEST-005] Utils Module Test Coverage (2-3 hours) - Validate migrated utility functions **READY TO EXECUTE**
- 🔄 [TYPESYNC-001] Fix 85 Type Sync Drift Issues (6-8 hours) - Resolve nullability and type mismatches between SQLAlchemy models and TypeScript interfaces **HIGH PRIORITY**
- 🎯 [REFACTOR-001] Code Maintainability (6-8 hours) - Technical debt cleanup
- 🎯 [INFRA-009] Dependency Strategy (4-6 hours) - Maintenance planning

**Priority 4: Core Functionality** (It does what it should)
- 🎯 [DOC-021](#doc-021-new-player-tutorial) New Player Tutorial (3-5 hours) - Onboarding walkthrough **READY**
- 🎯 [FEAT-005](#feat-005-team-statistics-dashboard) Team Statistics Dashboard (8-10 hours) - Performance analytics
- 🎯 [FEAT-008](#feat-008-next-game-analyser) Next Game Analyser (12-16 hours) - Tactical preparation and opponent analysis
- 🔮 [FEAT-003](#feat-003-formation-tester--tactics-analyzer) Formation Tester & Tactics Analyzer - Research Phase

**Priority 5: DevOps & Developer Experience** (Make it easy)
- 🎯 [DOC-019] macOS Setup Guide (30 min) - Platform support
- 🎯 [DOC-020] UV Installation Guide (30 min) - Environment onboarding
- 🎯 [DOC-010] Testing Prompts (30 min) - AI agent testing workflows
- 🎯 [INFRA-020] Fix GitHub Workflows (30 min) - CI reliability
- 🎯 [DEVOPS-001] Script Linting Cleanup (1-2 hours) - Fix 32 linting errors in test files **READY TO EXECUTE**
- 🎯 [FEAT-006] Default Player Groups for New Users (2-3 hours) - Onboarding

**Priority 6: Documentation & Polish** (Make it complete)
- 🎯 [DOC-023] Clean TECHNICAL.md Obsolete Content (1-2 hours) - Remove outdated route architecture descriptions **HIGH PRIORITY**
- 🎯 [DOC-024] Clean README.md Legacy Sections (1 hour) - Remove deprecated setup instructions
- 🎯 [DOC-025] Update architecture.md File Structure (30 min) - Reflect current blueprint architecture
- 🎯 [DOC-011-API] API Documentation (4-6 hours) - Developer experience
- 🎯 [DOC-005] User Documentation (4-6 hours) - User adoption
- 🎯 [DOC-004] Progress Metrics (1 hour) - Project visibility
- 🎯 [FEAT-007] Team Series View (4-6 hours) - Historical performance tracking
- 🎯 [FEAT-001] Data Visualization (12-15 hours) - Enhanced charts
- 🎯 [UI-004] Bulk Player Group Editor (3-4 hours) - Workflow optimization
- 🎯 [UI-005] Player Table Filtering (4-6 hours) - Advanced data discovery
- 🎯 [UI-006] Transfer Bid Display (2-3 hours) - Market visibility
- 🎯 [UI-007] Update Report Icon Display (2-3 hours) - Change visualization
- 🎯 [FEAT-004] Hattrick Language Localization (4-6 hours) - Multi-language support
- 🔮 [RESEARCH-001] Additional Integrations - Future research

**Priority 7: Potential Future Improvements**
- 🔮 [UPGRADE-001] Re-upgrade to pychpp 0.5.10 + Flask 3.1+ + werkzeug 3.1+ (2-3 hours) - Re-attempt library upgrades now that team ID bug is fixed
- 🔮 [FEAT-010] Collaborative League Intelligence (40-60 hours) - Multiplayer league-wide platform for shared scouting and collective tactical analysis
- 🔮 [FEAT-011] AI-Powered Training Optimization Engine (60-80 hours) - Machine learning on historical skill progression for optimal training schedules
- 🔮 [REFACTOR-004] Replace pyCHPP Dependency (16-24 hours) - Custom CHPP API integration for long-term independence
- 🔮 [FEAT-009] Trophy Data Integration (6-8 hours) - Add historical trophy/achievement display when pyCHPP supports it

---

## Priority 1: Testing & App Reliability

### [TEST-012-A] Fix 6 Player Group Fixture Issues
**Status**: 🎯 Ready to Execute | **Effort**: 2-3 hours | **Priority**: P1 | **Impact**: Complete test suite reliability
**Dependencies**: TEST-012 (completed) | **Strategic Value**: Final test reliability milestone

**Problem Statement**:
After successful TEST-012 implementation, 6 specific player group management tests still fail due to PostgreSQL foreign key constraint issues within the nested savepoint pattern. These tests pass individually but fail when run together.

**Root Cause**:
- Foreign key constraints fail during fixture creation in the `sample_group` fixture
- PostgreSQL doesn't allow foreign key references to uncommitted data within the same savepoint
- Current workaround disables foreign key checks temporarily but has ID assignment issues

**Specific Failures**:
- 4 failures in `test_blueprint_player.py::TestPlayerGroupManagement`
- 2 failures in `test_minimal_routes.py` (similar fixture dependency issues)

**Implementation**:
1. **Refactor Fixture Dependencies** (1-1.5 hours): Redesign `sample_user`, `sample_players`, `sample_group` fixtures to avoid foreign key issues
2. **Alternative Fixture Pattern** (30-45 min): Use factory functions or ensure proper commit ordering within savepoint context
3. **Validation** (15-30 min): Verify all 6 tests pass and Group 3 achieves 100% pass rate

**Technical Approach**:
- Either commit fixtures in proper dependency order within the savepoint
- Or create fixtures that don't require database-assigned IDs until test execution
- Maintain transaction isolation while resolving constraint issues

**Acceptance Criteria**:
- All 6 failing player group tests pass (104/104 in Group 3)
- Isolated test approach maintains 100% pass rate across all 3 groups
- No regression in existing fixture isolation

### [TEST-008] Residual Test Failures Resolution
**Status**: ✅ COMPLETED | **Effort**: 1-2 hours | **Priority**: P1 | **Impact**: Complete test suite reliability
**Dependencies**: All dependencies resolved (TEST-011, TEST-010 completed) | **Strategic Value**: Complete testing foundation

**MAJOR BREAKTHROUGH ACHIEVED**: Core test infrastructure stabilized
- ✅ **Fixed critical test pollution issue** - test_blueprint_player.py was dropping database tables
- ✅ Removed problematic player_app fixture with db.drop_all() call
- ✅ Switched to shared app fixture from conftest.py for consistency
- ✅ Added app_with_routes fixture for route-dependent tests
- ✅ **32/32 core tests pass consistently** - major reliability improvement maintained
- ✅ Blueprint player tests now pass with Flask Bootstrap registration fix (TEST-011 completed)

**Final Resolution**:
Fixed the final test failure by correcting type conversion in player.py (playerid as string → int(playerid) for database queries) and adding proper test isolation by including db_session dependency in authenticated_client fixture.

**Final Outcome**:
- **Core tests**: 32/32 passing (maintained)
- **Blueprint player tests**: 17/17 passing (perfect score)
- **Total achievement**: Complete test suite reliability for P1 priority achieved

**Next Steps**:
1. ✅ **Fix config mismatches** (completed): Updated test assertions to match TestConfig values
2. ✅ **Fix test expectations** (completed): Corrected test_blueprint_player.py assertions
3. ✅ **Fix fixture setup** (completed): Fixed initialize_routes() missing _db_instance parameter
4. 🎯 **Fix Flask Bootstrap registration** (TEST-011): Resolve registration order conflict
5. 🎯 **Fix database fixtures** (TEST-010): Fix UniqueViolation errors after bootstrap resolution

**Acceptance Criteria**: All blueprint player tests pass, contributing to overall test suite reliability

---

## Priority 2: Deployment & Operations

### [INFRA-021] Environment Parity Enforcement
**Status**: 🎯 Ready to Execute | **Effort**: 4-6 hours | **Priority**: P2 | **Impact**: Prevent production bugs from environment drift
**Dependencies**: None | **Strategic Value**: Production reliability through dev/test/prod consistency

**Problem Statement**:
Currently development, testing, and production environments may use different Python versions and dependency configurations, creating risk of "works on my machine" bugs reaching production:

**Current Issues**:
- Development: Python 3.14.2 (uv run python)
- Production: Unclear Python version (DEPLOYMENT.md says "3.9+")
- No .python-version file to pin Python across environments
- pyproject.toml specifies ">=3.9" (wide range allows drift)
- Docker configurations don't specify Python base image versions
- No Dockerfile to ensure consistent Python runtime in containers
- UV dependency resolution may differ between Python versions

**Impact**:
- Subtle bugs from Python version differences (3.9 vs 3.14 behavior changes)
- Dependency resolution differences cause production failures
- Testing doesn't validate production environment
- "Works in dev" failures in production waste debugging time
- Deployment confidence reduced without environment parity

**Implementation**:
1. **Production Environment Audit** (30-45 min):
   - SSH to production server: `ssh glader.local`
   - Check current Python version: `python --version` or `python3 --version`
   - Check installed packages: `pip list` or check virtual environment
   - Check if UV is installed: `uv --version`
   - Document current production configuration in task notes
   - Check application runtime environment (systemd service, Docker, direct)
   - Identify any production-specific configurations or workarounds

2. **Python Version Pinning** (1-2 hours):
   - Create .python-version file pinning to specific version (e.g., 3.11.8)
   - Update pyproject.toml requires-python to narrow range (e.g., ">=3.11,<3.12")
   - Document Python version choice rationale (stability, feature support)
   - Update DEPLOYMENT.md with specific Python version requirement

3. **Docker Environment Standardization** (2-3 hours):
   - Create Dockerfile with pinned Python base image (python:3.11.8-slim)
   - Add multi-stage build for production optimization
   - Ensure UV installs exact dependency versions from uv.lock
   - Test Docker build matches local development environment
   - Update docker-compose.yml to use Dockerfile instead of service configs

4. **Production Debugging Documentation** (45-60 min):
   - Document SSH access to glader.local in DEPLOYMENT.md
   - Add production debugging guide with common commands:
     - Check application status: systemd commands or Docker status
     - View logs: log file locations and tail commands
     - Check Python environment: version, packages, paths
     - Monitor resources: memory, CPU, disk usage
     - Test database connectivity from production
     - Check CHPP API connectivity and credentials
   - Document how to safely restart production application
   - Add troubleshooting section for common production issues
   - Document rollback procedures

5. **Documentation & Validation** (1 hour):
   - Update README.md with Python version requirements
   - Document environment parity strategy in TECHNICAL.md
   - Add "make verify-env" command to check Python version matches
   - Create CI check to validate Python version consistency

**Technical Details**:
- Recommended Python version: 3.11.x (stable, long-term support, good performance)
- Rationale: 3.14 too new (released late 2025), 3.9 too old (EOL Oct 2025), 3.11 optimal balance
- Docker base: python:3.11.8-slim-bookworm (Debian, security updates, minimal)
- UV lock file already pins exact versions - ensure respected across environments

**Acceptance Criteria**:
- [ ] Production environment audit completed (glader.local Python version documented)
- [ ] Production debugging guide added to DEPLOYMENT.md
- [ ] SSH access and common debugging commands documented
- [ ] .python-version file created with specific version (3.11.8)
- [ ] pyproject.toml requires-python updated to narrow range
- [ ] Dockerfile created with pinned Python base image
- [ ] docker-compose.yml uses Dockerfile for app service
- [ ] README.md and DEPLOYMENT.md updated with Python version
- [ ] TECHNICAL.md documents environment parity strategy
- [ ] CI validates Python version matches .python-version
- [ ] Local dev, testing, and Docker use same Python version
- [ ] UV lock file dependency resolution consistent across environments

**Validation Steps**:
1. SSH to glader.local and verify production Python version documented
2. Verify `python --version` matches .python-version in dev
3. Build Docker image and verify Python version inside container
4. Run test suite in Docker container - must pass with same results as local
5. SSH to glader.local after deployment and verify Python version matches
6. Test production debugging procedures from documentation
7. Confirm no dependency resolution differences between environments

**Expected Outcomes**: Elimination of environment drift bugs, confident deployments, "works everywhere" reliability, reduced debugging time from environment differences

---

## Priority 3: Stability & Maintainability

### [DOC-021] New Player Tutorial
**Status**: 🎯 Ready to Execute | **Effort**: 3-5 hours | **Impact**: User onboarding and feature discovery
**Dependencies**: Core UI features (completed) | **Strategic Value**: Reduced learning curve, improved user retention

**Problem Statement**:
New players need guided onboarding to understand HT Status features and workflows. Returning players also benefit from tutorials about newly added features. Currently, users must explore the interface without guidance, leading to:
- Longer initial learning curve
- Missed features and capabilities
- Support questions about basic functionality
- Reduced feature adoption for advanced capabilities

**Implementation**:
1. **Interactive Tutorial Walkthrough** (1.5-2 hours):
   - Create step-by-step guided tour of main features
   - Highlight key pages: Team, Players, Training, Matches, Settings
   - Add tooltips and highlights for UI elements
   - Implement "skip" and "restart" functionality
   - Persist tutorial completion state per user

2. **Feature-Specific Guides** (1-1.5 hours):
   - Player group management (just added as FEAT-006)
   - Training data tracking and interpretation
   - Match analysis features
   - Settings customization options
   - Data update and synchronization

3. **What's New Alerts** (0.5-1 hour):
   - Detect new features since user last login
   - Display contextual "New Feature" badges
   - Link to relevant tutorial sections for new features
   - Allow dismissal and "show later" options

4. **Tutorial Content** (1-1.5 hours):
   - Write clear, concise instructional text
   - Create or capture screenshots
   - Document common workflows
   - Include Hattrick-specific terminology explanations

**Acceptance Criteria**:
- Interactive tutorial available on first login or from help menu
- All major features have tutorial coverage
- Users can restart or skip tutorial anytime
- New feature alerts display appropriately
- Tutorial state persists across sessions
- Tutorial content is clear and actionable
- Mobile-responsive tutorial experience
- Tutorial works in multiple supported languages (if FEAT-004 completed)

**Scope**:
- **Includes**: Guided tour, feature explanations, new feature alerts, contextual help
- **Excludes**: Hattrick game rules education (out of scope), advanced strategy guides
- **Focus**: HT Status feature functionality and workflows

**Technical Approach**:
- Use a tutorial library (e.g., Intro.js, Shepherd.js, or custom implementation)
- Store tutorial state in user settings/preferences
- Implement feature detection for new alerts
- Create reusable tutorial component/system for future features

**Expected Outcomes**: Improved user onboarding, faster time-to-productivity, reduced support burden, better adoption of newly added features, increased user retention

---

### [UI-008] Implement UI Guidelines Across Existing Pages
**Status**: 🎯 Ready to Execute | **Effort**: 8-12 hours | **Impact**: User experience consistency and visual unification
**Dependencies**: DOC-022 (completed) | **Strategic Value**: Deliver unified user experience across dual frontend architecture

**Problem Statement**:
DOC-022 created comprehensive UI guidelines, but existing Flask templates and React components still use inconsistent styling patterns. Users experience jarring visual differences when navigating between different sections of the application. To deliver the promised unified user experience, existing pages must be refactored to follow the established design system.

**Current Inconsistencies**:
- Flask templates use Bootstrap 4.5 default styling vs unified football theme
- Button styles vary across pages (default Bootstrap vs custom implementations)
- Card components use different spacing and visual hierarchy
- Table styling inconsistent between data views
- Color usage doesn't follow established primary green palette
- Typography sizing varies from standardized scale

**Implementation**:
1. **Flask Template Refactoring** (4-6 hours):
   - Apply custom CSS classes to existing templates: `.btn-primary-custom`, `.card-custom`, `.table-custom`
   - Update `base.html` with unified CSS classes from implementation standards
   - Refactor main.html, team.html, player.html, training.html, matches.html, stats.html, settings.html
   - Replace Bootstrap default colors with football green theme
   - Standardize typography using unified scale (h1: 2.5rem, h2: 2rem, etc.)
   - Implement consistent spacing using 0.25rem increments

2. **React Component Alignment** (2-3 hours):
   - Review existing React components for compliance with style guide
   - Update button variants to use football theme consistently
   - Ensure card components follow unified spacing patterns
   - Verify table components match Flask styling patterns
   - Apply consistent color tokens throughout React pages

3. **Cross-Framework Validation** (1-2 hours):
   - Compare Flask and React pages side-by-side for visual consistency
   - Test responsive design across different screen sizes
   - Validate color contrast and accessibility standards
   - Ensure navigation patterns feel consistent across both systems

4. **Documentation Updates** (0.5-1 hour):
   - Update UI documentation with any refinements discovered during implementation
   - Document any edge cases or special considerations
   - Create before/after screenshots for reference

**Acceptance Criteria**:
- All Flask templates use unified CSS classes (.btn-primary-custom, .card-custom, .table-custom)
- React components maintain visual consistency with Flask pages
- Football green color theme applied consistently across all pages
- Typography follows standardized scale (h1: 2.5rem, h2: 2rem, body: 1rem)
- Spacing uses consistent 0.25rem increments throughout
- No jarring visual differences when navigating between Flask and React sections
- All changes validated through cross-browser testing
- Responsive design maintains consistency across screen sizes
- Accessibility standards (WCAG 2.1 AA) maintained or improved

**Pages to Update**:
**Flask Templates**:
- `main.html` - Dashboard/home page
- `team.html` - Team overview
- `player.html` - Player management
- `training.html` - Training progress
- `matches.html` - Match history
- `stats.html` - Team statistics
- `settings.html` - User configuration
- `login.html`, `logout.html` - Authentication pages

**React Components**:
- All pages in `src/pages/` (Players.tsx, Training.tsx, Matches.tsx, etc.)
- Shared components in `src/components/`
- Layout components (Header.tsx, Sidebar.tsx)

**Technical Approach**:
- Follow implementation standards from `.project/ui-implementation-standards.md`
- Use design templates from `.project/ui-design-guidelines.md`
- Validate against checklist in design guidelines
- Maintain backward compatibility for existing functionality
- Test changes incrementally to avoid breaking functionality

**Risk Mitigation**:
- Implement changes incrementally, testing each template individually
- Maintain Git commits for easy rollback if issues arise
- Validate all user workflows still function correctly
- Test with existing user data to ensure no data display issues

**Expected Outcomes**: Unified visual experience across all HTStatus pages, elimination of jarring transitions between Flask and React sections, improved user satisfaction, consistent brand presentation, enhanced accessibility compliance, foundation for future UI development

---

### [FEAT-003] Formation Tester & Tactics Analyzer
**Status**: 🔮 Research & Planning | **Effort**: 24-32 hours (estimated) | **Impact**: Tactical decision support
**Dependencies**: Player data system (completed), Backend API structure | **Strategic Value**: Competitive advantage, engagement

**Problem Statement**:
Users need a way to experiment with different formations and see how effective they would be based on player skills and positions. Currently only "Player" and "Training" pages exist per team. A third "Formations" page would allow users to:
- Visually design and test different formations
- Get feedback on formation quality (based on player skills and position-suitability)
- Compare different tactical approaches
- Export or save formations for reference

**Research Phase** (Required before implementation):
1. **Industry Analysis** (4-6 hours):
   - Study how Hattrick community (e.g., top guilds/clans) implements formation testing
   - Research existing Hattrick formation analyzers and tools
   - Identify best practices in formation evaluation algorithms
   - Check community recommendations and resources

2. **Technical Investigation** (3-4 hours):
   - Research drag-and-drop libraries (React DnD, dnd-kit, react-beautiful-dnd)
   - Evaluate soccer field visualization libraries
   - Investigate Hattrick position contribution calculations
   - Determine skill weighting algorithms

3. **Algorithm Design** (4-6 hours):
   - Define how formation quality is scored
   - Model position-to-player compatibility
   - Create skill contribution multipliers
   - Design formation comparison logic

**Implementation Phases** (Post-research):
1. **Backend API** (6-8 hours): Formation evaluation endpoints, player skill analysis
2. **UI Components** (8-10 hours): Soccer field visualization, drag-and-drop interface
3. **Integration** (4-6 hours): Connect to player data, save formations, export functionality
4. **Polish & Testing** (2-4 hours): Edge cases, performance, accessibility

**Acceptance Criteria** (Post-research):
- Formation tester page accessible from team view
- Drag-and-drop player placement on field
- Real-time formation quality feedback
- Formation comparison functionality
- Save/load formation templates
- Mobile-responsive design

**Expected Outcomes**: Enhanced tactical planning, improved user engagement, competitive advantage in Hattrick gameplay

---

### [FEAT-005] Team Statistics Dashboard
**Status**: 🎯 Ready to Execute | **Effort**: 8-10 hours | **Impact**: Performance analytics and insights
**Dependencies**: Player data system (completed), Match history (completed) | **Strategic Value**: Data-driven decisions, engagement

**Problem Statement** (Feature request from Dec 31, 2020, GitHub issue #40):
Users need a dedicated statistics page to view comprehensive team and player performance metrics. Currently, statistics are scattered across different pages. A unified "Statistics" dashboard would allow users to:
- View all-time team scorers and top performers
- Track player match history and playing time
- Analyze team performance trends
- Identify performance gaps and opportunities
- Make data-driven decisions about training and tactics

**Implementation**:
1. **Player Statistics** (3-4 hours):
   - All-time goal scorers (top scorers list)
   - Most appearances/matches played per player
   - Career statistics per player (goals, assists, rating)
   - Player performance trends over time
   - Best performing players by position

2. **Team Statistics** (2-3 hours):
   - Total goals scored/conceded by season
   - Team win/loss/draw record
   - Home/away performance comparison
   - Average team rating trends
   - Match statistics (possession, shots, etc. if available from CHPP)

3. **Comparative Analysis** (2-3 hours):
   - Compare players by position and role
   - Position-specific statistics
   - Form trends (recent vs career)
   - Training effectiveness analysis
   - Player development trajectories

4. **UI & Visualization** (1-2 hours):
   - Charts showing performance trends
   - Sortable/filterable statistics tables
   - Period selection (season, all-time, custom range)
   - Export statistics capability
   - Mobile-responsive design

**Acceptance Criteria**:
- Dedicated statistics page accessible from team view
- All-time goal scorers ranked list
- Matches played per player statistics
- Team aggregate statistics
- Trend charts showing performance over time
- Filterable/sortable statistics tables
- Period selection (season, all-time, custom)
- Mobile-responsive design maintained
- Export statistics data (CSV/PDF optional)

**Data Sources**:
- Player career data from database (matches, goals, assists)
- Team match history for aggregate statistics
- Hattrick match data from CHPP for detailed match stats
- Player rating data over time

**Statistics to Display**:
- **Player Stats**: Goals, assists, appearances, minutes, avg rating, specialties
- **Team Stats**: Total goals, goals conceded, wins/losses/draws, seasons played
- **Top Performers**: Best scorers, most appearances, highest rated, best position fit
- **Trends**: Performance trajectory, training progress, form changes

**UI Layout**:
- Tab-based navigation: "Overall", "Players", "Teams", "Trends"
- Dashboard with key metrics cards at top
- Detailed statistics tables below
- Charts for trend visualization
- Filter/sort controls for customization

**Expected Outcomes**: Better insight into team and player performance, data-driven decision making, improved user engagement

---

### [FEAT-008] Next Game Analyser
**Status**: 🎯 Ready to Execute | **Effort**: 12-16 hours | **Impact**: Tactical preparation and competitive intelligence
**Dependencies**: Match history (completed), CHPP integration (completed), Team Statistics (FEAT-005 recommended) | **Strategic Value**: Strategic planning, opponent analysis

**Problem Statement**:
Users need a way to prepare tactically for upcoming matches by analyzing their opponent's historical patterns and getting strategic recommendations. Currently, users must manually research opponents on external sites. A "Next Game Analyser" would allow users to:
- Select an upcoming fixture from their match schedule
- View opponent's historical formations, tactics, and player usage patterns
- Get AI-suggested tactical approaches to counter opponent strategies
- Compare their team's strengths against opponent's weaknesses
- Export or save tactical reports for match preparation

**Implementation**:
1. **Match Schedule Integration** (2-3 hours):
   - Fetch upcoming matches from Hattrick via CHPP API
   - Display future fixtures with opponent team details
   - Allow selection of specific match for analysis

2. **Opponent Data Analysis** (4-6 hours):
   - Retrieve opponent's recent match history and formations
   - Analyze opponent's typical tactical setups (positions, player roles)
   - Identify opponent's key players and strengths/weaknesses
   - Track opponent's home/away performance patterns

3. **Tactical Recommendation Engine** (4-5 hours):
   - Compare user's team strengths vs opponent weaknesses
   - Suggest formations that counter opponent's typical setup
   - Recommend specific player assignments and tactical instructions
   - Provide rationale for each recommendation based on historical data

4. **UI & Visualization** (2-3 hours):
   - Match selection interface showing upcoming fixtures
   - Opponent analysis dashboard with key metrics
   - Tactical recommendations with interactive formation view
   - Export tactical report functionality
   - Mobile-responsive design

**Acceptance Criteria**:
- Upcoming matches displayed with opponent details
- Comprehensive opponent analysis showing historical patterns
- Clear tactical recommendations with reasoning
- Formation suggestions integrated with existing player data
- Tactical reports can be saved/exported
- Analysis works for both league and cup matches
- Mobile-responsive interface maintained

**Data Sources**:
- Opponent match history from CHPP API
- Opponent player data and formations
- User's team strengths and player capabilities
- Historical head-to-head performance (if available)

**Analysis Features**:
- **Opponent Strengths**: Key players, preferred formations, home/away record
- **Tactical Patterns**: Common setups, substitution patterns, special tactics
- **Vulnerability Analysis**: Weak positions, poor away form, tactical gaps
- **Counter-Strategy**: Formation suggestions, player matchups, tactical advice
- **Historical Context**: Previous meetings, league position trends

**Expected Outcomes**: Enhanced match preparation, improved tactical decision-making, competitive advantage in Hattrick gameplay, increased user engagement with strategic features

---

## Priority 4: Core Functionality

### [DOC-021] New Player Tutorial
**Status**: 🚀 IN PROGRESS (90% complete) | **Effort**: 6-8 hours | **Impact**: Code organization
**Dependencies**: INFRA-011 (completed) | **Strategic Value**: Maintainability, scalability

**Implementation Status**:
- ✅ Created blueprint module structure in `/app/blueprints/` with `__init__.py`
- ✅ Created `auth.py` blueprint with login/logout authentication routes
- ✅ Created `main.py` blueprint with index/settings/admin routes
- ✅ Created `player.py` blueprint with player management and grouping routes
- ✅ Created `team.py` blueprint with team and data update routes
- ✅ Created `matches.py` blueprint with matches and stats routes
- ✅ Created `training.py` blueprint with player training progression routes
- ✅ Migrated all route functions from monolithic `/app/routes.py` to logical blueprints
- ✅ Updated `factory.py` to import, initialize, and register all blueprint modules
- ✅ Added shared helper functions to `routes_bp.py`: dprint, debug_print, diff_month, diff, get_training, player_diff
- ✅ Maintained backward compatibility using manual `add_url_rule()` registration
- ✅ Preserved session management, authentication patterns, and CHPP integration
- ✅ All application URLs remain functional and accessible
- ✅ 206/213 tests passing (96.7% success rate) - comprehensive functionality validated

**Remaining Work** (10%):
- Minor test assertion cleanups for blueprint registration expectations
- Optional: Documentation updates to reflect new blueprint architecture

**Acceptance Criteria**:
- ✅ All routes properly organized into functional blueprints
- ✅ Zero breaking changes to existing functionality - all URLs work
- ✅ Improved code organization with clear separation of concerns
- ✅ Better maintainability with modular blueprint structure
- ✅ Application functionality verified with 206/213 tests passing

**Expected Outcomes**: Better code maintainability, easier feature development, Flask best practices, significantly improved code organization enabling future refactoring

---

### [REFACTOR-003] Type Sync Issues Resolution
**Status**: 🔮 Future Task | **Effort**: 8-12 hours | **Impact**: Type safety improvement
**Dependencies**: INFRA-008 Type Sync Validation (completed) | **Strategic Value**: Clean dual architecture, reduced technical debt

**Implementation**:
1. **Nullability Analysis** (4-6 hours): Review 83 nullability mismatches between SQLAlchemy and TypeScript
2. **Type Field Resolution** (2-3 hours): Address User.password and User.player_columns type mismatches
3. **Database Schema Assessment** (1-2 hours): Determine safe nullability changes vs TypeScript optional fields
4. **Incremental Updates** (1-2 hours): Apply fixes in small batches with validation

**Acceptance Criteria**:
- Reduced type sync issues from 85 to under 20
- No breaking changes to existing functionality
- All changes validated through existing test suite
- Updated documentation reflecting changes

**Expected Outcomes**: Improved type consistency, reduced future integration bugs, cleaner dual architecture

---

### [REFACTOR-001] Code Maintainability
**Status**: 🎯 Ready to Execute | **Effort**: 6-8 hours | **Impact**: Long-term maintainability
**Dependencies**: Testing infrastructure (achieved) | **Strategic Value**: Development velocity, code quality

**Implementation Phases**:
1. **routes.py Refactoring** (8-10 hours): Break down 2,052-line monolith
2. **Service Layer Extraction** (6-8 hours): Separate business logic
3. **Type Annotations** (4-6 hours): Comprehensive type coverage
4. **Separation of Concerns** (2-4 hours): Clear architectural boundaries

**Acceptance Criteria**:
- Reduced cyclomatic complexity (<10 per function)
- Clear separation between routes, services, and data layers
- Comprehensive type annotations (>90% coverage)

**Expected Outcomes**: Improved maintainability, faster development, reduced bugs

---

### [INFRA-009] Dependency Strategy
**Status**: 🎯 Ready to Execute | **Effort**: 3-4 hours | **Impact**: Maintenance planning
**Dependencies**: None | **Strategic Value**: Security, long-term sustainability

**Implementation**:
1. Audit all Python and JavaScript dependencies
2. Create automated update strategy and schedule
3. Identify critical security dependencies
4. Document dependency management policies

**Acceptance Criteria**:
- Complete dependency audit with risk assessment
- Automated update procedures documented
- Security monitoring integrated

**Expected Outcomes**: Proactive dependency management, improved security, reduced technical debt

---

## Priority 5: DevOps & Developer Experience

### [DOC-019] macOS Setup Guide
**Status**: 🎯 Ready to Execute | **Effort**: 30 minutes | **Impact**: Platform support
**Dependencies**: None | **Strategic Value**: Developer onboarding

**Implementation**:
1. Create dedicated macOS setup section
2. Document Homebrew installation of dependencies
3. Include macOS-specific environment setup
4. Add troubleshooting for common macOS issues

**Acceptance Criteria**:
- Complete macOS setup instructions
- Homebrew-based dependency guide
- Platform-specific troubleshooting

**Expected Outcomes**: Improved macOS developer experience, reduced setup friction

---

### [DOC-020] UV Installation & Troubleshooting Guide
**Status**: 🎯 Ready to Execute | **Effort**: 30 minutes | **Impact**: Environment onboarding
**Dependencies**: None | **Strategic Value**: Development consistency

**Implementation**:
1. Create comprehensive UV installation guide for all platforms
2. Document common troubleshooting scenarios
3. Add environment debugging procedures
4. Include UV best practices

**Acceptance Criteria**:
- Installation instructions for macOS, Linux, Windows
- Common error scenarios with solutions
- UV-specific debugging procedures

**Expected Outcomes**: Reduced onboarding friction, consistent UV usage, faster issue resolution

---

### [DOC-010] Testing Prompts
**Status**: 🎯 Ready to Execute | **Effort**: 30 minutes | **Impact**: AI agent effectiveness
**Dependencies**: None | **Strategic Value**: Development efficiency

**Implementation**:
1. Document testing workflow and best practices
2. Create prompts for AI-assisted test development
3. Establish testing standards and coverage requirements
4. Document test debugging procedures

**Acceptance Criteria**:
- Comprehensive testing workflow documentation
- AI testing prompts created
- Testing standards clearly defined

**Expected Outcomes**: Consistent testing practices, improved AI agent capabilities

---

### [INFRA-020] Fix GitHub Workflows
**Status**: 🎯 Ready to Execute | **Effort**: 30 minutes | **Impact**: CI reliability
**Dependencies**: None | **Strategic Value**: Automated quality gates, deployment consistency

**Implementation**:
1. Update GitHub workflow files to use `make test-all` instead of individual test commands
2. Ensure CI pipeline uses the comprehensive 6-step quality gate process
3. Verify all workflow triggers and conditions remain appropriate
4. Test workflow execution in CI environment

**Acceptance Criteria**:
- GitHub workflows use `make test-all` command
- CI pipeline runs complete quality gate validation
- No regressions in workflow functionality
- Proper status reporting maintained

**Expected Outcomes**: Consistent CI validation, comprehensive quality gates in GitHub Actions, improved deployment confidence

---

## Priority 6: Documentation & Polish

### [DOC-011-API] API Documentation
**Status**: 🎯 Ready to Execute | **Effort**: 4-6 hours | **Impact**: Developer experience
**Dependencies**: None | **Strategic Value**: API adoption, integration support

**Implementation**:
1. Document all API endpoints with OpenAPI/Swagger
2. Create interactive API documentation
3. Add authentication flow documentation
4. Include example requests and responses

**Acceptance Criteria**:
- Complete API documentation with examples
- Interactive testing capability
- Authentication procedures documented

**Expected Outcomes**: Enhanced developer experience, easier API integration

---

### [DOC-005] User Documentation
**Status**: 🎯 Ready to Execute | **Effort**: 4-6 hours | **Impact**: User adoption
**Dependencies**: None | **Strategic Value**: Feature discovery, support reduction

**Implementation**:
1. Create comprehensive user guides for all features
2. Add screenshots and workflow examples
3. Document troubleshooting procedures
4. Create video tutorials for complex features

**Acceptance Criteria**:
- Complete feature documentation
- Visual guides and tutorials
- User troubleshooting resources

**Expected Outcomes**: Improved user onboarding, reduced support burden, increased feature adoption

---

### [DOC-004] Progress Metrics
**Status**: 🎯 Ready to Execute | **Effort**: 1 hour | **Impact**: Project visibility
**Dependencies**: None | **Strategic Value**: Progress tracking

**Implementation**:
1. Create automated progress metrics collection
2. Document key project health indicators
3. Establish baseline metrics and targets
4. Create dashboard or reporting mechanism

**Acceptance Criteria**:
- Automated metrics collection system
- Documented progress indicators
- Progress reporting mechanism

**Expected Outcomes**: Better project visibility, data-driven decisions, progress transparency

---

### [FEAT-007] Team Series View
**Status**: 🎯 Ready to Execute | **Effort**: 4-6 hours | **Impact**: Historical performance tracking and analysis
**Dependencies**: Match history (completed), Player data system (completed) | **Strategic Value**: Season-by-season analysis, trend identification

**Problem Statement**:
Users need a way to view their team's historical performance across multiple seasons (series in Hattrick terminology). Currently, the match and player history views show individual matches and player records, but there's no unified "Series" or "Seasons" view that aggregates team performance by season. This would allow managers to:
- Compare performance across different seasons
- Track team progression and improvement over time
- Identify seasonal patterns and trends
- View season-specific statistics and achievements
- Analyze peak performance periods

**Implementation**:
1. **Series Data Retrieval** (1-1.5 hours):
   - Fetch team season/series data from Hattrick via CHPP API
   - Extract season identifiers and timeframes
   - Retrieve season-specific match records and statistics
   - Build series aggregation from existing match history data

2. **Series Overview Tab** (1.5-2 hours):
   - Create new "Series" view/tab under team section (similar to Players, Training, Matches tabs)
   - Display list of all seasons with basic stats: Games Played, Wins/Draws/Losses, Goals For/Against
   - Show season dates and league/division information
   - Implement season selection for detailed view
   - Add sorting by season, performance, etc.

3. **Series Details View** (1-1.5 hours):
   - Show comprehensive statistics for selected season:
     - Full match history for that season
     - Top scorers for season
     - Best defensive performance
     - Average team rating
     - Position in league/cup standings if available
   - Display player availability/injuries during season
   - Show significant events (transfers, key matches)

4. **Visualization & Analysis** (0.5-1 hour):
   - Charts showing performance trends (wins/draws/losses by season)
   - Goals for/against comparison across seasons
   - Rating progression through season
   - Season-to-season comparison visualizations

**Acceptance Criteria**:
- Series tab visible in team view navigation
- All seasons displayed with key statistics
- Series detail view shows comprehensive season statistics
- Season-to-season comparison available
- Mobile-responsive layout
- Performance data accurately aggregated
- Matches historical Hattrick season terminology
- Works with multi-team support (each team's series shown separately)

**Scope**:
- **Includes**: Season overview, season details, statistics aggregation, visualizations, season comparison
- **Excludes**: Predictions or forecasting, deep tactical analysis (separate from match analysis)
- **Focus**: Historical performance tracking and trend analysis

**Technical Approach**:
- Query CHPP team API for series/season data
- Aggregate match records by season (use match dates to group)
- Use existing Match and MatchPlay tables, group by season identifier
- Create series aggregation queries in models/routes
- Visualize with Chart.js or Recharts
- Store series metadata for efficient access

**Expected Outcomes**: Enhanced team analysis capabilities, better performance tracking over time, improved decision-making based on historical trends, competitive advantage through seasonal analysis

---

### [FEAT-001] Data Visualization Features
**Status**: 🎯 Ready to Execute | **Effort**: 12-15 hours | **Impact**: User experience
**Dependencies**: Core functionality stability | **Strategic Value**: Data insights, competitive advantage

**Implementation**:
1. Enhance Chart.js integration for advanced visualizations
2. Add interactive dashboard capabilities
3. Implement data export and sharing features
4. Create customizable chart configurations

**Acceptance Criteria**:
- Advanced visualization options
- Interactive dashboard functionality
- Data export capabilities

**Expected Outcomes**: Enhanced user experience, better data insights, competitive differentiation

---

### [UI-004] Bulk Player Group Editor
**Status**: 🎯 Ready to Execute | **Effort**: 3-4 hours | **Impact**: Workflow optimization
**Dependencies**: Player management system (completed) | **Strategic Value**: Improved user efficiency

**Problem Statement**:
When managing a team with 20+ players, reassigning multiple players to different groups (e.g., "Formation 1", "Reserves", "Youth Development") requires clicking individual player edit buttons. A bulk edit feature with checkboxes would allow users to:
- Select multiple players at once
- Change all selected players' groups simultaneously
- Save time on repetitive team organization tasks
- Improve workflow efficiency for team managers

**Implementation**:
1. **UI Components** (1-1.5 hours):
   - Add checkboxes to player list rows
   - Add "Select All" / "Deselect All" buttons
   - Create bulk action toolbar (appears when items selected)
   - Add group dropdown selector in toolbar

2. **State Management** (0.5-1 hour):
   - Track selected player IDs in component state
   - Handle checkbox change logic
   - Manage selection count display

3. **Backend API** (1-1.5 hours):
   - Create bulk update endpoint: `PUT /api/players/bulk-update`
   - Validate group assignments
   - Update all selected players' groups atomically
   - Return success/error response

4. **User Feedback** (0.5 hour):
   - Toast notification on successful bulk update
   - Error handling for failed updates
   - Confirmation dialog before applying bulk changes

**Acceptance Criteria**:
- Checkboxes appear on all player list rows
- "Select All" functionality works correctly
- Bulk action toolbar appears/disappears appropriately
- Group dropdown allows selection of any valid group
- Bulk update applies to all selected players
- Confirmation dialog prevents accidental bulk changes
- Success/error messages displayed to user
- Mobile-responsive design maintained

**Expected Outcomes**: Faster team organization, reduced clicks for bulk operations, improved user experience

---

### [UI-005] Player Table Filtering
**Status**: 🎯 Ready to Execute | **Effort**: 4-6 hours | **Impact**: Data discovery and analysis
**Dependencies**: Player table UI (completed) | **Strategic Value**: Improved workflow efficiency

**Problem Statement** (Feature request from June 2020):
The player table currently supports sorting but lacks filtering capabilities. Users need to be able to filter players by multiple criteria (skill levels, age, status, group, position) to:
- Quickly find players matching specific criteria
- Identify potential lineup candidates based on skill thresholds
- Discover training opportunities and development gaps
- Manage and organize players more efficiently across groups
- Plan tactics and formations based on available skill pools

**Implementation**:
1. **Filter Controls** (1.5-2 hours):
   - Add filter bar above player table with multiple filter options
   - Filters: Skill ranges (keeper, defender, playmaker, etc.), Age range, Status, Group, Position
   - Searchable dropdowns for group and position selection
   - Range sliders for skill levels and age
   - "Reset Filters" button to clear all selections

2. **Filter Logic** (1-1.5 hours):
   - Implement client-side filtering for instant feedback
   - Support multiple simultaneous filters (AND logic)
   - Preserve sort order when filtering applied
   - Display count of filtered results vs total players

3. **State Management** (0.5-1 hour):
   - Store filter state in URL query parameters for bookmarkable searches
   - Persist filter preferences in localStorage (optional)
   - Handle filter updates efficiently

4. **UI/UX Polish** (1-1.5 hours):
   - Visual indication of active filters
   - Clear filter badge showing count of active criteria
   - Responsive design for mobile/tablet
   - Accessibility: ARIA labels for filter controls

**Acceptance Criteria**:
- Filter controls appear above player table with intuitive UI
- Multiple filters can be applied simultaneously
- Results update instantly as filters change
- Filtered count displayed (e.g., "Showing 12 of 23 players")
- Sort order persists when filters applied
- Reset filters button works correctly
- Filter state preserved in URL for sharing/bookmarking
- Mobile-responsive design maintained
- All filter types work correctly (skills, age, status, group, position)

**Filter Types Supported**:
- **Skill Ranges**: Separate sliders for each of 7 core skills (0-20 scale)
- **Age Range**: Min/max age selector
- **Status**: Dropdown (Active, Injured, Sold, etc.)
- **Group**: Multi-select from user-defined groups
- **Position**: Multi-select from field positions
- **Search**: Text search on player name/number

**Expected Outcomes**: Faster player discovery, easier tactical planning, improved team management workflow

---

### [UI-006] Transfer Bid Display
**Status**: 🎯 Ready to Execute | **Effort**: 2-3 hours | **Impact**: Transfer market visibility
**Dependencies**: CHPP API (pychpp 0.2.11+, completed) | **Strategic Value**: Real-time transfer information

**Problem Statement** (Feature request from June 2020):
Users need to see current bids on players they've listed for transfer/sale directly in the player table. Currently, they must:
- Navigate to transfer market separately
- Find their listed players manually
- Check bids elsewhere in the interface

A new column showing current bids would allow users to:
- Monitor transfer activity at a glance
- Make quick decisions about bid acceptance
- Track selling opportunities in the player management view
- Improve transfer workflow efficiency

**Historical Context**:
- Requested June 23, 2020 (GitHub issue #27)
- Required additional CHPP API data that wasn't available
- Blocked until pychpp 0.2.11 fix was released (January 13, 2021)
- Now unblocked and ready to implement

**Implementation**:
1. **Backend API Integration** (0.5-1 hour):
   - Add transfer/bid data retrieval from CHPP API (pychpp 0.2.11+)
   - Fetch current bids for players listed for sale
   - Cache bid data with appropriate TTL (e.g., 10-15 minutes)
   - Handle players not on market gracefully (null/empty display)

2. **Data Processing** (0.5 hour):
   - Match player IDs to transfer listings
   - Extract current bid amount and bidding team
   - Format bid information for display
   - Handle multiple bids/countries

3. **UI Implementation** (1-1.5 hours):
   - Add "Current Bid" column to player table
   - Display bid amount and team name (if available)
   - Show "Not listed" or empty for players without active bids
   - Add tooltip with bid details (amount, bidding team, deadline)
   - Sort capability on bid column

**Acceptance Criteria**:
- "Current Bid" column appears in player table (optional column, can be toggled)
- Shows bid amount for players listed for transfer
- Displays bidding team name when available
- Shows "Not listed" or empty for players not on market
- Bid data updates with API calls
- Column sortable by bid amount
- Mobile-responsive design maintained
- No performance degradation

**UI Considerations**:
- Column position: Near the end of table (after group, before actions)
- Display format: Currency amount + team name (e.g., "€150,000 - Hamburg")
- Conditional formatting: Highlight rows with active bids?
- Refresh: Auto-update when transfer data is fetched

**Technical Notes**:
- Requires pychpp 0.2.11+ (already available as of January 2021)
- CHPP transfer data only reflects bids from public transfer market
- Bid data may have slight delay from Hattrick interface

**Expected Outcomes**: Improved transfer market visibility, faster decision-making for selling players, better integration of transfer activities

---

### [UI-007] Update Report Icon Display
**Status**: 🎯 Ready to Execute | **Effort**: 2-3 hours | **Impact**: Change visualization and readability
**Dependencies**: Update/change report UI (completed) | **Strategic Value**: Better visual communication of important changes

**Problem Statement** (Feature request from June 2020, GitHub issue #37):
The update/change report currently displays player changes as text (e.g., "cards 1->0", "injury band-aid"). Users need visual icon-based representation to:
- Quickly identify critical changes (red cards, injuries)
- Reduce text clutter in change reports
- Visually highlight the most important changes
- Make important stats/changes more prominent

**Historical Context**:
- Requested June 28, 2020
- Partially implemented in January 2021 (commit 6cbfcf7)
- Current implementation shows icons for red cards and injuries
- Enhancement requested: Make important changes bold/larger, improve visual hierarchy

**Implementation**:
1. **Icon Display** (0.5-1 hour):
   - Display red card icon instead of text (🟥 or red card icon)
   - Display injury icon instead of text (⚕️ or band-aid icon)
   - Only show red cards (not yellow), only show real injuries (not band-aids)
   - Use consistent icon set throughout application

2. **Visual Hierarchy** (1-1.5 hours):
   - Make main stat changes bold or larger font
   - Highlight trained/developed skills with emphasis
   - Differentiate critical changes (red card, injury) from minor changes
   - Use color coding for different change types
   - Add visual spacing and grouping for readability

3. **UI Refinement** (0.5 hour):
   - Ensure icons are accessible (alt text, tooltips)
   - Maintain responsive design
   - Test readability across device sizes
   - Ensure icons are color-blind friendly

**Acceptance Criteria**:
- Red card changes display with icon (not text)
- Injury changes display with icon (not text)
- Yellow cards NOT shown as icons (red cards only)
- Band-aids NOT shown as icons (injuries only)
- Main stat changes (trained) displayed bold or larger
- Important changes visually distinguished from minor ones
- Tooltips explain what each icon represents
- Mobile-responsive display maintained
- No layout breaks due to icon display

**Icon Usage**:
- **Red Card**: 🟥 or card icon (when red card given)
- **Injury**: ⚕️ or medical icon (when player injured)
- **Trained**: Bold/larger text for skill increases (main training)
- **Stats**: Regular text for minor changes

**Visual Hierarchy Examples**:
- "**Defender 14→15** ⚕️ Injured" (main change + critical status)
- "Keeper 12→13" (secondary improvement, regular text)
- "Passing 8→9 🟥 Red card" (with penalty/disciplinary info)

**Expected Outcomes**: Improved change report readability, faster identification of critical player updates, better visual communication of update data

---

### [FEAT-006] Default Player Groups for New Users
**Status**: 🎯 Ready to Execute | **Effort**: 2-3 hours | **Impact**: Onboarding and user experience
**Dependencies**: Player grouping system (completed) | **Strategic Value**: Reduced onboarding friction, improved adoption

**Problem Statement** (Feature request from Oct 16, 2023, GitHub issue #52):
New users starting with HT Status have a blank slate with no player groups, making it difficult to understand:
- What groups are and how to use them
- How to organize their squad effectively
- How to get started quickly with the application

The threshold for understanding what to do and making the interface useful is too high. Default groups would lower the barrier to entry and help new users:
- Get started immediately without confusion
- Understand the grouping system by example
- Have a structured team organization from day one
- Improve time-to-value for new users

**Implementation**:
1. **Default Group Templates** (0.5-1 hour):
   - Create sensible default groups on new user registration
   - Suggested defaults: "Formation 1", "Substitutes", "Youth", "Development", "For Sale"
   - Alternative approach: Groups based on common strategies (e.g., "Starters", "Bench", "Prospects")
   - Allow users to customize defaults in settings (future enhancement)

2. **Automatic Group Assignment** (0.5-1 hour):
   - On first team import, suggest automatic assignment of players to groups
   - Based on match role, age, or player status
   - Allow user to review and modify assignments
   - Manual override of automatic suggestions

3. **Onboarding Enhancement** (1 hour):
   - Show tooltip/hint explaining groups on first visit
   - Highlight default groups in UI
   - Link to help documentation explaining group usage
   - Optional guided tour (future enhancement)

**Acceptance Criteria**:
- New users automatically receive default player groups on registration
- Default groups are sensible and useful for common use cases
- Group names are clear and self-explanatory
- Users can view and modify default groups
- Users can delete default groups if desired
- Existing users unaffected (no retroactive group creation)
- Default groups appear in group dropdown/selector
- Help text explains purpose of each default group
- Mobile-responsive interface maintained

**Suggested Default Groups**:
1. **Formation 1** - Current starting lineup
2. **Formation 2** - Alternative tactics/formation
3. **Substitutes** - Backup players
4. **Youth** - Young development players
5. **Development** - Players being trained/improved
6. **For Sale** - Players listed for transfer

**Alternative Approach** (based on team size):
- Small teams (0-20 players): Simplified defaults ("Starters", "Subs", "Youth")
- Larger teams (20+ players): Full defaults with more categories

**User Customization** (Phase 2, future):
- Allow users to choose default group templates on signup
- Pre-built templates: "Competitive", "Development", "Minimal", "Advanced"
- Custom group templates created by experienced users

**Technical Implementation**:
- Create database seeding for default groups
- Trigger on first user/team registration
- Handle existing users gracefully (no changes)
- Provide admin/management option to reset to defaults

**Expected Outcomes**: Reduced onboarding friction, faster time-to-value, improved user adoption, better first-time user experience

---

### [FEAT-004] Hattrick Language Localization
**Status**: 🎯 Ready to Execute | **Effort**: 4-6 hours | **Impact**: User experience and accessibility
**Dependencies**: CHPP API integration (completed) | **Strategic Value**: Multi-language support, consistency with Hattrick

**Problem Statement**:
Currently, HT Status displays content in English regardless of the user's language preference in their Hattrick account. Users need the application to use Hattrick's official translations from their CHPP translation files to:
- Maintain consistency with Hattrick's UI language
- Provide native language experience matching their account setting
- Reuse existing, professionally maintained translations
- Support a global user base across different regions

**Implementation**:
1. **Extract Language from Hattrick** (1 hour):
   - Retrieve user's language preference from CHPP `user()` response
   - Store language preference in session on user login
   - Map language code to supported language

2. **Integrate Hattrick Translation Files** (1.5-2 hours):
   - Access Hattrick's translation files via CHPP API (if available) or documentation
   - Parse Hattrick translation strings for supported languages
   - Create translation mapping for common UI terms
   - Build fallback structure for untranslated terms

3. **Apply Translations to Templates** (1.5-2 hours):
   - Update Flask templates to use Hattrick translations
   - Translate UI strings (buttons, labels, messages, form placeholders)
   - Handle common team management terminology
   - Apply locale-specific formatting (dates, numbers)

4. **Scope & Supported Languages**:
   - Languages available in Hattrick translation system
   - Primary focus: Swedish, English, German, French, Finnish, Norwegian
   - Use Hattrick's official terminology for consistency

**Acceptance Criteria**:
- User's Hattrick language preference is detected on login
- Flask templates display strings using Hattrick translations
- All supported languages properly mapped and displayed
- Date and number formatting respects user's language/locale
- Fallback to English for untranslated strings
- No breaking changes to existing functionality
- UI terminology matches Hattrick's official translations

**Scope Notes**:
- **Includes**: UI strings, buttons, labels, form messages using Hattrick translations
- **Excludes**: Player/team data from Hattrick (already in user's language), custom app-specific strings
- **Focus**: Reusing Hattrick's existing translation infrastructure

**Technical Approach**:
- Retrieve translations from CHPP translation files documentation
- Create mapping dictionary for common UI terms
- Apply translations in Jinja2 templates
- Store mapping in configuration for easy updates

**Expected Outcomes**: Consistent experience with Hattrick, improved user experience for non-English speakers, reduced language barrier for international adoption

---

### [RESEARCH-001] Additional Integrations
**Status**: 🔮 Future Research | **Effort**: Variable | **Impact**: Feature expansion
**Dependencies**: Core functionality maturity | **Strategic Value**: Ecosystem integration

**Research Areas**:
1. Additional sports data APIs
2. Social features and team collaboration
3. Advanced analytics and predictions
4. Third-party service integrations

**Expected Outcomes**: Expanded feature set, increased user value, competitive advantages

---

## Task Details: Security & Maintenance (Added from REFACTOR-002 Review)

### [SECURITY-001] Werkzeug Security Update
**Status**: 🎯 Ready to Execute | **Effort**: 30-45 minutes | **Priority**: P3 Stability
**Dependencies**: None | **Strategic Value**: Security compliance, dependency maintenance

**Problem Statement**:
Safety scan identified 4 CVE vulnerabilities in Werkzeug 2.3.8:
- CVE-2024-49767: Resource exhaustion when parsing file data in forms
- CVE-2024-49766: Path Traversal (CWE-22) on Windows systems with Python < 3.x
- CVE-2025-66221: Denial of Service (DoS) due to improper handling of Windows special characters
- CVE-2024-34069: Debugger vulnerability allowing unauthorized access

**Implementation**:
1. **Update Dependencies** (15-20 min):
   - Update pyproject.toml to require `werkzeug>=3.1.4`
   - Run `uv sync` to update lockfile
   - Test application startup and basic functionality

2. **Validation** (10-15 min):
   - Run security scan to verify vulnerabilities resolved
   - Execute test suite to ensure no breaking changes
   - Update any deprecated Werkzeug API usage if needed

**Acceptance Criteria**:
- Werkzeug updated to 3.1.4 or later
- All 4 CVE vulnerabilities resolved in safety scan
- Test suite passes without Werkzeug-related failures
- Application starts and functions normally

**Expected Outcomes**: Eliminated security vulnerabilities, improved dependency health

### [DEVOPS-001] Script Linting Cleanup
**Status**: 🎯 Ready to Execute | **Effort**: 1-2 hours | **Priority**: P5 DevOps
**Dependencies**: None | **Strategic Value**: Code quality consistency

**Problem Statement**:
Linting scan identified 32 errors in test files (production code is lint-free):
- ARG001: Unused function arguments (7 instances) - test fixtures with unused `app` parameter
- F841: Local variable assigned but never used (5 instances) - response variables in blueprint auth tests

**Implementation**:
1. **Unused Test Fixture Parameters** (45-60 min):
   - tests/test_blueprint_player.py: Remove unused `app` parameters from sample_user, sample_players fixtures
   - tests/test_blueprint_routes_focused.py: Fix unused `app` parameter in sample_user fixture
   - tests/test_chpp_integration.py: Remove unused `mock_chpp_response` parameter
   - tests/test_database.py: Remove unused `db_session` parameter

2. **Unused Variables Cleanup** (15-30 min):
   - tests/test_blueprint_auth.py: Remove or use response variables in login tests (lines 169, 187, 210)
   - Apply appropriate fix: either use the variable or remove assignment

**Acceptance Criteria**:
- All 32 linting errors resolved
- Tests maintain full functionality and coverage
- No test behavior changes
- No new linting errors introduced

**Expected Outcomes**: Consistent code quality across entire project, improved maintainability

---

### [UPGRADE-001] Re-upgrade to pychpp 0.5.10 + Flask 3.1+ + werkzeug 3.1+
**Status**: 🔮 Future Task | **Effort**: 2-3 hours | **Priority**: P7 | **Impact**: Access to latest library features and bug fixes
**Dependencies**: BUG-001 team ID fix (completed) | **Strategic Value**: Stay current with library ecosystem

**Problem Statement**:
During BUG-001 investigation, we downgraded from pychpp 0.5.10 → 0.3.12, Flask 3.1.2 → 2.3.3, and werkzeug 3.1.5 → 2.3.8 because player skills were displaying as 0. However, the root cause was a logic bug in auth.py (using user ID 182085 instead of team ID 9838), not library incompatibility. Now that the team ID bug is fixed, the newer library versions should work correctly.

**Why Consider Re-upgrading**:
- pychpp 0.5.10 has newer features and bug fixes compared to 0.3.12
- Flask 3.1+ provides security updates and modern features
- werkzeug 3.1+ has performance improvements and bug fixes
- Staying on older versions accumulates technical debt
- The downgrade may have been unnecessary (bug existed in both versions)

**Why It's P7 (Low Priority)**:
- Current versions (0.3.12, 2.3.3, 2.3.8) are working correctly
- "If it ain't broke, don't fix it" principle applies
- Re-upgrade introduces risk of new compatibility issues
- Limited immediate benefit since functionality is stable
- Other P0-P6 tasks provide more value

**Implementation** (if attempted):
1. **Backup Current State** (15 min):
   - Create git branch for upgrade attempt
   - Document current working versions
   - Note any version-specific workarounds in code

2. **Upgrade Libraries** (30 min):
   - Update pyproject.toml: pychpp==0.5.10, flask>=3.1.0, werkzeug>=3.1.4
   - Run `uv sync` to update dependencies
   - Check for dependency conflicts

3. **Test Compatibility** (45-60 min):
   - Run full test suite: `make test-all`
   - Test player data import: /update route
   - Verify all skills display correctly (team 9838)
   - Test OAuth and password login flows
   - Check all routes still work

4. **Fix Any Issues** (30-45 min):
   - Address API changes in pychpp 0.5.10
   - Fix any Flask/werkzeug compatibility issues
   - Update code if API patterns changed
   - Re-test after fixes

**Acceptance Criteria**:
- All tests pass (100% success rate maintained)
- Player skills display correctly for all teams
- OAuth and password authentication work
- No regressions in existing functionality
- All routes accessible and functional
- Data import from CHPP API works correctly

**Rollback Plan**:
- If issues arise, revert to current versions: 0.3.12, 2.3.3, 2.3.8
- Current configuration is proven stable
- No pressure to complete upgrade

**Expected Outcomes**: Access to latest library features, improved security posture, reduced technical debt accumulation, OR confirmation that current versions are best choice for stability

---

### [FEAT-009] Trophy Data Integration
**Status**: 🔮 Future Task | **Effort**: 6-8 hours | **Priority**: P7 | **Impact**: User engagement

**Problem Statement**:
Stats page was designed to display team trophies and achievements, but current pyCHPP version doesn't expose trophy data through the API. Need to implement trophy display when library support becomes available or find alternative data source.

**Current State**:
- Stats page template has trophy display section ready
- Competition status fallback implemented (jerseys, league, cup, power rating)
- Debug investigation confirmed pyCHPP v0.x lacks trophy attribute
- React Analytics page has trophy display capability

**Acceptance Criteria**:
- [ ] Research if newer pyCHPP versions support trophy data
- [ ] Investigate alternative CHPP API endpoints for trophy/achievement data
- [ ] Implement trophy data fetching when source identified
- [ ] Connect to existing template trophy display section
- [ ] Add historical achievement tracking
- [ ] Test with teams that have trophy history

**Implementation Notes**:
- Check pyCHPP GitHub for updates or feature requests
- May require direct CHPP XML file parsing if library unsupported
- Consider storing trophy data in database for historical tracking
- Template already structured for season, level, division, date display

**Technical Context**:
- Current implementation: app/blueprints/matches.py stats() route
- Template: app/templates/stats.html
- Competition info extraction working as reference pattern

---

### [REFACTOR-004] Replace pyCHPP Dependency
**Status**: 🔮 Research & Planning | **Effort**: 16-24 hours | **Priority**: P7 Future
**Dependencies**: CHPP API documentation research, REFACTOR-001 completion | **Strategic Value**: Long-term dependency independence, custom optimization

**Problem Statement**:
The application currently depends on the third-party `pychpp` library for Hattrick CHPP API integration. This creates several maintenance and control issues:
- External dependency maintenance burden and update compatibility
- Limited control over API interaction patterns and error handling
- Potential for library abandonment or breaking changes
- Inability to optimize for HTStatus-specific use cases
- Testing complexity with external library mocking

**Research Phase** (Required before implementation):
1. **CHPP API Documentation Analysis** (4-6 hours):
   - Study official Hattrick CHPP API documentation and endpoints
   - Document all currently used API calls and response formats
   - Identify authentication flows (OAuth 1.0) and session management
   - Map pychpp functionality to raw API calls

2. **Reference Implementation Analysis** (2-3 hours):
   - **lucianoq/hattrick** (Go): Clean OAuth 1.0 implementation with structured API calls
     - Uses mrjones/oauth library for authentication
     - XML parsing with Go structs and xml tags
     - Modular file structure: `/chpp/` (data models), `/api/` (endpoints), `/parsed/` (XML handling)
     - Clear separation: Raw API → Parsed XML → Typed objects
   - **pychpp** (Python): Comprehensive Python framework with 57/57 CHPP files supported
     - Two-layer architecture: XML models (`/xml/`) and Custom models (`/custom/`)
     - OAuth authentication with request/access token flow
     - HTProxyField pattern for selective data parsing
     - Consistent interface: `chpp.user()`, `chpp.team(id)`, `chpp.player(id)`

3. **Current Usage Audit** (2-3 hours):
   - Catalog all pychpp usage across application (routes, auth, updates)
   - Document expected data structures and transformation logic
   - Identify error handling patterns and retry mechanisms
   - Assess testing requirements and mock strategies

4. **Architecture Design** (2-4 hours):
   - Design custom CHPP client class structure based on reference implementations
   - Plan OAuth 1.0 authentication pattern (similar to Go implementation)
   - Design response parsing and data transformation (XML → Python objects)
   - Plan backward compatibility during transition (identical interface to pychpp)

**Implementation Phases** (Post-research):
1. **Core CHPP Client** (4-6 hours):
   - OAuth 1.0 authentication implementation (request_token → access_token flow)
   - HTTP request handling with proper error handling and retry logic
   - XML response parsing with lxml or xml.etree
   - Base client class with standard CHPP API patterns

2. **Data Models** (3-4 hours):
   - User, team, player, match data structures matching pychpp interface
   - XML to Python object mapping (similar to Go struct tags)
   - Implement consistent object interface (user(), team(id), player(id))
   - Add navigation between objects (team.players, player.team, etc.)

3. **Integration & Migration** (4-6 hours):
   - Replace pychpp calls throughout application with custom client
   - Maintain identical interface for zero breaking changes
   - Add improved error handling and logging
   - Ensure session management and OAuth token handling

4. **Testing & Validation** (3-4 hours):
   - Comprehensive test coverage without external dependencies
   - Mock CHPP responses for reliable testing
   - Performance validation against pychpp
   - Integration testing with real CHPP API

**Acceptance Criteria**:
- Custom CHPP client with identical interface to pychpp for seamless replacement
- All current functionality maintained (authentication, data fetching, updates)
- Improved error handling and logging for debugging
- Comprehensive test coverage without external dependencies
- Performance equal or superior to pychpp
- Documentation for custom CHPP client usage and maintenance
- OAuth 1.0 authentication flow properly implemented
- XML parsing with proper data type conversion
- Consistent object navigation patterns

**Implementation Insights from Research**:
- **Authentication**: Both implementations use OAuth 1.0 with request_token/access_token flow
- **Architecture**: Clear separation between raw API, XML parsing, and typed objects
- **Error Handling**: Proper CHPP error code parsing and custom exceptions
- **Modularity**: File-per-API approach (lucianoq) vs unified client (pychpp)
- **Data Models**: XML tags drive object structure with type conversion

**Expected Outcomes**: Eliminated external dependency, improved control and maintainability, enhanced testing capability



---

## Task Details: New Tasks

---

### [INFRA-021] Quality Intelligence Platform Documentation
**Status**: 🎯 Ready to Execute | **Effort**: 1-2 hours | **Priority**: P1 | **Impact**: Strategic milestone recognition, documentation accuracy
**Dependencies**: Quality Intelligence Platform implementation (completed) | **Strategic Value**: Strategic communication, project visibility

**Problem Statement**:
The successful Quality Intelligence Platform implementation represents a major strategic achievement that needs proper documentation and recognition:
- Contrarian "look-outside-the-box" approach transformed dual coverage report confusion into competitive advantage
- 140+ line Makefile modularized into professional 21-line orchestration + 116-line quality assessment script
- Multi-dimensional quality analysis provides deployment confidence scoring
- Innovation documented in [.project/innovation-testing-intelligence.md](.project/innovation-testing-intelligence.md)
- Progress.md needs updating to reflect this P3 completion and strategic milestone

**Strategic Value**:
- Demonstrates innovative problem-solving approach (transformation vs. removal)
- Provides template for future "look-outside-the-box" opportunities
- Establishes quality intelligence as competitive advantage
- Shows progression from P3 stability towards advanced quality analysis

**Implementation**:
1. **Progress Documentation Update** (0.5-1 hour):
   - Mark Quality Intelligence Platform as completed milestone in progress.md
   - Update P3 Stability progress (9/9 tasks now complete with this + TEST-007)
   - Add strategic analysis of contrarian approach success
   - Document deployment confidence scoring capability

2. **Strategic Milestone Recognition** (0.5-1 hour):
   - Add Quality Intelligence Platform to major achievements section
   - Document innovation methodology for future reference
   - Update project metrics to reflect enhanced quality analysis
   - Note transition from dual coverage confusion to strategic advantage

**Acceptance Criteria**:
- Progress.md accurately reflects Quality Intelligence Platform completion
- P3 Stability section updated with final task completion status
- Strategic milestone properly documented with implementation approach
- Innovation methodology captured for future "look-outside-the-box" opportunities
- Documentation clearly communicates the contrarian transformation approach

**Expected Outcomes**: Accurate project documentation, strategic milestone recognition, innovation methodology template

---

### [TEST-004] Blueprint Test Coverage
**Status**: 🎯 Ready to Execute | **Effort**: 3-4 hours | **Priority**: P3 | **Impact**: Quality assurance and maintainability
**Dependencies**: REFACTOR-006 Routes Code Consolidation (✅ completed) | **Strategic Value**: Validation of blueprint architecture

**Problem Statement**:
Recent blueprint migration (REFACTOR-002 and REFACTOR-006) created new code organization but test coverage dropped to 35% (target: 80%). The new blueprint modules need comprehensive test coverage to ensure:
- Blueprint route functionality works correctly
- Authentication and session handling is reliable
- Error handling and edge cases are covered
- Regression prevention for future changes

**Current State**:
- Fast test coverage: 35% (significantly below 80% target)
- Blueprint modules with low coverage:
  - app/blueprints/auth.py: 20% coverage
  - app/blueprints/main.py: 12% coverage
  - app/blueprints/matches.py: 19% coverage
  - app/blueprints/player.py: 12% coverage
  - app/blueprints/team.py: 11% coverage
  - app/blueprints/training.py: 11% coverage

**Implementation**:
1. **Test Coverage Analysis** (0.5 hours):
   - Run detailed coverage report for blueprint modules
   - Identify critical code paths requiring tests
   - Map existing test coverage and gaps
   - Prioritize high-impact, low-coverage areas

2. **Blueprint Route Testing** (1.5-2 hours):
   - Test all blueprint route handlers with various authentication states
   - Mock CHPP API responses for data-dependent routes
   - Test session management and team selection functionality
   - Verify template rendering with proper context variables

3. **Error Handling and Edge Cases** (1-1.5 hours):
   - Test unauthenticated access patterns
   - Test invalid team IDs and malformed requests
   - Test database connection issues and recovery
   - Test CHPP API failure scenarios

4. **Integration Testing** (0.5-1 hour):
   - Test blueprint registration and initialization
   - Test cross-blueprint functionality
   - Verify utils module integration works correctly
   - Test application startup with all blueprints

**Acceptance Criteria**:
- Blueprint module coverage increases to >70%
- All blueprint routes have basic functionality tests
- Authentication and session handling tested
- Error scenarios properly covered
- make test-fast achieves >80% overall coverage
- No existing functionality regressions
- Mock CHPP responses for isolated testing

**Technical Approach**:
- Extend existing test_blueprint_routes_focused.py
- Use pytest fixtures for authentication setup
- Mock CHPP API calls for deterministic testing
- Leverage existing test infrastructure and patterns

**Expected Outcomes**: Increased confidence in blueprint architecture, prevention of regressions, achievement of coverage targets

---

### [TEST-005] Utils Module Test Coverage
**Status**: 🎯 Ready to Execute | **Effort**: 2-3 hours | **Priority**: P3 | **Impact**: Validation of utility function migration
**Dependencies**: REFACTOR-006 Routes Code Consolidation (✅ completed) | **Strategic Value**: Confidence in shared utilities

**Problem Statement**:
The newly created app/utils.py module (300+ lines) contains critical shared utilities migrated from routes.py and routes_bp.py. Currently showing only 13% test coverage, these functions need validation to ensure:
- Utility functions work correctly after migration
- No regressions in shared functionality
- Proper integration with blueprint modules
- Edge cases and error conditions handled

**Current State**:
- app/utils.py: 13% coverage (151/151 statements, 125 missed)
- Critical functions with no test coverage:
  - calculateContribution(), calculateManmark() - core business logic
  - player_diff(), get_training() - data processing
  - create_page() - template rendering
  - dprint(), debug_print() - debugging utilities

**Implementation**:
1. **Function Coverage Analysis** (0.5 hours):
   - Analyze which utility functions are tested vs untested
   - Identify high-risk functions needing immediate coverage
   - Map function dependencies and integration points
   - Review existing tests that might cover utility usage

2. **Core Business Logic Testing** (1-1.5 hours):
   - Test calculateContribution() with various positions and player skills
   - Test calculateManmark() calculations and edge cases
   - Test player skill calculation and rating functions
   - Validate team statistics computation functions

3. **Data Processing Function Testing** (0.5-1 hour):
   - Test player_diff() with various time periods
   - Test get_training() with different player data sets
   - Test date utilities (diff_month, diff) with edge cases
   - Test data filtering and transformation functions

4. **Template and Utility Testing** (0.5-1 hour):
   - Test create_page() with various template contexts
   - Test debug print functions (dprint, debug_print)
   - Test utility initialization (initialize_utils)
   - Verify proper integration with Flask app context

**Acceptance Criteria**:
- Utils module coverage increases to >70%
- All core business logic functions tested
- Data processing functions have comprehensive tests
- Template utilities tested with mock contexts
- Debug utilities tested for proper output
- No regressions in functionality
- Integration with blueprints verified

**Technical Approach**:
- Create dedicated test_utils.py module
- Mock Flask app context for template testing
- Use sample player data for business logic tests
- Mock database queries for data processing tests

**Expected Outcomes**: Validated utility function reliability, increased confidence in shared code, prevention of silent failures

---

### [DOC-023] Clean TECHNICAL.md Obsolete Content
**Status**: 🎯 Ready to Execute | **Effort**: 1-2 hours | **Priority**: P6 | **Impact**: Documentation clarity
**Dependencies**: REFACTOR-007 (✅ completed) | **Strategic Value**: Accurate technical documentation

**Problem Statement**:
TECHNICAL.md contains extensive outdated information about route architecture that contradicts the current system:
- **Line 22**: "Dual registration system with functional routes in routes.py and blueprint organization in routes_bp.py" - routes.py no longer exists
- **Lines 30-55**: Entire "Route Ownership Strategy" section describes BUG-001 resolution and "dual registration" - this is historical context, not current architecture
- **Line 58**: "/app/routes.py: Main Flask app logic" - file no longer exists
- Multiple references to "blueprint stubs", "functional routes", "route conflicts" - all resolved by REFACTOR-007

**Current Impact**:
- New developers receive incorrect architecture information
- Documentation describes non-existent files and patterns
- Historical troubleshooting information obscures current design
- Wastes developer time following outdated guidance

**Implementation**:
1. **Remove Obsolete Route Architecture Section** (30 min):
   - Delete or compress "Route Ownership Strategy" section (lines 30-55)
   - If kept for history, move to a brief "Historical Note" subsection
   - Update "Route Architecture" bullet to describe current blueprint-only design

2. **Update File Structure Section** (15 min):
   - Remove `/app/routes.py` reference (line 58)
   - Add `/app/constants.py` - Hattrick data definitions
   - Add `/app/factory.py` - Application factory with blueprint registration
   - Update `/app/utils.py` description to reflect enhanced functionality

3. **Clean Implementation Details** (30 min):
   - Update "Route Architecture" in line 22 to reflect blueprint-only design
   - Remove references to "dual registration", "route conflicts", "blueprint stubs"
   - Add brief note: "Previously used monolithic routes.py (removed January 2026)"
   - Focus content on current architecture, not migration history

4. **Verify Consistency** (15 min):
   - Cross-reference with architecture.md for consistency
   - Ensure no broken internal links
   - Validate all file paths are current

**Acceptance Criteria**:
- [ ] No references to routes.py as current file
- [ ] Route architecture describes blueprint-only system
- [ ] Historical context compressed to <5 lines or removed
- [ ] File structure matches current codebase
- [ ] Technical implementation section reflects REFACTOR-007 completion
- [ ] Documentation focuses on "how it works now" not "how we got here"

**Expected Outcomes**: Clear, accurate technical documentation that helps developers understand current architecture without wading through resolved historical issues

---

### [DOC-024] Clean README.md Legacy Sections
**Status**: 🎯 Ready to Execute | **Effort**: 1 hour | **Priority**: P6 | **Impact**: New developer onboarding
**Dependencies**: None | **Strategic Value**: Clear setup instructions

**Problem Statement**:
README.md contains significant legacy content that confuses new developers:
- **Lines 315-385**: Entire "Migration from Legacy config.py" section with old setup instructions
- **Lines 350-400**: Legacy SQLAlchemy and Postgres commands using deprecated manage.py
- Mixing of "Modern Setup (UV + Docker Compose)" with "Legacy Setup (Deprecated)" creates confusion
- Old pipreqs/pip workflow instructions alongside UV instructions

**Current Impact**:
- New developers unsure which setup path to follow
- Legacy instructions no longer work with current codebase
- Mixing old and new patterns reduces confidence in documentation
- Extra reading burden to distinguish current vs historical

**Implementation**:
1. **Remove/Archive Legacy Setup Section** (20 min):
   - Delete "Legacy Setup (Deprecated)" section entirely
   - Remove pipreqs and pip install instructions
   - Keep only UV-based dependency management

2. **Clean Database Migration Instructions** (15 min):
   - Remove old `python manage.py db` commands
   - Keep only modern `make db-migrate` and `make db-upgrade` commands
   - Remove "On problems" section with deprecated stamp commands

3. **Simplify Configuration Section** (15 min):
   - Remove or significantly compress "Migration from Legacy config.py"
   - Focus on current setup: config.py.template or .env
   - Keep instructions concise and current-focused

4. **Verify Command Accuracy** (10 min):
   - Test all remaining commands work with current setup
   - Ensure no references to removed files or deprecated workflows
   - Cross-reference with Makefile help output

**Acceptance Criteria**:
- [ ] No "Legacy" or "Deprecated" sections remain
- [ ] All commands use UV or Make (no direct python/pip commands)
- [ ] Configuration instructions focus on current templates
- [ ] README length reduced by removing historical content
- [ ] All setup steps validated as current

**Expected Outcomes**: Streamlined README that confidently guides new developers through current setup without legacy distractions

---

### [DOC-025] Update architecture.md File Structure
**Status**: 🎯 Ready to Execute | **Effort**: 30 min | **Priority**: P6 | **Impact**: Architecture documentation accuracy
**Dependencies**: REFACTOR-007 (✅ completed) | **Strategic Value**: Accurate system documentation

**Problem Statement**:
architecture.md File Structure section (around line 130) still references old file organization:
- References to routes.py in file tree
- Missing app/constants.py in structure
- Blueprint organization may not reflect current state after REFACTOR-007

**Implementation**:
1. **Update File Tree** (15 min):
   - Remove routes.py from app/ directory listing
   - Add constants.py to app/ directory
   - Verify factory.py description matches current implementation
   - Update routes_bp.py description (maintained for compatibility)

2. **Verify Directory Structure** (10 min):
   - Compare documented structure with actual filesystem
   - Check all referenced files exist
   - Ensure descriptions match current functionality

3. **Add Brief Architecture Note** (5 min):
   - Add note about REFACTOR-007 completion (January 2026)
   - Brief mention of blueprint architecture completion
   - Link to progress.md or goals.md for detailed history

**Acceptance Criteria**:
- [ ] File structure matches actual filesystem
- [ ] All referenced files exist in codebase
- [ ] Blueprint architecture completion noted
- [ ] No references to removed routes.py

**Expected Outcomes**: Accurate architecture documentation that matches current codebase structure

---

### [DOC-026] Clean backlog.md Historical References
**Status**: 🎯 Ready to Execute | **Effort**: 30 min | **Priority**: P6 | **Impact**: Documentation clarity
**Dependencies**: REFACTOR-007 (✅ completed) | **Strategic Value**: Remove confusing historical context

**Problem Statement**:
backlog.md contains scattered references to resolved historical issues (BUG-001, route conflicts) that confuse current development focus:
- Line 206: Reference to `app_with_routes` fixture timing/ordering conflicts
- Lines 1916-1919: Multiple references to "dual registration", "blueprint stubs", "route conflicts"
- Line 1941: Repeated references to resolved architectural issues
- These describe historical debugging context, not current development concerns

**Current Impact**:
- Developers reading backlog get confused about current system state
- Historical troubleshooting notes appear as active concerns
- Documentation reads as "still migrating" when migration is complete
- Obscures actual current priorities

**Implementation**:
1. **Mark Historical Context** (15 min):
   - Add "Historical Note:" prefix to lines referencing BUG-001 resolution
   - Move detailed historical context to brief footnotes
   - Consider moving extensive history to .project/history/ with reference links

2. **Update Current Focus Section** (10 min):
   - Ensure Current Focus describes actual current work
   - Remove any references to "dual registration" or "route conflicts"
   - Focus on forward-looking tasks (BUG-002/003/004, CLEANUP-001)

3. **Clean Task Descriptions** (5 min):
   - Review all P0-P3 task descriptions
   - Remove historical troubleshooting references
   - Keep focus on "what to do" not "what was wrong"

**Acceptance Criteria**:
- [ ] No references to "dual registration" or "route conflicts" as current issues
- [ ] Historical context clearly marked as past resolution, not current concern
- [ ] Current Focus section describes forward-looking work only
- [ ] Task descriptions focus on implementation, not historical debugging

**Expected Outcomes**: Clear backlog that focuses on current and future work without confusing historical debugging notes

---

### [FEAT-010] Collaborative League Intelligence
**Status**: 🔮 Future Research | **Effort**: 40-60 hours | **Priority**: P7 | **Impact**: Viral growth, network effects
**Dependencies**: None (greenfield feature) | **Strategic Value**: Multiplayer platform transformation, natural viral loops

**Problem Statement**:
HTStatus currently operates as single-team management tool, but Hattrick's real competitive dynamics happen at league level. Managers in the same league could benefit from shared opponent intelligence, collective tactical analysis, and coordinated strategy - yet no tool enables this collaboration. This creates opportunity for:
- Viral growth (one user converts entire league - 10-15x multiplier)
- Network effects (each new manager increases collective data value)
- High retention (switching costs when entire league depends on platform)
- Natural monetization (free individual → paid league workspace)

**Vision**:
Transform HTStatus from single-team tool to league-wide collaborative platform where allied managers pool scouting data, share opponent insights, and collectively analyze tactical trends. "Notion for football leagues" - multiplayer by default, focused on trust-based cooperatives.

**Key Features**:
1. **League Workspaces**: Invite-based league instances with shared data
2. **Collaborative Scouting**: Crowd-sourced opponent match observations and tactical patterns
3. **Collective Analytics**: League-wide aggregate statistics and trend detection
4. **Privacy Controls**: Granular control over what data is shared vs kept private
5. **Tactical Discussions**: Lightweight comments and voting on formations/strategies

**Technical Implementation**:
- New `League` table in PostgreSQL with foreign keys to Users
- Invite system (email invitations, league code join links)
- Shared opponent scouting database (crowd-sourced match observations)
- League-wide analytics dashboards (aggregate statistics)
- Permission system (league admin, member, viewer roles)
- React components for league dashboards and collaborative UI

**Acceptance Criteria**:
- [ ] League workspace creation and invitation system
- [ ] Shared scouting database with privacy controls
- [ ] League-wide aggregate analytics dashboard
- [ ] Collaborative discussion threads on tactical decisions
- [ ] Permission system (admin/member/viewer roles)
- [ ] Viral invitation mechanics tested

**Monetization Model**:
- Solo: Free - Individual team management
- League: $4.99/manager/mo - Up to 15 managers, shared scouting
- Conference: $2.99/manager/mo - 16-30 managers, volume discount
- Championship: Custom - 30+ managers, dedicated support

**Expected Outcomes**: Viral growth through league adoption, high retention through network lock-in, natural upsell path from free to paid

---

### [FEAT-011] AI-Powered Training Optimization Engine
**Status**: 🔮 Future Research | **Effort**: 60-80 hours | **Priority**: P7 | **Impact**: Differentiation through AI insights
**Dependencies**: Significant historical player data, ML infrastructure | **Strategic Value**: Premium feature differentiation, data science moat

**Problem Statement**:
Managers currently make training decisions based on intuition and basic skill tracking, but HTStatus has rich historical time-series data on player development that could power predictive insights. Machine learning on this data could:
- Predict optimal training schedules for specific player archetypes
- Forecast skill progression trajectories based on age and current level
- Identify training inefficiencies and suggest corrections
- Provide data-driven recommendations instead of guesswork

**Vision**:
Machine learning engine analyzes historical skill progression data across all HTStatus users to predict optimal training schedules and player development trajectories. "Moneyball for Hattrick training" - data-driven decisions replace intuition.

**Key Features**:
1. **Training Schedule Optimizer**: ML recommends optimal training focus based on player age, current skills, target position
2. **Progression Forecasting**: Predict skill levels 4-12 weeks ahead based on current training
3. **Efficiency Analysis**: Identify players not progressing as expected and suggest interventions
4. **Archetype Matching**: "Your defender profiles similar to top-performing defenders who trained X"
5. **Counterfactual Analysis**: "If you'd trained passing instead of scoring, you'd be +0.5 levels ahead"

**Technical Implementation**:
- Time-series ML models (LSTM/Transformer) on player skill progression data
- Feature engineering from existing player attributes (age, skills, training history)
- Python ML stack (scikit-learn, PyTorch/TensorFlow, pandas)
- Model training pipeline (offline batch processing)
- API endpoint for inference (Flask route returning predictions)
- React dashboard for ML insights visualization
- A/B testing framework to validate prediction accuracy

**Acceptance Criteria**:
- [ ] ML model trained on historical player data with >70% accuracy
- [ ] Training schedule recommendation API endpoint
- [ ] Skill progression forecasting (4-12 week horizons)
- [ ] React UI for ML insights visualization
- [ ] Model retraining pipeline (weekly batch updates)
- [ ] A/B test framework to validate real-world accuracy

**Data Requirements**:
- Minimum 6-12 months historical player data across multiple users
- Player skill progression time-series (existing in Players table)
- Training type metadata (may need to be added to data model)
- Match performance correlation data (MatchPlay table)

**Expected Outcomes**: Premium analytics differentiation, predictable revenue through AI insights subscriptions, potential expansion to other football management games

---

*Backlog updated January 21, 2026 with FEAT-010 Collaborative League Intelligence and FEAT-011 AI-Powered Training Optimization Engine added to P7 Future Improvements. Total: 28 active tasks across 7 priority levels.*

```*Backlog updated January 21, 2026 with documentation cleanup tasks following REFACTOR-007 completion and analyze-project review. P6 documentation tasks prioritized for accuracy and clarity. Total: 26 active tasks across 7 priority levels.*
