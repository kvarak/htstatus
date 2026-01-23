# UI Design Guidelines & Templates

> **Purpose**: Practical templates and checklists for maintaining UI consistency across HTStatus
> **Audience**: Developers and AI agents creating UI components
> **Related**: [UI Style Guide](ui-style-guide.md), [UI Audit](ui-audit-analysis.md)

## Design Validation Checklist

Use this checklist before submitting any UI component:

### Color & Theme ✅
- [ ] Uses design system color tokens (primary: `hsl(120, 45%, 25%)`)
- [ ] Maintains football/soccer theme consistency
- [ ] Semantic colors used appropriately (success green, warning yellow, destructive red)
- [ ] Color contrast meets WCAG 2.1 AA standards (4.5:1 ratio)
- [ ] Works in both light and dark modes (if applicable)

### Typography ✅
- [ ] Uses consistent font hierarchy (h1: 2.5rem, h2: 2rem, etc.)
- [ ] Body text uses 1rem base with 1.6 line-height
- [ ] Small text uses standard sizes (.text-sm: 0.875rem, .text-xs: 0.75rem)
- [ ] Font weights appropriate (700 for h1, 600 for h2-h4, 500 for h5-h6)
- [ ] Text maintains readability on all backgrounds

### Spacing & Layout ✅
- [ ] Uses 0.25rem spacing increments (4px, 8px, 12px, 16px, etc.)
- [ ] Consistent padding/margin patterns
- [ ] Proper grid system usage (container-custom, grid utilities)
- [ ] Responsive design implemented for all breakpoints
- [ ] Component spacing follows design system

### Components ✅
- [ ] Buttons use consistent styling (.btn-primary-custom or Button component)
- [ ] Tables follow unified patterns (.table-custom or Table component)
- [ ] Cards use standard styling (.card-custom or Card component)
- [ ] Forms follow design system (.form-control-custom or Input component)
- [ ] Icons consistent with theme and size

### Cross-Framework Compatibility ✅
- [ ] Flask templates use custom CSS classes for consistency
- [ ] React components maintain same visual appearance
- [ ] Both frameworks achieve identical user experience
- [ ] No visual inconsistencies between Flask and React pages

### Accessibility ✅
- [ ] Semantic HTML elements used appropriately
- [ ] ARIA labels provided for interactive elements
- [ ] Keyboard navigation works correctly
- [ ] Focus states clearly visible
- [ ] Screen reader compatibility verified

### Performance ✅
- [ ] CSS optimized and minimal
- [ ] Images optimized (WebP with fallbacks)
- [ ] No unnecessary re-renders (React)
- [ ] Assets loaded efficiently

## Component Templates

### Flask/Bootstrap 4.5 Templates

#### Button Templates
```html
<!-- Primary Action Button -->
<button type="button" class="btn btn-primary-custom">
  Primary Action
</button>

<!-- Success Button -->
<button type="button" class="btn btn-success-custom">
  Save Changes
</button>

<!-- Warning Button -->
<button type="button" class="btn btn-warning-custom">
  Proceed with Caution
</button>

<!-- Destructive Button -->
<button type="button" class="btn btn-destructive-custom">
  Delete Item
</button>

<!-- Secondary/Outline Button -->
<button type="button" class="btn btn-outline-primary">
  Secondary Action
</button>
```

#### Card Templates
```html
<!-- Standard Card -->
<div class="card-custom">
  <div class="card-header-custom">
    <h4 class="card-title-custom">Card Title</h4>
  </div>
  <div class="card-body">
    <p class="card-text">Card content goes here.</p>
  </div>
</div>

<!-- Card with Actions -->
<div class="card-custom">
  <div class="card-header-custom">
    <h4 class="card-title-custom">Player Statistics</h4>
  </div>
  <div class="card-body">
    <p class="card-text">Statistics content...</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary-custom btn-sm">View Details</button>
    <button class="btn btn-outline-secondary btn-sm">Export</button>
  </div>
</div>
```

#### Table Templates
```html
<!-- Sortable Data Table -->
<div class="table-responsive">
  <table class="table table-custom table-sortable">
    <thead>
      <tr>
        <th scope="col">Player Name</th>
        <th scope="col">Position</th>
        <th scope="col">Age</th>
        <th scope="col">Rating</th>
        <th scope="col">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>John Doe</td>
        <td>Forward</td>
        <td>25</td>
        <td>8.5</td>
        <td>
          <button class="btn btn-sm btn-outline-primary">Edit</button>
          <button class="btn btn-sm btn-destructive-custom">Remove</button>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

#### Form Templates
```html
<!-- Standard Form -->
<form>
  <div class="form-group">
    <label class="form-label-custom" for="player-name">Player Name</label>
    <input type="text" class="form-control form-control-custom" id="player-name" placeholder="Enter player name">
  </div>

  <div class="form-group">
    <label class="form-label-custom" for="player-position">Position</label>
    <select class="form-control form-control-custom" id="player-position">
      <option>Select position...</option>
      <option>Goalkeeper</option>
      <option>Defender</option>
      <option>Midfielder</option>
      <option>Forward</option>
    </select>
  </div>

  <div class="form-group">
    <button type="submit" class="btn btn-success-custom">Save Player</button>
    <button type="button" class="btn btn-outline-secondary">Cancel</button>
  </div>
</form>
```

#### Alert Templates
```html
<!-- Success Alert -->
<div class="alert alert-success-custom" role="alert">
  <strong>Success!</strong> Player data has been updated successfully.
  <button type="button" class="close" aria-label="Close">
    <span aria-hidden="true">&times;</span>
  </button>
</div>

<!-- Warning Alert -->
<div class="alert alert-warning-custom" role="alert">
  <strong>Warning!</strong> This action cannot be undone.
