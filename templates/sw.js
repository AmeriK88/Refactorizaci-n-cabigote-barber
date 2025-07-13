// templates/sw.js
self.addEventListener('install', event => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  clients.claim();
});

// Simple offline fallback
self.addEventListener('fetch', event => {
  event.respondWith(fetch(event.request).catch(() => caches.match('/offline.html')));
});
