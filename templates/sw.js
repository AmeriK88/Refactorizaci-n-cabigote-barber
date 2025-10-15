// sw.js — Cabigote PWA
// feat(pwa,csp,offline): stabilize offline flow, harden CSP, and align offline page with site styles

// Bump this when you change offline.html or caching logic to force recache
const SW_VERSION = 'v3';
const CACHE_NAME = `offline-cache-${SW_VERSION}`;

// Use absolute origin-based URL to avoid scope surprises
const OFFLINE_URL = new URL('/offline.html', self.location.origin).pathname;

// Routes the SW must never intercept (auth/admin)
const IGNORE_PATHS = [
  '/accounts/',  // allauth (logins, callbacks…)
  '/admin/',     // Django admin
];

// ---- INSTALL: precache only the offline page, but never break install on failure
self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    try {
      const req = new Request(OFFLINE_URL, { cache: 'reload' });
      const res = await fetch(req);
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      await cache.put(req, res.clone());
      console.log('[SW] offline precached OK');
    } catch (err) {
      console.warn('[SW] Failed to precache OFFLINE_URL:', OFFLINE_URL, err);
    }
    self.skipWaiting();
  })());
});

// ---- ACTIVATE: clean old caches and take control immediately
self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(
      keys.map((k) => (k !== CACHE_NAME ? caches.delete(k) : Promise.resolve()))
    );
    await self.clients.claim();
  })());
});

// ---- FETCH (navigation only): network-first with offline fallback
self.addEventListener('fetch', (event) => {
  // Only handle top-level navigations to our own origin
  if (
    event.request.mode !== 'navigate' ||
    event.request.method !== 'GET' ||
    !event.request.url.startsWith(self.location.origin)
  ) {
    return; // Let the browser handle all other requests
  }

  // Bypass critical paths (auth/admin) completely
  if (IGNORE_PATHS.some((p) => event.request.url.includes(p))) {
    return;
  }

  event.respondWith(
    (async () => {
      try {
        // Try network first for fresh content
        return await fetch(event.request);
      } catch {
        // If offline or network fails, serve the offline page (if cached)
        const cached = await caches.match(OFFLINE_URL);
        return cached || Response.error();
      }
    })()
  );
});