</div>

<!-- Error Alert -->
<div class="alert alert-danger-custom" role="alert">
  <strong>Error!</strong> Failed to save player data. Please try again.
</div>
```

### React/TailwindCSS Templates

#### Button Templates
```tsx
import { Button } from "@/components/ui/button";

// Primary Action Button
<Button variant="default">Primary Action</Button>

// Success Button
<Button variant="success">Save Changes</Button>

// Warning Button
<Button className="bg-warning text-warning-foreground hover:bg-warning/90">
  Proceed with Caution
</Button>

// Destructive Button
<Button variant="destructive">Delete Item</Button>

// Secondary Button
<Button variant="outline">Secondary Action</Button>

// Football-themed Button
<Button variant="pitch">Special Action</Button>
```

#### Card Templates
```tsx
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";

// Standard Card
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description or subtitle</CardDescription>
  </CardHeader>
  <CardContent>
    <p>Card content goes here.</p>
  </CardContent>
</Card>

// Card with Actions
<Card>
  <CardHeader>
    <CardTitle>Player Statistics</CardTitle>
  </CardHeader>
  <CardContent>
    <p>Statistics content...</p>
  </CardContent>
  <CardFooter className="flex gap-2">
    <Button size="sm">View Details</Button>
    <Button variant="outline" size="sm">Export</Button>
  </CardFooter>
</Card>
```

#### Table Templates
```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// Data Table
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Player Name</TableHead>
      <TableHead>Position</TableHead>
      <TableHead>Age</TableHead>
      <TableHead>Rating</TableHead>
      <TableHead>Actions</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell className="font-medium">John Doe</TableCell>
      <TableCell>Forward</TableCell>
      <TableCell>25</TableCell>
      <TableCell>8.5</TableCell>
      <TableCell className="flex gap-2">
        <Button size="sm" variant="outline">Edit</Button>
        <Button size="sm" variant="destructive">Remove</Button>
      </TableCell>
    </TableRow>
  </TableBody>
</Table>
```

#### Form Templates
```tsx
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// Standard Form
<form>
  <div className="space-y-4">
    <div>
      <Label htmlFor="player-name">Player Name</Label>
      <Input id="player-name" placeholder="Enter player name" />
    </div>

    <div>
      <Label htmlFor="player-position">Position</Label>
      <Select>
        <SelectTrigger>
          <SelectValue placeholder="Select position..." />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="goalkeeper">Goalkeeper</SelectItem>
          <SelectItem value="defender">Defender</SelectItem>
          <SelectItem value="midfielder">Midfielder</SelectItem>
          <SelectItem value="forward">Forward</SelectItem>
        </SelectContent>
      </Select>
    </div>

    <div className="flex gap-2">
      <Button type="submit" variant="success">Save Player</Button>
      <Button type="button" variant="outline">Cancel</Button>
    </div>
  </div>
</form>
```

## Common Patterns

### Page Layout Templates

#### Flask Page Layout
```html
{% extends 'base.html' %}

{% block content %}
<div class="container-custom">
  <!-- Breadcrumbs -->
  <nav aria-label="breadcrumb" class="mb-4">
    <ol class="breadcrumb-custom">
      <li class="breadcrumb-item">
        <a href="{{ url_for('main.index') }}" class="breadcrumb-link">Home</a>
      </li>
      <li class="breadcrumb-item active" aria-current="page">Page Title</li>
    </ol>
  </nav>

  <!-- Page Header -->
  <div class="page-header mb-6">
    <h1 class="h1">Page Title</h1>
    <p class="text-muted-custom">Page description or subtitle</p>
  </div>

  <!-- Main Content -->
  <div class="row">
    <div class="col-md-8">
      <!-- Primary content -->
    </div>
    <div class="col-md-4">
      <!-- Sidebar content -->
    </div>
  </div>
</div>
{% endblock %}
```

#### React Page Layout
```tsx
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";

export default function PageTemplate() {
  return (
    <div className="min-h-screen bg-background">
      <Header user={user} />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          {/* Breadcrumbs */}
          <nav className="mb-4">
            <ol className="flex items-center space-x-2 text-sm text-muted-foreground">
              <li><a href="/" className="hover:text-primary">Home</a></li>
              <li>/</li>
              <li className="text-foreground">Page Title</li>
            </ol>
          </nav>

          {/* Page Header */}
          <div className="mb-6">
            <h1 className="text-4xl font-bold">Page Title</h1>
            <p className="text-muted-foreground">Page description or subtitle</p>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              {/* Primary content */}
            </div>
            <div>
              {/* Sidebar content */}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
```

## Quick Reference

### Color Variables
```css
/* Use these in both Flask and React */
--primary: hsl(120, 45%, 25%)
--success: hsl(120, 70%, 35%)
--warning: hsl(45, 90%, 55%)
--destructive: hsl(0, 84%, 60%)
--background: hsl(120, 8%, 97%)
--muted: hsl(120, 15%, 92%)
--border: hsl(120, 20%, 85%)
```

### Spacing Scale
```css
/* Consistent spacing across frameworks */
1 = 0.25rem = 4px
2 = 0.5rem = 8px
3 = 0.75rem = 12px
4 = 1rem = 16px
6 = 1.5rem = 24px
8 = 2rem = 32px
```

### Typography Scale
```css
/* Consistent text sizes */
h1: 2.5rem (40px) / 700 weight
h2: 2rem (32px) / 600 weight
h3: 1.5rem (24px) / 600 weight
h4: 1.25rem (20px) / 600 weight
body: 1rem (16px) / 1.6 line-height
small: 0.875rem (14px)
xs: 0.75rem (12px)
tiny: 0.625rem (10px)
```
