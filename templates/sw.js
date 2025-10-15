const CACHE_NAME  = 'offline-cache-v2';
const OFFLINE_URL = '/offline.html';

// Rutas que el SW jamás debe interceptar (OAuth, admin, etc.)
const IGNORE_PATHS = [
  '/accounts/',        // allauth (login‑social, callbacks…)
  '/admin/',           // panel Django
];

self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_NAME);
    try {
      const req = new Request(OFFLINE_URL, { cache: 'reload' });
      const res = await fetch(req);
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      await cache.put(req, res.clone());
      console.log('[SW] offline precached OK');
    } catch (err) {
      console.warn('[SW] No se pudo cachear OFFLINE_URL:', OFFLINE_URL, err);
    }
    self.skipWaiting();
  })());
});


self.addEventListener('activate',  e => e.waitUntil(clients.claim()));

// ────────── NAVIGATION FETCH ──────────
self.addEventListener('fetch', event => {

  // Sólo navegaciones a *nuestro* origen
  if (event.request.mode !== 'navigate' ||
      event.request.method !== 'GET'    ||
      !event.request.url.startsWith(self.location.origin)) {
    return;                     // deja que el navegador lo gestione
  }

  // ¿Está en la lista de rutas ignoradas?
  if (IGNORE_PATHS.some(path => event.request.url.includes(path))) {
    return;                     // ni cache ni offline: by‑pass total
  }

  event.respondWith(
    fetch(event.request)
      .catch(() => caches.match(OFFLINE_URL))
  );
});
