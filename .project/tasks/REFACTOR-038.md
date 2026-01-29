# REFACTOR-038: Simplify CSS Design System & UI Consistency

**Status**: 🎯 Ready to Execute | **Effort**: 90 min | **Priority**: P4 | **Impact**: Code maintainability & visual consistency
**Dependencies**: React removal completed (REFACTOR-044) | **Strategic Value**: Unified Flask-only design system

## Problem Statement
Multiple Flask UI consistency and CSS issues need addressing:

### 1. CSS Design System Bloat (REFACTOR-038)
Recent CSS implementation in base.html adds 300+ lines that largely duplicate Bootstrap functionality, creating maintenance overhead.

### 2. Chart Component Inconsistency (UI-015)
Hardcoded Chart.js implementations throughout templates lead to repetitive cleanup work and maintenance burden.

### 3. Page Style Drift (UI-016)
Training page styling differs from stats page patterns, creating visual inconsistency across the application.

*Consolidates UI-015 (modular charts) and UI-016 (training page consistency) for efficient execution*

## Implementation
1. **CSS Simplification** (40 min):
   - Remove redundant CSS that duplicates Bootstrap classes
   - Keep only football-themed color variables and essential customizations
   - Use CSS custom properties for colors only, leverage Bootstrap for layout/typography
   - Reduce CSS from 300+ lines to <100 lines

2. **Chart Component System** (30 min) [UI-015]:
   - Create `/app/static/js/chart-components.js` with modular functions
   - Standardize chart theming with CSS variables
   - Refactor existing charts in stats.html and training.html
   - Enable chart configuration without template editing

3. **Page Style Consistency** (20 min) [UI-016]:
   - Align training page with stats page design patterns
   - Standardize table headers, progress bars, spacing
   - Ensure consistent responsive behavior

## Acceptance Criteria
- [ ] CSS reduced from 300+ lines to <100 lines focusing on colors only
- [ ] All existing functionality maintained
- [ ] Bootstrap classes used where appropriate instead of custom duplicates
- [ ] Design tokens centralized and consistently used
- [ ] No visual regressions on any page

## Priority
P2 - Part of simplification hierarchy (reduce complexity)
