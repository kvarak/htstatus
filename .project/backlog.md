# HattrickPlanner Backlog

**Purpose**: Active development tasks in priority order
**Rule**: Work top to bottom, update status when starting (🚀 ACTIVE) or completing (✅ COMPLETE)
**Task IDs**: Use `./scripts/get-next-task-id.sh <TYPE>` to get next sequential ID (e.g., `./scripts/get-next-task-id.sh FEAT` → `FEAT-020`)
**Task Counts**: Use `uv run python scripts/count_tasks_by_priority.py --line` to get current task distribution for updates
**📚 CHPP Reference**: For CHPP API development, see [docs/chpp/](../docs/chpp/) for comprehensive API documentation

**Recent Organization** (February 5, 2026): CHPP API Documentation Foundation COMPLETED - Created comprehensive reference for 21/79 CHPP APIs with implementation examples, authentication patterns, and strategic usage guidelines. All P2 features now have complete API coverage: matches-basic, matchorders, leaguedetails, players, playerdetails, currentbids, translations, matchdetails, matchlineup, playerevents, leaguelevels. Ready for confident P2 implementation without API research delays. Quality gates: 8/9 passing (HIGH deployment confidence). **Active: 102 tasks** (P0=0, P1=0, P2=11, P3=8, P4=83)

---

## P0: Production-Breaking 🚨

*No active P0 issues*

## P1: Critical 🔥

*No active P1 issues*

## P2: Features 🎯

