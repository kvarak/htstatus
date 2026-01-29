# HattrickPlanner Backlog

**Purpose**: Active development tasks in priority order
**Rule**: Work top to bottom, update status when starting (🚀 ACTIVE) or completing (✅ COMPLETE)

**Recent Organization** (January 29, 2026): Applied hobby project philosophy to reorganize backlog. Consolidated simplification tasks, elevated database protection priority, archived enterprise features. Added critical review improvements from simplification review. **Active: 37 tasks | Archived: 8 enterprise tasks**

---

## P0: Production-Breaking 🚨

*All P0 production-breaking issues resolved as of January 28, 2026*

## P1: Critical 🔥

*All P1 critical issues resolved as of January 29, 2026*

## P2: Features 🎯

- **[FEAT-009]** Display Player Group Names in Update Timeline → [Details](.project/tasks/FEAT-009.md)
- **[DOC-021]** New Player Tutorial → [Details](.project/tasks/DOC-021.md)
- **[FEAT-005]** Team Statistics Dashboard → [Details](.project/tasks/FEAT-005.md)
- **[FEAT-008]** Next Game Analyser → [Details](.project/tasks/FEAT-008.md)
- **[FEAT-006]** Default Player Groups for New Users - Create default groupings to improve new user experience
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

### Improvements from Critical Review (January 29, 2026)

#### Test Isolation & Architecture (from simplification review)
- **[REFACTOR-028]** Evaluate Model Registry Necessity - Assess whether the model registry pattern is justified for this hobby project or if simpler import restructuring would suffice (30 min)
- **[TEST-034]** Focus Coverage on Business Logic - Prioritize test coverage for blueprint routes (auth, main, team, matches, training) over utility functions (60 min)
- **[REFACTOR-029]** Consolidate Model Import Patterns - Choose single approach (registry OR direct imports) to eliminate dual maintenance paths (45 min)
- **[DOC-018]** Document Import Architecture Decision - Record why the model registry pattern was chosen over alternatives for future reference (15 min)

#### Authentication & User Session Issues
- **[REFACTOR-050]** Authentication Flow Analysis - Investigate why authenticated sessions reference non-existent users (root cause of BUG-011)
- **[REFACTOR-051]** Systematic User Query Audit - Review all User.filter_by() patterns for consistency and safety
- **[FEAT-018]** Automatic User Creation Strategy - Ensure user records exist for all authenticated sessions
- **[TEST-010]** Authentication Test Environment - Fix test setup to properly create user records for authenticated clients
- **[REFACTOR-052]** Consolidate Repetitive File Processing Patterns - Merge fileformat and fileformat-fix rule processing loops
- **[REFACTOR-053]** Make Coverage Thresholds Configurable - Replace hardcoded 50% with environment-specific settings
- **[REFACTOR-054]** Unified Quality Gate Architecture - Merge test-coverage-files and test-python into single comprehensive test gate
- **[REFACTOR-055]** Optimize Quality Intelligence Script - Single-pass JSON parsing instead of multiple file reads per gate
- **[REFACTOR-056]** Filesystem-First File Discovery - Replace git ls-files with filesystem discovery to eliminate existence checks

### Core Hattrick Features (Aligned with Geek Audience)
- **[FEAT-016]** Alternative Leadership Indicators (30 min) - Replace complex charts with simple metrics → [Details](.project/tasks/FEAT-016.md)
- **[FEAT-017]** User Preference System (60 min) - Store user chart/visualization preferences to avoid future rejections → [Details](.project/tasks/FEAT-017.md)
- **[FEAT-003]** Formation Tester & Tactics Analyzer → [Details](.project/tasks/FEAT-003.md)
- **[FEAT-010]** Player Comparison Tool → [Details](.project/tasks/FEAT-010.md)
- **[FEAT-011]** Training Camp Planner → [Details](.project/tasks/FEAT-011.md)

### Simple Improvements
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
