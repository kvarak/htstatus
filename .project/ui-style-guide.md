# UI Design System

**Football Theme**: Professional green-based team management interface

## Design Tokens
```css
--primary: hsl(120, 45%, 25%)      /* Football green */
--success: hsl(120, 70%, 35%)      /* Goal green */
--warning: hsl(45, 90%, 55%)       /* Yellow card */
--destructive: hsl(0, 84%, 60%)    /* Red card */
--background: hsl(120, 8%, 97%)    /* Light field */
```

## Implementation
**Flask**: `.btn-primary-custom`, `.table-custom`, `.card-custom`
**React**: Use existing Button/Table/Card components

## Typography Scale
**h1**: 2.5rem/700, **h2**: 2rem/600, **body**: 1rem/1.6, **spacing**: 4px increments

## Quality Gates
- ✅ WCAG 2.1 AA contrast (4.5:1)
- ✅ Responsive breakpoints
- ✅ Keyboard navigation
- ✅ Cross-framework consistency
