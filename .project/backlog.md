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

**Priority 0: Critical Bugs** - ✅ COMPLETE - All critical functionality bugs resolved, no active regressions

**Priority 1: Testing & App Reliability** - 🎯 ACTIVE - Custom CHPP client development in progress (3 incremental tasks: 2 complete, 1 pending)
- ✅ [TEST-016] CHPP API Research & Documentation (3.5 hours) - **COMPLETE Jan 26, 2026** Research findings, XML capture script, reference implementation analysis
- ✅ [REFACTOR-016] Design & Implement Custom CHPP Client (2 hours) - **COMPLETE Jan 26, 2026** Module structure created (7 files), OAuth/parsers/models/client implemented, architecture documented
- 🎯 [TEST-017] Custom CHPP Client Test Suite (2-3 hours) - **NEXT TASK** Unit tests for OAuth, parsers, models, integration tests **READY TO EXECUTE**
- 🎯 [INFRA-025] Deploy Custom CHPP with Feature Flag (1-2 hours) - Add USE_CUSTOM_CHPP flag, side-by-side validation **DEPENDENCIES: TEST-017**
- 🎯 [INFRA-026] Finalize Custom CHPP Migration (1 hour) - Remove pychpp dependency, cleanup, production deployment **DEPENDENCIES: INFRA-025**

**Priority 2: Deployment & Operations** - ✅ MILESTONE COMPLETE

**Priority 3: Stability & Maintainability** (It stays working) - 🎯 CURRENT FOCUS
- 🎯 [REFACTOR-012] Extract CHPP Client Utilities (2-3 hours) - **NEW** Consolidate CHPP initialization and team data fetching patterns **SIMPLIFICATION**
- 🎯 [REFACTOR-002] Type System Consolidation (6-8 hours) - **CONSOLIDATED TASK** Address 85 type drift issues between SQLAlchemy and TypeScript **HIGH PRIORITY SIMPLIFICATION**
- 🎯 [UI-011] Core UI Guidelines Implementation (10-14 hours) - **CONSOLIDATED TASK**
  - Apply unified design system to Flask templates and React components (UI-008: 8-12 hours)
  - Document Content-in-Boxes pattern references and link from ui-design-guidelines.md (UI-009: 1-2 hours)
  - Apply UI guidelines to core pages: Players, training, stats, settings (UI-010: 4-6 hours)
  - **Value**: Unified UI implementation sprint vs scattered individual tasks **SIMPLIFICATION**
- 🎯 [TEST-014] Fix Auth Blueprint Tests (1-2 hours) - **NEW** Update tests for YouthTeamId handling and session validation **READY TO EXECUTE**
- 🎯 [TEST-015] Blueprint & Utils Test Coverage (4-6 hours) - Achieve 80% coverage for blueprint modules and validate migrated utility functions **READY TO EXECUTE**
- 🎯 [REFACTOR-013] Remove Temporary Debug Scripts (15 min) - **NEW** Clean up check_historical_data.py, test_team_ids.py **READY TO EXECUTE**
- 🎯 [REFACTOR-014] Extract YouthTeamId Workaround (1 hour) - **NEW** Create chpp_utils.get_user_teams() to centralize workaround **SIMPLIFICATION**
- 🎯 [REFACTOR-015] Simplify prompts.json UI Guidelines (30 min) - **NEW** Remove redundant UI definitions, reference .project/ui-guidelines.md instead **SIMPLIFICATION**
- 🎯 [REFACTOR-009] CHPP Mock Pattern Standardization (1-2 hours) - Consolidate CHPP test patterns from test_chpp_integration_comprehensive.py for reuse across test suite **SIMPLIFICATION**
- 🎯 [REFACTOR-001] Code Maintainability (6-8 hours) - Technical debt cleanup
- 🎯 [INFRA-009] Dependency Strategy (4-6 hours) - Maintenance planning

