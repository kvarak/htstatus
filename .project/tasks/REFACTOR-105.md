# REFACTOR-105: Audit Chart.js Responsive Configuration

## Problem Statement

Chart.js responsive configuration is inconsistent across templates, leading to sizing issues and maintenance drift. Recent player modal work revealed that charts don't respect canvas dimensions due to responsive defaults, requiring manual overrides that may not be applied consistently throughout the application.

## Current Issues
- Inconsistent Chart.js responsive settings across different templates
- Recent fix required `responsive: false, maintainAspectRatio: false` in player.html
- Chart sizing problems when responsive configuration conflicts with canvas dimensions
- Configuration drift - different templates may have different Chart.js version syntax
- Maintenance overhead when chart behavior needs to be standardized

## Implementation

### Audit All Chart.js Instances
Search for Chart.js usage across templates:
- `app/templates/player.html` (recently fixed)
- `app/templates/debug.html`
- `app/templates/team.html`
- Any other templates with Chart.js implementations

### Document Current Configuration
Create inventory of:
- Chart.js version (should be v4.4.0 consistently)
- Responsive settings per template
- Canvas sizing approaches
- Options object patterns

### Standardize Configuration
Create consistent pattern for all Chart.js instances:
```javascript
var options = {
  responsive: false,          // Consistent responsive behavior
  maintainAspectRatio: false, // Allow exact canvas dimensions
  // ... other standard options
};
```

### Create Global Chart Configuration
Consider centralizing common Chart.js options in a shared JavaScript file to eliminate configuration duplication and ensure consistency.

## Acceptance Criteria

✅ Complete audit of all Chart.js usage in templates
✅ Document current configuration differences
✅ Standardize responsive settings across all charts
✅ Verify consistent Chart.js version usage
✅ Test chart sizing behavior in all templates
✅ No visual regressions or chart rendering issues

## Effort Estimate
45 minutes

## Priority
P4 - Technical standardization, prevents future sizing issues
