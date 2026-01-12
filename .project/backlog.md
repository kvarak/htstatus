# Project Backlog

## Quick Navigation
🔗 **Related**: [Plan](plan.md) • [Progress](progress.md) • [Goals](goals.md) • [Architecture](architecture.md)
📊 **Project Health**: 97/100 • 173/173 Tests ✅ • 17 Tasks Complete • **Repository Analysis Complete** ✅

*Repository analysis complete with excellent health score! New strategic tasks identified from comprehensive analysis. Testing infrastructure enables confident development.*

## Backlog Management Rules

**For AI Agents**: Use [Priority Summary](#priority-summary) for automatic next-task identification. Navigate to [Task Catalog](#task-catalog) for full details.

**For Humans**: Priority tiers indicate execution readiness. Quick wins in Tier 1-2, strategic work in Tier 3-4.

**Task Status Legend**:
- ✅ **COMPLETED** - Task finished and validated
- 🎯 **Ready to Execute** - No blockers, can start immediately
- 🔒 **Blocked** - Waiting on dependencies
- 📋 **In Analysis** - Requirements being refined

**Task ID Format**: [TYPE-###] where TYPE = FEAT, DOC, INFRA, TEST, SEC, PROJ, RESEARCH, MONITOR, ORG

## Priority Summary

### 🚨 **CRITICAL: Application Broken** (Fix Immediately)
1. **[INFRA-011] Fix Broken /login Route** → [Details](#infra-011-fix-broken-login-route) | *🔥 CRITICAL - 10-15 min - App cannot authenticate users*

### 🎯 **Tier 1: Quick Wins** (Execute First - Low Effort, High Value)
2. **[DOC-015] Fix Architecture Placeholder** → [Details](#doc-015-fix-architecture-placeholder) | *15 min - Remove incomplete section*
3. **[DOC-018] Config.py Template & Documentation** → [Details](#doc-018-configpy-template--documentation) | *20-30 min - Create root template matching actual structure*
4. **[DOC-017] Document Deployment Process** → [Details](#doc-017-document-deployment-process) | *30-45 min - Document push.sh & Raspberry Pi deployment*
5. **[DOC-016] Document Root Scripts** → [Details](#doc-016-document-root-scripts) | *15 min - Clarify command.sh purpose*
6. **[DOC-004] Progress Metrics** → [Details](#doc-004-progress-metrics) | *1 hour - Add measurable tracking*
7. **[DOC-010] Testing Prompts** → [Details](#doc-010-testing-prompts) | *1 hour - Workflow integration*

### 🚀 **Tier 2: High Impact Development** (Execute Next - Strategic Value)
8. **[INFRA-006] Schema Validation** → [Details](#infra-006-database-schema-validation) | *Critical - Resolve 11 test failures*
9. **[INFRA-007] Model Schema Fixes** → [Details](#infra-007-model-schema-fixes) | *Foundation for schema validation*
10. **[FEAT-002] PWA Development** → [Details](#feat-002-mobile-first-pwa) | *Game-changing mobile experience*
11. **[SEC-001] Production Readiness** → [Details](#sec-001-production-readiness) | *91 quality issues + security*

### 📚 **Tier 3: Strategic Enhancement** (Medium Priority - Foundation Building)
12. **[DOC-011-API] API Documentation** → [Details](#doc-011-api-api-documentation) | *Developer experience*
13. **[DOC-005] User Documentation** → [Details](#doc-005-user-documentation) | *User adoption*
14. **[INFRA-008] Type Sync Validation** → [Details](#infra-008-type-sync-validation) | *Prevent type drift*
15. **[INFRA-009] Dependency Strategy** → [Details](#infra-009-dependency-strategy) | *Maintenance planning*
16. **[INFRA-010] Audit Non-Tracked Files** → [Details](#infra-010-audit-and-cleanup-non-tracked-files) | *Repository hygiene*

### 🔮 **Tier 4: Future Opportunities** (Long-term Strategic)
17. **[FEAT-001] Data Visualization** → [Details](#feat-001-data-visualization-features) | *Enhanced charts*
18. **[REFACTOR-001] Code Maintainability** → [Details](#refactor-001-code-maintainability) | *Technical debt*
19. **[RESEARCH-001] Additional Integrations** → [Details](#research-001-additional-integrations) | *Expansion*
20. **[PROJ-001] Advanced Development** → [Details](#proj-001-advanced-development-phase) | *After SEC-001*

---

## Task Catalog

### 🚨 CRITICAL: Application Broken

#### [INFRA-011] Fix Broken /login Route
**Priority**: 🔥 CRITICAL - Application Cannot Authenticate Users | **Status**: 🎯 Ready to Execute
**Estimated Time**: 10-15 minutes
**Dependencies**: None
**Strategic Value**: Application is non-functional without working authentication
**Problem**:
- /login route returns 404 "Not Found" error
- Users cannot log in to application
- Application is effectively broken for all users
**Root Cause Analysis**:
- Factory pattern ([app/factory.py](app/factory.py#L68)) only registers Blueprint from routes_bp.py
- Legacy routes.py (1,993 lines) containing actual OAuth login logic is never imported
- Blueprint routes_bp.py has stub routes that only render templates (no business logic)
- Incomplete Blueprint migration left app in broken state
**Technical Details**:
- routes.py line 1093: Full OAuth login implementation with GET/POST methods
- routes_bp.py line 143: Stub route removed (previously only accepted GET)
- factory.py setup_routes() only imports/registers routes_bp.py Blueprint
- No import statement for legacy routes.py anywhere
**Solution Options**:
1. **Quick Fix (10 min)**: Import and register legacy routes.py in factory.py alongside Blueprint
2. **Proper Fix (2-4 hours)**: Complete Blueprint migration by moving OAuth logic to routes_bp.py
**Recommended Immediate Action**: Option 1 - Restore functionality, plan full migration as separate task
**Implementation (Quick Fix)**:
```python
# In app/factory.py setup_routes()
# After Blueprint registration, import legacy routes to make them available
from app import routes  # This registers @app.route decorators
```
**Acceptance Criteria**:
- /login route responds with login page (GET)
- /login accepts POST with OAuth authentication
- Users can successfully log in
- All existing tests pass
**Follow-up Task**: Create REFACTOR-002 for complete Blueprint migration

### 🎯 Tier 1: Quick Wins (Low Effort, High Value)

#### [DOC-015] Fix Architecture Placeholder
**Priority**: Low Impact, Very Low Effort (15 min) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: Documentation completeness
**Implementation**:
- Remove "...existing code..." placeholder at line 80 in architecture.md
- Complete file structure section or remove incomplete content
- Ensure all architectural descriptions are accurate and complete
**Rationale**: Discovered during repository analysis - minor documentation gap affecting professionalism

#### [DOC-018] Config.py Template & Documentation
**Priority**: Low Impact, Very Low Effort (20-30 min) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: Developer onboarding, configuration clarity
**Implementation**:
- Create `config.py.example` at project root matching actual simple structure
- Template should mirror current config.py (58 lines, 2 classes: Config and TestConfig)
- Update README.md Configuration section to reference the correct simplified template
- Clarify that environments/config.py.example is for advanced multi-environment setup
- Add clear comments explaining CONSUMER_KEY/CONSUMER_SECRETS source (https://chpp.hattrick.org/)
**Context**:
- Current config.py uses simple 2-class structure (Config, TestConfig)
- Documentation references more complex 4-class system with get_config() function
- No config.py.example exists at root to match actual structure
- Someone recreating config.py from docs would create wrong version
**Issue Found**:
- README.md lines 125-250 describe DevelopmentConfig, StagingConfig, ProductionConfig, get_config()
- environments/config.py.example has 104 lines with 4 config classes
- Actual config.py has 58 lines with only 2 classes and no get_config() function
- Documentation mismatch prevents accurate config recreation
**Acceptance Criteria**:
- Root config.py.example exists matching actual 58-line structure
- README.md Configuration section updated with correct instructions
- Distinction between simple (root) and advanced (environments/) templates documented
- Developer can recreate working config.py from template without seeing original

#### [DOC-016] Document Root Scripts
**Priority**: Low Impact, Very Low Effort (15 min) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: Code clarity, maintenance
**Implementation**:
- Add purpose comment headers to command.sh (if actively used)
- Document usage in README or mark as deprecated
- Note: push.sh documented separately in DOC-017
**Rationale**: Discovered during repository analysis - command.sh purpose unclear
**Note**: command.sh is generated dynamically by push.sh deployment script

#### [DOC-017] Document Deployment Process
**Priority**: Medium Impact, Very Low Effort (30-45 min) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: Knowledge preservation, risk mitigation, developer onboarding
**Implementation**:
- Add comprehensive inline comments to push.sh explaining deployment process
- Document local network deployment architecture in TECHNICAL.md:
  - Raspberry Pi target (glader.local)
  - SSH-based deployment process
  - Command.sh generation and execution
  - Major vs standard deployment (SECRET_KEY regeneration)
- Add deployment section reference in README.md
- Note: Document as-is without changing current deployment process
**Context**:
- push.sh deploys HTStatus to local network Raspberry Pi (glader.local)
- Automates git pull, migrations, dependency updates, application reload
- Critical production process currently undocumented
- Future infrastructure improvements possible but current process needs documentation
**Acceptance Criteria**:
- push.sh has header comments explaining purpose and usage
- TECHNICAL.md has "Deployment Architecture" section
- README.md references deployment documentation
- Both standard and major deployment modes documented
**Rationale**: Repository analysis identified push.sh as undocumented; production deployment knowledge must be preserved
**Implementation**:
- Add milestone completion dates to progress.md
- Track completion percentages for major initiatives
- Implement measurable metrics for velocity tracking
- Create progress visualization framework

#### [DOC-010] Testing Prompts
**Priority**: Medium Impact, Low Effort (1 hour) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: Workflow consistency, regression prevention
**Implementation**:
- Add testing validation steps to prompts.json workflows
- Reference `make test` commands in development prompts
- Establish testing gates for execute/review prompts

---

### 🚀 Tier 2: High Impact Development (Strategic Value)

#### [INFRA-006] Database Schema Validation
**Priority**: High Impact, Low Effort (2-3 hours) | **Status**: 🎯 Ready to Execute
**Dependencies**: INFRA-007 (schema fixes - execute together)
**Strategic Value**: **CRITICAL** - Prevents production issues, resolves 11 test failures
**Implementation**:
- Automated schema validation tests
- DDL generation verification checks
- DateTime format validation across all models
- Composite primary key constraint verification
- User model attribute consistency validation
**Context**: Repository analysis validated urgency - 11 test failures directly related to schema issues
**Testing**: Must resolve DateTime conflicts, MatchPlay composite keys, User model attributes

#### [INFRA-007] Model Schema Fixes
**Priority**: High Impact, Medium Effort (3-4 hours) | **Status**: 🎯 Ready to Execute
**Dependencies**: None (but enables INFRA-006)
**Strategic Value**: Foundation for reliable schema validation
**Implementation**:
- Fix DateTime format handling in User model (string vs datetime object conflicts)
- Resolve MatchPlay composite primary key autoincrement issues
- Address User model 'id' attribute access inconsistencies
- Ensure consistent date/time handling across all models
**Context**: Identified during DOC-012 validation and repository analysis
**Note**: Execute before or alongside INFRA-006 for maximum effectiveness

#### [FEAT-002] Mobile-First PWA
**Priority**: Very High Impact, Medium Effort (1-2 weeks) | **Status**: 🎯 Ready to Execute
**Dependencies**: None (React + Vite PWA-ready)
**Strategic Value**: Game-changing mobile experience, competitive advantage
**Implementation**:
- Mobile-optimized responsive design
- Progressive Web App capabilities (offline functionality)
- Real-time match management on mobile devices
- Touch-optimized player management interface
**Foundation**: React frontend ready, Vite supports PWA out-of-box

#### [SEC-001] Production Readiness
**Priority**: Very High Impact, High Effort (1-2 weeks) | **Status**: 🎯 Ready to Execute
**Dependencies**: TEST-001 ✅, TEST-003 ✅, INFRA-005 ✅ (all completed)
**Strategic Value**: Production deployment enablement, security hardening
**Implementation**:
- Address 91 ruff linting issues (56 auto-fixable)
- Security scanning with bandit and safety tools
- Production configuration validation
- SSL/TLS configuration verification
- Deployment readiness checklist completion
**Blocks**: PROJ-001 (advanced development phase)

---

### 📚 Tier 3: Strategic Enhancement (Foundation Building)

#### [DOC-011-API] API Documentation
**Priority**: Medium Impact, Medium Effort (4-6 hours) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: Developer experience, external integrations
**Implementation**:
- Document all Flask route endpoints in TECHNICAL.md
- Include request/response examples for each endpoint
- Document authentication flows and session management
- Add CHPP API integration patterns
- Consider OpenAPI/Swagger spec for future automation
**Rationale**: Repository analysis identified missing comprehensive API docs
**Note**: New task ID to avoid confusion with completed DOC-011

#### [DOC-005] User Documentation
**Priority**: Medium Impact, Medium Effort (6-8 hours) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: User adoption, onboarding acceleration
**Implementation**:
- User guides for core features
- Screenshots and walkthroughs
- FAQ section for common issues
- Integration with existing README.md

#### [INFRA-008] Type Sync Validation
**Priority**: Medium Impact, Low-Medium Effort (2-4 hours) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: Prevent Python model vs TypeScript type drift
**Implementation**:
- Create validation script comparing models.py to src/types/index.ts
- Detect field mismatches, type differences, missing properties
- Add to CI/CD pipeline or pre-commit hooks
- Document manual sync procedures if automation not feasible
**Rationale**: Repository analysis identified manual sync risk between Python and TypeScript types
**Alternative**: Investigate automated type generation tools

#### [INFRA-009] Dependency Strategy
**Priority**: Medium Impact, Low-Medium Effort (2-3 hours) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: Maintenance planning, security updates
**Implementation**:
- Review Flask-Bootstrap 3.3.7.1 necessity (legacy, used only in old templates)
- Check pychpp for available updates beyond 0.3.12
- Document version pinning strategy (exact `==` vs ranges `>=,<`)
- Create dependency update schedule/policy
- Assess migration path away from legacy dependencies
**Rationale**: Repository analysis found old dependencies and unclear versioning strategy

#### [INFRA-010] Audit and Cleanup Non-Tracked Files
**Priority**: Medium Impact, Low-Medium Effort (2-4 hours) | **Status**: 🎯 Ready to Execute
**Dependencies**: DOC-017 recommended (understand deployment needs first)
**Strategic Value**: Repository hygiene, disk space, security audit, developer clarity
**Implementation**:
- **Phase 1 - Audit**: Complete inventory of non-git-tracked files and directories
  - `env/` - Legacy Python 3.9 virtual environment (likely unused, .venv is current)
  - `data/` - Sample data files (dalby-players.raw 509KB, notes, templates)
  - `htmlcov/` - Coverage reports (should be ignored only, not tracked)
  - Cache directories (__pycache__, .pytest_cache, .ruff_cache) - normal, keep ignored
- **Phase 2 - Verification**: Search codebase for references to potential legacy files
- **Phase 3 - .gitignore Review**: Fix inconsistencies (migrations/ entry misleading)
- **Phase 4 - Cleanup**: Remove verified legacy files, update .gitignore
- **Phase 5 - Validation**: Run `make test` to ensure nothing broken
**Findings**:
- `env/` appears to be legacy venv (replaced by .venv managed by UV)
- `data/dalby-players.*` may be test fixtures - verify before deletion
- `migrations/` in .gitignore but 30 migration files ARE tracked (confusing)
- `htmlcov/` coverage reports probably shouldn't be in repository
**Safety Measures**:
- Create branch before deletions
- Document all findings
- Test after each major deletion
- Keep deletions reversible
**Acceptance Criteria**:
- Complete inventory documented
- No code references to deleted files
- .gitignore corrected and simplified
- Tests pass after cleanup
- Repository cleaner and more maintainable
**Rationale**: Repository analysis identified multiple non-tracked directories; systematic audit needed to distinguish legacy from active files

---

### 🔮 Tier 4: Future Opportunities (Long-term Strategic)

#### [FEAT-001] Data Visualization Features
**Priority**: High Impact, High Effort (2-3 weeks) | **Status**: 🎯 Ready to Execute
**Dependencies**: TEST-001 ✅, TEST-003 ✅, INFRA-005 ✅ (all completed)
**Strategic Value**: Enhanced user experience with data-driven insights
**Implementation**:
- New/improved charts and visualizations in React frontend
- Player skill progression graphs
- Match performance analytics dashboards
- Team comparison visualizations
- Test-driven development with 173-test safety net

#### [REFACTOR-001] Code Maintainability
**Priority**: Medium Impact, High Effort (2-3 weeks) | **Status**: 🎯 Ready to Execute
**Dependencies**: TEST-001 ✅, TEST-003 ✅, INFRA-005 ✅ (all completed)
**Strategic Value**: Technical debt reduction, long-term maintainability
**Implementation**:
- Refactor routes.py (1,992 lines) into modular components
- Extract business logic from routes into service layer
- Improve code organization and separation of concerns
- Confident refactoring enabled by 173 passing tests

#### [RESEARCH-001] Additional Integrations
**Priority**: Medium Impact, Medium Effort (variable) | **Status**: 🎯 Ready to Execute
**Dependencies**: None
**Strategic Value**: Ecosystem expansion, feature enhancement
**Implementation**:
- Research additional Hattrick data sources
- Explore third-party integrations
- Evaluate complementary tools and services
- Document integration opportunities

#### [PROJ-001] Advanced Development Phase
**Priority**: Very High Impact, Variable Effort | **Status**: 🔒 Blocked by SEC-001
**Dependencies**: SEC-001 (production readiness)
**Strategic Value**: Next development cycle with production-ready foundation
**Implementation**:
- Begin advanced feature development after production readiness
- Execute strategic opportunities from plan.md
- Scale application with production deployment experience

---

## Completed Achievements

### ✅ Foundation Excellence (January 2026)

#### Testing Foundation (4 major tasks):
- [x] **[TEST-001]**: Comprehensive testing framework (86 tests, professional infrastructure) - January 2
- [x] **[TEST-003]**: Advanced testing infrastructure (173 tests, strategic coverage) - January 3
- [x] **[INFRA-005]**: Testing execution reliability (transaction cleanup, hanging fixed) - January 3
- [x] **[TEST-002]**: Integration test resolution (100% success rate) - January 2

#### Documentation & Navigation (5 tasks):
- [x] **[DOC-003]**: Cross-reference navigation system - January 2
- [x] **[DOC-011]**: Documentation path updates - January 2
- [x] **[DOC-007]**: Project documentation structure - January 1
- [x] **[DOC-008]**: Advanced development prompts - January 1
- [x] **[DOC-012]**: Comprehensive debugging guide - January 3

#### Infrastructure & Quality (3 tasks):
- [x] **[INFRA-002]**: 'make test' dependency resolution - January 1
- [x] **[INFRA-001]**: Environment configuration templates - January 2
- [x] **[ORG-001]**: Configuration architecture analysis - January 2

#### Project Identity (3 tasks):
- [x] **[DOC-001]**: Professional CHANGELOG.md - January 1
- [x] **[DOC-002]**: HTStatus branding enhancement - January 1
- [x] **[DOC-009]**: Backlog structure with typed IDs - January 1

### Latest Completion: Repository Analysis (January 12, 2026)
- **Comprehensive Health Assessment**: 97/100 project health score
- **File Inventory**: 95 tracked files cataloged and validated
- **Documentation Consistency**: All cross-references verified
- **Configuration Completeness**: Multi-environment setup validated
- **Standards Compliance**: Flask best practices confirmed
- **Gap Identification**: 5 new tasks identified and prioritized
- **Actionable Recommendations**: Tiered priority framework established

---

## Task Management Notes

### Quick Reference
- **Total Tasks**: 18 active + 17 completed = 35 tasks managed
- **Ready to Execute**: 17 tasks (no blockers)
- **Blocked Tasks**: 1 task (PROJ-001 waiting for SEC-001)
- **Completion Rate**: 17 tasks completed in 12 days (January 2026)

### Execution Strategy
1. **Start with Tier 1**: Quick wins build momentum (combined effort: ~3 hours)
2. **Focus on Tier 2**: High-impact development resolves critical issues
3. **Plan Tier 3**: Strategic enhancements during Tier 2 work
4. **Vision Tier 4**: Long-term opportunities after production readiness

### Priority Rationale
- **Tier 1 (Quick Wins)**: Low effort, immediate value, documentation completeness
- **Tier 2 (High Impact)**: Critical infrastructure, production readiness, strategic features
- **Tier 3 (Strategic)**: Foundation building, developer experience, maintenance
- **Tier 4 (Future)**: Long-term value, requires sustained effort, post-production

---

*Backlog restructured January 12, 2026 following comprehensive repository analysis. Priority framework based on effort vs impact analysis.*