- **[FEAT-029]** Matches System Integration and Archive - Restore matches functionality with recent/upcoming match downloads and on-demand archive system → [Details](.project/tasks/FEAT-029.md)
- **[FEAT-031]** Enhanced Match Analytics Through CHPP API - Implement comprehensive match statistics, player performance tracking, and tactical insights using matchdetails, matchlineup, and playerevents APIs → [Details](.project/tasks/FEAT-031.md)
- **[FEAT-008]** Next Game Analyser → [Details](.project/tasks/FEAT-008.md)
- **[FEAT-030]** Series League Table with Next Round Insights - Display complete league standings with tactical insights for upcoming matches → [Details](.project/tasks/FEAT-030.md)
- **[FEAT-010]** Player Comparison Tool (Connected to GitHub Issue #15 - User-requested feature for viewing multiple players side-by-side for comparison analysis) → [Details](.project/tasks/FEAT-010.md)
- **[FEAT-025]** Transfer Current Bid Display (Connected to GitHub Issue #27 - Show current bid amounts for players on transfer market) → [Details](.project/tasks/FEAT-025.md)
- **[FEAT-026]** Batch Player Group Management (Connected to GitHub Issue #23 - Enable bulk group assignment operations for multiple players) → [Details](.project/tasks/FEAT-026.md)
- **[FEAT-027]** Hattrick Language Localization (Connected to GitHub Issue #13 - Translate interface to match user's Hattrick language setting) → [Details](.project/tasks/FEAT-027.md)
- **[FEAT-028]** Player Table Filtering System (Connected to GitHub Issue #10 - Add filtering capabilities to complement existing table sorting) → [Details](.project/tasks/FEAT-028.md)
- **[REFACTOR-036]** Consolidate Activity Tracking Pattern → [Details](.project/tasks/REFACTOR-036.md)
- **[REFACTOR-037]** Optimize User Context Queries → [Details](.project/tasks/REFACTOR-037.md)

## P3: Maintenance 🔧

### Database Protection (Highest Priority)
- **[INFRA-033]** Database Protection Enhancement - Implement hobby-focused backup automation and safety checks → [Details](.project/tasks/INFRA-033.md)
- **[REFACTOR-034]** Database Script Consolidation → [Details](.project/tasks/REFACTOR-034.md)

### Hobby Project Simplification
- **[REFACTOR-049]** Comprehensive Hobby Project Simplification - Consolidate documentation, assets, and configuration (Consolidates REFACTOR-045, 046, 047, 048, DOC-024) → [Details](.project/tasks/REFACTOR-049.md)
- **[REFACTOR-030]** Implement Rate Limiting for CHPP Requests → [Details](.project/tasks/REFACTOR-030.md)
- **[REFACTOR-031]** Clean Up Unused View Functions → [Details](.project/tasks/REFACTOR-031.md)
- **[REFACTOR-032]** Optimize Database Query Performance → [Details](.project/tasks/REFACTOR-032.md)
### User Interface (Hobby-Focused)
- **[UI-013]** Implement Loading States for CHPP Operations → [Details](.project/tasks/UI-013.md)
- **[UI-014]** Add Dark Mode Support → [Details](.project/tasks/UI-014.md)

## P4: Possibilities 🔮

### Recent Critical Review Improvements (February 3, 2026 - Player Modal Layout Enhancement Analysis)

#### Template Architecture Quality & Simplification
- **[REFACTOR-104]** Extract Player Field Display Logic - Replace repeated conditional display logic (nick_name, statement, owner_notes) with reusable Jinja2 macros to eliminate DRY violations (15 min)
- **[UI-018]** Standardize Modal Content Width Constraints - Replace inline max-width styles (450px) with CSS classes following established logical component architecture (30 min)
- **[REFACTOR-105]** Audit Chart.js Responsive Configuration - Standardize Chart.js responsive settings across all implementations to prevent sizing inconsistencies and reduce configuration drift (45 min)

### Recent Critical Review Improvements (February 3, 2026 - BUG-077 Bootstrap Fix Analysis)

#### Bootstrap Architecture & Technical Debt Cleanup
- **[REFACTOR-103]** Complete Bootstrap 4.x Migration and Flask-Bootstrap Cleanup - Remove Flask-Bootstrap dependency entirely, standardize all templates to Bootstrap 4.x syntax, eliminate version conflicts discovered during player details fix (2 hours)

### Recent Critical Review Improvements (February 3, 2026 - Responsive Tutorial Help Button Analysis)

#### Responsive Design & Architecture Simplification
- **[REFACTOR-086]** Replace Responsive JavaScript with CSS-Only Solution - Replace 24-line JavaScript resize listeners and navbar-toggler detection with simple CSS media queries matching Bootstrap breakpoints (20 min)
- **[DOC-028]** Document Responsive Design Decision Rationale - Record responsive design approach decisions and alternative CSS/JavaScript approaches considered for future reference (15 min)

### Recent Critical Review Improvements (February 3, 2026 - Tutorial Analytics Implementation Review)

#### Tutorial System Quality & Architecture
- **[REFACTOR-102]** Consolidate Chart Creation Patterns - Replace repetitive Chart.js implementations in debug.html with factory pattern to eliminate ~70% of JavaScript duplication (45 min)
- **[TEST-012]** Add Unit Tests for Tutorial Analytics - Create test coverage for tutorial tracking logic, analytics calculations, and event mapping missing from recent implementation (60 min)
- **[DOC-029]** Document Tutorial Analytics Data Model - Define tutorial analytics data model and intended usage patterns to guide future development and prevent schema drift (30 min)

### Recent Critical Review Improvements (February 2, 2026 - TEST-010 Coverage Expansion Analysis)

#### Test Infrastructure Over-Engineering & Quality Issues
- **[REFACTOR-101]** Simplify Coverage Reporting - Replace 211-line coverage_report.py with simple Makefile targets using built-in coverage tools and basic shell commands (30 min)

### Recent Critical Review Improvements (February 2, 2026 - TEST-010 Test Coverage Analysis)

#### Test Infrastructure Quality & Consolidation
- **[REFACTOR-099]** Consolidate Authentication Test Fixtures - Move all authentication fixtures to conftest.py, eliminate per-file duplication, use single app configuration pattern (20 min)
- **[TEST-011]** Fix Failing Test Infrastructure (CONSOLIDATED: includes BUG-076) - Resolve actual 500 errors in main/team routes, fix model registry issues, address template rendering problems rather than masking with defensive test assertions (60 min)
- **[REFACTOR-100]** Test Strategy Realignment - Shift focus from test volume to test value, fix infrastructure before expanding coverage, establish quality thresholds over quantity metrics (30 min)

### Recent Critical Review Improvements (February 2, 2026 - JavaScript Architecture Analysis)

#### JavaScript Architecture Quality & Simplification
- **[REFACTOR-096]** Simplify Chart Utilities Architecture - Evaluate if HattrickCharts class is necessary or if simple configuration objects/functions would reduce complexity while maintaining DRY benefits (30 min)
- **[REFACTOR-097]** Backend Chart Data Preparation - Move repetitive skill data preparation loops from templates to view layer, returning pre-formatted chart data structures (45 min)
- **[REFACTOR-098]** JavaScript Architecture Simplification Study - Compare current multi-file approach vs single app.js with modules for maintainability and loading performance in hobby project context (30 min)

### Recent Critical Review Improvements (February 2, 2026 - CSS Logical Architecture Analysis)

#### CSS Architecture Simplification & Quality
- **[REFACTOR-093]** Evaluate CSS Architecture Simplification - Consider consolidating ui-components.css, utilities.css, and layout.css into a single reusable-components.css file to reduce file count while preserving logical organization for complex features (15 min)
- **[REFACTOR-094]** CSS Pattern Consolidation - Standardize color, spacing, and border patterns across all component files using CSS variables and shared utility patterns to eliminate duplication (30 min)
- **[REFACTOR-095]** CSS Architecture Simplification Experiment - Create a 3-file alternative (commons.css, timeline.css, formations.css) and compare maintenance overhead vs organizational benefits for hobby project context (45 min)

### Recent Critical Review Improvements (February 2, 2026 - INFRA-085 Error Logging Analysis)

#### Error Logging Simplification & Quality
- **[REFACTOR-087]** Simplify Error Logging Model - Reduce ErrorLog model from 9 fields to essential fields only (timestamp, message, stack_trace) to eliminate over-engineering (15 min)
- **[INFRA-086]** Add Error Log Rotation/Cleanup - Implement automatic cleanup mechanism to prevent unbounded database growth in production (30 min)
- **[REFACTOR-088]** Split Debug Route Responsibilities - Separate user administration from error management to improve separation of concerns (/admin/errors route) (30 min)
- **[TEST-083]** Add Error Logging Test Coverage - Comprehensive test coverage for error logging functionality missing from recent implementation (45 min) → **CONSOLIDATED INTO TEST-010**
- **[FEAT-024]** Error Rate Limiting/Deduplication - Add protection against log flooding from same error to prevent database abuse (20 min)
- **[REFACTOR-089]** Replace Production Environment Check - Use configurable logging levels instead of hard-coded production-only activation (15 min)

### Recent Critical Review Improvements (February 2, 2026 - BUG-075 Template Architecture Analysis)

#### Template Architecture & Flask-Bootstrap Improvements
- **[REFACTOR-090]** Consolidate Error Template Pattern - Remove error.html template and modify main.html to conditionally render route-dependent elements only when routes are available, eliminating template duplication (20 min)
- **[REFACTOR-091]** Isolate Flask-Bootstrap Dependency - Move Flask-Bootstrap initialization to a conditional plugin pattern so the core app can function without it during testing (30 min)
- **[REFACTOR-092]** Template Architecture Audit - Systematic review of all Jinja2 templates for inheritance optimization, duplicate content elimination, and consistent component patterns (45 min)

### Recent Critical Review Improvements (February 1, 2026 - Changelog System Over-Engineering Analysis)

#### Test Coverage & Quality Priority
- **[INFRA-084]** Resolve Dependency Security Warnings - Address 13 dependency warnings identified in security scan, update vulnerable packages or document acceptable risk (60 min)

#### Simplification Opportunities
- **[REFACTOR-028]** Simplify Changelog System - Replace JSON-based changelog with static CHANGELOG.md, remove bash generation scripts and debug page complexity (30 min)
- **[REFACTOR-085]** Remove Unused Script Arguments - Fix broken usage instructions in scripts/ directory (`python` → `uv run python`) and remove dead debugging code (15 min)
- **[REFACTOR-086]** Eliminate Changelog Animation Complexity - Replace 80+ lines of CSS transitions and JavaScript for debug page with simple show/hide toggle (20 min)

### Recent Critical Review Improvements (February 1, 2026 - FEAT-019 Timeline Analysis)

#### Feature Implementation Quality
- **[FEAT-019]** Player Skill Changes - 4 Week Timeline on Player Details Page → [Details](.project/tasks/FEAT-019.md) - Retry implementation with better browser compatibility testing and simplified approach
- **[REFACTOR-083]** Remove Orphaned Timeline Utility - Clean up `get_team_timeline()` function from utils.py if not needed for other features (15 min)
- **[TEST-082]** Improve Test Coverage for Template Changes - Address test coverage regression to 41.7% from recent template modifications (45 min)

### Recent Critical Review Improvements (January 31, 2026 - FEAT-023 Session Management)

#### Quality & Testing Improvements
- **[REFACTOR-081]** Simplify PWA session persistence - Replace 195-line JavaScript solution with server-side session configuration investigation (30 min)
- **[REFACTOR-082]** Evaluate Cookie Consent Necessity - Research if hobby project actually requires cookie consent for essential authentication cookies (15 min)
- **[TEST-081]** Add PWA session persistence tests - Create proper test coverage for session management JavaScript (45 min)
- **[INFRA-082]** Investigate Server-Side Session Configuration - Research Flask session cookie settings for PWA compatibility before complex client-side solutions (30 min)

### Recent Critical Review Improvements (January 30, 2026 - Team Model Analysis)

#### Architecture & Testing Quality
- **[TEST-070]** Team Model Comprehensive Test Coverage - Add tests for Team model creation, competition data updates, error handling, and database constraints (60 min)
- **[REFACTOR-072]** Eliminate Circular Import Anti-Pattern - Restructure model imports to avoid `from models import Team` inside functions in stats.py and team.py (30 min)
- **[REFACTOR-073]** Simplify Team Competition Data Storage - Replace 9-parameter update method with JSON field or upsert pattern for simpler data management (45 min)
- **[BUG-074]** Add Transaction Safety for Team Data Storage - Wrap team competition data updates in proper database transactions with rollback handling (30 min)

### Recent Critical Review Improvements (January 30, 2026 - Consolidation)

#### Simplification & Technical Debt (UI & Database)
- **[REFACTOR-066]** Simplify Admin Feedback Count Queries - Replace complex SQLAlchemy exists() subqueries with simple COUNT/GROUP BY for hobby project scale <50 items (15 min)
- **[REFACTOR-067]** Extract Navigation Component Logic - Move admin indicator conditional logic from Jinja2 templates to view layer for better testability (30 min)
- **[REFACTOR-068]** Simplify Admin Feedback Test Mocking - Replace complex 15-line SQLAlchemy mocks with simple fake data for hobby project testing (20 min)
- **[REFACTOR-065]** Simplify Feedback Vote Caching - Remove premature optimization (update_vote_score method); use simple query count for hobby project scale <50 items (15 min)

#### Testing & Architecture Quality
- **[TEST-037]** Add Blueprint Route Testing Infrastructure - Enhance conftest.py to support blueprint testing, add route tests for feedback routes (list, new, detail, vote, comment, status) - 0% coverage currently (60 min)
- **[REFACTOR-063]** Organize Template Directory Structure - Move legacy templates into subdirectories for consistent organization (30 min)
- **[DOC-028]** Consolidate CHPP Documentation - Merge 168-line CHPP-ENFORCEMENT.md into TECHNICAL.md to reduce documentation redundancy (30 min)

### Recent Critical Review Improvements (January 29, 2026)

#### Formation System & Architecture Improvements
- **[REFACTOR-058]** Simplify calculateContribution Function - Normalize position inputs to single format, remove dual-mode complexity (45 min)
- **[REFACTOR-059]** Extract Frontend Formation API - Replace JavaScript position calculations with API endpoints to eliminate code duplication (60 min)
- **[REFACTOR-060]** Externalize Position Configuration - Move formation templates and skill weightings from hardcoded dictionaries to JSON/YAML config (30 min)
- **[TEST-036]** Comprehensive calculateContribution Test Coverage - Add missing test coverage for position code mapping and tactical variations (45 min)
- **[REFACTOR-061]** Blueprint Architecture Review - Systematic analysis of all blueprints for consistency and logical responsibility boundaries (90 min)
- **[DOC-022]** Architecture Decision Records - Document rationale for blueprint separation, calculation approaches, and frontend business logic decisions (30 min)

### Previously Identified Improvements

#### Test Isolation & Architecture (from simplification review)
- **[REFACTOR-028]** Evaluate Model Registry Necessity - Assess whether the model registry pattern is justified for this hobby project or if simpler import restructuring would suffice (30 min) → [Details](.project/tasks/REFACTOR-028.md)
- **[TEST-034]** Focus Coverage on Business Logic - Prioritize test coverage for blueprint routes (auth, main, team, matches, training) over utility functions (60 min)
- **[REFACTOR-029]** Consolidate Model Import Patterns - Choose single approach (registry OR direct imports) to eliminate dual maintenance paths (45 min)
- **[DOC-018]** Document Import Architecture Decision - Record why the model registry pattern was chosen over alternatives for future reference (15 min)

#### Authentication & User Session Issues
- **[REFACTOR-050]** Authentication Flow Analysis - Investigate why authenticated sessions reference non-existent users (root cause of BUG-011)
- **[REFACTOR-051]** Systematic User Query Audit - Review all User.filter_by() patterns for consistency and safety
- **[FEAT-018]** Automatic User Creation Strategy - Ensure user records exist for all authenticated sessions
- **[REFACTOR-052]** Consolidate Repetitive File Processing Patterns - Merge fileformat and fileformat-fix rule processing loops
- **[REFACTOR-053]** Make Coverage Thresholds Configurable - Replace hardcoded 50% with environment-specific settings
- **[REFACTOR-054]** Unified Quality Gate Architecture - Merge test-coverage-files and test-python into single comprehensive test gate
- **[REFACTOR-055]** Optimize Quality Intelligence Script - Single-pass JSON parsing instead of multiple file reads per gate
- **[REFACTOR-056]** Filesystem-First File Discovery - Replace git ls-files with filesystem discovery to eliminate existence checks

### Radical Innovation Ideas (January 30, 2026 - Outside-the-Box Analysis)

#### Architecture Simplification Experiments
- **[REFACTOR-075]** Blueprint Consolidation Experiment - Prototype merging 8 blueprints into 3 core modules (auth+main, hattrick data, community) to reduce complexity (90 min)
- **[REFACTOR-076]** JSON Storage Feasibility Study - Analyze replacing database with file-based JSON storage for hobby project scale <100 players per user (60 min)
- **[INFRA-077]** Static Site Generation Prototype - Experiment with daily HTML generation approach to eliminate deployment complexity (120 min)

#### Quality vs Velocity Balance
- **[REFACTOR-078]** Essential Feature Audit - Systematic review of which features justify their maintenance burden in hobby project context (45 min)
- **[INFRA-079]** Quality Gate Simplification - Consolidate 7 quality gates into essential-only checks to improve development velocity (30 min)

### Core Hattrick Features (Aligned with Geek Audience)
- **[FEAT-016]** Alternative Leadership Indicators (30 min) - Replace complex charts with simple metrics → [Details](.project/tasks/FEAT-016.md)
- **[FEAT-017]** User Preference System (60 min) - Store user chart/visualization preferences to avoid future rejections → [Details](.project/tasks/FEAT-017.md)
- **[FEAT-011]** Training Camp Planner → [Details](.project/tasks/FEAT-011.md)

### Simple Improvements
- **[REFACTOR-057]** Replace individual group queries with single JOIN query for performance optimization (15 min)
- **[REFACTOR-059]** Evaluate SQL-level sorting vs Python-level sorting for timeline changes (30 min)
- **[TEST-035]** Create shared test fixture for new player display data structure (20 min)
- **[REFACTOR-038]** Simplify CSS Design System & UI Consistency (Consolidates UI-015, UI-016) → [Details](.project/tasks/REFACTOR-038.md)
- **[REFACTOR-040]** Template Inheritance for Breadcrumb Pattern → [Details](.project/tasks/REFACTOR-040.md)
- **[REFACTOR-041]** Consolidate Debug Scripts & Country Data Migration (Consolidates REFACTOR-039) → [Details](.project/tasks/REFACTOR-041.md)
- **[TEST-008]** Test Coverage Quality Gates → [Details](.project/tasks/TEST-008.md)

---

## Archived (Enterprise Features Removed)

**Rationale**: Following hobby project philosophy redefinition, these tasks exceed hobby project complexity or don't align with Hattrick geek focus:

- **FEAT-012** Mobile App Development - Major complexity addition not aligned with hobby project
- **FEAT-014** Collaborative League Intelligence - Enterprise social features exceed scope
- **FEAT-015** AI-Powered Training Optimization - Over-engineered for hobby project
- **INFRA-030** Add Health Check Endpoints - Enterprise monitoring pattern
- **INFRA-031** Application Metrics Collection - Enterprise observability
- **INFRA-032** Multi-Region Deployment - Enterprise deployment pattern
- **INFRA-037** Add Pre-commit Hooks - May add unnecessary complexity
- **INFRA-024** Re-upgrade to pychpp 0.5.10 + Flask 3.1+ - Deferred until needed

*These may be reconsidered if project scope changes, but currently don't align with hobby project simplicity goals.*
