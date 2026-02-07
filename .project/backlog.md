# HattrickPlanner Backlog

**Task Organization**: Use **numbered Epic structure** (EPIC-XXX) for maintenance tasks - related tasks grouped under Epic goals (🎯) with smaller actionable increments (15-90 min). All P3 tasks must be under an Epic. This allows working toward bigger objectives while maintaining progress visibility and partial completion capability.
**Rule**: Work top to bottom, update status when starting (🚀 ACTIVE) or completing (✅ COMPLETE)
**Task IDs**: Use `./scripts/get-next-task-id.sh <TYPE>` to get next sequential ID (e.g., `./scripts/get-next-task-id.sh FEAT` → `FEAT-032`, `./scripts/get-next-task-id.sh EPIC` → `EPIC-011`)
**Task Counts**: Use `uv run python scripts/count_tasks_by_priority.py --line` to get current task distribution for updates
**📚 CHPP Reference**: For CHPP API development, see [docs/chpp/](../docs/chpp/) for comprehensive API documentation

**Recent Organization** (February 6, 2026): Implemented numbered EPIC structure requiring all P3 maintenance tasks to be under an Epic. Three-tier priority structure (P1/P2/P3) with aggressive consolidation. 10 focused epics addressing hobby project simplicity goals. Quality gates: 6/9 passing (MODERATE deployment confidence). Test coverage at 48.2% after test infrastructure creation. **Active: 93 tasks** (P1=0, P2=7, P3=86)

---

## P1: Critical 🔥

*No active P1 issues*

## P2: Features 🎯

