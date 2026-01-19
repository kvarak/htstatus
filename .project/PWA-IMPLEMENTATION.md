# PWA Implementation Guide

## Overview
HTStatus now includes Progressive Web App (PWA) capabilities enabling mobile installation, offline functionality, and responsive design.

## Features Implemented

### 1. Service Worker (`/static/sw.js`)
- **Cache Strategy**: Cache-first for static assets, network-first for dynamic content
- **Offline Support**: Core routes cached for offline access (`/`, `/player`, `/team`, `/matches`, `/training`, `/settings`)
- **Static Asset Caching**: All essential JS, CSS, and image files cached
- **Background Sync**: Automatic cache refresh when back online
- **Error Handling**: Graceful fallbacks for offline scenarios

### 2. App Manifest (`/static/manifest.json`)
- **Installation**: PWA installable on mobile devices and desktop
- **App Identity**: HTStatus branding with custom icons and theme colors
- **App Shortcuts**: Quick access to Players, Team, and Matches pages
- **Display Mode**: Standalone app experience without browser UI

### 3. Responsive Design
- **Mobile-First CSS**: Optimized layouts for mobile/tablet/desktop
- **Touch-Friendly**: Improved navigation for touch interfaces
- **Responsive Tables**: Font size and padding adjustments for small screens
- **Viewport Optimization**: Proper viewport meta tag for mobile scaling

### 4. PWA Installation
- **Install Prompt**: Floating install button appears when PWA criteria met
- **Auto-Registration**: Service worker registered automatically on page load
- **Update Notification**: Prompts users to refresh when new version available

## Technical Implementation

### Service Worker Registration
```javascript
// Automatic registration in base.html
navigator.serviceWorker.register('/static/sw.js')
```

### Mobile Optimizations
- Responsive CSS breakpoints (768px, 480px)
- Mobile-specific table styling
- Touch-friendly button sizes
- Optimized container padding

### Caching Strategy
- **Static Assets**: Cache-first (JS, CSS, images)
- **Dynamic Routes**: Network-first with cache fallback
- **API Requests**: Network-only (no stale data caching)

## Usage

### Installing as PWA
1. Visit HTStatus in supported browser (Chrome, Safari, Firefox)
2. Look for install prompt or "Install App" button
3. Click to install as standalone app
4. Launch from home screen/app drawer

### Offline Functionality
- Core pages available offline after first visit
- Static assets served from cache
- Graceful error messages for unavailable features
- Automatic sync when connection restored

## Browser Support
- **Chrome/Edge**: Full PWA support including installation
- **Safari**: iOS 11.3+ with Add to Home Screen
- **Firefox**: Service worker support, limited install prompt
- **Mobile Browsers**: Full responsive experience

## Performance Benefits
- **Faster Loading**: Cached assets load instantly
- **Reduced Bandwidth**: Static resources served from cache
- **Offline Access**: Core functionality available without network
- **App-Like Experience**: Full-screen standalone mode

## Next Steps
- Monitor PWA metrics and user adoption
- Add push notification support (service worker ready)
- Implement data sync for offline updates
- Consider additional offline functionality