**Priority 4: Core Functionality** (It does what it should)
- 🎯 [BUG-008] Fix sorttable.js TypeError (30-45 min) - Fix `node.getAttribute is not a function` error preventing table sorting on update page **NEW**
- 🎯 [BUG-009] Fix Player Changes Calculation Error (1-2 hours) - Resolve "list index out of range" error in main.py preventing player change display **NEW**
- 🎯 [BUG-006] Fix Players Page "Last Updated" Display (30 min) - Display missing timestamp **READY**
- 🎯 [FEAT-013] Error Monitoring System (4-6 hours) - Database-backed error tracking with debug page dashboard **NEW**
- 🎯 [FEAT-009] Display Player Group Names in Update Timeline (1-2 hours) - Show group names after player names when players belong to user groups **NEW**
- 🎯 [BUG-007] Fix Debug Page Issues (1-2 hours) - Visibility and changelog display **READY**
- 🎯 [DOC-021](#doc-021-new-player-tutorial) New Player Tutorial (3-5 hours) - Onboarding walkthrough **READY**
- 🎯 [FEAT-005](#feat-005-team-statistics-dashboard) Team Statistics Dashboard (8-10 hours) - Performance analytics
- 🎯 [FEAT-008](#feat-008-next-game-analyser) Next Game Analyser (12-16 hours) - Tactical preparation and opponent analysis
- 🔮 [FEAT-003](#feat-003-formation-tester--tactics-analyzer) Formation Tester & Tactics Analyzer - Research Phase

**Priority 5: DevOps & Developer Experience** (Make it easy)
- 🎯 [DOC-019] macOS Setup Guide (30 min) - Platform support
- 🎯 [DOC-020] UV Installation Guide (30 min) - Environment onboarding
- 🎯 [DOC-010] Testing Prompts (30 min) - AI agent testing workflows
- 🎯 [INFRA-020] Fix GitHub Workflows (30 min) - CI reliability
- 🎯 [INFRA-023] Script Linting Cleanup (1-2 hours) - Fix 32 linting errors in test files **READY TO EXECUTE**
- 🎯 [FEAT-006] Default Player Groups for New Users (2-3 hours) - Onboarding

**Priority 6: Documentation & Polish** (Make it complete)
- 🎯 [DOC-029] Comprehensive Documentation Cleanup (4-5 hours) - **CONSOLIDATED TASK** (includes UI consolidation, env config, navigation, waste elimination)
  - Remove legacy configuration files and unused configs/duplicates (DOC-026) - ✅ requirements.txt COMPLETE, .flake8 remaining
  - Consolidate environment templates from 3 to 2 variants (DOC-027)
  - Merge scattered README setup instructions (DOC-028)
  - Clean TECHNICAL.md obsolete route architecture content (DOC-023)
  - Remove deprecated README.md setup instructions (DOC-024)
  - Update architecture.md file structure (DOC-025)
  - **Value**: Single focused cleanup session vs 6 separate tasks **SIMPLIFICATION**

**Priority 7: Potential Future Improvements**
- 🔮 [INFRA-024] Re-upgrade to pychpp 0.5.10 + Flask 3.1+ (2-3 hours) - Re-attempt library upgrades (Note: werkzeug 3.1+ covered by SECURITY-001)
- 🔮 [FEAT-010] Collaborative League Intelligence (40-60 hours) - Multiplayer league-wide platform for shared scouting and collective tactical analysis
- 🔮 [FEAT-011] AI-Powered Training Optimization Engine (60-80 hours) - Machine learning on historical skill progression for optimal training schedules
- 🔮 [REFACTOR-004] Replace pyCHPP Dependency (16-24 hours) - Custom CHPP API integration for long-term independence
- 🔮 [FEAT-012] Trophy Data Integration (6-8 hours) - Add historical trophy/achievement display when pyCHPP supports it

---

## ✅ All Priority Levels Summary

**P0**: ✅ COMPLETE - All critical bugs resolved, no active functionality regressions
**P1**: 🎯 ACTIVE - Custom CHPP client development (3 tasks: 2 complete → TEST-017 next), testing infrastructure operational (19/24 gates)
**P2**: ✅ MILESTONE COMPLETE - Deployment & Operations infrastructure stable (INFRA-018 ✅ COMPLETE, INFRA-021 ✅ COMPLETE)
**P3**: 🎯 CURRENT FOCUS - Type sync resolution (85 failures), security updates (SECURITY-001), blueprint auth test fix
**P4**: Ready - Core functionality improvements and bug fixes
**P5**: Ready - DevOps and developer experience enhancements
**P6**: Ready - Documentation cleanup consolidation and new content
**P7**: Future - Strategic improvements and major features (REFACTOR-004 parent task archived, replaced by P1 increments)

## Ready to Execute Tasks (🎯 Immediate)

**Priority 1: Custom CHPP Client Development** (3 incremental tasks, 6-8 hours total):
1. **[TEST-016] CHPP API Research** ✅ COMPLETE (3.5 hours) - OAuth flow documented, XML schemas analyzed, pychpp patterns extracted
2. **[REFACTOR-016] Design & Implement CHPP Client** ✅ COMPLETE (2 hours) - 7 modules created (auth, parsers, models, client, exceptions, constants, __init__), architecture documented
3. **[TEST-017] CHPP Test Suite** (2-3 hours) - P1 - Comprehensive validation **START HERE - NEXT TASK**
4. **[INFRA-025] Deploy with Feature Flag** (1-2 hours) - P1 - Safe rollout
5. **[INFRA-026] Finalize Migration** (1 hour) - P1 - Remove pychpp dependency

**Priority 3: Stability Tasks** (Alternative to P1 CHPP work):
1. **[REFACTOR-012] Extract CHPP Client Utilities** (2-3 hours) - P3 - Consolidate CHPP patterns
2. **[TEST-014] Fix Auth Blueprint Tests** (1-2 hours) - P3 - Update tests for YouthTeamId handling
3. **[REFACTOR-002] Type System Consolidation** (6-8 hours) - P3 - Address 85 type drift issues
4. **[UI-011] Core UI Guidelines Implementation** (10-14 hours) - P3 - Unified design system application
5. **[TEST-015] Blueprint & Utils Test Coverage** (4-6 hours) - P3 - Achieve 80% coverage for blueprint modules

**Next Action**: Choose between P1 custom CHPP development (TEST-016 research phase) or P3 stability work (REFACTOR-012 consolidation). P1 tasks are incremental and independently releasable.

---

## Priority 1: Testing & App Reliability - Custom CHPP Client Development
- Unit tests passing with >90% coverage
- No actual CHPP API calls in unit tests (mocked)
- Code follows project standards (ruff, mypy)

**Releasability**: Can be merged without affecting existing pychpp usage. Sets foundation for REFACTOR-020 integration.

**Expected Outcomes**: Working OAuth implementation, validated authentication flow, foundation for authenticated CHPP requests

---

### [REFACTOR-018] Implement Custom CHPP XML Parsers
**Status**: 🎯 Ready to Execute | **Effort**: 2-3 hours | **Priority**: P1 | **Impact**: Data transformation foundation
**Dependencies**: REFACTOR-016 (Architecture Design) | **Strategic Value**: YouthTeamId fix, clean data extraction

**Problem Statement**:
Implement XML parsing logic as second independent component. This transforms CHPP XML responses into Python data structures and fixes the YouthTeamId bug at source.

**Implementation**:
1. **Create Parser Module** (1.5-2 hours):
   - Implement `app/chpp/parsers.py` with parsing functions
   - Function: `parse_user(xml_root)` → extracts ht_id, username, team_ids (handles missing YouthTeamId gracefully)
   - Function: `parse_team(xml_root)` → extracts team_id, name, short_name
   - Function: `parse_players(xml_root)` → extracts player list with all 7 skills + metadata
   - Use `xml.etree.ElementTree` for XPath queries
   - Helper: `safe_find_text(node, xpath, default=None)` for optional fields
   - Add data type conversions (string → int, bool, datetime)

2. **YouthTeamId Fix Implementation** (15 min):
   - Make YouthTeamId field optional in `parse_user()`
   - Pattern: `youth_team_id = safe_find_text(root, ".//YouthTeamId", default=None)`
   - Remove need for try/except workarounds in application code

3. **Unit Tests with Real XML** (45 min-1 hour):
   - Create `tests/test_chpp_parsers.py`
   - Use XML samples from TEST-016 research in `app/chpp/test_data/`
   - Test `parse_user()` with and without YouthTeamId
   - Test `parse_team()` with various team data
   - Test `parse_players()` with full player dataset
   - Test edge cases: missing fields, null values, malformed XML

**Deliverables**:
- `app/chpp/parsers.py` with parsing functions
- `tests/test_chpp_parsers.py` with real XML fixtures
- YouthTeamId bug fix validated

**Acceptance Criteria**:
- All 3 parser functions implemented (user, team, players)
- YouthTeamId handled as optional field (no exceptions)
- Data type conversions working correctly
- Edge cases handled gracefully (missing/null values)
- Unit tests passing with >90% coverage
- Tests use real XML samples from research phase
- No external API calls required for testing
- Code follows project standards

**Releasability**: Can be merged independently. Parsers don't affect existing pychpp usage until integrated in REFACTOR-020.

**Expected Outcomes**: Robust XML parsing, YouthTeamId bug eliminated, validated data transformation, foundation for REFACTOR-019 data models

---

### [REFACTOR-019] Implement Custom CHPP Data Models
**Status**: 🎯 Ready to Execute | **Effort**: 1-2 hours | **Priority**: P1 | **Impact**: Interface compatibility
**Dependencies**: REFACTOR-018 (XML Parsers) | **Strategic Value**: Zero breaking changes, pychpp interface match

**Problem Statement**:
Implement data model classes that exactly match pychpp interface, ensuring drop-in replacement compatibility. These models wrap parsed data and provide the same attributes and methods as pychpp objects.

**Implementation**:
1. **Create Model Classes** (1-1.5 hours):
   - Implement `app/chpp/models.py` with data classes
   - Class: `CHPPUser` with attributes: `ht_id`, `username`, `_teams_ht_id`, `_SOURCE_FILE`
   - Class: `CHPPTeam` with attributes: `team_id`, `name`, `short_team_name`, `_players`, method: `players()`
   - Class: `CHPPPlayer` with all skill attributes: `keeper`, `defender`, `playmaker`, `winger`, `passing`, `scorer`, `set_pieces`, plus `experience`, `form`, `stamina`, `loyalty`
   - Add `__getitem__` for dict-like access (backward compatibility)
   - Use dataclasses or simple classes matching pychpp patterns

2. **Integration with Parsers** (15-30 min):
   - Update parser functions to return model instances
   - `parse_user()` returns `CHPPUser` object
   - `parse_team()` returns `CHPPTeam` object
   - `parse_players()` returns list of `CHPPPlayer` objects

3. **Unit Tests** (15-30 min):
   - Create `tests/test_chpp_models.py`
   - Test model instantiation with parsed data
   - Test attribute access patterns
   - Test dict-like access (`player['scorer']` works)
   - Test `team.players()` method returns list
   - Validate interface matches pychpp exactly

**Deliverables**:
- `app/chpp/models.py` with 3 data model classes
- `tests/test_chpp_models.py` with interface validation
- Updated parsers returning model instances

**Acceptance Criteria**:
- All 3 model classes implemented matching pychpp interface
- Attribute names identical to pychpp (ht_id, _teams_ht_id, etc.)
- Dict-like access supported for backward compatibility
- `team.players()` method works identically to pychpp
- Unit tests passing validating interface match
- No breaking changes from pychpp interface
- Code follows project standards

**Releasability**: Can be merged independently. Models tested separately before REFACTOR-020 integration.

**Expected Outcomes**: Interface-compatible models, zero breaking changes guaranteed, foundation for REFACTOR-020 client integration

---

### [REFACTOR-020] Integrate Custom CHPP Client
**Status**: 🎯 Ready to Execute | **Effort**: 2-3 hours | **Priority**: P1 | **Impact**: Complete custom CHPP implementation
**Dependencies**: REFACTOR-017 (OAuth), REFACTOR-019 (Models) | **Strategic Value**: Full custom client, pychpp replacement ready

**Problem Statement**:
Integrate OAuth (REFACTOR-017), parsers (REFACTOR-018), and models (REFACTOR-019) into unified CHPP client class matching pychpp interface exactly. This completes the custom implementation.

**Implementation**:
1. **Create CHPP Client Class** (1.5-2 hours):
   - Implement `app/chpp/client.py` with main `CHPP` class
   - Method: `__init__(consumer_key, consumer_secret, access_key=None, access_secret=None)` → stores credentials, initializes OAuth session
   - Method: `get_auth(callback_url, scope="")` → calls auth.get_request_token(), returns formatted dict
   - Method: `get_access_token(request_token, request_secret, verifier)` → calls auth.get_access_token(), returns {key, secret}
   - Method: `request(file, version, **params)` → makes authenticated CHPP API request, returns parsed XML ElementTree
   - Method: `user()` → calls request("managercompendium", "1.6"), parses with parse_user(), returns CHPPUser
   - Method: `team(ht_id)` → calls request("teamdetails", version), parses with parse_team(), returns CHPPTeam
   - Add error handling wrapping all calls with CHPPAPIError

2. **Public API Export** (15 min):
   - Update `app/chpp/__init__.py`:
   - Export `CHPP` class
   - Export exceptions: `CHPPAuthError`, `CHPPAPIError`
   - Add `__version__ = "1.0.0"`

3. **Integration Tests** (30-45 min):
   - Create `tests/test_chpp_client_integration.py`
   - Test full OAuth flow (mocked)
   - Test `user()` returns CHPPUser with correct data
   - Test `team()` returns CHPPTeam with correct data
   - Test error handling (network failures, auth failures)
   - Validate interface matches pychpp exactly

**Deliverables**:
- `app/chpp/client.py` with unified CHPP class
- `app/chpp/__init__.py` exporting public API
- `tests/test_chpp_client_integration.py` validating full client

### [TEST-017] Custom CHPP Client Test Suite
**Status**: 🎯 Ready to Execute | **Effort**: 2-3 hours | **Priority**: P1 | **Impact**: Quality assurance, regression prevention
**Dependencies**: REFACTOR-016 (Complete) | **Strategic Value**: Confidence for production deployment, comprehensive validation

**Problem Statement**:
Validate custom CHPP client against all requirements: unit tests for components, integration tests with mocked API, compatibility tests against existing test suite, optional real API validation.

**Implementation**:
1. **Comprehensive Unit Test Review** (30-45 min):
   - Verify all component tests for app/chpp/ module
   - Ensure >90% coverage for `app/chpp/` module
   - Add missing edge case tests
   - Validate error handling coverage

2. **Compatibility Testing** (1-1.5 hours):
   - Update `tests/mock_chpp.py` to support custom CHPP client
   - Create `MockCustomCHPP` class if needed
   - Run existing test suite with custom client imported (without feature flag)
   - Verify test_blueprint_auth.py passes unchanged
   - Verify test_blueprint_team.py passes unchanged
   - Verify test_chpp_integration.py passes unchanged
   - Fix any interface mismatches discovered

3. **Real API Integration Tests** (30-45 min):
   - Create `tests/test_chpp_real_api.py` (gated by env var)
   - Test OAuth flow with real Hattrick CHPP API
   - Test `user()` with real API (validate data structure)
   - Test `team()` with real API
   - Compare responses with pychpp (data equivalence validation)
   - Only runs when `TEST_REAL_CHPP_API=true`

**Deliverables**:
- Complete test suite for `app/chpp/` module
- Updated `tests/mock_chpp.py` supporting custom client
- Real API integration tests (optional, gated)
- Test coverage report showing >90% for custom client

**Acceptance Criteria**:
- All unit tests passing for auth, parsers, models, client
- Test coverage >90% for `app/chpp/` module
- Existing test suite passes with custom client
- No behavioral differences detected vs pychpp
- Real API tests pass when enabled (validates against production)
- Mock strategy proven simpler than pychpp mocking
- All tests follow project standards
- `make test-all` passes completely

**Releasability**: Validates custom client ready for production deployment via INFRA-025 feature flag.

**Expected Outcomes**: High confidence in custom CHPP client quality, regression prevention, validated pychpp replacement

---

### [INFRA-025] Deploy Custom CHPP with Feature Flag
**Status**: 🎯 Ready to Execute | **Effort**: 1-2 hours | **Priority**: P1 | **Impact**: Safe production rollout
**Dependencies**: TEST-017 (Test Suite) | **Strategic Value**: Risk mitigation, instant rollback capability

**Problem Statement**:
Deploy custom CHPP client to production with feature flag enabling side-by-side validation and instant rollback if issues arise. This de-risks the migration by allowing gradual validation.

**Implementation**:
1. **Feature Flag Setup** (30 min):
   - Add to `config.py`: `USE_CUSTOM_CHPP = os.getenv('USE_CUSTOM_CHPP', 'false').lower() == 'true'`
   - Update `app/blueprints/auth.py`:
     ```python
     if app.config.get('USE_CUSTOM_CHPP'):
         from app.chpp import CHPP
     else:
         from pychpp import CHPP
     ```
   - Update `app/blueprints/team.py` (same pattern)
   - Update any other files importing pychpp

2. **Development Validation** (30-45 min):
   - Set `USE_CUSTOM_CHPP=true` in local `.env`
   - Run `make dev` and test full application flow
   - Test OAuth login with custom client
   - Test `/update` route (player data fetch)
   - Test team switching functionality
   - Compare behavior with pychpp (set USE_CUSTOM_CHPP=false)
   - Monitor logs for errors or warnings

3. **Staging Deployment** (15-30 min):
   - Deploy to staging with `USE_CUSTOM_CHPP=false` (default)
   - Verify staging works with pychpp
   - Toggle to `USE_CUSTOM_CHPP=true`
   - Run full regression test suite
   - Monitor application logs and error rates
   - Test with multiple user accounts

**Deliverables**:
- Feature flag implemented in config and all import locations
- Documentation in TECHNICAL.md explaining feature flag usage
- Validated deployment to staging
- Rollback procedure documented

**Acceptance Criteria**:
- Feature flag working correctly (toggles between pychpp and custom client)
- All routes functional with `USE_CUSTOM_CHPP=true`
- OAuth flow works identically to pychpp
- Player data updates work correctly
- No errors in logs during testing
- Performance comparable to pychpp
- Staging deployment successful
- Rollback tested (toggle flag back to false)
- `make test-all` passes with both flag settings

**Releasability**: Deploys custom CHPP to production (disabled by default), ready for gradual rollout and final migration in INFRA-026.

**Expected Outcomes**: Safe production deployment, validated functionality, confidence for final migration, instant rollback available if needed

---

### [INFRA-026] Finalize Custom CHPP Migration
**Status**: 🎯 Ready to Execute | **Effort**: 1 hour | **Priority**: P1 | **Impact**: Dependency elimination, migration complete
**Dependencies**: INFRA-025 (Feature Flag Deployment), 1-2 weeks production monitoring | **Strategic Value**: Long-term independence, custom optimization capability

**Problem Statement**:
After successful validation in production with feature flag (1-2 weeks monitoring), finalize migration by removing pychpp dependency and feature flag, completing the transition to custom CHPP client.

**Implementation**:
1. **Production Validation** (outside this task - 1-2 weeks):
   - Monitor production with `USE_CUSTOM_CHPP=true` for 1-2 weeks
   - Track error rates, performance metrics, user reports
   - Validate OAuth success rates match pychpp baseline
   - Confirm no YouthTeamId workaround needed
   - Decision point: Proceed with finalization if metrics good

2. **Remove Feature Flag** (15-20 min):
   - Remove `USE_CUSTOM_CHPP` config variable
   - Remove conditional imports from auth.py, team.py
   - Hardcode custom CHPP import: `from app.chpp import CHPP`
   - Clean up any flag-related comments

3. **Remove pychpp Dependency** (10 min):
   - Remove `pychpp==0.5.10` from `pyproject.toml` dependencies
   - Run `uv sync` to update lockfile
   - Keep `requests-oauthlib` (still used by custom client)
   - Verify no stray pychpp references: `grep -r "from pychpp\|import pychpp"`

4. **Documentation Updates** (20-30 min):
   - Update TECHNICAL.md: Remove pychpp references, document custom CHPP client
   - Update `.github/copilot-instructions.md`: Change to custom client patterns
   - Update `app/chpp/README.md` if needed
   - Remove YouthTeamId workaround notes from code comments
   - Update architecture docs

5. **Final Validation** (10 min):
   - Run `make test-all` one final time
   - Verify all 19/22+ quality gates still passing
   - Deploy to production
   - Monitor for 24 hours post-deployment

**Deliverables**:
- Feature flag and conditional imports removed
- pychpp dependency removed from pyproject.toml
- Documentation updated throughout
- Git commit: "Complete migration to custom CHPP client"

**Acceptance Criteria**:
- No pychpp imports remaining in codebase
- pychpp removed from dependencies
- Feature flag logic removed
- All routes using custom CHPP client only
- Documentation updated (TECHNICAL.md, copilot-instructions.md)
- `make test-all` passes (19/22+ gates)
- Production deployment successful
- No regressions detected post-deployment
- YouthTeamId bug confirmed fixed (no workarounds)

**Rollback Plan** (if needed):
- Revert commit restores pychpp
- Add back to pyproject.toml, run `uv sync`
- Restore conditional imports with flag
- Should only be needed if critical issues found

**Expected Outcomes**: Complete migration to custom CHPP client, pychpp dependency eliminated, long-term independence achieved, YouthTeamId bug permanently fixed

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

### [FEAT-013] Error Monitoring System
**Status**: 🎯 Ready to Execute | **Effort**: 4-6 hours | **Priority**: P4 | **Impact**: Production debugging and user support
**Dependencies**: None | **Strategic Value**: Proactive issue detection, improved user support, reduced troubleshooting time

**Problem Statement**:
When users encounter errors or crashes in the application, there is currently no centralized system to capture, store, and analyze these issues. This makes it difficult to:
- Diagnose problems reported by users
- Identify patterns in errors across different users
- Proactively detect issues before users report them
- Track error frequency and severity
- Debug production issues without direct access to user environments

A database-backed error monitoring system would allow administrators to:
- View all errors/crashes from any user in a centralized dashboard
- Filter and search errors by user, timestamp, error type, severity
- Analyze error patterns and frequency trends
- Prioritize bug fixes based on actual user impact
- Support users more effectively with detailed error context

**Implementation**:
1. **Database Model** (1-1.5 hours):
   - Create `ErrorLog` table with fields: id, user_id, timestamp, error_type, message, stack_trace, url, user_agent, severity, status (new/acknowledged/resolved)
   - Add indexes for efficient querying (user_id, timestamp, error_type)
   - Create migration file with `uv run python scripts/database/apply_migrations.py`
   - Support for categorizing errors: exception, crash, warning, info

2. **Error Capture Middleware** (1-1.5 hours):
   - Create Flask error handler middleware to catch all unhandled exceptions
   - Extract error details: type, message, stack trace, request context
   - Store error in database with user context if authenticated
   - Support manual error logging via utility function for specific error tracking
   - Implement rate limiting to prevent database flooding from repeated errors

3. **Debug Page Dashboard** (1.5-2 hours):
   - Add new "Error Monitoring" section to existing debug page
   - Display recent errors in sortable/filterable table: timestamp, user, error type, message, status
   - Show error statistics: total errors, errors by type, errors by user, trend chart
   - Add detail view for individual errors with full stack trace and context
   - Implement pagination for large error sets
   - Add status update capability (acknowledge/resolve errors)

4. **Admin Features** (0.5-1 hour):
   - Add error count badge to debug page navigation (show unacknowledged errors)
   - Create API endpoint for retrieving error data
   - Add filtering by date range, user, error type, severity
   - Export capability (CSV/JSON) for external analysis

**Acceptance Criteria**:
- ErrorLog database table created with proper indexes
- All unhandled exceptions automatically logged to database
- Error logs include user context, stack trace, request details
- Debug page displays error monitoring dashboard
- Error list is sortable and filterable
- Individual error detail view shows full context
- Admin can mark errors as acknowledged/resolved
- Error statistics and trends displayed
- No performance impact on normal application operations
- Rate limiting prevents database flooding
- Works for both authenticated and anonymous users

**Data to Capture**:
- **Error Context**: Type, message, stack trace, timestamp
- **User Context**: User ID (if logged in), session data
- **Request Context**: URL, HTTP method, user agent, IP address (anonymized)
- **Severity**: Critical (crashes), Error (exceptions), Warning, Info
- **Status**: New, Acknowledged, Resolved, Ignored

**Debug Page Display**:
- **Summary Cards**: Total errors (last 24h), Unacknowledged errors, Error rate trend
- **Error Table**: Columns: Timestamp, User, Type, Message (truncated), Severity, Status, Actions
- **Filters**: Date range, User ID, Error type, Severity, Status
- **Detail Modal**: Full error with stack trace, request details, user context
- **Actions**: Acknowledge, Resolve, Ignore, View similar errors

**Privacy Considerations**:
- Do not log sensitive data (passwords, API keys, tokens) in error messages
- Anonymize IP addresses (store first 3 octets only)
- Allow users to opt-out of detailed error tracking in settings
- Implement automatic cleanup of old error logs (>90 days)

**Technical Approach**:
- Use Flask's `@app.errorhandler` decorator for exception catching
- SQLAlchemy model for ErrorLog table
- Async logging to prevent blocking request handling
- Integration with existing debug page template
- Chart.js for error trend visualization

**Expected Outcomes**: Improved production debugging capability, faster issue resolution, proactive error detection, better user support with detailed error context, data-driven bug prioritization

---

### [BUG-006] Fix Players Page "Last Updated" Display
**Status**: 🎯 Ready to Execute | **Effort**: 30 minutes | **Priority**: P4 | **Impact**: User experience clarity
**Dependencies**: None | **Strategic Value**: Information completeness

**Problem Statement**:
The players page displays "Last updated" text without showing the actual date or timestamp, leaving users without visibility into data freshness.

**Implementation**:
1. **Identify Data Source** (10 min):
   - Check if last update timestamp exists in session or database
   - Locate where "Last updated" text is rendered in template
   - Determine appropriate timestamp format for display

2. **Template Update** (15 min):
   - Add timestamp variable to template context
   - Format timestamp for user-friendly display (e.g., "January 24, 2026 at 2:30 PM")
   - Handle cases where timestamp might be missing

3. **Validation** (5 min):
   - Test display with and without available timestamp
   - Verify formatting across different screen sizes
   - Ensure consistent styling with UI guidelines

**Acceptance Criteria**:
- "Last updated" shows actual date and time when data available
- Graceful handling when timestamp unavailable
- Consistent formatting with application UI standards
- Mobile-responsive display maintained

**Expected Outcomes**: Users have clear visibility into when their data was last synchronized with Hattrick.

---

### [FEAT-009] Display Player Group Names in Update Timeline
**Status**: 🎯 Ready to Execute | **Effort**: 1-2 hours | **Priority**: P4 | **Impact**: Enhanced player identification in updates
**Dependencies**: None | **Strategic Value**: Improved user experience for players in custom groups

**Problem Statement**:
When viewing the update timeline, players are displayed by name only. Users who have organized their players into custom groups (e.g., "Ytterback", "Formation 1", "Reserves") cannot easily identify which group a player belongs to when viewing skill changes and updates.

**User Request Example**:
```
Current:
Jalal Allaoui
📈 Winger: 4 → 5

Desired:
Jalal Allaoui (Ytterback)
📈 Winger: 4 → 5
```

**Database Structure**:
- `PlayerSetting` table links `player_id` to `group_id` for a given `user_id`
- `Group` table contains group `name`, `textcolor`, `bgcolor` for display
- Relationship: player_id → PlayerSetting → Group.name

**Implementation**:
1. **Update get_player_changes() Function** (30-45 min):
   - Add group name lookup to player change detection logic
   - Query PlayerSetting and Group tables to find player's group name
   - Include group name in change data structure for template use
   - Handle players without group assignments gracefully

2. **Enhance Template Display Logic** (30-45 min):
   - Update `update_timeline.html` to display group names after player names
   - Format as "Player Name (Group Name)" when group exists
   - Maintain existing styling while adding group information
   - Consider group text color for visual consistency

3. **Testing & Validation** (15-30 min):
   - Test with players assigned to different groups
   - Test with players not assigned to any group
   - Verify display works with various group name lengths
   - Ensure responsive design maintained

**Acceptance Criteria**:
- Players with group assignments show "Player Name (Group Name)"
- Players without groups show "Player Name" (no change)
- Group names display consistently throughout timeline
- No impact on timeline loading performance
- Visual styling remains consistent with UI guidelines

**Technical Notes**:
- Requires JOIN between Players → PlayerSetting → Group tables
- Consider caching group lookups for performance if needed
- Group colors could be used for future enhancement

**Expected Outcomes**: Users can easily identify which tactical group or formation players belong to when reviewing skill changes and updates.

---

### [BUG-008] Fix sorttable.js TypeError
**Status**: 🎯 Ready to Execute | **Effort**: 30-45 min | **Priority**: P4 | **Impact**: User experience and data interaction
**Dependencies**: None | **Strategic Value**: Core functionality restoration

**Problem Statement**:
JavaScript error `Uncaught TypeError: node.getAttribute is not a function` occurs in sorttable.js line 212, preventing table sorting functionality on the update data page. The error occurs in the getInnerText function when it tries to call getAttribute on a node that doesn't have this method (likely a text node instead of an element node).

**Error Details**:
```
Uncaught TypeError: node.getAttribute is not a function
    getInnerText http://localhost:5010/static/sorttable.js:212
    getInnerText http://localhost:5010/static/sorttable.js:237
    guessType http://localhost:5010/static/sorttable.js:171
    makeSortable http://localhost:5010/static/sorttable.js:87
    init http://localhost:5010/static/sorttable.js:36
```

**Root Cause**:
The sorttable.js library is attempting to process table cells that may contain text nodes directly, or the table structure has changed after the pychpp 0.5.10 upgrade modifications, causing the sorting script to encounter unexpected node types.

**Implementation**:
1. Add null/type checking before calling `getAttribute()` in getInnerText function
2. Verify that table structure in update.html template is correct
3. Test table sorting functionality after fix

**Acceptance Criteria**:
- No JavaScript errors in console when loading update page
- Table sorting works correctly on all columns
- No regressions in table display or functionality

---

### [BUG-009] Fix Player Changes Calculation Error
**Status**: 🎯 Ready to Execute | **Effort**: 1-2 hours | **Priority**: P4 | **Impact**: User experience and data display
**Dependencies**: None | **Strategic Value**: Core functionality restoration

**Problem Statement**:
Error `[main.py] Error calculating player changes: list index out of range` occurs when displaying the home page, preventing player skill change timeline from displaying correctly. This error appears after the pychpp 0.5.10 upgrade.

**Error Context**:
- Occurs in main.py when trying to calculate player changes for display
- Related to accessing list indices that may not exist
- Likely caused by changes in data structure after pychpp upgrade
- May be related to how player data or team names are stored/accessed

**Root Cause Investigation**:
The error suggests that code is trying to access a list index that doesn't exist, possibly:
1. Accessing team names by index when list is empty or shorter than expected
2. Player data structure changes from pychpp 0.5.10 affecting list access patterns
3. Session data structure inconsistencies after API changes

**Implementation**:
1. Locate the specific code in main.py that calculates player changes
2. Add bounds checking before accessing list indices
3. Verify data structure assumptions are still valid after pychpp upgrade
4. Handle edge cases (empty lists, None values)
5. Test with various player data scenarios

**Acceptance Criteria**:
- No errors in logs when loading home page
- Player change timeline displays correctly
- All player statistics and changes show properly
- Handles edge cases gracefully (no players, new users, etc.)

---

### [BUG-007] Fix Debug Page Issues
**Status**: 🎯 Ready to Execute | **Effort**: 1-2 hours | **Priority**: P4 | **Impact**: Development and troubleshooting capability
**Dependencies**: None | **Strategic Value**: Development experience

**Problem Statement**:
Debug page has multiple issues affecting development workflow:
1. Not visible on development server (make dev) but appears on production
2. Doesn't display changelog under changes section

**Implementation**:
1. **Debug Page Visibility Issue** (30-45 min):
   - Check route registration in blueprints for debug page
   - Verify environment-based conditional logic
   - Test debug page access in development mode
   - Ensure proper authentication/authorization checks

2. **Changelog Display Issue** (30-45 min):
   - Investigate changelog data source and processing
   - Check template rendering logic for changes section
   - Verify changelog file generation and access
   - Test changelog display across different data states

3. **Environment Consistency** (15-30 min):
   - Ensure debug functionality works consistently across environments
   - Document any environment-specific behavior requirements
   - Test debug page functionality in both dev and production modes

**Acceptance Criteria**:
- Debug page accessible in development server (make dev)
- Changelog displays properly under changes section
- Consistent behavior between development and production
- All debug information displays correctly
- No regressions in existing debug functionality

**Technical Investigation Areas**:
- Blueprint route registration patterns
- Environment variable handling
- Changelog generation and file access
- Template data context and rendering

**Expected Outcomes**: Reliable debug page functionality supporting development workflow with proper changelog visibility.

---
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

### [REFACTOR-015] Simplify prompts.json UI Guidelines
**Status**: 🎯 Ready to Execute | **Effort**: 30 minutes | **Priority**: P3 | **Impact**: Reduced duplication, single source of truth
**Dependencies**: DOC-031 (UI Documentation Consolidation) | **Strategic Value**: Eliminate redundant definitions, improve maintainability

**Problem Statement**:
The `.project/prompts.json` file contains **46 lines of UI guidelines** (color system, typography, spacing, components) that duplicate information from UI documentation files:
- Color definitions: `hsl(120, 45%, 25%)` repeated in prompts.json AND ui-*.md files
- Typography rules duplicated
- Component patterns duplicated
- Framework notes duplicated

This creates:
- Maintenance burden (update in 2 places: prompts.json + UI docs)
- Risk of inconsistency between prompts.json and authoritative UI docs
- Bloated prompts.json file (46 lines of redundant data)
- Confusion about which source is authoritative

**Implementation**:
1. **Remove Redundant Definitions** (15 min):
   - Delete detailed color_system object (7 HSL color definitions)
   - Delete detailed typography object (headings, body, line_height)
   - Delete detailed spacing rules
   - Delete detailed components object
   - Keep ONLY high-level reference to UI docs

2. **Add Reference Pointer** (10 min):
   - Replace detailed definitions with: "See .project/ui-guidelines.md for complete design system"
   - Keep minimal hints for AI agents (e.g., "Use football green theme, see ui-guidelines.md")
   - Add direct file path reference for easy lookup
   - Preserve framework_notes (Flask vs React differences) as these are implementation-specific

3. **Validate Prompts Still Work** (5 min):
   - Test that "execute" prompt still references UI guidelines correctly
   - Ensure AI agents can find UI documentation from simplified reference
   - Verify no functionality lost

**Before** (46 lines):
```json
"ui_guidelines": {
  "color_system": {
    "primary": "hsl(120, 45%, 25%)",
    "success": "hsl(120, 70%, 35%)",
    // ... 5 more colors
  },
  "typography": { /* detailed rules */ },
  "spacing": "0.25rem increments...",
  "components": { /* detailed patterns */ },
  "framework_notes": { /* Flask/React differences */ }
}
```

**After** (~10 lines):
```json
"ui_guidelines": {
  "design_system": "See .project/ui-guidelines.md for complete color system, typography, spacing, and component patterns",
  "quick_reference": "Football green theme (hsl(120, 45%, 25%)), responsive design, accessibility standards",
  "framework_notes": {
    "flask": "Use .btn-primary-custom, .table-custom, .card-custom classes",
    "react": "Use existing button/table/card components, consistent with TailwindCSS utilities"
  }
}
```

**Acceptance Criteria**:
- prompts.json ui_guidelines section reduced from 46 lines to ~10 lines
- Redundant color/typography/spacing definitions removed
- Clear reference to .project/ui-guidelines.md added
- Framework-specific notes preserved (Flask vs React implementation)
- AI agent prompts (execute, review) still function correctly
- No loss of essential information for AI agents
- Single source of truth established (ui-guidelines.md)

**Expected Outcomes**: 75% reduction in prompts.json UI section, eliminated duplication, improved maintainability, single authoritative source for design system

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

### [DOC-029] Comprehensive Documentation Cleanup
**Status**: 🎯 Ready to Execute | **Effort**: 4-5 hours | **Priority**: P6 | **Impact**: Major documentation and configuration simplification
**Dependencies**: None | **Strategic Value**: Eliminate 40% documentation redundancy, single source of truth, cleaner repository

**Problem Statement** (Consolidated cleanup addressing multiple issues):

**1. UI Documentation Proliferation** - 5 separate UI documentation files (2,264 total lines) with significant overlap:
- `ui-style-guide.md` (610 lines) - Color system, typography, components
- `ui-design-guidelines.md` (444 lines) - Design patterns and templates
- `ui-implementation-standards.md` (640 lines) - Flask/React implementation code examples
- `ui-content-boxes-pattern.md` (389 lines) - Specific pattern documentation
- `ui-audit-analysis.md` (181 lines) - Historical audit from January 2026 (completed work)

This creates:
- Confusion about which file to reference
- Duplicate information across multiple files (color definitions, typography rules)
- Maintenance burden (updates needed in multiple places)
- Difficulty for AI agents and developers finding the right information

**2. Environment Configuration Duplication** - 5 configuration files (440 lines) in `environments/` directory with 80%+ duplicate content:
- `.env.development.example`, `.env.staging.example`, `.env.production.example` (440 lines total)
- Each file repeats same variables with minor differences
- Creates maintenance burden (update same variable 3 times)
- Risk of inconsistency between files

**3. Legacy Configuration Waste** - Obsolete files creating confusion:
- `configs/requirements.txt` - **COMPLETELY EMPTY** (dependencies moved to pyproject.toml)
- `configs/.flake8` - **OBSOLETE** (6 lines, replaced by ruff in pyproject.toml)
- Add clutter and false impression of active use

**4. Documentation Navigation Complexity** - 21+ documentation files without clear entry points:
- 3 root docs + 14+ .project/ docs + 4 docs/ files
- No clear "you are here" navigation
- Duplication between .project/README.md and main README.md
- Uncertainty about which file to read first

**Implementation**:
1. **Eliminate Legacy Configuration Waste** (15 min):
   - Delete `configs/requirements.txt` (empty file)
   - Delete `configs/.flake8` (obsolete, using ruff)
   - Update configs/README.md if needed
   - Verify no references in codebase or CI/CD

2. **Consolidate Core Design System** (1-1.5 hours):
   - Merge `ui-style-guide.md` + `ui-design-guidelines.md` + `ui-content-boxes-pattern.md` → `ui-guidelines.md`
   - Structure: Colors → Typography → Spacing → Components → Patterns → Design Philosophy
   - Remove duplicate color/typography definitions
   - Integrate content-boxes pattern as section in main guidelines
   - Create single authoritative source for design decisions

2. **Archive Historical Content** (15 min):
   - Move `ui-audit-analysis.md` to `.project/history/ui-audit-analysis.md`
   - Update with "Completed January 2026" header
   - This is historical context, not active development guidance

3. **Refine Implementation Guide** (30 min):
   - Keep `ui-implementation-standards.md` as separate file (implementation details)
   - Remove redundant design theory (reference ui-guidelines.md instead)
   - Focus purely on Flask/React code examples and integration patterns
   - Add "See ui-guidelines.md for design system" cross-reference

4. **Update All References** (30-45 min):
   - Update `backlog.md` task descriptions referencing old UI docs
   - Update `prompts.json` UI guidelines section (see REFACTOR-015)
   - Update any cross-references in other .project/ docs
   - Fix broken links and ensure consistency

**Acceptance Criteria**:
- 5 UI documentation files reduced to 2 active files
- `ui-guidelines.md` created as single source of truth for design system
- `ui-implementation-standards.md` focused on code examples only
- `ui-audit-analysis.md` moved to .project/history/
- Old files (`ui-style-guide.md`, `ui-design-guidelines.md`, `ui-content-boxes-pattern.md`) deleted
- All backlog.md and prompts.json references updated
- No duplicate color/typography definitions across files
- Clear navigation between guidelines (design) and implementation (code)

**File Structure After Consolidation**:
- `ui-guidelines.md` (~900 lines) - Design system authority: colors, typography, components, patterns
- `ui-implementation-standards.md` (~500 lines) - Code examples: Flask classes, React components
- `.project/history/ui-audit-analysis.md` - Historical audit (archived)

**Expected Reduction**: 2,264 lines → ~1,400 lines (38% reduction), 5 files → 2 active files

**Expected Outcomes**: Single source of truth for UI design, reduced maintenance burden, improved clarity for developers and AI agents, eliminated duplication

3. **Environment Configuration Simplification** (1 hour):
   - Create unified `.env.template` with inline environment variants
   - Format: `# Development: value1 | Staging: value2 | Production: value3`
   - Delete 3 separate `.env.*.example` files (development, staging, production)
   - Enhance `config.py.example` with detailed comments
   - Update environments/README.md and main README.md
   - Expected: 440 lines → ~200 lines (55% reduction)

4. **Documentation Navigation Simplification** (1-2 hours):
   - Add "Documentation Index" section to main README.md
   - Create categories: Getting Started, Development, Architecture, Planning, Deployment
   - Consolidate or reference .project/README.md content
   - Add cross-references and "See Also" links to all major docs
   - Create consistent "Quick Navigation" sections
   - Ensure new developers can find docs in <30 seconds

5. **Update AI Agent References** (15 min):
   - Update `prompts.json` UI guidelines section (see REFACTOR-015)
   - Update all task references in backlog.md
   - Fix any broken cross-references

**Acceptance Criteria**:
- ✅ Legacy waste eliminated: configs/requirements.txt and configs/.flake8 deleted
- ✅ UI docs consolidated: 5 files → 2 active files (ui-guidelines.md + ui-implementation-standards.md)
- ✅ ui-audit-analysis.md moved to .project/history/
- ✅ Environment configs: Single .env.template replacing 3 duplicate .env.*.example files
- ✅ Documentation navigation: README.md has clear index, .project/README.md consolidated or focused
- ✅ All backlog.md and prompts.json references updated
- ✅ No duplicate color/typography definitions across files
- ✅ Total reduction: ~850 lines eliminated, 6 files removed, 38% documentation reduction
- ✅ Clear single sources of truth established for UI design, environment config, navigation

**Expected Outcomes**:
- Cleaner repository (6 fewer files)
- 38% reduction in UI documentation lines (2,264 → ~1,400)
- 55% reduction in environment config lines (440 → ~200)
- Eliminated maintenance burden from duplicate definitions
- Single authoritative sources for all documentation categories
- Improved developer and AI agent navigation
- Faster onboarding with clearer entry points

---

### [DOC-011] API Documentation
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

### [REFACTOR-004] Replace pyCHPP Dependency (ARCHIVED - Replaced by P1 Incremental Tasks)
**Status**: 📦 ARCHIVED - Superseded by 9 incremental P1 tasks | **Effort**: 16-24 hours total | **Priority**: P7 → P1 (Promoted)
**Dependencies**: See P1 task chain (TEST-016 → INFRA-026) | **Strategic Value**: Long-term dependency independence, custom optimization

**⚠️ NOTE**: This parent task has been broken down into 9 smaller, releasable increments in Priority 1:
1. **TEST-016**: CHPP API Research & Documentation (3-4 hours)
2. **REFACTOR-016**: Design Custom CHPP Client Architecture (2-3 hours)
3. **REFACTOR-017**: Implement Custom CHPP OAuth Flow (2-3 hours)
4. **REFACTOR-018**: Implement Custom CHPP XML Parsers (2-3 hours)
5. **REFACTOR-019**: Implement Custom CHPP Data Models (1-2 hours)
6. **REFACTOR-020**: Integrate Custom CHPP Client (2-3 hours)
7. **TEST-017**: Custom CHPP Client Test Suite (2-3 hours)
8. **INFRA-025**: Deploy Custom CHPP with Feature Flag (1-2 hours)
9. **INFRA-026**: Finalize Custom CHPP Migration (1 hour)

**Execute P1 tasks instead of this archived task.** See detailed plan in `.project/plans/refactor-004-replace-pychpp.md`.

**Original Problem Statement**:
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

### [TEST-004-005] Blueprint & Utils Test Coverage
**Status**: 🎯 Ready to Execute | **Effort**: 4-6 hours | **Priority**: P3 | **Impact**: Foundation reliability validation
**Dependencies**: None (blueprint migration complete) | **Strategic Value**: Validation of blueprint architecture and shared utilities

**Problem Statement**:
Recent blueprint migration created new code organization but test coverage dropped to 35% (target: 80%). The new blueprint modules and migrated utilities need comprehensive test coverage to ensure:
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
   - Test shared utility functions (calculateContribution, player_diff, create_page)

**Acceptance Criteria**:
- Blueprint module coverage increases to >70%
- Utils module coverage increases to >70%
- All blueprint routes have basic functionality tests
- Critical utility functions comprehensively tested
- Authentication and session handling tested
- Error scenarios properly covered
- make test-fast achieves >80% overall coverage
- No existing functionality regressions
- Mock CHPP responses for isolated testing

**Technical Approach**:
- Extend existing test_blueprint_routes_focused.py for blueprints
- Create dedicated test_utils.py module for utilities
- Mock Flask app context for template testing
- Use pytest fixtures for authentication setup
- Mock CHPP API calls for deterministic testing
- Use sample player data for business logic tests
- Leverage existing test infrastructure and patterns

**Expected Outcomes**: Increased confidence in blueprint architecture and utility functions, prevention of regressions, achievement of coverage targets, validated shared code reliability

**Note**: This task consolidates TEST-004 (Blueprint Coverage) and TEST-005 (Utils Coverage) as they share common testing infrastructure and can be executed efficiently together.

---

### [DOC-023] Update TECHNICAL.md Route Architecture
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

*Backlog updated January 26, 2026 with major simplification milestone achieved: Test Infrastructure Excellence complete with coverage contexts implementation (19/22 quality gates passing), P2 Deployment Operations milestone complete (INFRA-018, INFRA-021), redundant task consolidation applied (UI-008/UI-010 → UI-011). Focus: Type sync resolution, security updates. Total: 25+ active tasks across 7 priority levels.*
