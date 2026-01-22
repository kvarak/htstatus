# HTStatus Implementation Standards

> **Purpose**: Technical standards for implementing consistent UI across Flask and React frontends
> **Audience**: Developers maintaining and extending HTStatus UI components
> **Related**: [UI Style Guide](ui-style-guide.md), [Design Guidelines](ui-design-guidelines.md)

## CSS Architecture Standards

### Custom CSS Classes for Flask Templates

Add these classes to `app/templates/base.html` for unified styling:

```css
/* =============================================================================
   HTStatus Unified UI System - Add to base.html <style> section
   ============================================================================= */

/* Color System Extensions */
.bg-primary-custom { background-color: hsl(120, 45%, 25%) !important; }
.bg-success-custom { background-color: hsl(120, 70%, 35%) !important; }
.bg-warning-custom { background-color: hsl(45, 90%, 55%) !important; }
.bg-danger-custom { background-color: hsl(0, 84%, 60%) !important; }
.bg-muted-custom { background-color: hsl(120, 15%, 92%) !important; }

.text-primary-custom { color: hsl(120, 45%, 25%) !important; }
.text-success-custom { color: hsl(120, 70%, 35%) !important; }
.text-warning-custom { color: hsl(45, 20%, 15%) !important; }
.text-danger-custom { color: hsl(0, 84%, 60%) !important; }
.text-muted-custom { color: hsl(120, 10%, 45%) !important; }

.border-primary-custom { border-color: hsl(120, 45%, 25%) !important; }
.border-muted-custom { border-color: hsl(120, 20%, 85%) !important; }

/* Button System */
.btn-primary-custom {
  background-color: hsl(120, 45%, 25%);
  border-color: hsl(120, 45%, 25%);
  color: white;
  font-weight: 500;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px hsla(120, 45%, 25%, 0.2);
}

.btn-primary-custom:hover {
  background-color: hsl(120, 45%, 20%);
  border-color: hsl(120, 45%, 20%);
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px hsla(120, 45%, 25%, 0.3);
}

.btn-success-custom {
  background-color: hsl(120, 70%, 35%);
  border-color: hsl(120, 70%, 35%);
  color: white;
  font-weight: 500;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.btn-success-custom:hover {
  background-color: hsl(120, 70%, 30%);
  border-color: hsl(120, 70%, 30%);
  color: white;
  transform: translateY(-1px);
}

.btn-warning-custom {
  background-color: hsl(45, 90%, 55%);
  border-color: hsl(45, 90%, 55%);
  color: hsl(45, 20%, 15%);
  font-weight: 500;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.btn-warning-custom:hover {
  background-color: hsl(45, 90%, 50%);
  border-color: hsl(45, 90%, 50%);
  color: hsl(45, 20%, 15%);
}

.btn-destructive-custom {
  background-color: hsl(0, 84%, 60%);
  border-color: hsl(0, 84%, 60%);
  color: white;
  font-weight: 500;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

.btn-destructive-custom:hover {
  background-color: hsl(0, 84%, 55%);
  border-color: hsl(0, 84%, 55%);
  color: white;
  transform: translateY(-1px);
}

/* Card System */
.card-custom {
  background-color: white;
  border: 1px solid hsl(120, 20%, 85%);
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px hsla(120, 20%, 12%, 0.1);
  transition: box-shadow 0.2s ease;
  margin-bottom: 1.5rem;
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

.card-footer {
  border-top: 1px solid hsl(120, 20%, 85%);
  padding-top: 1rem;
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Table System */
.table-custom {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  line-height: 1.5;
  background-color: white;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 1px 3px hsla(120, 20%, 12%, 0.1);
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

.table-custom tbody tr:last-child td {
  border-bottom: none;
}

/* Form System */
.form-control-custom {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid hsl(120, 20%, 85%);
  border-radius: 0.375rem;
  font-size: 0.875rem;
  line-height: 1.5;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
  background-color: white;
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

.form-control-error {
  border-color: hsl(0, 84%, 60%);
}

.form-control-error:focus {
  border-color: hsl(0, 84%, 60%);
  box-shadow: 0 0 0 3px hsla(0, 84%, 60%, 0.1);
}

.form-control-success {
  border-color: hsl(120, 70%, 35%);
}

.form-control-success:focus {
  border-color: hsl(120, 70%, 35%);
  box-shadow: 0 0 0 3px hsla(120, 70%, 35%, 0.1);
}

/* Alert System */
.alert-success-custom {
  background-color: hsl(120, 70%, 95%);
  border: 1px solid hsl(120, 70%, 75%);
  color: hsl(120, 70%, 20%);
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.alert-warning-custom {
  background-color: hsl(45, 90%, 95%);
  border: 1px solid hsl(45, 90%, 75%);
  color: hsl(45, 90%, 25%);
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.alert-danger-custom {
  background-color: hsl(0, 84%, 95%);
  border: 1px solid hsl(0, 84%, 75%);
  color: hsl(0, 84%, 25%);
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

/* Typography Extensions */
.text-base { font-size: 1rem; line-height: 1.6; }
.text-lg { font-size: 1.125rem; line-height: 1.5; }
.text-sm { font-size: 0.875rem; line-height: 1.5; }
.text-xs { font-size: 0.75rem; line-height: 1.4; }
.text-tiny { font-size: 0.625rem; line-height: 1.2; white-space: nowrap; }

/* Spacing Extensions */
.m-1-custom { margin: 0.25rem !important; }
.m-2-custom { margin: 0.5rem !important; }
.m-3-custom { margin: 0.75rem !important; }
.m-4-custom { margin: 1rem !important; }
.m-5-custom { margin: 1.25rem !important; }
.m-6-custom { margin: 1.5rem !important; }

.p-1-custom { padding: 0.25rem !important; }
.p-2-custom { padding: 0.5rem !important; }
.p-3-custom { padding: 0.75rem !important; }
.p-4-custom { padding: 1rem !important; }
.p-5-custom { padding: 1.25rem !important; }
.p-6-custom { padding: 1.5rem !important; }

.mt-1-custom { margin-top: 0.25rem !important; }
.mt-2-custom { margin-top: 0.5rem !important; }
.mt-3-custom { margin-top: 0.75rem !important; }
.mt-4-custom { margin-top: 1rem !important; }
.mt-6-custom { margin-top: 1.5rem !important; }

.mb-1-custom { margin-bottom: 0.25rem !important; }
.mb-2-custom { margin-bottom: 0.5rem !important; }
.mb-3-custom { margin-bottom: 0.75rem !important; }
.mb-4-custom { margin-bottom: 1rem !important; }
.mb-6-custom { margin-bottom: 1.5rem !important; }

/* Layout System */
.container-custom {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (min-width: 576px) {
  .container-custom { padding: 0 1.5rem; }
}

@media (min-width: 768px) {
  .container-custom { padding: 0 2rem; }
}

.page-header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid hsl(120, 20%, 85%);
}

/* Navigation System */
.breadcrumb-custom {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  color: hsl(120, 10%, 45%);
  margin-bottom: 1rem;
  padding: 0;
  list-style: none;
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
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: hsl(120, 45%, 20%);
  text-decoration: underline;
}
```

