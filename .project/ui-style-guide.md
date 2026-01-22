# HTStatus UI Style Guide

> **Created**: January 22, 2026
> **Purpose**: Unified design standards for HTStatus dual frontend architecture
> **Audience**: Developers, AI agents, designers
> **Scope**: Cross-framework compatibility patterns for Flask/Bootstrap 4.5 and React/TailwindCSS

## Design Philosophy

HTStatus follows a **football/soccer management theme** with professional, data-driven interface patterns. The design system balances:
- **Functionality**: Clear data presentation for team management
- **Consistency**: Unified experience across Flask and React frontends
- **Accessibility**: WCAG 2.1 AA compliance
- **Performance**: Optimized loading and responsive design

## Color Palette

### Core Color System
Use these colors consistently across both Flask and React systems:

#### Primary Colors
```css
/* Primary - Football Green */
--primary: hsl(120, 45%, 25%)        /* #1f6b2e */
--primary-light: hsl(120, 45%, 35%)  /* #2a8f3b */
--primary-dark: hsl(120, 45%, 15%)   /* #14471c */

/* Background */
--background: hsl(120, 8%, 97%)      /* #f9fafa */
--surface: hsl(0, 0%, 100%)          /* #ffffff */
```

#### Semantic Colors
```css
/* Success - Goal Green */
--success: hsl(120, 70%, 35%)        /* #197038 */
--success-light: hsl(120, 70%, 45%)  /* #1f8a47 */

/* Warning - Yellow Card */
--warning: hsl(45, 90%, 55%)         /* #f4cc15 */
--warning-light: hsl(45, 90%, 65%)   /* #f6d644 */

/* Destructive - Red Card */
--destructive: hsl(0, 84%, 60%)      /* #ef4444 */
--destructive-light: hsl(0, 84%, 70%) /* #f87171 */

/* Neutral Grays */
--muted: hsl(120, 15%, 92%)          /* #eaecea */
--muted-foreground: hsl(120, 10%, 45%) /* #6b736b */
--border: hsl(120, 20%, 85%)         /* #d1d9d1 */
```

### Cross-Framework Implementation

#### Flask/Bootstrap 4.5
```css
/* Add to base.html styles */
.bg-primary { background-color: hsl(120, 45%, 25%) !important; }
.text-primary { color: hsl(120, 45%, 25%) !important; }
.bg-success-custom { background-color: hsl(120, 70%, 35%) !important; }
.bg-warning-custom { background-color: hsl(45, 90%, 55%) !important; }
.bg-danger-custom { background-color: hsl(0, 84%, 60%) !important; }

/* Border utilities */
.border-primary-custom { border-color: hsl(120, 45%, 25%) !important; }
.border-muted-custom { border-color: hsl(120, 20%, 85%) !important; }
```

#### React/TailwindCSS
```css
/* Already implemented in index.css */
/* Use existing CSS custom properties */
```

## Typography

### Font Hierarchy

#### Headings
```css
/* H1 - Page Titles */
h1, .h1 {
  font-size: 2.5rem;      /* 40px */
  font-weight: 700;       /* bold */
  line-height: 1.2;
  margin-bottom: 1rem;
  color: var(--foreground);
}

/* H2 - Section Headers */
h2, .h2 {
  font-size: 2rem;        /* 32px */
  font-weight: 600;       /* semibold */
  line-height: 1.25;
  margin-bottom: 0.75rem;
}

/* H3 - Subsection Headers */
h3, .h3 {
  font-size: 1.5rem;      /* 24px */
  font-weight: 600;
  line-height: 1.375;
  margin-bottom: 0.5rem;
}

/* H4 - Component Titles */
h4, .h4 {
  font-size: 1.25rem;     /* 20px */
  font-weight: 600;
  line-height: 1.4;
  margin-bottom: 0.5rem;
}

/* H5 - Sub-component Titles */
h5, .h5 {
  font-size: 1.125rem;    /* 18px */
  font-weight: 500;       /* medium */
  line-height: 1.5;
  margin-bottom: 0.25rem;
}

/* H6 - Labels */
h6, .h6 {
  font-size: 1rem;        /* 16px */
  font-weight: 500;
  line-height: 1.5;
  margin-bottom: 0.25rem;
}
```

