# REFACTOR-104: Extract Player Field Display Logic

## Problem Statement

Player details template contains repeated conditional display logic for optional fields (nick_name, statement, owner_notes) that violates DRY principles and creates maintenance overhead. Each field uses identical conditional patterns that could be consolidated into reusable components.

## Current Issues
- Duplicated conditional logic: `{% if p['field'] and p['field'] != "None" and p['field'].strip() %}`
- Maintenance overhead when display logic changes
- Template code verbosity reducing readability
- Missed opportunity for consistent field formatting

## Implementation

### Extract Jinja2 Macro
Create `app/templates/macros/player_fields.html`:
```jinja2
{% macro display_optional_field(value, prefix="", suffix="", class="card-text") %}
  {% if value and value != "None" and value.strip() %}
    <p class="{{ class }}">
      {{ prefix }}<i>"{{ value }}"</i>{{ suffix }}
    </p>
  {% endif %}
{% endmacro %}
```

### Update Player Template
Replace repeated conditionals in `app/templates/player.html`:
```jinja2
{% from 'macros/player_fields.html' import display_optional_field %}

<!-- Replace current conditionals with: -->
{{ display_optional_field(p['nick_name']) }}
{{ display_optional_field(p['statement']) }}
{{ display_optional_field(p['owner_notes']) }}
```

## Acceptance Criteria

✅ Create reusable Jinja2 macro for optional field display
✅ Replace all three field conditionals in player template
✅ Maintain identical visual output and functionality
✅ No test failures or template rendering errors
✅ Reduce template line count and improve readability

## Effort Estimate
15 minutes

## Priority
P4 - Technical debt reduction, improves maintainability