## React Component Standards

### Component Extension Guidelines

For React components, ensure consistency with existing patterns:

```tsx
// Button component variants should include:
const buttonVariants = cva(
  // Base classes...
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90 shadow-football",
        success: "bg-success text-success-foreground hover:bg-success/90 shadow-md",
        warning: "bg-warning text-warning-foreground hover:bg-warning/90 shadow-md",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-md",
        // ... other variants
      }
    }
  }
)
```

### Custom Hook Standards

```tsx
// Use consistent data fetching patterns
const usePlayerData = (teamId: string) => {
  return useQuery({
    queryKey: ['players', teamId],
    queryFn: () => fetchPlayerData(teamId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
};

// Use consistent error handling
const useErrorHandler = () => {
  return useCallback((error: Error) => {
    console.error('Application error:', error);
    toast({
      title: "Error",
      description: error.message || "An unexpected error occurred",
      variant: "destructive",
    });
  }, []);
};
```

## Development Workflow Standards

### Pre-Development Checklist

Before starting any UI work:

1. **Review Current State**
   - [ ] Check existing component patterns in both Flask and React
   - [ ] Review [UI Style Guide](ui-style-guide.md) for color/typography standards
   - [ ] Examine similar existing components for consistency

2. **Planning Phase**
   - [ ] Define component requirements and acceptance criteria
   - [ ] Choose appropriate patterns from [Design Guidelines](ui-design-guidelines.md)
   - [ ] Plan for both Flask and React implementations if needed

3. **Implementation Setup**
   - [ ] Ensure development environment running (`make dev`)
   - [ ] Have style guide and templates available for reference
   - [ ] Plan testing approach for cross-framework consistency

### Implementation Workflow

#### For Flask Template Changes

1. **Add Custom CSS Classes**
   ```bash
   # Edit base.html to add unified styling
   vim app/templates/base.html
   ```

2. **Update Template**
   ```html
   <!-- Use unified classes -->
   <button class="btn btn-primary-custom">Action</button>
   <div class="card-custom">...</div>
   <table class="table table-custom">...</table>
   ```

3. **Test Visual Consistency**
   ```bash
   # Start development server
   make dev
   # Visit localhost:5000 to test changes
   ```

#### For React Component Changes

1. **Use Existing Components**
   ```tsx
   import { Button } from "@/components/ui/button";
   import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

   // Maintain consistent patterns
   <Button variant="default">Action</Button>
   ```