- **[FEAT-008]** Next Game Analyser → [Details](.project/tasks/FEAT-008.md)
- **[FEAT-030]** Series League Table with Next Round Insights - Display complete league standings with tactical insights for upcoming matches → [Details](.project/tasks/FEAT-030.md)
- **[FEAT-025]** Transfer Current Bid Display (Connected to GitHub Issue #27 - Show current bid amounts for players on transfer market) → [Details](.project/tasks/FEAT-025.md)
- **[FEAT-027]** Hattrick Language Localization (Connected to GitHub Issue #13 - Translate interface to match user's Hattrick language setting) → [Details](.project/tasks/FEAT-027.md)
- **[UI-014]** Add Dark Mode Support - Implement theme switching between dark mode and light mode with user preference persistence → [Details](.project/tasks/UI-014.md)
- **[REFACTOR-036]** Consolidate Activity Tracking Pattern → [Details](.project/tasks/REFACTOR-036.md)
- **[REFACTOR-037]** Optimize User Context Queries → [Details](.project/tasks/REFACTOR-037.md)

## P3: Maintenance 🔧

### **EPIC-001: Critical Database & Infrastructure** 🎯
*Goal: Essential database protection and security foundation for hobby project*

- **[TEST-113]** Restore Database Test Coverage - Add comprehensive tests for db_utils.py module and database scripts to restore 50%+ coverage threshold (60 min)
- **[INFRA-084]** Resolve Dependency Security Warnings - Address 13 dependency warnings identified in security scan, update vulnerable packages or document acceptable risk (60 min)
- **[BUG-074]** Add Transaction Safety for Team Data Storage - Wrap team competition data updates in proper database transactions with rollback handling (30 min)

### **EPIC-002: Hobby Project Simplification** 🎯
*Goal: Consolidate documentation, assets, and configuration for hobby project maintainability*

- **[REFACTOR-049]** Comprehensive Hobby Project Simplification - Consolidate documentation, assets, and configuration (Consolidates REFACTOR-045, 046, 047, 048, DOC-024) → [Details](.project/tasks/REFACTOR-049.md)
- **[DOC-032]** Consolidate and Reduce Documentation Overhead - Reduce project docs from 66 to <40 files, preserve CHPP reference docs, merge setup instructions → [Details](.project/tasks/DOC-032.md)
- **[REFACTOR-109]** Remove Test Stub Waste and TODO Overhead - Remove test files with only TODO comments, eliminate false coverage signals → [Details](.project/tasks/REFACTOR-109.md)
- **[INFRA-088]** Simplify Configuration Complexity for Hobby Scale - Consolidate Docker configs, simplify environment variables, streamline Makefile targets → [Details](.project/tasks/INFRA-088.md)
- **[REFACTOR-110]** Evaluate and Simplify Blueprint Architecture for Hobby Scale - Right-size blueprint patterns, error handling, and model access for hobby project complexity → [Details](.project/tasks/REFACTOR-110.md)
- **[REFACTOR-030]** Implement Rate Limiting for CHPP Requests → [Details](.project/tasks/REFACTOR-030.md)
- **[REFACTOR-031]** Clean Up Unused View Functions → [Details](.project/tasks/REFACTOR-031.md)
- **[REFACTOR-032]** Optimize Database Query Performance → [Details](.project/tasks/REFACTOR-032.md)

### **EPIC-003: User Interface Enhancement** 🎯
*Goal: Essential UI improvements focused on hobby project user experience*

- **[UI-013]** Implement Loading States for CHPP Operations → [Details](.project/tasks/UI-013.md)
- **[UI-019]** Formation Page Visual and Interaction Enhancements - Add hover tooltips to assigned players, fix overall rating calculation to include empty positions, and color-code position effectiveness → [Details](.project/tasks/UI-019.md)

### **EPIC-004: Test Infrastructure & Security** 🎯
*Goal: Essential testing foundation and security for hobby project*

- **[REFACTOR-086]** Implement Progressive Enhancement Fallback for Chart Management - Add graceful fallback for disabled JavaScript, server-side state management option for chart functionality (15 min)
- **[TEST-011]** Add Comprehensive Test Coverage for Simplified Debug Chart Functionality - Create test suite for admin preferences API, event delegation patterns, drag-and-drop state persistence (45 min)
- **[REFACTOR-113]** Replace Skipped Test Infrastructure with Simple Integration Tests - Remove all @pytest.mark.skip decorators and replace with straightforward tests that don't require complex mocking, focusing on 2.2% coverage gap closure using real database fixtures (30 min)
- **[REFACTOR-099]** Consolidate Authentication Test Fixtures - Move all authentication fixtures to conftest.py, eliminate per-file duplication (20 min)
- **[TEST-037]** Add Blueprint Route Testing - Enhance conftest.py for blueprint testing, add route tests for feedback routes (60 min)
- **[REFACTOR-114]** Test Pattern Standardization - Analyze existing working tests (test_db_utils, test_training_utils) and establish consistent patterns for new test creation, eliminate environment-specific failures (45 min)
- **[TEST-116]** Strategic Coverage Gap Analysis - Identify specific functions/branches representing the 2.2% gap between 48.2% and 50% threshold, prioritize by implementation complexity (15 min)
- **[REFACTOR-100]** Test Strategy Realignment - Establish quality thresholds over quantity metrics, fix infrastructure before expanding coverage (30 min)
- **[REFACTOR-108]** Implement Consistent API Validation Patterns - Add comprehensive input validation, rate limiting, and consistent error responses across all new API endpoints to prevent bypass vulnerabilities (90 min)

### **EPIC-005: Database Optimization** 🎯
*Goal: Optimize database architecture and queries for hobby project scale*

- **[REFACTOR-106]** Simplify Match Model Schema with Analytics Table - Refactor Match model into lean core table (teams, datetime, score, type) with separate MatchAnalytics table for optional enhanced data (90 min)
- **[INFRA-087]** Add Match Analytics Database Indexes - Create indexes on Match.attendance, Match.weather_id, Match.home_team_formation (30 min)
- **[REFACTOR-073]** Simplify Team Competition Data Storage - Replace 9-parameter update method with JSON field or upsert pattern (45 min)
- **[REFACTOR-072]** Eliminate Circular Import Anti-Pattern - Restructure model imports to avoid `from models import Team` inside functions (30 min)
- **[REFACTOR-057]** Replace Individual Group Queries with JOINs - Optimize performance with single JOIN queries (15 min)
- **[REFACTOR-066]** Simplify Admin Feedback Count Queries - Replace complex SQLAlchemy exists() with COUNT/GROUP BY for <50 items (15 min)
- **[REFACTOR-065]** Remove Feedback Vote Caching - Remove premature optimization, use simple query count for hobby scale (15 min)
- **[REFACTOR-059]** Optimize Timeline Sorting - Evaluate SQL vs Python sorting for timeline changes (30 min)

### **EPIC-006: Frontend Simplification** 🎯
*Goal: Consolidate templates, CSS/JS architecture for hobby project maintainability*

- **[REFACTOR-103]** Complete Bootstrap 4.x Migration - Remove Flask-Bootstrap dependency, standardize templates to Bootstrap 4.x syntax (120 min)
- **[REFACTOR-092]** Template Architecture Audit - Systematic review of all templates for inheritance optimization and consistent patterns (45 min)
- **[REFACTOR-104]** Extract Player Field Display Logic - Replace repeated conditional logic with reusable Jinja2 macros (15 min)
- **[REFACTOR-090]** Consolidate Error Template Pattern - Remove error.html template, modify main.html for conditional rendering (20 min)
- **[UI-018]** Standardize Modal Content Width - Replace inline max-width styles with CSS classes (30 min)
- **[REFACTOR-063]** Organize Template Directory Structure - Move legacy templates into logical subdirectories (30 min)
- **[REFACTOR-107]** Extract Player Table Features - Separate bulk operations, filtering, and comparison into composable JavaScript modules (60 min)
- **[UI-020]** Progressive Enhancement for Player Table - Add server-side filtering fallbacks and graceful degradation (45 min)
- **[REFACTOR-093]** Evaluate CSS Architecture Simplification - Consider consolidating ui-components.css, utilities.css, layout.css (15 min)
- **[REFACTOR-094]** CSS Pattern Consolidation - Standardize color, spacing, border patterns using CSS variables (30 min)
- **[REFACTOR-086]** Replace Responsive JavaScript with CSS - Replace JS resize listeners with CSS media queries (20 min)
- **[REFACTOR-096]** Simplify Chart Utilities Architecture - Evaluate HattrickCharts class vs simple configuration objects (30 min)
- **[REFACTOR-102]** Consolidate Chart Creation Patterns - Replace repetitive Chart.js implementations with factory pattern (45 min)
- **[REFACTOR-105]** Audit Chart.js Responsive Configuration - Standardize responsive settings across implementations (45 min)

### **EPIC-007: System Quality & Development Tools** 🎯
*Goal: Essential error handling and simplified development tooling*

- **[DOC-028]** Evaluate Chart Persistence Requirements vs Hobby Project Scope - Document design decisions for AdminPreferences data persistence, assess complexity/value tradeoff for hobby project (30 min)
- **[REFACTOR-087]** Simplify Error Logging Model - Reduce ErrorLog from 9 fields to essentials (timestamp, message, stack_trace) (15 min)
- **[INFRA-086]** Add Error Log Rotation/Cleanup - Implement automatic cleanup to prevent database growth (30 min)
- **[REFACTOR-088]** Split Debug Route Responsibilities - Separate user admin from error management (/admin/errors route) (30 min)
- **[FEAT-024]** Error Rate Limiting/Deduplication - Protect against log flooding from same error (20 min)
- **[REFACTOR-089]** Replace Production Environment Check - Use configurable logging levels vs hard-coded activation (15 min)
- **[REFACTOR-101]** Simplify Coverage Reporting - Replace 211-line script with Makefile targets using built-in tools (30 min)
- **[REFACTOR-028]** Simplify Changelog System - Replace JSON-based changelog with static CHANGELOG.md (30 min)
- **[REFACTOR-085]** Remove Unused Script Arguments - Fix script usage docs, remove dead debugging code (15 min)
- **[DOC-022]** Architecture Decision Records - Document rationale for blueprint separation, calculation approaches, and frontend business logic decisions (30 min)
- **[TEST-115]** Database Utilities Test Coverage - Create comprehensive test suite for db_utils.py module to restore coverage threshold and validate consolidation benefits (60 min)

### **EPIC-008: Core Hattrick Features** 🎯
*Goal: Essential player analysis and team management features*

- **[REFACTOR-058]** Simplify calculateContribution Function - Normalize position inputs to single format, remove dual-mode complexity (45 min)
- **[REFACTOR-059]** Extract Frontend Formation API - Replace JavaScript calculations with API endpoints to eliminate duplication (60 min)
- **[REFACTOR-060]** Externalize Position Configuration - Move formation templates and skill weightings from hardcoded dictionaries to JSON/YAML (30 min)
- **[TEST-036]** Add calculateContribution Test Coverage - Cover position code mapping and tactical variations (45 min)
- **[FEAT-019]** Player Skill Changes Timeline - 4-week timeline with better browser compatibility and simplified approach
- **[REFACTOR-081]** Investigate Server-Side Session Config - Research Flask session settings vs 195-line PWA JavaScript solution (30 min)
- **[REFACTOR-067]** Extract Navigation Component Logic - Move admin indicator logic from templates to view layer (30 min)
- **[REFACTOR-068]** Simplify Admin Feedback Test Mocking - Replace complex mocks with simple fake data (20 min)
- **[FEAT-016]** Alternative Leadership Indicators (30 min) - Replace complex charts with simple metrics
- **[FEAT-017]** User Preference System (60 min) - Store user chart/visualization preferences
- **[FEAT-011]** Training Camp Planner

### **EPIC-009: Application Architecture** 🎯
*Goal: Simplify import patterns and essential authentication*

- **[REFACTOR-028]** Evaluate Model Registry Necessity - Assess if model registry is justified for hobby project vs simpler imports (30 min)
- **[REFACTOR-029]** Consolidate Model Import Patterns - Choose single approach (registry OR direct imports) to eliminate dual paths (45 min)
- **[REFACTOR-050]** Authentication Flow Analysis - Investigate why authenticated sessions reference non-existent users (30 min)
- **[REFACTOR-051]** User Query Audit - Review all User.filter_by() patterns for consistency and safety (45 min)
- **[REFACTOR-061]** Blueprint Architecture Review - Analyze all blueprints for logical responsibility boundaries (90 min)
- **[FEAT-018]** Automatic User Creation Strategy - Ensure user records exist for all authenticated sessions (30 min)
- **[REFACTOR-091]** Isolate Flask-Bootstrap Dependency - Conditional plugin pattern for core app functionality (30 min)

### **EPIC-010: Essential Testing & Quality** 🎯
*Goal: Focus testing on business logic and modernize quality processes*

- **[TEST-070]** Team Model Comprehensive Coverage - Add tests for Team model creation, competition data updates, error handling (60 min)
- **[TEST-034]** Business Logic Route Coverage - Prioritize blueprint routes (auth, main, team, matches, training) over utilities (60 min)
- **[TEST-012]** Tutorial Analytics Test Coverage - Create coverage for tracking logic, calculations, event mapping (60 min)
- **[TEST-082]** Template Changes Test Coverage - Address coverage regression to 41.7% from recent modifications (45 min)
- **[TEST-035]** Shared Test Fixture Creation - Create shared fixture for new player display data structure (20 min)
- **[REFACTOR-052]** Consolidate File Processing Patterns - Merge fileformat and fileformat-fix rule processing loops (30 min)
- **[REFACTOR-053]** Configurable Coverage Thresholds - Replace hardcoded 50% with environment-specific settings (20 min)
- **[REFACTOR-054]** Unified Quality Gate Architecture - Merge test-coverage-files and test-python into comprehensive gate (45 min)
- **[REFACTOR-055]** Optimize Quality Intelligence Script - Single-pass JSON parsing vs multiple file reads (25 min)
- **[REFACTOR-056]** Filesystem-First File Discovery - Replace git ls-files with filesystem discovery (30 min)
- **[REFACTOR-038]** Simplify CSS Design System & UI Consistency (60 min)
- **[REFACTOR-040]** Template Inheritance for Breadcrumb Pattern (45 min)
- **[REFACTOR-041]** Debug Scripts & Country Data Migration (45 min)

---