#### Body Text
```css
/* Base body text */
body, .text-base {
  font-size: 1rem;        /* 16px */
  line-height: 1.6;
  color: var(--foreground);
}

/* Small text - stats, metadata */
.text-sm, .text-sm13 {
  font-size: 0.875rem;    /* 14px */
  line-height: 1.5;
}

/* Extra small text - helper text */
.text-xs, .text-sm11 {
  font-size: 0.75rem;     /* 12px */
  line-height: 1.4;
}

/* Tiny text - minimal metadata */
.text-tiny, .text-small {
  font-size: 0.625rem;    /* 10px */
  line-height: 1.2;
  white-space: nowrap;
}

/* Large text - emphasis */
.text-lg {
  font-size: 1.125rem;    /* 18px */
  line-height: 1.5;
}
```

### Cross-Framework Implementation

#### Flask/Bootstrap 4.5
```html
<!-- Use existing custom classes, add standardized versions -->
<p class="text-sm13">Standard small text</p>
<p class="text-sm11">Extra small text</p>
<p class="text-small">Tiny text</p>

<!-- Add new unified classes to base.html -->
<style>
.text-base { font-size: 1rem; line-height: 1.6; }
.text-lg { font-size: 1.125rem; line-height: 1.5; }
.text-sm { font-size: 0.875rem; line-height: 1.5; }
.text-xs { font-size: 0.75rem; line-height: 1.4; }
.text-tiny { font-size: 0.625rem; line-height: 1.2; white-space: nowrap; }
</style>
```

#### React/TailwindCSS
```tsx
// Use TailwindCSS utilities
<p className="text-base">Base text</p>
<p className="text-lg">Large text</p>
<p className="text-sm">Small text</p>
<p className="text-xs">Extra small text</p>

// Custom utility for tiny text
<p className="text-[10px] leading-tight whitespace-nowrap">Tiny text</p>
```

## Spacing System

### Unified Spacing Scale
Use consistent spacing across both systems:

```css
/* Spacing scale (multiples of 0.25rem = 4px) */
--space-1: 0.25rem;      /* 4px */
--space-2: 0.5rem;       /* 8px */
--space-3: 0.75rem;      /* 12px */
--space-4: 1rem;         /* 16px */
--space-5: 1.25rem;      /* 20px */
--space-6: 1.5rem;       /* 24px */
--space-8: 2rem;         /* 32px */
--space-10: 2.5rem;      /* 40px */
--space-12: 3rem;        /* 48px */
--space-16: 4rem;        /* 64px */
--space-20: 5rem;        /* 80px */
--space-24: 6rem;        /* 96px */
```

### Cross-Framework Implementation

#### Flask/Bootstrap 4.5
```css
/* Add to base.html - extend Bootstrap spacing */
.m-1-custom { margin: 0.25rem !important; }
.m-2-custom { margin: 0.5rem !important; }
.m-3-custom { margin: 0.75rem !important; }
/* Continue pattern for p-, mt-, mb-, etc. */

.p-1-custom { padding: 0.25rem !important; }
.p-2-custom { padding: 0.5rem !important; }
/* Continue pattern */
```

#### React/TailwindCSS
```tsx
// Use TailwindCSS spacing utilities (already implemented)
<div className="m-1">Margin 4px</div>
<div className="p-4">Padding 16px</div>
<div className="space-y-6">Vertical spacing 24px</div>
```

## Component Standards

### Buttons