2. **Extend Components if Needed**
   ```tsx
   // Add new variants following existing patterns
   const buttonVariants = cva(
     "...", // base classes
     {
       variants: {
         variant: {
           // ... existing variants
           football: "bg-gradient-pitch text-primary-foreground hover:shadow-glow"
         }
       }
     }
   )
   ```

3. **Test Component Integration**
   ```bash
   # Start React dev server
   npm run dev
   # Visit localhost:8080 to test changes
   ```

### Quality Assurance Standards

#### Visual Consistency Testing

1. **Cross-Framework Comparison**
   - [ ] Compare Flask and React versions side by side
   - [ ] Ensure identical visual appearance
   - [ ] Verify consistent spacing and typography
   - [ ] Check responsive behavior on both systems

2. **Accessibility Testing**
   ```bash
   # Use automated accessibility testing
   npm run a11y-test  # If available

   # Manual testing checklist:
   # - Keyboard navigation works
   # - Screen reader compatibility
   # - Color contrast meets standards
   # - Focus states clearly visible
   ```

3. **Performance Testing**
   ```bash
   # Check CSS bundle size impact
   npm run build
   # Verify no significant size increase

   # Test loading performance
   # - Lighthouse audit
   # - Network throttling test
   ```

#### Code Review Standards

##### For CSS Changes
```css
/* ✅ Good: Uses design system tokens */
.new-component {
  background-color: hsl(120, 45%, 25%);
  padding: 1rem;
  border-radius: 0.375rem;
  transition: all 0.2s ease;
}

/* ❌ Bad: Hard-coded colors and inconsistent spacing */
.bad-component {
  background-color: #28a745;
  padding: 15px;
  border-radius: 5px;
}
```

##### For React Components
```tsx
// ✅ Good: Follows existing patterns
<Button
  variant="default"
  size="sm"
  className="w-full"
  onClick={handleAction}
>
  Action
</Button>

// ❌ Bad: Custom styling that breaks consistency
<button
  style={{
    backgroundColor: '#28a745',
    padding: '15px'
  }}
  onClick={handleAction}
>
  Action
</button>
```

##### For Flask Templates
```html
<!-- ✅ Good: Uses unified CSS classes -->
<div class="card-custom">
  <div class="card-header-custom">
    <h4 class="card-title-custom">Title</h4>
  </div>
  <div class="card-body">
    Content
  </div>
</div>

<!-- ❌ Bad: Inconsistent Bootstrap + custom styling -->
<div class="card" style="margin: 20px; border: 2px solid green;">
  <div class="card-header bg-success">
    <h4>Title</h4>
  </div>
  <div class="card-body">
    Content
  </div>
</div>
```

## Testing Standards

### Manual Testing Checklist

#### Component Testing
- [ ] **Visual**: Component appears correctly in both Flask and React
- [ ] **Interactive**: All buttons, links, forms work as expected
- [ ] **Responsive**: Component adapts to different screen sizes
- [ ] **Accessibility**: Keyboard navigation and screen reader support
- [ ] **Performance**: No slow rendering or layout shifts

#### Cross-Framework Testing
- [ ] **Identical Appearance**: Flask and React versions look the same
- [ ] **Consistent Behavior**: Interactions work identically
- [ ] **Shared Patterns**: Both use same design system tokens
- [ ] **Error Handling**: Error states display consistently

#### Browser Testing
- [ ] **Chrome**: Latest version
- [ ] **Firefox**: Latest version
- [ ] **Safari**: Latest version (macOS)
- [ ] **Mobile**: iOS Safari, Android Chrome

### Automated Testing Integration

```bash
# Run visual regression tests (if available)
npm run test:visual

# Run accessibility tests
npm run test:a11y

# Run unit tests for React components
npm test

# Run Flask template tests
uv run python -m pytest tests/test_templates.py
```

## Deployment Standards

### Pre-Deployment Checklist

- [ ] **Style Guide Compliance**: All components follow design system
- [ ] **Cross-Framework Consistency**: No visual differences between Flask/React
- [ ] **Performance Impact**: CSS bundle size within acceptable limits
- [ ] **Accessibility**: WCAG 2.1 AA compliance verified
- [ ] **Browser Testing**: Components work across supported browsers
- [ ] **Documentation**: Updates to style guide if new patterns added

### Production Deployment

1. **CSS Optimization**
   ```bash
   # Minify custom CSS additions
   # Verify critical CSS loading
   # Check for unused styles
   ```

2. **Asset Management**
   ```bash
   # Ensure all custom assets included in build
   # Verify CDN resources still accessible
   # Check cache headers for CSS files
   ```

3. **Monitoring Setup**
   ```bash
   # Set up visual regression monitoring
   # Monitor CSS bundle size
   # Track accessibility scores
   ```

This implementation standard ensures consistent, maintainable UI development across HTStatus's dual frontend architecture.