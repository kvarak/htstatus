# REFACTOR-038: Simplify CSS Design System

## Problem Statement
The recent CSS design system implementation in base.html adds 300+ lines that largely duplicate existing Bootstrap functionality, creating maintenance overhead without clear benefit.

## Implementation
- Remove redundant CSS that duplicates Bootstrap classes
- Keep only football-themed color variables and essential customizations
- Use CSS custom properties for colors only, leverage Bootstrap for layout/typography
- Consolidate styling approach to reduce cognitive load

## Acceptance Criteria
- [ ] CSS reduced from 300+ lines to <100 lines focusing on colors only
- [ ] All existing functionality maintained
- [ ] Bootstrap classes used where appropriate instead of custom duplicates
- [ ] Design tokens centralized and consistently used
- [ ] No visual regressions on any page

## Priority
P2 - Part of simplification hierarchy (reduce complexity)