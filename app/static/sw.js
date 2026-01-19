// Service Worker for HTStatus PWA
// Cache strategy: Cache First for static assets, Network First for dynamic content

const CACHE_NAME = 'htstatus-v1';
const STATIC_CACHE = 'htstatus-static-v1';
const DYNAMIC_CACHE = 'htstatus-dynamic-v1';

// Core files to cache immediately
const CORE_ASSETS = [
  '/',
  '/static/Chart.bundle.js',
  '/static/jsuites.js',
  '/static/jsuites.css',
  '/static/ico.png',
  '/static/soccer_ball.png',
  '/static/background.jpg',
  '/static/plotly-latest.min.js',
  '/static/Sortable.js'
];

// Routes to cache for offline access
const CACHE_ROUTES = [
  '/',
  '/player',
  '/team',
  '/matches',
  '/training',
  '/settings'
];

// Install event - cache core assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE)
            .map(cacheName => caches.delete(cacheName))
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - implement caching strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Static assets - Cache First
  if (request.url.includes('/static/')) {
    event.respondWith(
      caches.match(request)
        .then(response => {
          return response || fetch(request)
            .then(fetchResponse => {
              const responseClone = fetchResponse.clone();
              caches.open(STATIC_CACHE)
                .then(cache => cache.put(request, responseClone));
              return fetchResponse;
            });
        })
        .catch(() => {
          // Offline fallback for static assets
          if (request.url.includes('.js')) {
            return new Response('// Offline - JS file unavailable', {
              headers: { 'Content-Type': 'application/javascript' }
            });
          }
          if (request.url.includes('.css')) {
            return new Response('/* Offline - CSS file unavailable */', {
              headers: { 'Content-Type': 'text/css' }
            });
          }
        })
    );
    return;
  }

  // Core routes - Network First with cache fallback
  if (CACHE_ROUTES.includes(url.pathname)) {
    event.respondWith(
      fetch(request)
        .then(response => {
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE)
            .then(cache => cache.put(request, responseClone));
          return response;
        })
        .catch(() => {
          return caches.match(request)
            .then(response => {
              return response || caches.match('/')
                .then(fallback => fallback || new Response(
                  '<!DOCTYPE html><html><head><title>HTStatus - Offline</title></head>' +
                  '<body><h1>HTStatus</h1><p>You are offline. Please check your connection.</p></body></html>',
                  { headers: { 'Content-Type': 'text/html' } }
                ));
            });
        })
    );
    return;
  }

  // API requests - Network only (no caching for dynamic data)
  if (request.url.includes('/api/') || request.url.includes('/update')) {
    event.respondWith(
      fetch(request)
        .catch(() => new Response('{"error": "Offline - API unavailable"}', {
          headers: { 'Content-Type': 'application/json' }
        }))
    );
    return;
  }
});

// Background sync for data updates when online
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(
      // Clear dynamic cache to force fresh data on next visit
      caches.delete(DYNAMIC_CACHE)
    );
  }
});

// Push notification support (future enhancement)
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/static/ico.png',
      badge: '/static/soccer_ball.png'
    });
  }
});