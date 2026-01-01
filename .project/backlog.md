
# Project Backlog

> **Reminder:** Regularly update this file as tasks are completed or reprioritized. See project analysis recommendations.

*This backlog is adapted to the new format, preserving all 2.0 planning and requirements. Update as the project evolves.*

## Priority Summary

### COMPLETED
- [x] **[DOC-007] Organize project documentation structure**
	- *Completed*: January 1, 2026 - All .project files created and structured
- [x] **[DOC-008] Integrate advanced development prompts**
	- *Completed*: January 1, 2026 - prompts.json updated with comprehensive workflows
- [x] **[DOC-009] Restructure backlog with typed IDs**
	- *Completed*: January 1, 2026 - All items categorized (DOC, INFRA, TEST, etc.)
- [x] **[INFRA-002] Fix 'make test' dependency setup for new machines**
	- *Completed*: January 1, 2026 - Added UV dependency checking, helpful error messages, config.py creation, and fallback support for systems without UV
- [x] **[DOC-001] Create CHANGELOG.md**
	- *Completed*: January 1, 2026 - CHANGELOG.md created following Keep a Changelog format with comprehensive 2.0.0 documentation; referenced in README.md
- [x] **[DOC-002] Remove ROTWA-specific language from documentation**
	- *Completed*: January 1, 2026 - All ROTWA references removed from HTStatus documentation; project focus is clear and consistent with enhanced HTStatus branding

### HIGH Priority
- [ ] **[TEST-002] Resolve remaining integration test failures**
	- *Acceptance Criteria*: All 34 tests pass consistently; integration test suite provides reliable CI/CD foundation.
	- *Dependencies*: None (isolated to 2 specific complex integration tests)
	- *Status*: **Ready for Implementation** - Testing infrastructure stable, specific tests identified for refinement
	- *Progress Note*: 32/34 tests passing (94% success), 2 integration tests need fixture or environment refinement
- [ ] **[INFRA-001] Implement environment configuration templates for deployment**
	- *Acceptance Criteria*: Templates exist for all required environments; setup is documented in README and plan.md.
	- *Dependencies*: None
	- *Status*: **Ready for Implementation** - Benefits from established config.py foundation with environment-specific classes
	- *Implementation Note*: Can build upon existing Config/TestConfig/ProductionConfig structure
- [ ] **[TEST-001] Add automated tests for core features**
	- *Acceptance Criteria*: Test suite covers all critical app logic; `make test` passes with >80% coverage.
	- *Dependencies*: None (infrastructure ready)
	- *Status*: **Ready for Implementation** - Professional testing infrastructure in place (94% current success rate)
	- *Progress Note*: Testing foundation established, SQLAlchemy fixtures modernized, quality gates operational
- [ ] **[SEC-001] Security & Quality Remediation (Task 2.0.1)**
	- *Acceptance Criteria*: All critical security and code quality issues are resolved; linter and security checks pass.
	- *Dependencies*: TEST-001 (expanded test coverage recommended)
	- *Status*: **Partially Ready** - Code quality tools operational, security scanning needs expanded test foundation
	- *Progress Note*: Quality gates implemented (ruff, black, mypy), 91 code quality issues identified with improvement path
- [ ] **[DOC-003] Add cross-references between related .project files**
	- *Acceptance Criteria*: Logical connections between .project files are linked; navigation between related documents is improved.
	- *Dependencies*: None
	- *Status*: **Ready for Implementation** - Documentation cleanup complete, optimal time to enhance cross-references
	- *Implementation Note*: Build upon clean HTStatus branding foundation established by DOC-002

### MEDIUM Priority
- [ ] **[DOC-004] Enhance progress tracking with specific metrics**
	- *Acceptance Criteria*: Progress.md includes specific milestone dates, completion percentages, and measurable metrics.
	- *Dependencies*: None
- [ ] **[DOC-005] Improve documentation (user guides, API docs)**
	- *Acceptance Criteria*: User and API documentation is complete and up to date in README and docs.
	- *Dependencies*: None
- [ ] **[DOC-010] Add testing requirements to development prompts**
	- *Acceptance Criteria*: All relevant prompts in prompts.json include appropriate testing validation steps; testing requirements reference existing Makefile commands.
	- *Dependencies*: None (enhancement to existing documentation)
- [ ] **[FEAT-001] Enhance data visualization features**
	- *Acceptance Criteria*: New or improved charts/visuals are available in the UI; user feedback is positive.
	- *Dependencies*: TEST-001 (test foundation)
- [ ] **[PROJ-001] Resume Task 3+ (after functional web app requirement)**
	- *Acceptance Criteria*: Next phase tasks are unblocked and started after web app is functional.
	- *Dependencies*: SEC-001 (remediation)

### LOW Priority
- [ ] **[DOC-006] Clarify architecture documentation purposes**
	- *Acceptance Criteria*: Clear distinction between architecture.md and TECHNICAL.md; no overlapping content or consolidated appropriately.
	- *Dependencies*: None
- [ ] **[REFACTOR-001] Refactor code for maintainability**
	- *Acceptance Criteria*: Codebase is cleaner, more modular, and easier to maintain; no major regressions.
	- *Dependencies*: TEST-001 (test foundation)
- [ ] **[RESEARCH-001] Explore additional integrations (e.g., external APIs)**
	- *Acceptance Criteria*: Feasibility of new integrations is documented; proof-of-concept or plan exists.
	- *Dependencies*: None

---

*Update this backlog regularly to reflect current priorities and completed tasks. See PLAN.md for detailed status and dependencies.*