#### Design Specifications
```css
/* Base button styles */
.btn-primary-custom {
  background-color: hsl(120, 45%, 25%);
  border-color: hsl(120, 45%, 25%);
  color: white;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.btn-primary-custom:hover {
  background-color: hsl(120, 45%, 20%);
  border-color: hsl(120, 45%, 20%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px hsla(120, 45%, 25%, 0.3);
}

/* Success button */
.btn-success-custom {
  background-color: hsl(120, 70%, 35%);
  border-color: hsl(120, 70%, 35%);
  color: white;
}

/* Warning button */
.btn-warning-custom {
  background-color: hsl(45, 90%, 55%);
  border-color: hsl(45, 90%, 55%);
  color: hsl(45, 20%, 15%);
}

/* Destructive button */
.btn-destructive-custom {
  background-color: hsl(0, 84%, 60%);
  border-color: hsl(0, 84%, 60%);
  color: white;
}
```

#### Cross-Framework Implementation

##### Flask/Bootstrap 4.5
```html
<!-- Use custom button classes -->
<button class="btn btn-primary-custom">Primary Action</button>
<button class="btn btn-success-custom">Success Action</button>
<button class="btn btn-warning-custom">Warning Action</button>
<button class="btn btn-destructive-custom">Delete Action</button>

<!-- Or extend existing Bootstrap classes -->
<button class="btn btn-primary">Standard Primary</button>
```

##### React/TailwindCSS
```tsx
// Use existing button component with variants
<Button variant="default">Primary Action</Button>
<Button variant="success">Success Action</Button>
<Button variant="destructive">Delete Action</Button>

// Custom variant for warning
<Button className="bg-warning text-warning-foreground hover:bg-warning/90">
  Warning Action
</Button>
```

### Tables

#### Design Specifications
```css
/* Unified table styling */
.table-custom {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  line-height: 1.5;
}

.table-custom thead {
  background-color: hsl(120, 15%, 92%);
  border-bottom: 2px solid hsl(120, 20%, 85%);
}

.table-custom th {
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  color: hsl(120, 20%, 12%);
  border-bottom: 1px solid hsl(120, 20%, 85%);
}

.table-custom td {
  padding: 0.75rem;
  border-bottom: 1px solid hsl(120, 20%, 90%);
  vertical-align: middle;
}

.table-custom tbody tr:hover {
  background-color: hsl(120, 25%, 96%);
}

/* Sortable table indicators */
.table-sortable th {
  cursor: pointer;
  user-select: none;
  position: relative;
}

.table-sortable th:hover {
  background-color: hsl(120, 15%, 88%);
}
```

### Forms

#### Design Specifications
```css
/* Unified form styling */
.form-control-custom {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid hsl(120, 20%, 85%);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  line-height: 1.5;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-control-custom:focus {
  outline: none;
  border-color: hsl(120, 45%, 25%);
  box-shadow: 0 0 0 3px hsla(120, 45%, 25%, 0.1);
}

.form-label-custom {
  font-weight: 500;
  font-size: 0.875rem;
  color: hsl(120, 20%, 12%);
  margin-bottom: 0.5rem;
  display: block;
}

/* Form validation states */
.form-control-error {
  border-color: hsl(0, 84%, 60%);
}

.form-control-success {
  border-color: hsl(120, 70%, 35%);
}
```

### Cards and Containers

#### Design Specifications
```css
/* Unified card styling */
.card-custom {
  background-color: white;
  border: 1px solid hsl(120, 20%, 85%);
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px hsla(120, 20%, 12%, 0.1);
  transition: box-shadow 0.2s ease;
}

.card-custom:hover {
  box-shadow: 0 4px 12px hsla(120, 20%, 12%, 0.15);
}

.card-header-custom {
  border-bottom: 1px solid hsl(120, 20%, 85%);
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.card-title-custom {
  font-size: 1.25rem;
  font-weight: 600;
  color: hsl(120, 20%, 12%);
  margin: 0;
}
```

## Layout Patterns

### Grid System

