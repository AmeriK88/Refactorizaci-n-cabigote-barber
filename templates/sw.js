const CACHE_NAME  = 'offline-cache-v1';
const OFFLINE_URL = '/offline.html';

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
          .then(cache =>
            cache.add(new Request(OFFLINE_URL, {cache: 'reload'}))
          )
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => event.waitUntil(clients.claim()));

self.addEventListener('fetch', event => {

  // Interceptamos SOLAMENTE navegaciones de nuestro dominio
  // excluyendo todo lo que empiece por /accounts/  (allauth)
  if (
      event.request.mode   === 'navigate' &&
      event.request.method === 'GET'      &&
      event.request.url.startsWith(self.location.origin) &&
      !event.request.url.includes('/accounts/')
  ) {

    event.respondWith(
      fetch(event.request)
        .then(resp => {
          //  Si la respuesta es redirect → la dejamos pasar
          if (resp.type === 'opaqueredirect' || resp.redirected) {
            return resp;
          }
          return resp;           // normal
        })
        .catch(() => caches.match(OFFLINE_URL))   // solo sin red
    );
  }
  // Todo lo demás (Google OAuth, APIs…) lo maneja el navegador
});
