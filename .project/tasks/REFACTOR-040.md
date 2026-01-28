# REFACTOR-040: Template Inheritance for Breadcrumb Pattern

## Problem Statement
The breadcrumb navigation pattern is copied across stats.html, training.html, and matches.html templates, violating DRY principle and creating maintenance overhead.

## Implementation
- Create breadcrumb macro or partial template
- Update all templates to use shared breadcrumb component
- Maintain consistent styling and behavior across pages
- Reduce code duplication and improve maintainability

## Acceptance Criteria
- [ ] Breadcrumb macro/partial created in templates/includes/ or similar
- [ ] All templates (stats, training, matches) use shared breadcrumb
- [ ] Breadcrumb appearance and behavior identical to current
- [ ] Code duplication eliminated
- [ ] Easy to modify breadcrumb styling in single location

## Priority
P2 - Code consolidation and maintainability