#### Unified Container System
```css
/* Consistent container sizes */
.container-custom {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.container-sm { max-width: 640px; }
.container-md { max-width: 768px; }
.container-lg { max-width: 1024px; }
.container-xl { max-width: 1280px; }

/* Grid utilities */
.grid-1 { display: grid; grid-template-columns: 1fr; }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); }

.grid-gap-4 { gap: 1rem; }
.grid-gap-6 { gap: 1.5rem; }
.grid-gap-8 { gap: 2rem; }
```

### Responsive Breakpoints
```css
/* Unified breakpoint system */
/* Mobile first approach */

/* Small devices (landscape phones, 576px and up) */
@media (min-width: 576px) { /* sm */ }

/* Medium devices (tablets, 768px and up) */
@media (min-width: 768px) { /* md */ }

/* Large devices (desktops, 992px and up) */
@media (min-width: 992px) { /* lg */ }

/* Extra large devices (large desktops, 1200px and up) */
@media (min-width: 1200px) { /* xl */ }
```

## Navigation Patterns

### Header/Navigation
```css
/* Unified header styling */
.header-custom {
  background-color: white;
  border-bottom: 1px solid hsl(120, 20%, 85%);
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 50;
  backdrop-filter: blur(10px);
  background-color: hsla(0, 0%, 100%, 0.95);
}

.nav-link-custom {
  color: hsl(120, 20%, 12%);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: background-color 0.2s ease;
}

.nav-link-custom:hover {
  background-color: hsl(120, 25%, 96%);
  color: hsl(120, 45%, 25%);
}

.nav-link-active {
  background-color: hsl(120, 45%, 25%);
  color: white;
}
```

### Breadcrumbs
```css
.breadcrumb-custom {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  color: hsl(120, 10%, 45%);
  margin-bottom: 1rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-item + .breadcrumb-item::before {
  content: "/";
  margin: 0 0.5rem;
  color: hsl(120, 10%, 60%);
}

.breadcrumb-link {
  color: hsl(120, 45%, 25%);
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}
```

## Accessibility Guidelines

### ARIA and Semantic HTML
- Use semantic HTML elements (`main`, `nav`, `section`, `article`)
- Provide ARIA labels for interactive elements
- Ensure proper heading hierarchy (h1 → h2 → h3)
- Use `role` attributes when needed

### Color Contrast
- All text meets WCAG 2.1 AA standards (4.5:1 ratio)
- Interactive elements have clear focus states
- Color is not the only means of conveying information

### Keyboard Navigation
- All interactive elements accessible via keyboard
- Logical tab order
- Visible focus indicators
- Escape key closes modals/dropdowns

### Screen Reader Support
- Alt text for all images
- Form labels properly associated
- Status updates announced
- Loading states communicated

## Performance Standards

### CSS Organization
```css
/* Load order for optimal performance */
1. Critical above-the-fold CSS (inlined)
2. Bootstrap CSS (CDN with integrity)
3. TailwindCSS (built/optimized)
4. Custom component CSS
5. Page-specific CSS
```

### Asset Loading Strategy
- Preload critical fonts
- Use WebP images with fallbacks
- Optimize icon usage (prefer SVG)
- Implement lazy loading for images

## Implementation Guidelines

### Development Workflow

1. **Design Token First**: Always reference color/spacing variables
2. **Component Isolation**: Test components in isolation
3. **Cross-Framework Testing**: Verify consistency between Flask and React
4. **Accessibility Auditing**: Use automated tools + manual testing
5. **Performance Monitoring**: Track CSS bundle size and render performance

### Quality Checklist

Before implementing any UI component:
- [ ] Colors use design system tokens
- [ ] Typography follows hierarchy
- [ ] Spacing uses consistent scale
- [ ] Accessibility requirements met
- [ ] Responsive design implemented
- [ ] Performance optimized
- [ ] Cross-browser tested
- [ ] Documentation updated

This style guide provides the foundation for consistent UI development across HTStatus's dual frontend architecture.